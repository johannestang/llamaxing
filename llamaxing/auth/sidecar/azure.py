from auth.sidecar import AuthenticationInterface
from azure.identity.aio import DefaultAzureCredential
from sidecar_settings import settings


class Authentication(AuthenticationInterface):
    def on_startup(self):
        self.scope = settings.sidecar_auth_method_azure_scope
        self.credential = DefaultAzureCredential()

    async def on_shutdown(self):
        await self.credential.close()

    async def get_headers(self):
        token = await self.credential.get_token(self.scope)
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token.token}",
        }
