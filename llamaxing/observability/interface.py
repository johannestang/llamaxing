from abc import ABC, abstractmethod
from datetime import datetime

from identity import Identity


class ObservabilityClientInterface(ABC):
    @abstractmethod
    def on_startup(self):
        pass

    @abstractmethod
    async def on_shutdown(self):
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass
