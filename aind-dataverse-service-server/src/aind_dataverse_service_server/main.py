"""Starts and runs a FastAPI Server"""

import logging
import os

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from aind_dataverse_service_server import __version__ as service_version
from aind_dataverse_service_server.route import router
from redis.asyncio import from_url  # noqa
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache
from aind_dataverse_service_server.configs import settings

# The log level can be set by adding an environment variable before launch.
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=log_level)

description = """
## aind-dataverse-service

Service to pull data from Allen Institute's Dataverse database.

"""


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Init cache and add to lifespan of app"""
    if settings.redis_url is not None:
        redis = from_url(settings.redis_url.unicode_string())
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    else:
        FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield


# noinspection PyTypeChecker
app = FastAPI(
    title="aind-dataverse-service",
    description=description,
    summary="Retrieves information from Dataverse.",
    version=service_version,
    lifespan=lifespan,
)

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.include_router(router)

# Clean up the methods names that is generated in the client code
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name
