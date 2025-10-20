"""Module to handle endpoint responses"""

from typing import List

from fastapi import APIRouter, Depends, Path, status
from aind_dataverse_service_server.models import HealthCheck, ProjectsTableRow
from fastapi_cache.decorator import cache
from azure.core.credentials import AccessToken
from azure.identity import ClientSecretCredential
from aind_dataverse_service_server.configs import settings
import allen_dataverse_client
from allen_dataverse_client.rest import ApiException

router = APIRouter()


@router.get(
    "/healthcheck",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Endpoint to perform a healthcheck on.

    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck()


@cache(expire=3500)
async def get_access_token() -> str:
    """
    Get access token from either Azure or cache. Token is valid for 60 minutes.
    We set cache ttl to 3500 seconds.

    Returns
    -------
    str

    """
    credentials: AccessToken = ClientSecretCredential(
        tenant_id=settings.tenant_id,
        client_id=settings.client_id,
        client_secret=settings.client_secret.get_secret_value(),
    ).get_token(settings.scope)
    return credentials.token


@router.get(
    "/project_names",
    response_model=List[ProjectsTableRow],
)
async def get_project_names():
    """
    ## Project Names
    Retrieve project names.
    """
    bearer_token = await get_access_token()
    configuration = (
        allen_dataverse_client.Configuration()
        if settings.host is None
        else allen_dataverse_client.Configuration(
            host=settings.host,
        )
    )
    configuration.access_token = bearer_token
    with allen_dataverse_client.ApiClient(configuration) as api_client:
        api_instance = allen_dataverse_client.DefaultApi(api_client)
        api_version = settings.api_version
        body = allen_dataverse_client.FetchTableByNameRequest(
            tableName=settings.project_table_id
        )
        api_response = api_instance.fetch_table_by_name(api_version, body)
        models = [ProjectsTableRow(**row) for row in api_response]
    return models
