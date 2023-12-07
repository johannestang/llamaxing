import json
import os
import random
from importlib import import_module

from fastapi import HTTPException
from httpx import AsyncClient
from identity import Identity
from llm.logging import LoggingClientInterface
from observability import ObservabilityClientInterface
from settings import settings


class LLMDispatcher:
    def __init__(self) -> None:
        self.load_models()

    def load_models(self):
        with open("models.json") as f:
            models = json.load(f)
        model_list = []
        for m in models:
            item = m.copy()
            aliases = item.pop("aliases")
            for instance in item["instances"]:
                if "azure_api_key" in instance:
                    instance["azure_api_key"] = os.path.expandvars(
                        instance["azure_api_key"]
                    )
                if "azure_endpoint" in instance:
                    instance["azure_endpoint"] = os.path.expandvars(
                        instance["azure_endpoint"]
                    )
                if "openai_api_key" in instance:
                    instance["openai_api_key"] = os.path.expandvars(
                        instance["openai_api_key"]
                    )
            model_list.append(item)
            if len(aliases) > 0:
                for a in aliases:
                    alias = item.copy()
                    alias["id"] = a
                    model_list.append(alias)
        self.models = model_list

    def get_models(self):
        return {
            "data": [
                {
                    "id": x["id"],
                    "capabilities": x["capabilities"],
                    "object": "model",
                    "proxied_by": settings.app_name,
                }
                for x in self.models
            ],
            "object": "list",
        }

    def get_model(self, id):
        m = next((model for model in self.models if model["id"] == id), None)
        return m

    async def call(
        self,
        endpoint: str,
        data: dict,
        identity: Identity,
        requests_client: AsyncClient,
        logging_client: LoggingClientInterface = None,
        observability_client: ObservabilityClientInterface = None,
    ):
        if "model" not in data:
            raise HTTPException(400, "No model specified in request")

        model = self.get_model(data["model"])
        if model is None:
            raise HTTPException(404, detail="Model not found")

        if endpoint not in model["capabilities"]:
            raise HTTPException(405, detail="Model not valid for this endpoint")

        # Naive load balancing
        model_instance = random.choice(model["instances"])

        llm_provider_module = import_module(
            f"llm.provider.{model_instance['provider']}"
        )
        llm_provider = llm_provider_module.LLMProvider
        method = getattr(llm_provider, endpoint)
        return await method(
            data,
            identity,
            requests_client,
            model_instance,
            logging_client,
            observability_client,
        )
