from identity.identity import Identity
from identity.store.interface import IdentityStoreInterface


class IdentityStore(IdentityStoreInterface):
    def __init__(self) -> None:
        pass

    def find_identity(self, key) -> Identity:
        raise Exception(
            "App is configured to not use an identity store. "
            "This should not have been called."
        )
