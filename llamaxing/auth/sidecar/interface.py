from abc import ABC, abstractmethod


class AuthenticationInterface(ABC):
    @abstractmethod
    def on_startup(self):
        pass

    @abstractmethod
    async def on_shutdown(self):
        pass

    @abstractmethod
    async def get_headers(self):
        pass
