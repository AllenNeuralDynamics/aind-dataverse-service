"""Set up fixtures to be used across all test modules."""

import os
from pathlib import Path
from typing import Any, Generator, List
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PowerPlatform.Dataverse.models import Record
from pydantic import RedisDsn

from aind_dataverse_service_server.configs import settings

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


patch(
    "fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f
).start()


@pytest.fixture
def client() -> Generator[TestClient, Any, None]:
    """Creating a client for testing purposes."""
    # Import moved to be able to mock cache
    from aind_dataverse_service_server.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_table_data():
    """Mock table data response from Dataverse API."""
    return [
        {
            "cr138_projectid": "test-project-1",
            "cr138_projectcode": "P001",
            "cr138_projectname": "Test Project 1",
            "cr138_projectlimsid": "LIMS001",
        },
        {
            "cr138_projectid": "test-project-2",
            "cr138_projectcode": "P002",
            "cr138_projectname": "Test Project 2",
            "cr138_projectlimsid": "LIMS002",
        },
    ]


@pytest.fixture
def mock_entity_table_rows():
    """Mock entity table rows response from Dataverse API."""
    return [
        {
            "entityid": "123",
            "entitysetname": "cr138_projects",
            "name": "cr138_Project",
            "logicalname": "cr138_project",
        },
        {
            "entityid": "456",
            "entitysetname": "cr138_donorses",
            "name": "cr138_Donors",
            "logicalname": "cr138_donors",
        },
        {
            "entityid": "789",
            "entitysetname": "cr138_blockses",
            "name": "cr138_Blocks",
            "logicalname": "cr138_blocks",
        },
    ]


@pytest.fixture
def mock_funding_records() -> List[Record]:
    """Mock a list of Dataverse funding records."""
    return [
        Record(
            id="",
            table="",
            data={
                "grant_number": "R61AG094651",
                "project_code": "127-01-006-20",
                "project_name": "Magnetogenetic control of AD cell types",
                "subproject": "Subproject 1",
                "funding_institution": "National Institutes of Health",
                "fundees": "Person One",
                "investigators": "Person Two",
            },
        ),
        Record(
            id="",
            table="",
            data={
                "project_code": "127-01-004-10",
                "project_name": "BHA Precision Medicine Program",
                "funding_institution": "Allen Institute",
            },
        ),
    ]


@pytest.fixture
def mock_water_restriction_records() -> List[Record]:
    """Mock a list of Dataverse water restriction records."""
    return [
        Record(
            id="",
            table="",
            data={
                "aibs_dim_miceid": "921c2fd6-a16a-f111-a826-0022481e1c24",
                "active_record": True,
                "water_restriction_status": 252080002,
                "last_watered_datetime": "2026-08-13T23:31:52Z",
                "new_value": "active water restriction",
                "low_weight_threshold": 22.57,
                "record_name": "858802_20260806T232937Z",
                "mouse_id": "858802",
                "change_date_time": "2026-08-12T22:08:28Z",
                "target_weight": 26.07,
                "targeted_weight_percentage": 0.85,
                "baseline_weight": 30.67,
                "old_value": "adlib: baseline weight establishment",
            },
            etag='W/"187243480"',
        ),
        Record(
            id="",
            table="",
            data={
                "aibs_dim_miceid": "921c2fd6-a16a-f111-a826-0022481e1c24",
                "active_record": True,
                "water_restriction_status": 252080002,
                "last_watered_datetime": "2026-08-13T23:31:52Z",
                "new_value": "adlib: paused water restriction",
                "low_weight_threshold": 22.57,
                "record_name": "858802_20260806T232937Z",
                "mouse_id": "858802",
                "change_date_time": "2026-08-13T23:32:30Z",
                "target_weight": 26.07,
                "targeted_weight_percentage": 0.85,
                "baseline_weight": 30.67,
                "old_value": "active water restriction",
            },
            etag='W/"187243480"',
        ),
    ]


@pytest.fixture(scope="function")
def client_with_redis() -> Generator[TestClient, Any, None]:
    """Creating a client when settings have a redis_url."""

    # Import moved to be able to mock cache
    from aind_dataverse_service_server.main import app

    settings_with_redis = settings.model_copy(
        update={"redis_url": RedisDsn("redis://example.com:1234")}, deep=True
    )

    with (
        patch(
            "aind_dataverse_service_server.main.settings",
            return_value=settings_with_redis,
        ),
        patch(
            "aind_dataverse_service_server.main.from_url", return_value=None
        ),
        patch(
            "aind_dataverse_service_server.main.RedisBackend",
            return_value=None,
        ),
        patch(
            "aind_dataverse_service_server.main.Semaphore",
            return_value=None,
        ),
    ):
        with TestClient(app) as c:
            yield c
