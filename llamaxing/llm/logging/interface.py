from abc import ABC, abstractmethod


class LoggingClientInterface(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    async def on_shutdown(self):
        pass

    @abstractmethod
    async def log_api_call(self, endpoint, metadata, request, response):
        pass
