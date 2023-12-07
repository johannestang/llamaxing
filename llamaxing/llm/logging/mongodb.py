from llm.logging import LoggingClientInterface
from logging_utils import log_exception
from motor.motor_asyncio import AsyncIOMotorClient
from settings import settings


class LoggingClient(LoggingClientInterface):
    def __init__(self) -> None:
        self.client = AsyncIOMotorClient(settings.logging_client_mongodb_uri)
        self.db = self.client[settings.logging_client_mongodb_db_name]
        self.collection = self.db["apicalls"]

    async def on_shutdown(self):
        self.client.close()

    async def log_api_call(self, endpoint, metadata, request, response):
        try:
            await self.collection.insert_one(
                {
                    "endpoint": endpoint,
                    "metadata": metadata,
                    "request": request,
                    "response": response,
                }
            )
        except Exception:
            log_exception()
