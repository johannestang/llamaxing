from contextlib import asynccontextmanager
from importlib import import_module
from typing import Annotated

import httpx
import version
from fastapi import Depends, FastAPI, HTTPException, Request
from identity import Identity
from llm import LLMDispatcher
from logging_utils import log_exception, logger
from settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.requests_client = httpx.AsyncClient(timeout=settings.app_requests_timeout)
    logging_module = import_module(f"llm.logging.{settings.logging_client}")
    app.logging_client = logging_module.LoggingClient()
    observability_module = import_module(
        f"observability.{settings.observability_client}"
    )
    app.observability_client = observability_module.ObservabilityClient()
    yield
    await app.requests_client.aclose()
    await app.logging_client.on_shutdown()
    await app.observability_client.on_shutdown()


if settings.auth_method == "none":
    logger.warning("Authentication disabled!")

app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    version=version.__version__,
    docs_url="/",
    redoc_url=None,
)

identity_store_module = import_module(f"identity.store.{settings.identity_store}")
identity_store = identity_store_module.IdentityStore()
auth_module = import_module(f"auth.{settings.auth_method}")
auth_handler = auth_module.AuthHandler(identity_store)

llm_dispatcher = LLMDispatcher()


@app.post("/chat/completions")
@app.post("/v1/chat/completions")
async def chat_completions(
    request: Request, identity: Annotated[Identity, Depends(auth_handler)]
):
    try:
        data = await request.json()
    except Exception:
        log_exception()
        raise HTTPException(400, detail="Input not valid JSON") from None

    try:
        return await llm_dispatcher.call(
            "chat_completions",
            data,
            identity,
            request.app.requests_client,
            request.app.logging_client,
            request.app.observability_client,
        )
    except httpx.ReadTimeout:
        raise HTTPException(408) from None
    except Exception:
        log_exception()
        raise HTTPException(500) from None


@app.post("/completions")
@app.post("/v1/completions")
async def completions(
    request: Request, identity: Annotated[Identity, Depends(auth_handler)]
):
    try:
        data = await request.json()
    except Exception:
        log_exception()
        raise HTTPException(400, detail="Input not valid JSON") from None

    try:
        return await llm_dispatcher.call(
            "completions",
            data,
            identity,
            request.app.requests_client,
            request.app.logging_client,
            request.app.observability_client,
        )
    except httpx.ReadTimeout:
        raise HTTPException(408) from None
    except Exception:
        log_exception()
        raise HTTPException(500) from None


@app.post("/embeddings")
@app.post("/v1/embeddings")
async def embeddings(
    request: Request, identity: Annotated[Identity, Depends(auth_handler)]
):
    try:
        data = await request.json()
    except Exception:
        log_exception()
        raise HTTPException(400, detail="Input not valid JSON") from None

    try:
        return await llm_dispatcher.call(
            "embeddings",
            data,
            identity,
            request.app.requests_client,
            request.app.logging_client,
            request.app.observability_client,
        )
    except httpx.ReadTimeout:
        raise HTTPException(408) from None
    except Exception:
        log_exception()
        raise HTTPException(500) from None


@app.post("/images/generations")
@app.post("/v1/images/generations")
async def images_generations(
    request: Request, identity: Annotated[Identity, Depends(auth_handler)]
):
    try:
        data = await request.json()
    except Exception:
        log_exception()
        raise HTTPException(400, detail="Input not valid JSON") from None

    try:
        return await llm_dispatcher.call(
            "images_generations",
            data,
            identity,
            request.app.requests_client,
            request.app.logging_client,
            request.app.observability_client,
        )
    except httpx.ReadTimeout:
        raise HTTPException(408) from None
    except Exception:
        log_exception()
        raise HTTPException(500) from None


@app.get("/models")
@app.get("/v1/models")
async def models(identity: Annotated[Identity, Depends(auth_handler)]):
    try:
        return llm_dispatcher.get_models()
    except httpx.ReadTimeout:
        raise HTTPException(408) from None
    except Exception:
        log_exception()
        raise HTTPException(500) from None


if __name__ == "__main__":
    import uvicorn

    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["loggers"]["uvicorn"]["level"] = "DEBUG"
    log_config["loggers"]["uvicorn.error"]["level"] = "DEBUG"
    log_config["loggers"]["uvicorn.access"]["level"] = "DEBUG"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
