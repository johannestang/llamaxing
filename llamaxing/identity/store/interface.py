from abc import ABC, abstractmethod

from identity.identity import Identity


class IdentityStoreInterface(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def find_identity(self, key) -> Identity:
        pass
