import copy
import json
from datetime import datetime, timezone
from functools import partial

from httpx import AsyncClient
from identity import Identity
from llm.logging import LoggingClientInterface
from llm.utils.openai import num_tokens_from_messages, num_tokens_from_string
from llm.utils.responses import LoggingStreamingResponse
from logging_utils import log_exception, logger
from nested_lookup import nested_alter
from observability import ObservabilityClientInterface
from settings import settings
from starlette.background import BackgroundTask, BackgroundTasks
from starlette.responses import JSONResponse


def trim_url(url: str):
    if url[:10] == "data:image":
        return url[:30] + "...[truncated]"
    return url


def trim_data(data: dict):
    trimmed_data = copy.deepcopy(data)
    trimmed_data = nested_alter(trimmed_data, "url", trim_url)
    trimmed_data = nested_alter(
        trimmed_data, "b64_json", lambda x: x[:10] + "...[truncated]"
    )
    return trimmed_data


async def chat_completions_wrapper(
    data: dict,
    url: str,
    headers: dict,
    requests_client: AsyncClient,
    identity: Identity = None,
    logging_client: LoggingClientInterface = None,
    observability_client: ObservabilityClientInterface = None,
    sidecar_mode: bool = False,
):
    trimmed_request = trim_data(data)
    logger.debug(f"Chat completion request: {trimmed_request}")
    if not sidecar_mode:
        request_start_time = datetime.now(timezone.utc)
        observation_metadata = data.pop("observation_metadata", None)

    request = requests_client.build_request(
        "POST", url, headers=headers, data=json.dumps(data)
    )

    if logging_client is not None:
        logging_call = partial(
            logging_client.log_api_call,
            endpoint="chat_completions",
            metadata={"caller": identity.model_dump()},
            request=trimmed_request,
        )
    else:
        logging_call = None
    if observability_client is not None:
        observability_call = partial(
            observability_client.chat_completions,
            identity=identity,
            metadata=observation_metadata,
            request=trimmed_request,
            start_time=request_start_time,
        )
    else:
        observability_call = None

    if "stream" in data and data["stream"] is True:
        try:
            prompt_tokens = num_tokens_from_messages(data["messages"], data["model"])
        except Exception:
            log_exception()
            prompt_tokens = None
        r = await requests_client.send(request, stream=True)
        return LoggingStreamingResponse(
            r.aiter_raw(),
            status_code=r.status_code,
            headers=r.headers,
            background=BackgroundTask(r.aclose),
            logger=logger,
            prompt_tokens=prompt_tokens,
            object_type="chat.completion.chunk",
            logging_call=logging_call,
            observability_call=observability_call,
        )
    else:
        r = await requests_client.send(request)
        response = r.json()
        trimmed_response = trim_data(response)
        request_end_time = datetime.now(timezone.utc)
        logger.debug(f"Chat completion response: {trimmed_response}")
        background_tasks = BackgroundTasks()
        if observability_client is not None:
            background_tasks.add_task(
                partial(
                    observability_call,
                    response=trimmed_response,
                    end_time=request_end_time,
                )
            )
        if logging_client is not None:
            background_tasks.add_task(partial(logging_call, response=trimmed_response))
        return JSONResponse(response, background=background_tasks)


async def completions_wrapper(
    data: dict,
    url: str,
    headers: dict,
    requests_client: AsyncClient,
    identity: Identity = None,
    logging_client: LoggingClientInterface = None,
    observability_client: ObservabilityClientInterface = None,
    sidecar_mode: bool = False,
):
    logger.debug(f"Completion request: {data}")
    if not sidecar_mode:
        request_start_time = datetime.now(timezone.utc)
        observation_metadata = data.pop("observation_metadata", None)

    request = requests_client.build_request(
        "POST", url, headers=headers, data=json.dumps(data)
    )

    if logging_client is not None:
        logging_call = partial(
            logging_client.log_api_call,
            endpoint="completions",
            metadata={"caller": identity.model_dump()},
            request=data,
        )
    else:
        logging_call = None
    if observability_client is not None:
        observability_call = partial(
            observability_client.completions,
            identity=identity,
            metadata=observation_metadata,
            request=data,
            start_time=request_start_time,
        )
    else:
        observability_call = None

    if "stream" in data and data["stream"] is True:
        prompt_tokens = num_tokens_from_string(data["prompt"], data["model"])
        r = await requests_client.send(request, stream=True)
        return LoggingStreamingResponse(
            r.aiter_raw(),
            status_code=r.status_code,
            headers=r.headers,
            background=BackgroundTask(r.aclose),
            logger=logger,
            prompt_tokens=prompt_tokens,
            object_type="text_completion",
            logging_call=logging_call,
            observability_call=observability_call,
        )
    else:
        r = await requests_client.send(request)
        response = r.json()
        request_end_time = datetime.now(timezone.utc)
        logger.debug(f"Completion response: {response}")
        background_tasks = BackgroundTasks()
        if observability_client is not None:
            background_tasks.add_task(
                partial(
                    observability_call, response=response, end_time=request_end_time
                )
            )
        if logging_client is not None:
            background_tasks.add_task(partial(logging_call, response=response))
        return JSONResponse(response, background=background_tasks)


async def embeddings_wrapper(
    data: dict,
    url: str,
    headers: dict,
    requests_client: AsyncClient,
    identity: Identity = None,
    logging_client: LoggingClientInterface = None,
    observability_client: ObservabilityClientInterface = None,
    sidecar_mode: bool = False,
):
    logger.debug(f"Embeddings request: {data}")
    if not sidecar_mode:
        request_start_time = datetime.now(timezone.utc)
        observation_metadata = data.pop("observation_metadata", None)
    response = await requests_client.post(
        url,
        data=json.dumps(data),
        headers=headers,
    )
    response = response.json()
    if settings.debug_level > 0:
        trimmed_response = copy.deepcopy(response)
        for d in trimmed_response["data"]:
            d["embedding"] = d["embedding"][:5]
        logger.debug(f"Embeddings response: {trimmed_response}")
    request_end_time = datetime.now(timezone.utc)

    background_tasks = BackgroundTasks()
    if logging_client is not None:
        background_tasks.add_task(
            partial(
                logging_client.log_api_call,
                "embeddings",
                {"caller": identity.model_dump()},
                data,
                response,
            )
        )
    if observability_client is not None:
        background_tasks.add_task(
            partial(
                observability_client.embeddings,
                identity=identity,
                metadata=observation_metadata,
                request=data,
                start_time=request_start_time,
                response=response,
                end_time=request_end_time,
            )
        )
    return JSONResponse(response, background=background_tasks)


async def images_generations_wrapper(
    data: dict,
    url: str,
    headers: dict,
    requests_client: AsyncClient,
    identity: Identity = None,
    logging_client: LoggingClientInterface = None,
    observability_client: ObservabilityClientInterface = None,
    sidecar_mode: bool = False,
):
    logger.debug(f"Images generations request: {data}")
    if not sidecar_mode:
        request_start_time = datetime.now(timezone.utc)
        observation_metadata = data.pop("observation_metadata", None)
    response = await requests_client.post(
        url,
        data=json.dumps(data),
        headers=headers,
    )
    response = response.json()
    trimmed_response = trim_data(response)
    logger.debug(f"Images generations response: {trimmed_response}")
    request_end_time = datetime.now(timezone.utc)

    background_tasks = BackgroundTasks()
    if logging_client is not None:
        background_tasks.add_task(
            partial(
                logging_client.log_api_call,
                "images_generations",
                {"caller": identity.model_dump()},
                data,
                trimmed_response,
            )
        )
    if observability_client is not None:
        background_tasks.add_task(
            partial(
                observability_client.images_generations,
                identity=identity,
                metadata=observation_metadata,
                request=data,
                start_time=request_start_time,
                response=trimmed_response,
                end_time=request_end_time,
            )
        )
    return JSONResponse(response, background=background_tasks)
