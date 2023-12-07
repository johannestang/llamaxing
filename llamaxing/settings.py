from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "llamaxing"
    app_mode: str = "gateway"
    app_requests_timeout: int = 300
    debug_level: int = 0
    auth_method: str = "none"
    auth_method_apikey_header_name: str = "Authorization"
    auth_method_jwt_header_name: str = "Authorization"
    auth_method_jwt_id_key: str = "oid"
    auth_method_jwt_verify_signature: bool = False
    auth_method_jwt_jwks_uri: str | None = None
    auth_method_jwt_issuer: str | None = None
    auth_method_jwt_audience: str | None = None
    identity_store: str = "none"
    identity_store_json_filename: str | None = "identities.json"
    logging_client: str = "none"
    logging_client_mongodb_uri: str = "mongodb://admin:password@localhost:27017"
    logging_client_mongodb_db_name: str = "llamaxing"
    observability_client: str = "langfuse"
    observability_client_langfuse_host: str = "http://localhost:3000"


settings = Settings(_env_file=".env")
