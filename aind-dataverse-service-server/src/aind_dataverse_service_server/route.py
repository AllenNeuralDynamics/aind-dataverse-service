"""Module to handle endpoint responses"""

from asyncio import to_thread
from typing import List

import allen_powerplatform_client
from azure.core.credentials import AccessToken
from azure.identity import ClientSecretCredential
from fastapi import APIRouter, HTTPException, Path, Query, Request, status
from fastapi_cache.decorator import cache
from PowerPlatform.Dataverse.client import DataverseClient

from aind_dataverse_service_server.configs import settings
from aind_dataverse_service_server.handler import funding_sql_query
from aind_dataverse_service_server.models import (
    EntityTableRow,
    FundingModel,
    HealthCheck,
)

router = APIRouter()


@router.get(
    "/healthcheck",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
    operation_id="get_health",
)
async def get_health() -> HealthCheck:
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
    ).get_token(settings.flow_scope)
    return credentials.token


@router.get(
    "/tables/{entity_set_table_name}",
    response_model=List[dict],
    operation_id="get_table",
)
@cache(expire=900)
async def get_table(
    entity_set_table_name: str = Path(
        ...,
        description="The entity set name of the table to fetch",
        openapi_examples={
            "default": {
                "summary": "A sample entity set name ID",
                "description": "Example entity set name",
                "value": "cr138_projects",
            }
        },
    ),
    columns: str = Query(
        default=None,
        description="Comma-separated column names to select from the table",
        openapi_examples={
            "default": {
                "summary": "Example columns query parameter",
                "description": "Fetch only specific columns from the table",
                "value": "modifiedon,statecode,cr138_projectname",
            }
        },
    ),
    filter: str = Query(
        default=None,
        description="OData-style filter expression",
        openapi_examples={
            "default": {
                "summary": "Example filter query parameter",
                "description": "Filter rows based on specific conditions",
                "value": "cr138_projectname eq 'Barseq_GeneticTools'",
            }
        },
    ),
):
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
        try:
            api_version = settings.api_version
            body = allen_powerplatform_client.GetTableDataRequest(
                table_name=entity_set_table_name,
                columns=columns,
                filter=filter,
            )
            api_response = api_instance.get_table_data(
                api_version=api_version, body=body, _request_timeout=10
            )
        except allen_powerplatform_client.exceptions.ApiException as e:
            raise HTTPException(
                status_code=e.status,
                detail=f"Error fetching {entity_set_table_name}: {e.reason}",
            )
    return api_response


@router.get(
    "/tables",
    response_model=List[EntityTableRow],
    operation_id="get_table_info",
)
async def get_table_info():
    """
    ## Get entity table identifying information
    Retrieves identifying information for tables in an environment.
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
        api_response = api_instance.get_table_names(api_version)
        if api_response is None:
            api_response = []
    return api_response


@cache(expire=600)
async def get_funding_data():
    """Fetch funding data from Dataverse and cache the response"""
    credential = ClientSecretCredential(
        tenant_id=settings.tenant_id,
        client_id=settings.client_id,
        client_secret=settings.client_secret.get_secret_value(),
    )
    dataverse_client = DataverseClient(
        base_url=f"{settings.environment_url}",
        credential=credential,
    )

    rows = await to_thread(dataverse_client.query.sql, funding_sql_query)
    return rows


@router.get(
    "/funding", response_model=List[FundingModel], operation_id="get_funding"
)
@cache(expire=600)
async def get_funding(request: Request):
    """
    ## Funding
    Retrieves funding and project information.
    """
    # Limit number of requests that will be sent to Dataverse
    semaphore = request.app.state.semaphore
    async with semaphore:
        rows = await get_funding_data()
    funding = []
    for r in rows:
        r_dict = r.to_dict()
        funding.append(FundingModel.model_validate(r_dict))

    return funding
