from abc import ABC, abstractmethod

from fastapi import Request
from identity.store import IdentityStoreInterface


class AuthHandlerInterface(ABC):
    def __init__(self, identity_store: IdentityStoreInterface):
        self.identity_store = identity_store

    @abstractmethod
    def __call__(self, request: Request):
        pass
