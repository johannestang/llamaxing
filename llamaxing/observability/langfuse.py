from datetime import datetime
from uuid import uuid4

import pydash
from identity import Identity
from langfuse import Langfuse
from logging_utils import log_exception
from observability.interface import ObservabilityClientInterface
from settings import settings


class ObservabilityClient(ObservabilityClientInterface):
    def __init__(self) -> None:
        self.langfuse_clients = {}

    def get_langfuse_client(self, identity: Identity):
        if identity.id not in self.langfuse_clients:
            self.langfuse_clients[identity.id] = Langfuse(
                host=settings.observability_client_langfuse_host,
                public_key=identity.observability.langfuse_public_key.get_secret_value(),  # noqa E501
                secret_key=identity.observability.langfuse_secret_key.get_secret_value(),  # noqa E501
            )
        return self.langfuse_clients[identity.id]

    def on_startup(self):
        pass

    async def on_shutdown(self):
        for _, lc in self.langfuse_clients.items():
            lc.flush()

    async def completions(
        self,
        identity: Identity,
        metadata: dict,
        request: dict,
        response: dict,
        start_time: datetime,
        end_time: datetime,
        completion_start_time: datetime | None = None,
    ):
        if identity.observability is not None:
            if metadata is None:
                metadata = {}
            model_params_keys = [
                "best_of",
                "echo",
                "frequency_penalty",
                "logprobs",
                "max_tokens",
                "n",
                "presence_penalty",
                "seed",
                "stop",
                "stream",
                "suffix",
                "temperature",
                "top_p",
            ]
            model_params = {}
            for key in model_params_keys:
                if key in request and request[key] is not None:
                    model_params[key] = request[key]
            response_format = pydash.get(request, "response.format.type")
            if response_format is not None:
                model_params["response_format"] = response_format
            try:
                langfuse = self.get_langfuse_client(identity)
                trace = langfuse.trace(
                    id=metadata.pop("trace_id", str(uuid4())),
                    name=metadata.pop("trace_name", None),
                    tags=metadata.pop("trace_tags", None),
                    metadata=metadata.pop("trace_metadata", None),
                    user_id=identity.id,
                )
                trace.generation(
                    id=metadata.pop("generation_id", str(uuid4())),
                    start_time=start_time,
                    end_time=end_time,
                    completion_start_time=completion_start_time,
                    model=request["model"],
                    model_parameters=model_params,
                    input=request["messages"],
                    output=response["choices"][0]["message"],
                    usage=response["usage"],
                    name=metadata.pop("name", None),
                    status_message=metadata.pop("status_message", None),
                    metadata=metadata,
                )
            except Exception:
                log_exception()

    async def chat_completions(
        self,
        identity: Identity,
        metadata: dict,
        request: dict,
        response: dict,
        start_time: datetime,
        end_time: datetime,
        completion_start_time: datetime | None = None,
    ):
        if identity.observability is not None:
            if metadata is None:
                metadata = {}
            model_params_keys = [
                "max_tokens",
                "temperature",
                "n",
                "stream",
                "frequency_penalty",
                "logprobs",
                "top_logprobs",
                "presence_penalty",
                "seed",
                "stop",
                "top_p",
            ]
            model_params = {}
            for key in model_params_keys:
                if key in request and request[key] is not None:
                    model_params[key] = request[key]
            response_format = pydash.get(request, "response.format.type")
            if response_format is not None:
                model_params["response_format"] = response_format
            try:
                langfuse = self.get_langfuse_client(identity)
                trace = langfuse.trace(
                    id=metadata.pop("trace_id", str(uuid4())),
                    name=metadata.pop("trace_name", None),
                    tags=metadata.pop("trace_tags", None),
                    metadata=metadata.pop("trace_metadata", None),
                    user_id=identity.id,
                )
                trace.generation(
                    id=metadata.pop("generation_id", str(uuid4())),
                    start_time=start_time,
                    end_time=end_time,
                    completion_start_time=completion_start_time,
                    model=request["model"],
                    model_parameters=model_params,
                    input=request["messages"],
                    output=response["choices"][0]["message"],
                    usage=response.get("usage"),
                    name=metadata.pop("name", None),
                    status_message=metadata.pop("status_message", None),
                    metadata=metadata,
                )
            except Exception:
                log_exception()

    async def embeddings(
        self,
        identity: Identity,
        metadata: dict,
        request: dict,
        response: dict,
        start_time: datetime,
        end_time: datetime,
        completion_start_time: datetime | None = None,
    ):
        if identity.observability is not None:
            if metadata is None:
                metadata = {}
            model_params_keys = [
                "encoding_format" "dimensions",
            ]
            model_params = {}
            for key in model_params_keys:
                if key in request and request[key] is not None:
                    model_params[key] = request[key]
            try:
                langfuse = self.get_langfuse_client(identity)
                trace = langfuse.trace(
                    id=metadata.pop("trace_id", str(uuid4())),
                    name=metadata.pop("trace_name", None),
                    tags=metadata.pop("trace_tags", None),
                    metadata=metadata.pop("trace_metadata", None),
                    user_id=identity.id,
                )
                trace.generation(
                    id=metadata.pop("generation_id", str(uuid4())),
                    start_time=start_time,
                    end_time=end_time,
                    completion_start_time=completion_start_time,
                    model=request["model"],
                    model_parameters=model_params,
                    input=request["input"],
                    usage=response["usage"],
                    name=metadata.pop("name", None),
                    status_message=metadata.pop("status_message", None),
                    metadata=metadata,
                )
            except Exception:
                log_exception()

    async def images_generations(
        self,
        identity: Identity,
        metadata: dict,
        request: dict,
        response: dict,
        start_time: datetime,
        end_time: datetime,
        completion_start_time: datetime | None = None,
    ):
        if identity.observability is not None:
            if metadata is None:
                metadata = {}
            model_params_keys = ["n" "quality", "response_format", "size", "style"]
            model_params = {}
            for key in model_params_keys:
                if key in request and request[key] is not None:
                    model_params[key] = request[key]
            try:
                langfuse = self.get_langfuse_client(identity)
                trace = langfuse.trace(
                    id=metadata.pop("trace_id", str(uuid4())),
                    name=metadata.pop("trace_name", None),
                    tags=metadata.pop("trace_tags", None),
                    metadata=metadata.pop("trace_metadata", None),
                    user_id=identity.id,
                )
                trace.generation(
                    id=metadata.pop("generation_id", str(uuid4())),
                    start_time=start_time,
                    end_time=end_time,
                    completion_start_time=completion_start_time,
                    model=request["model"],
                    model_parameters=model_params,
                    input=request["prompt"],
                    output=response["data"],
                    usage={"total": len(response["data"]), "unit": "IMAGES"},
                    name=metadata.pop("name", None),
                    status_message=metadata.pop("status_message", None),
                    metadata=metadata,
                )
            except Exception:
                log_exception()
