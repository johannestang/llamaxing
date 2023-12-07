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
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": "Bearer " + endpoint_params["openai_api_key"],
            "Content-Type": "application/json",
        }
        org = endpoint_params.get("openai_organization")
        if org is not None and len(org) > 0:
            headers = headers | {"OpenAI-Organization": org}

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
        url = "https://api.openai.com/v1/completions"
        headers = {
            "Authorization": "Bearer " + endpoint_params["openai_api_key"],
            "Content-Type": "application/json",
        }
        org = endpoint_params.get("openai_organization")
        if org is not None and len(org) > 0:
            headers = headers | {"OpenAI-Organization": org}

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
        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": "Bearer " + endpoint_params["openai_api_key"],
            "Content-Type": "application/json",
        }
        org = endpoint_params.get("openai_organization")
        if org is not None and len(org) > 0:
            headers = headers | {"OpenAI-Organization": org}

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
        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Authorization": "Bearer " + endpoint_params["openai_api_key"],
            "Content-Type": "application/json",
        }
        org = endpoint_params.get("openai_organization")
        if org is not None and len(org) > 0:
            headers = headers | {"OpenAI-Organization": org}

        return await images_generations_wrapper(
            data,
            url,
            headers,
            requests_client,
            identity,
            logging_client,
            observability_client,
        )
