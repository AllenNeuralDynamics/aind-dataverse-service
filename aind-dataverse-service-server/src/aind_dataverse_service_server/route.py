"""Module to handle endpoint responses"""

from typing import List

from fastapi import APIRouter, Depends, Path, status
from aind_dataverse_service_server.models import HealthCheck, EntityTableRow
from fastapi_cache.decorator import cache
from azure.core.credentials import AccessToken
from azure.identity import ClientSecretCredential
from aind_dataverse_service_server.configs import settings
import allen_powerplatform_client
from allen_powerplatform_client.rest import ApiException
from allen_powerplatform_client.models.get_table_request import GetTableRequest

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
    "/table/{entity_set_table_name}",
    response_model=List[dict],
)
async def get_table(entity_set_table_name: str = Path(..., description="The entity set name of the table to fetch")):
    """
    ## Table Data
    Retrieve data from the specified entity set table.
    """
    bearer_token = await get_access_token()
    configuration = (
        allen_powerplatform_client.Configuration()
        if settings.host is None
        else allen_powerplatform_client.Configuration(
            host=settings.host,
        )
    )
    configuration.access_token = bearer_token
    with allen_powerplatform_client.ApiClient(configuration) as api_client:
        api_instance = allen_powerplatform_client.DefaultApi(api_client)
        api_version = settings.api_version
        body = allen_powerplatform_client.GetTableRequest(
            table_name=entity_set_table_name
        )
        api_response = api_instance.get_table(api_version=api_version, body=body)
    return api_response

@router.get(
    "/table_data",
    response_model=List[EntityTableRow],
)
async def get_table_data():
    """
    ## Get entity table rows
    Retrieve information about all tables in an environment.
    """
    bearer_token = await get_access_token()
    configuration = (
        allen_powerplatform_client.Configuration()
        if settings.host is None
        else allen_powerplatform_client.Configuration(
            host=settings.host,
        )
    )
    configuration.access_token = bearer_token
    with allen_powerplatform_client.ApiClient(configuration) as api_client:
        api_instance = allen_powerplatform_client.DefaultApi(api_client)
        api_version = settings.api_version
        api_response = api_instance.fetch_table_names(api_version)
    return api_response
    