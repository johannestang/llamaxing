from auth.sidecar import AuthenticationInterface
from sidecar_settings import settings


class Authentication(AuthenticationInterface):
    async def get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.sidecar_auth_method_apikey_key}",
        }
