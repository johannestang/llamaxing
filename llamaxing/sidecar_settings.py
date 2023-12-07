from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sidecar_app_name: str = "llamaxing sidecar proxy"
    sidecar_app_requests_timeout: int = 300
    sidecar_upstream_url: str
    sidecar_auth_method: str
    sidecar_auth_method_azure_scope: str | None = None
    sidecar_auth_method_apikey_key: str | None = None


settings = Settings(_env_file=".env-sidecar")
