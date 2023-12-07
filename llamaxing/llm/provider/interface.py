from abc import ABC, abstractmethod

from httpx import AsyncClient
from identity import Identity
from llm.logging import LoggingClientInterface
from observability import ObservabilityClientInterface


class LLMProviderInterface(ABC):
    @staticmethod
    @abstractmethod
    async def chat_completions(
        data,
        identity: Identity,
        requests_client: AsyncClient,
        endpoint_params: dict,
        logging_client: LoggingClientInterface,
        observability_client: ObservabilityClientInterface,
    ):
        pass

    @staticmethod
    @abstractmethod
    async def completions(
        data,
        identity: Identity,
        requests_client: AsyncClient,
        endpoint_params: dict,
        logging_client: LoggingClientInterface,
        observability_client: ObservabilityClientInterface,
    ):
        pass

    @staticmethod
    @abstractmethod
    async def embeddings(
        data,
        identity: Identity,
        requests_client: AsyncClient,
        endpoint_params: dict,
        logging_client: LoggingClientInterface,
        observability_client: ObservabilityClientInterface,
    ):
        pass

    @staticmethod
    @abstractmethod
    async def images_generations(
        data,
        identity: Identity,
        requests_client: AsyncClient,
        endpoint_params: dict,
        logging_client: LoggingClientInterface,
        observability_client: ObservabilityClientInterface,
    ):
        pass
