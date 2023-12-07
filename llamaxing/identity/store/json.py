import json

from identity.identity import Identity
from identity.store.interface import IdentityStoreInterface
from settings import settings


class IdentityStore(IdentityStoreInterface):
    def __init__(self) -> None:
        with open(settings.identity_store_json_filename) as f:
            self.identities = json.load(f)

    def find_identity(self, key) -> Identity:
        id = next((id for id in self.identities if id["auth_key"] == key), None)
        if id is not None:
            return Identity.model_validate(id)
        return None
