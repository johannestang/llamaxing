import jwt
from auth import AuthHandlerInterface
from fastapi import HTTPException, Request
from identity.store import IdentityStoreInterface
from logging_utils import log_exception, logger
from settings import settings


class AuthHandler(AuthHandlerInterface):
    def __init__(self, identity_store: IdentityStoreInterface):
        super().__init__(identity_store)

        if settings.auth_method_jwt_verify_signature:
            self.jwks_client = jwt.PyJWKClient(settings.auth_method_jwt_jwks_uri)

    def __call__(self, request: Request):
        token = request.headers.get(settings.auth_method_jwt_header_name)
        if token is None:
            raise HTTPException(500, "Could not get JWT from headers.")
        trimmed_token = token[7:] if token[:6].lower() == "bearer" else token
        if settings.debug_level >= 3:
            logger.debug(f"Raw token: {trimmed_token}")
        token_headers = jwt.get_unverified_header(trimmed_token)
        logger.debug(f"Token headers: {token_headers}")

        if settings.auth_method_jwt_verify_signature:
            try:
                signing_key = self.jwks_client.get_signing_key_from_jwt(trimmed_token)
                decoded_token = jwt.decode(
                    trimmed_token,
                    signing_key.key,
                    algorithms=[token_headers["alg"]],
                    issuer=settings.auth_method_jwt_issuer,
                    audience=settings.auth_method_jwt_audience,
                    options={"verify_signature": True},
                )
            except Exception:
                log_exception()
                decoded_token = jwt.decode(
                    trimmed_token, options={"verify_signature": False}
                )
                logger.debug(f"Unverified decoded token: {decoded_token}")
                raise HTTPException(401, detail="Could not verify JWT") from None
        else:
            decoded_token = jwt.decode(
                trimmed_token, options={"verify_signature": False}
            )
        logger.debug(f"Decoded token: {decoded_token}")
        key = decoded_token[settings.auth_method_jwt_id_key]
        identity = self.identity_store.find_identity(key)
        if identity is None:
            raise HTTPException(401, detail="JWT does not match valid identity")
        logger.debug(f"Matched identity: {identity}")
        return identity
