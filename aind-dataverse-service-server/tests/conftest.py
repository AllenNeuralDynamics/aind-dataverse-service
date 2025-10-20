"""Set up fixtures to be used across all test modules."""

import json
import os
from pathlib import Path
from typing import Any, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import URL, AsyncClient
from pytest_httpx import HTTPXMock

from aind_dataverse_service_server.main import app

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


@pytest.fixture(scope="function")
async def mock_async_client_get_pvalb(httpx_mock: HTTPXMock) -> AsyncClient:
    """Generate an async session for testing."""

    with open(RESOURCES_DIR / "example_response.json") as f:
        contents = json.load(f)

    base_url = "http://example.com/quicksearch/alleleBucket"
    base_params = {
        "queryType": "exactPhrase",
        "submit": "Quick+Search",
    }
    params = {"query": "Parvalbumin-IRES-Cre"} | base_params
    httpx_mock.add_response(url=URL(base_url, params=params), json=contents)
    return AsyncClient(base_url="http://example.com")


@pytest.fixture(scope="function")
async def mock_async_client_get_nothing(httpx_mock: HTTPXMock) -> AsyncClient:
    """Generate an async session for testing."""

    base_url = "http://example.com/quicksearch/alleleBucket"
    base_params = {
        "queryType": "exactPhrase",
        "submit": "Quick+Search",
    }
    params = {"query": "NOTHING"} | base_params
    httpx_mock.add_response(
        url=URL(base_url, params=params),
        json={"summaryRows": [], "totalCount": 0, "meta": None},
    )
    return AsyncClient(base_url="http://example.com")


@pytest.fixture
def client() -> Generator[TestClient, Any, None]:
    """Creating a client for testing purposes."""

    with TestClient(app) as c:
        yield c
