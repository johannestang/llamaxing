from urllib.parse import urljoin

from httpx import AsyncClient
from identity import Identity
from llm import (
    chat_completions_wrapper,
    completions_wrapper,
    embeddings_wrapper,
    images_generations_wrapper,
)
from llm.logging import LoggingClientInterface
from llm.provider import LLMProviderInterface
from observability import ObservabilityClientInterface


class LLMProvider(LLMProviderInterface):
    @staticmethod
    async def chat_completions(
        data,
        identity: Identity,
        requests_client: AsyncClient,
        endpoint_params: dict,
        logging_client: LoggingClientInterface = None,
        observability_client: ObservabilityClientInterface = None,
    ):
        url = urljoin(
            endpoint_params["azure_endpoint"],
            (
                f"/openai/deployments/{endpoint_params['azure_deployment']}"
                f"/chat/completions?api-version={endpoint_params['azure_api_version']}"
            ),
        )
        headers = {
            "api-key": endpoint_params["azure_api_key"],
            "Content-Type": "application/json",
        }
        return await chat_completions_wrapper(
            data,
            url,
            headers,
            requests_client,
            identity,
            logging_client,
            observability_client,
        )

    @staticmethod
    async def completions(
        data,
        identity: Identity,
        requests_client: AsyncClient,
        endpoint_params: dict,
        logging_client: LoggingClientInterface = None,
        observability_client: ObservabilityClientInterface = None,
    ):
        url = urljoin(
            endpoint_params["azure_endpoint"],
            (
                f"/openai/deployments/{endpoint_params['azure_deployment']}"
                f"/completions?api-version={endpoint_params['azure_api_version']}"
            ),
        )
        headers = {
            "api-key": endpoint_params["azure_api_key"],
            "Content-Type": "application/json",
        }
        return await completions_wrapper(
            data,
            url,
            headers,
            requests_client,
            identity,
            logging_client,
            observability_client,
        )

    @staticmethod
    async def embeddings(
        data,
        identity: Identity,
        requests_client: AsyncClient,
        endpoint_params: dict,
        logging_client: LoggingClientInterface = None,
        observability_client: ObservabilityClientInterface = None,
    ):
        url = urljoin(
            endpoint_params["azure_endpoint"],
            (
                f"/openai/deployments/{endpoint_params['azure_deployment']}"
                f"/embeddings?api-version={endpoint_params['azure_api_version']}"
            ),
        )
        headers = {
            "api-key": endpoint_params["azure_api_key"],
            "Content-Type": "application/json",
        }
        return await embeddings_wrapper(
            data,
            url,
            headers,
            requests_client,
            identity,
            logging_client,
            observability_client,
        )

    @staticmethod
    async def images_generations(
        data,
        identity: Identity,
        requests_client: AsyncClient,
        endpoint_params: dict,
        logging_client: LoggingClientInterface = None,
        observability_client: ObservabilityClientInterface = None,
    ):
        url = urljoin(
            endpoint_params["azure_endpoint"],
            (
                f"/openai/deployments/{endpoint_params['azure_deployment']}/images/"
                f"/generations?api-version={endpoint_params['azure_api_version']}"
            ),
        )
        headers = {
            "api-key": endpoint_params["azure_api_key"],
            "Content-Type": "application/json",
        }
        return await images_generations_wrapper(
            data,
            url,
            headers,
            requests_client,
            identity,
            logging_client,
            observability_client,
        )
