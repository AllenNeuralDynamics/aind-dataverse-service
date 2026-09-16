"""Module to handle endpoint responses"""

from typing import List

import allen_powerplatform_client
from azure.core.credentials import AccessToken
from azure.identity import ClientSecretCredential
from fastapi import APIRouter, HTTPException, Path, Query, status
from fastapi_cache.decorator import cache
from PowerPlatform.Dataverse.client import DataverseClient

from aind_dataverse_service_server.configs import settings
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
    ).get_token(settings.flow_scope)
    return credentials.token


@router.get(
    "/tables/{entity_set_table_name}",
    response_model=List[dict],
    operation_id="get_table"
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
    operation_id="get_table_info"
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


@router.get(
    "/funding",
    response_model=List[FundingModel],
    operation_id="get_funding"
)
async def get_funding():
    """
    ## Funding
    Retrieves funding and project information.
    """

    credential = ClientSecretCredential(
        tenant_id=settings.tenant_id,
        client_id=settings.client_id,
        client_secret=settings.client_secret.get_secret_value(),
    )
    dataverse_client = DataverseClient(
        f"{settings.environment_url}",
        credential
    )

    rows = dataverse_client.query.sql(
        "SELECT p.cr138_project as project_name, "
        "p.cr138_sub_project as subproject, u1.fullname as investigators, "
        "fc.cr138_grant as grant_number, u2.fullname as fundees, "
        "fc.cr138_funding_code as project_code, "
        "fi.aibs_institutionname as funding_institution "
        "FROM cr138_funding_codes fc "
        "LEFT JOIN cr138_projects_cr138_funding_codes pfc "
        "ON fc.cr138_funding_codesid = pfc.cr138_funding_codesid "
        "LEFT JOIN cr138_projects p "
        "ON pfc.cr138_projectsid = p.cr138_projectsid "
        "LEFT JOIN cr138_projects_systemuser pu "
        "ON p.cr138_projectsid = pu.cr138_projectsid "
        "LEFT JOIN systemuser u1 ON pu.systemuserid = u1.systemuserid "
        "LEFT JOIN aibs_funding_institution fi "
        "ON fc.cr138_funding_institution = fi.aibs_funding_institutionid "
        "LEFT JOIN cr138_funding_codes_systemuser fcu "
        "ON fc.cr138_funding_codesid = fcu.cr138_funding_codesid "
        "LEFT JOIN systemuser u2 ON fcu.systemuserid = u2.systemuserid"
    )

    funding = []
    for r in rows:
        r_dict = r.to_dict()
        funding.append(FundingModel.model_validate(r_dict))

    return funding
