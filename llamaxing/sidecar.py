from contextlib import asynccontextmanager
from importlib import import_module

import httpx
import version
from fastapi import FastAPI, HTTPException, Request
from llm import (
    chat_completions_wrapper,
    completions_wrapper,
    embeddings_wrapper,
    images_generations_wrapper,
)
from logging_utils import log_exception
from sidecar_settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.requests_client = httpx.AsyncClient(
        timeout=settings.sidecar_app_requests_timeout
    )
    auth_module = import_module(f"auth.sidecar.{settings.sidecar_auth_method}")
    app.authentication_client = auth_module.Authentication()
    app.authentication_client.on_startup()
    yield
    await app.requests_client.aclose()
    await app.authentication_client.on_shutdown()


app = FastAPI(
    lifespan=lifespan,
    title=settings.sidecar_app_name,
    version=version.__version__,
    docs_url="/",
    redoc_url=None,
)


@app.post("/chat/completions")
@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    headers = await request.app.authentication_client.get_headers()
    try:
        data = await request.json()
    except Exception:
        log_exception()
        raise HTTPException(400, detail="Input not valid JSON") from None

    try:
        return await chat_completions_wrapper(
            data,
            f"{settings.sidecar_upstream_url}/v1/chat/completions",
            headers,
            request.app.requests_client,
            sidecar_mode=True,
        )
    except httpx.ReadTimeout:
        raise HTTPException(408) from None
    except Exception:
        log_exception()
        raise HTTPException(500) from None


@app.post("/completions")
@app.post("/v1/completions")
async def completions(request: Request):
    headers = await request.app.authentication_client.get_headers()
    try:
        data = await request.json()
    except Exception:
        log_exception()
        raise HTTPException(400, detail="Input not valid JSON") from None

    try:
        return await completions_wrapper(
            data,
            f"{settings.sidecar_upstream_url}/v1/completions",
            headers,
            request.app.requests_client,
            sidecar_mode=True,
        )
    except httpx.ReadTimeout:
        raise HTTPException(408) from None
    except Exception:
        log_exception()
        raise HTTPException(500) from None


@app.post("/embeddings")
@app.post("/v1/embeddings")
async def embeddings(request: Request):
    headers = await request.app.authentication_client.get_headers()
    try:
        data = await request.json()
    except Exception:
        log_exception()
        raise HTTPException(400, detail="Input not valid JSON") from None

    try:
        return await embeddings_wrapper(
            data,
            f"{settings.sidecar_upstream_url}/v1/embeddings",
            headers,
            request.app.requests_client,
            sidecar_mode=True,
        )
    except httpx.ReadTimeout:
        raise HTTPException(408) from None
    except Exception:
        log_exception()
        raise HTTPException(500) from None


@app.post("/images/generations")
@app.post("/v1/images/generations")
async def images_generations(request: Request):
    headers = await request.app.authentication_client.get_headers()
    try:
        data = await request.json()
    except Exception:
        log_exception()
        raise HTTPException(400, detail="Input not valid JSON") from None

    try:
        return await images_generations_wrapper(
            data,
            f"{settings.sidecar_upstream_url}/v1/images/generations",
            headers,
            request.app.requests_client,
            sidecar_mode=True,
        )
    except httpx.ReadTimeout:
        raise HTTPException(408) from None
    except Exception:
        log_exception()
        raise HTTPException(500) from None


@app.get("/models")
@app.get("/v1/models")
async def models(request: Request):
    headers = await request.app.authentication_client.get_headers()
    try:
        response = await request.app.requests_client.get(
            f"{settings.sidecar_upstream_url}/v1/models", headers=headers
        )
        return response.json()
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
    uvicorn.run("sidecar:app", host="0.0.0.0", port=8000, reload=True)
