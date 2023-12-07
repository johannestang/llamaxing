from pydantic import BaseModel, SecretStr, model_serializer


class ObservabilityConfig(BaseModel):
    langfuse_public_key: SecretStr | None = None
    langfuse_secret_key: SecretStr | None = None


class Identity(BaseModel):
    id: str
    auth_key: SecretStr | None = None
    name: str | None = None
    info: dict | None = None
    observability: ObservabilityConfig | None = None

    @model_serializer()
    def serialize_model(self):
        return {
            "id": self.id,
            "name": self.name,
            "info": self.info,
        }
