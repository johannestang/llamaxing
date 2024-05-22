import logging
import typing
from datetime import datetime, timezone
from functools import partial

import anyio
from llm.utils.openai import merge_response_chunks
from logging_utils import log_exception
from starlette.background import BackgroundTask
from starlette.concurrency import iterate_in_threadpool
from starlette.responses import Response
from starlette.types import Receive, Scope, Send

Content = str | bytes
SyncContentStream = typing.Iterator[Content]
AsyncContentStream = typing.AsyncIterable[Content]
ContentStream = AsyncContentStream | SyncContentStream


class LoggingStreamingResponse(Response):
    body_iterator: AsyncContentStream

    def __init__(
        self,
        content: ContentStream,
        status_code: int = 200,
        headers: typing.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
        logger: logging.Logger | None = None,
        log_level: int = 0,
        prompt_tokens: int = 0,
        object_type: str = "chat.completion.chunk",
        logging_call: typing.Callable | None = None,
        observability_call: typing.Callable | None = None,
    ) -> None:
        if isinstance(content, typing.AsyncIterable):
            self.body_iterator = content
        else:
            self.body_iterator = iterate_in_threadpool(content)
        self.status_code = status_code
        self.media_type = self.media_type if media_type is None else media_type
        self.background = background
        self.init_headers(headers)
        self.logger = logger
        self.log_level = log_level
        self.prompt_tokens = prompt_tokens
        self.object_type = object_type
        self.logging_call = logging_call
        self.observability_call = observability_call
        self.response_chunks = []
        self.completion_start_time = None
        self.request_end_time = None

    async def listen_for_disconnect(self, receive: Receive) -> None:
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                break

    async def stream_response(self, send: Send) -> None:
        self.completion_start_time = datetime.now(timezone.utc)
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        async for chunk in self.body_iterator:
            if not isinstance(chunk, bytes):
                chunk = chunk.encode(self.charset)
            if self.log_level >= 2:
                self.logger.debug(f"Stream chunk: {chunk}")
            self.response_chunks.append(chunk.decode(self.charset))
            await send({"type": "http.response.body", "body": chunk, "more_body": True})

        await send({"type": "http.response.body", "body": b"", "more_body": False})

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async with anyio.create_task_group() as task_group:

            async def wrap(func: "typing.Callable[[], typing.Awaitable[None]]") -> None:
                await func()
                task_group.cancel_scope.cancel()

            task_group.start_soon(wrap, partial(self.stream_response, send))
            await wrap(partial(self.listen_for_disconnect, receive))

        self.request_end_time = datetime.now(timezone.utc)

        if self.background is not None:
            await self.background()

        await self.log_response()

    async def log_response(self):
        if (
            self.logging_call is not None
            or self.observability_call is not None
            or self.log_level > 0
        ):
            try:
                m = merge_response_chunks(
                    self.response_chunks, object_type=self.object_type
                )
            except Exception:
                self.logger.warning("Failed to merge response chunks")
                log_exception()
                return

            if "usage" in m and isinstance(self.prompt_tokens, int):
                m["usage"]["prompt_tokens"] = self.prompt_tokens
                m["usage"]["total_tokens"] = (
                    m["usage"]["completion_tokens"] + self.prompt_tokens
                )
            if self.logger:
                self.logger.debug(f"Stream response: {m}")
            if self.logging_call:
                try:
                    await self.logging_call(response=m)
                except Exception:
                    self.logger.warning("Failed to log response")
                    log_exception()
            if self.observability_call:
                try:
                    await self.observability_call(
                        response=m,
                        completion_start_time=self.completion_start_time,
                        end_time=self.request_end_time,
                    )
                except Exception:
                    self.logger.warning("Failed to make observability call")
                    log_exception()
