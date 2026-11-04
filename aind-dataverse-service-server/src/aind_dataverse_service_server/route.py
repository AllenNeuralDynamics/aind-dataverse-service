"""Module to handle endpoint responses"""

from asyncio import gather, to_thread
from datetime import datetime
from typing import List, Optional

import allen_powerplatform_client
from azure.core.credentials import AccessToken
from azure.identity import ClientSecretCredential
from fastapi import APIRouter, HTTPException, Path, Query, Request, status
from fastapi.openapi.models import Example
from fastapi_cache.decorator import cache
from PowerPlatform.Dataverse.client import DataverseClient

from aind_dataverse_service_server.configs import settings
from aind_dataverse_service_server.handler import (
    delipidation_fetchxml,
    funding_sql_query,
    group_delipidation_rows,
    labeling_fetchxml,
    labeling_rows_to_histology,
    water_restriction_sql_query,
)
from aind_dataverse_service_server.models import (
    EntityTableRow,
    FundingModel,
    HealthCheck,
    HistologyModel,
    WaterRestrictionModel,
)
from aind_dataverse_service_server.session import StaticTokenCredential

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
async def get_dataverse_access_token(
    scope_url: str = settings.dataverse_api_scope_url,
) -> dict:
    """
    Get access token from either Azure or cache. Token is valid for 60 minutes.
    We set cache ttl to 3500 seconds.

    Parameters
    ----------
    scope_url : str
      The scope of the Dataverse environment the token is for. Defaults to
      the environment that holds the funding and water restriction tables.

    Returns
    -------
    dict
      A dictionary representation of the AccessToken

    """
    credential = ClientSecretCredential(
        tenant_id=settings.tenant_id,
        client_id=settings.client_id,
        client_secret=settings.client_secret.get_secret_value(),
    )
    access_token = credential.get_token(scope_url)
    return {"token": access_token.token, "expires_on": access_token.expires_on}


# TODO: We should switch to using the Python Dataverse API for reading data
#  instead of interacting with PowerAutomate flows.
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
            "default": Example(
                summary="A sample entity set name ID",
                description="Example entity set name",
                value="cr138_projects",
            )
        },
    ),
    columns: str = Query(
        default=None,
        description="Comma-separated column names to select from the table",
        openapi_examples={
            "default": Example(
                summary="Example columns query parameter",
                description="Fetch only specific columns from the table",
                value="modifiedon,statecode,cr138_projectname",
            )
        },
    ),
    filter: str = Query(
        default=None,
        description="OData-style filter expression",
        openapi_examples={
            "default": Example(
                summary="Example filter query parameter",
                description="Filter rows based on specific conditions",
                value="cr138_projectname eq 'Barseq_GeneticTools'",
            )
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
async def get_funding_data() -> List[dict]:
    """Fetch funding data from Dataverse and cache the response"""
    access_token = await get_dataverse_access_token()
    static_token = StaticTokenCredential(access_token)
    with DataverseClient(
        base_url=f"{settings.environment_url}", credential=static_token
    ) as dataverse_client:
        rows = await to_thread(dataverse_client.query.sql, funding_sql_query)
    return [r.to_dict() for r in rows]


@router.get(
    "/funding", response_model=List[FundingModel], operation_id="get_funding"
)
async def get_funding(request: Request):
    """
    ## Funding
    Retrieves funding and project information.
    """
    semaphore = request.app.state.semaphore
    async with semaphore:
        rows = await get_funding_data()
    funding = []
    for r in rows:
        funding.append(FundingModel.model_validate(r))
    return funding


@cache(expire=60)
async def get_water_restriction_data(mouse_id: str) -> List[dict]:
    """Fetch water restriction data from Dataverse and cache the response"""
    access_token = await get_dataverse_access_token()
    static_token = StaticTokenCredential(access_token)
    with DataverseClient(
        base_url=f"{settings.environment_url}", credential=static_token
    ) as dataverse_client:
        sql_query = water_restriction_sql_query(mouse_id=mouse_id)
        rows = await to_thread(dataverse_client.query.sql, sql_query)
    return [r.to_dict() for r in rows]


@router.get(
    "/water_restriction",
    response_model=List[WaterRestrictionModel],
    operation_id="get_water_restriction",
)
async def get_water_restriction(
    request: Request,
    mouse_id: str = Query(
        ...,
        openapi_examples={
            "default": Example(
                summary="A mouse with water restriction data",
                description="Mouse ID",
                value="858802",
            )
        },
    ),
):
    """
    ## Water Restriction
    Retrieves Water Restriction Data.
    """
    semaphore = request.app.state.semaphore
    async with semaphore:
        rows = await get_water_restriction_data(mouse_id=mouse_id)
    water_restrictions = []
    for r in rows:
        water_restrictions.append(WaterRestrictionModel.model_validate(r))

    return water_restrictions


class MultiPageResultError(RuntimeError):
    """A FetchXML result needed more than one page, so joined rows would be
    lost."""


def _fetch_single_page(client: DataverseClient, fetchxml: str) -> List[dict]:
    """
    Run a FetchXML query and return its only page of rows.

    The histology queries join to the many side of a relationship, so one root
    record spans several rows. Dataverse's paging cookie resumes after the
    last root record, so any rows of that record left on the next page are
    silently dropped. Results that need a second page are therefore refused
    instead of being returned incomplete.

    Parameters
    ----------
    client : DataverseClient
      The Dataverse client.
    fetchxml : str
      The FetchXML query.

    Returns
    -------
    List[dict]
      The result rows as dictionaries.

    Raises
    ------
    MultiPageResultError
      The result has more than one page.
    """
    pages = iter(client.query.fetchxml(fetchxml).execute_pages())
    rows = [r.to_dict() for r in next(pages, [])]
    if next(pages, None) is not None:
        raise MultiPageResultError(
            "FetchXML result spans more than one page; paging would drop "
            "joined rows."
        )
    return rows


@cache(expire=600)
async def get_histology_data(
    subject_id: str,
    start_date_gte: Optional[datetime],
    end_date_lte: Optional[datetime],
) -> dict:
    """
    Fetch delipidation and labeling rows from the new Dataverse environment
    and cache the response.

    Parameters
    ----------
    subject_id : str
      Only return this mouse.
    start_date_gte : Optional[datetime]
      Only return records created on or after this time.
    end_date_lte : Optional[datetime]
      Only return records created on or before this time.

    Returns
    -------
    dict
      The ``delipidation`` and ``labeling`` rows as dictionaries.
    """
    access_token = await get_dataverse_access_token(
        scope_url=settings.new_dataverse_api_scope_url
    )
    static_token = StaticTokenCredential(access_token)
    filters = {
        "subject_id": subject_id,
        "start_date_gte": start_date_gte,
        "end_date_lte": end_date_lte,
    }
    with DataverseClient(
        base_url=f"{settings.new_environment_url}", credential=static_token
    ) as dataverse_client:
        delipidation, labeling = await gather(
            to_thread(
                _fetch_single_page,
                dataverse_client,
                delipidation_fetchxml(**filters),
            ),
            to_thread(
                _fetch_single_page,
                dataverse_client,
                labeling_fetchxml(**filters),
            ),
        )
    return {"delipidation": delipidation, "labeling": labeling}


@router.get(
    "/histology",
    response_model=List[HistologyModel],
    operation_id="get_histology",
)
async def get_histology(
    request: Request,
    subject_id: str = Query(
        ...,
        min_length=1,
        description="Subject ID",
        openapi_examples={
            "default": Example(
                summary="A subject with histology data",
                description="Subject ID",
                value="782745",
            )
        },
    ),
    start_date_gte: Optional[datetime] = Query(
        None,
        description=(
            "Created on or after. ISO format; times without a timezone are "
            "UTC."
        ),
        openapi_examples={
            "iso_date": Example(summary="ISO date", value="2026-09-01"),
            "iso_datetime_z": Example(
                summary="ISO datetime in UTC", value="2026-09-01T00:00:00Z"
            ),
        },
    ),
    end_date_lte: Optional[datetime] = Query(
        None,
        description=(
            "Created on or before. ISO format; times without a timezone are "
            "UTC."
        ),
        openapi_examples={
            "iso_date": Example(summary="ISO date", value="2026-10-01"),
            "iso_datetime_z": Example(
                summary="ISO datetime in UTC", value="2026-10-01T00:00:00Z"
            ),
        },
    ),
):
    """
    ## Histology
    Retrieves SmartSPIM labeling, delipidation and refractive index matching
    data. Returns one record per specimen and procedure.
    """
    semaphore = request.app.state.semaphore
    async with semaphore:
        data = await get_histology_data(
            subject_id=subject_id,
            start_date_gte=start_date_gte,
            end_date_lte=end_date_lte,
        )
    # Grouping runs in a worker thread so large results don't block the
    # event loop.
    return await to_thread(
        lambda: (
            labeling_rows_to_histology(data["labeling"])
            + group_delipidation_rows(data["delipidation"])
        )
    )
