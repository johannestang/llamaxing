from llm.logging import LoggingClientInterface


class LoggingClient(LoggingClientInterface):
    def __init__(self) -> None:
        pass

    async def on_shutdown(self):
        pass

    async def log_api_call(self, endpoint, metadata, request, response):
        pass
