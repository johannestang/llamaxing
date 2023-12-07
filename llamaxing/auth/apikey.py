from auth import AuthHandlerInterface
from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyHeader
from logging_utils import logger
from settings import settings

header_scheme = APIKeyHeader(name=settings.auth_method_apikey_header_name)


class AuthHandler(AuthHandlerInterface):
    def __call__(self, request: Request, key: str = Depends(header_scheme)):
        trimmed_key = key[7:] if key[:6].lower() == "bearer" else key
        identity = self.identity_store.find_identity(trimmed_key)
        if identity is None:
            raise HTTPException(401, detail="Invalid API key")
        logger.debug(f"Matched identity: {identity}")
        return identity
