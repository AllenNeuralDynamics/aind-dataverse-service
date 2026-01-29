"""Set up fixtures to be used across all test modules."""

import os
from pathlib import Path
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from aind_dataverse_service_server.main import app

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


@pytest.fixture
def client() -> Generator[TestClient, Any, None]:
    """Creating a client for testing purposes."""

    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_access_token():
    """Mock access token for Azure authentication."""
    return "mock_bearer_token_12345"


@pytest.fixture
def mock_table_data():
    """Mock table data response from Dataverse API."""
    return [
        {
            "cr138_projectid": "test-project-1",
            "cr138_projectcode": "P001",
            "cr138_projectname": "Test Project 1",
            "cr138_projectlimsid": "LIMS001"
        },
        {
            "cr138_projectid": "test-project-2",
            "cr138_projectcode": "P002",
            "cr138_projectname": "Test Project 2",
            "cr138_projectlimsid": "LIMS002"
        }
    ]


@pytest.fixture
def mock_entity_table_rows():
    """Mock entity table rows response from Dataverse API."""
    return [
        {
            "entityid": "6ed9e9eb-6e46-4e28-a505-c5849688913d",
            "entitysetname": "cr138_projects",
            "name": "cr138_Project",
            "logicalname": "cr138_project"
        },
        {
            "entityid": "7f7159f7-a992-4ada-b28a-d2ff9d1ecae2",
            "entitysetname": "cr138_donorses",
            "name": "cr138_Donors",
            "logicalname": "cr138_donors"
        },
        {
            "entityid": "f262d933-8c6b-4d76-81fd-b7a442afbdb8",
            "entitysetname": "cr138_blockses",
            "name": "cr138_Blocks",
            "logicalname": "cr138_blocks"
        }
    ]
