from auth import AuthHandlerInterface
from fastapi import Request
from identity import Identity


class AuthHandler(AuthHandlerInterface):
    def __call__(self, request: Request):
        identity = Identity(id="anonymous", name="Anonymous")
        return identity
