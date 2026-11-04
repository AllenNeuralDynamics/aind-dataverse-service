"""Test routes"""

from datetime import datetime
from typing import List
from unittest.mock import MagicMock, call, patch

import pytest
from allen_powerplatform_client.exceptions import NotFoundException
from azure.core.credentials import AccessToken
from PowerPlatform.Dataverse.models import Record
from starlette.testclient import TestClient

from aind_dataverse_service_server.route import (
    MultiPageResultError,
    _fetch_single_page,
    get_access_token,
    get_dataverse_access_token,
    get_funding_data,
    get_histology_data,
    get_water_restriction_data,
)


class TestRoute:
    """Test Routes."""

    def test_get_health(self, client: TestClient):
        """Tests a good response"""
        response = client.get("/healthcheck")
        assert 200 == response.status_code
        assert "OK" == response.json()["status"]

    @patch("aind_dataverse_service_server.route.ClientSecretCredential")
    async def test_get_access_token(self, mock_azure_credentials: MagicMock):
        """Tests get_access_token method"""
        mock_azure_credentials.return_value.get_token.return_value = (
            AccessToken(token="abc", expires_on=100)
        )
        token = await get_access_token()
        mock_azure_credentials.assert_has_calls(
            [
                call(
                    tenant_id="example_tenant_id",
                    client_id="example_client_id",
                    client_secret="example_client_secret",
                ),
                call().get_token(
                    "https://service.flow.microsoft.com//.default"
                ),
            ]
        )
        assert "abc" == token

    @patch("aind_dataverse_service_server.route.ClientSecretCredential")
    async def test_get_dataverse_access_token(
        self, mock_azure_credentials: MagicMock
    ):
        """Tests get_dataverse_access_token method"""
        mock_azure_credentials.return_value.get_token.return_value = (
            AccessToken(token="abc", expires_on=100)
        )
        access_token = await get_dataverse_access_token()
        mock_azure_credentials.assert_has_calls(
            [
                call(
                    tenant_id="example_tenant_id",
                    client_id="example_client_id",
                    client_secret="example_client_secret",
                ),
                call().get_token("http://example.com/.default"),
            ]
        )
        assert {"token": "abc", "expires_on": 100} == access_token

    @patch("aind_dataverse_service_server.route.ClientSecretCredential")
    async def test_get_dataverse_access_token_with_scope(
        self, mock_azure_credentials: MagicMock
    ):
        """Tests get_dataverse_access_token requests the given scope"""
        mock_azure_credentials.return_value.get_token.return_value = (
            AccessToken(token="abc", expires_on=100)
        )
        await get_dataverse_access_token(
            scope_url="http://new.example.com/.default"
        )
        mock_azure_credentials.return_value.get_token.assert_called_once_with(
            "http://new.example.com/.default"
        )

    @patch(
        "aind_dataverse_service_server.route."
        "allen_powerplatform_client.DefaultApi"
    )
    @patch(
        "aind_dataverse_service_server.route."
        "allen_powerplatform_client.ApiClient"
    )
    @patch("aind_dataverse_service_server.route.get_access_token")
    def test_get_table_data_200_response(
        self,
        mock_get_token: MagicMock,
        mock_api_client: MagicMock,
        mock_default_api: MagicMock,
        client: TestClient,
        mock_table_data,
    ):
        """Tests a successful table data retrieval"""

        mock_get_token.return_value = "mock_token"
        mock_instance = MagicMock()
        mock_instance.get_table_data.return_value = mock_table_data
        mock_default_api.return_value = mock_instance
        mock_api_client.return_value.__enter__.return_value = MagicMock()

        response = client.get("/tables/cr138_projects")
        assert 200 == response.status_code
        assert isinstance(response.json(), list)
        assert len(response.json()) == 2

    @patch(
        "aind_dataverse_service_server.route."
        "allen_powerplatform_client.DefaultApi"
    )
    @patch(
        "aind_dataverse_service_server.route."
        "allen_powerplatform_client.ApiClient"
    )
    @patch("aind_dataverse_service_server.route.get_access_token")
    def test_get_table_data_exception_response(
        self,
        mock_get_token: MagicMock,
        mock_api_client: MagicMock,
        mock_default_api: MagicMock,
        client: TestClient,
        mock_table_data,
    ):
        """Tests error is properly handled during table data retrieval"""

        mock_get_token.return_value = "mock_token"
        mock_instance = MagicMock()

        # Create a proper NotFoundException instance with required attributes
        mock_http_resp = MagicMock()
        mock_http_resp.status = 404
        mock_http_resp.reason = "Not Found"
        not_found_exception = NotFoundException(
            http_resp=mock_http_resp,
            body="",
            data=None,
        )
        not_found_exception.status = 404
        not_found_exception.reason = "Not Found"

        mock_instance.get_table_data.side_effect = not_found_exception
        mock_default_api.return_value = mock_instance
        mock_api_client.return_value.__enter__.return_value = MagicMock()

        response = client.get("/tables/non_existent_table")
        assert 404 == response.status_code
        assert "Error fetching non_existent_table" in response.json()["detail"]

    @patch(
        "aind_dataverse_service_server.route."
        "allen_powerplatform_client.DefaultApi"
    )
    @patch(
        "aind_dataverse_service_server.route."
        "allen_powerplatform_client.ApiClient"
    )
    @patch("aind_dataverse_service_server.route.get_access_token")
    def test_get_table_info_200_response(
        self,
        mock_get_token: MagicMock,
        mock_api_client: MagicMock,
        mock_default_api: MagicMock,
        client: TestClient,
        mock_entity_table_rows,
    ):
        """Tests a successful table info retrieval"""

        mock_get_token.return_value = "mock_token"
        mock_instance = MagicMock()
        mock_instance.get_table_names.return_value = mock_entity_table_rows
        mock_default_api.return_value = mock_instance
        mock_api_client.return_value.__enter__.return_value = MagicMock()

        response = client.get("/tables")
        assert 200 == response.status_code
        assert isinstance(response.json(), list)
        assert len(response.json()) == 3
        assert response.json()[0]["entitysetname"] == "cr138_projects"

    @patch(
        "aind_dataverse_service_server.route."
        "allen_powerplatform_client.DefaultApi"
    )
    @patch(
        "aind_dataverse_service_server.route."
        "allen_powerplatform_client.ApiClient"
    )
    @patch("aind_dataverse_service_server.route.get_access_token")
    def test_get_table_info_empty_response(
        self,
        mock_get_token: MagicMock,
        mock_api_client: MagicMock,
        mock_default_api: MagicMock,
        client: TestClient,
        mock_entity_table_rows,
    ):
        """Tests a successful table info retrieval with empty response"""

        mock_get_token.return_value = "mock_token"
        mock_instance = MagicMock()
        mock_instance.get_table_names.return_value = None
        mock_default_api.return_value = mock_instance
        mock_api_client.return_value.__enter__.return_value = MagicMock()

        response = client.get("/tables")
        assert 200 == response.status_code
        assert isinstance(response.json(), list)
        assert len(response.json()) == 0

    @patch(
        "aind_dataverse_service_server.route."
        "allen_powerplatform_client.DefaultApi"
    )
    @patch(
        "aind_dataverse_service_server.route."
        "allen_powerplatform_client.ApiClient"
    )
    @patch("aind_dataverse_service_server.route.get_access_token")
    def test_get_table_data_with_query_params(
        self,
        mock_get_token: MagicMock,
        mock_api_client: MagicMock,
        mock_default_api: MagicMock,
        client: TestClient,
        mock_table_data,
    ):
        """Tests table data retrieval with all optional query parameters"""
        mock_get_token.return_value = "mock_token"
        mock_instance = MagicMock()
        mock_instance.get_table_data.return_value = mock_table_data
        mock_default_api.return_value = mock_instance
        mock_api_client.return_value.__enter__.return_value = MagicMock()

        params = {
            "columns": "name,createdon",
            "filter": "status eq 'Active'",
        }
        response = client.get("/tables/cr138_projects", params=params)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 2

    @patch("aind_dataverse_service_server.route.ClientSecretCredential")
    @patch("aind_dataverse_service_server.route.DataverseClient")
    async def test_get_funding_data(
        self,
        mock_dataverse_client: MagicMock,
        mock_azure_credentials: MagicMock,
        client: TestClient,
        mock_funding_records,
    ):
        """Tests get_funding_data method"""
        mock_azure_credentials.return_value = MagicMock()
        mock_instance = (
            mock_dataverse_client.return_value.__enter__.return_value
        )
        mock_instance.query.sql.return_value = mock_funding_records
        response = await get_funding_data()
        assert [r.data for r in mock_funding_records] == response

    @patch("aind_dataverse_service_server.route.ClientSecretCredential")
    @patch("aind_dataverse_service_server.route.DataverseClient")
    async def test_get_water_restriction_data(
        self,
        mock_dataverse_client: MagicMock,
        mock_azure_credentials: MagicMock,
        client: TestClient,
        mock_water_restriction_records,
    ):
        """Tests get_water_restriction_data method"""
        mock_azure_credentials.return_value = MagicMock()
        mock_instance = (
            mock_dataverse_client.return_value.__enter__.return_value
        )
        mock_instance.query.sql.return_value = mock_water_restriction_records
        response = await get_water_restriction_data(mouse_id="858802")
        assert [r.data for r in mock_water_restriction_records] == response

    @patch("aind_dataverse_service_server.route.get_funding_data")
    async def test_get_funding_200(
        self,
        mock_get_funding_data: MagicMock,
        client: TestClient,
        mock_funding_records: List[Record],
    ):
        """Tests a good response when fetching funding info"""
        mock_get_funding_data.return_value = [
            r.data for r in mock_funding_records
        ]

        response = client.get("/funding")
        expected_response = [
            {
                "project_name": "Magnetogenetic control of AD cell types",
                "subproject": "Subproject 1",
                "project_code": "127-01-006-20",
                "funding_institution": "National Institutes of Health",
                "grant_number": "R61AG094651",
                "fundees": "Person One",
                "investigators": "Person Two",
            },
            {
                "project_name": "BHA Precision Medicine Program",
                "subproject": None,
                "project_code": "127-01-004-10",
                "funding_institution": "Allen Institute",
                "grant_number": None,
                "fundees": None,
                "investigators": None,
            },
        ]
        assert 200 == response.status_code
        assert expected_response == response.json()

    @patch("aind_dataverse_service_server.route.get_water_restriction_data")
    async def test_get_water_restriction_200(
        self,
        mock_get_water_restriction_data: MagicMock,
        client: TestClient,
        mock_water_restriction_records: List[Record],
    ):
        """Tests a good response when fetching water restriction info"""
        mock_get_water_restriction_data.return_value = [
            r.data for r in mock_water_restriction_records
        ]
        response = client.get(
            "/water_restriction", params={"mouse_id": "858802"}
        )
        expected_response = [
            {
                "mouse_id": "858802",
                "protocol_id": None,
                "record_name": "858802_20260806T232937Z",
                "active_record": True,
                "baseline_weight": "30.67",
                "last_watered_datetime": "2026-08-13T23:31:52Z",
                "low_weight_threshold": "22.57",
                "target_weight": "26.07",
                "targeted_weight_percentage": "0.85",
                "water_restriction_status": "252080002",
                "change_date_time": "2026-08-12T22:08:28Z",
                "new_value": "active water restriction",
                "old_value": "adlib: baseline weight establishment",
            },
            {
                "mouse_id": "858802",
                "protocol_id": None,
                "record_name": "858802_20260806T232937Z",
                "active_record": True,
                "baseline_weight": "30.67",
                "last_watered_datetime": "2026-08-13T23:31:52Z",
                "low_weight_threshold": "22.57",
                "target_weight": "26.07",
                "targeted_weight_percentage": "0.85",
                "water_restriction_status": "252080002",
                "change_date_time": "2026-08-13T23:32:30Z",
                "new_value": "adlib: paused water restriction",
                "old_value": "active water restriction",
            },
        ]
        assert 200 == response.status_code
        assert expected_response == response.json()

    def test_fetch_single_page_rejects_multiple_pages(
        self, mock_labeling_records: List[Record]
    ):
        """Tests a result that needs a second page is refused, not returned
        incomplete."""
        mock_client = MagicMock()
        mock_client.query.fetchxml.return_value.execute_pages.return_value = [
            mock_labeling_records[:1],
            mock_labeling_records[1:],
        ]
        with pytest.raises(MultiPageResultError):
            _fetch_single_page(mock_client, "<fetch />")

    def test_fetch_single_page_no_pages(self):
        """Tests a query that returns no pages gives no rows."""
        mock_client = MagicMock()
        mock_client.query.fetchxml.return_value.execute_pages.return_value = []
        assert [] == _fetch_single_page(mock_client, "<fetch />")

    @patch("aind_dataverse_service_server.route.ClientSecretCredential")
    @patch("aind_dataverse_service_server.route.DataverseClient")
    async def test_get_histology_data(
        self,
        mock_dataverse_client: MagicMock,
        mock_azure_credentials: MagicMock,
        mock_delipidation_records: List[Record],
        mock_labeling_records: List[Record],
    ):
        """Tests get_histology_data runs both queries against the new
        environment"""
        mock_azure_credentials.return_value.get_token.return_value = (
            AccessToken(token="abc", expires_on=100)
        )
        mock_instance = (
            mock_dataverse_client.return_value.__enter__.return_value
        )
        mock_pages = mock_instance.query.fetchxml.return_value.execute_pages
        mock_pages.side_effect = [
            [mock_delipidation_records],
            [mock_labeling_records],
        ]
        response = await get_histology_data(
            subject_id="782745", start_date_gte=None, end_date_lte=None
        )
        assert {
            "delipidation": [r.data for r in mock_delipidation_records],
            "labeling": [r.data for r in mock_labeling_records],
        } == response
        assert 2 == mock_instance.query.fetchxml.call_count
        assert (
            "http://new.example.com"
            == mock_dataverse_client.call_args.kwargs["base_url"]
        )
        mock_azure_credentials.return_value.get_token.assert_called_once_with(
            "http://new.example.com/.default"
        )

    @patch("aind_dataverse_service_server.route.get_histology_data")
    async def test_get_histology_200(
        self,
        mock_get_histology_data: MagicMock,
        client: TestClient,
        mock_delipidation_records: List[Record],
        mock_labeling_records: List[Record],
    ):
        """Tests a good response when fetching histology info"""
        mock_get_histology_data.return_value = {
            "delipidation": [r.data for r in mock_delipidation_records],
            "labeling": [r.data for r in mock_labeling_records],
        }
        response = client.get(
            "/histology",
            params={"subject_id": "782745", "start_date_gte": "2026-09-01"},
        )
        assert 200 == response.status_code
        body = response.json()
        assert [
            "SmartSPIM Labeling",
            "SmartSPIM Delipidation",
            "SmartSPIM Refractive Index Matching",
            "SmartSPIM Delipidation",
        ] == [r["procedure_name"] for r in body]
        assert {
            "procedure_name": "SmartSPIM Labeling",
            "experiment_run_created_on": "2026-09-16T21:16:37Z",
            "specimen_id": "782745",
            "subject_id": "782745",
            "protocol_id": None,
            "protocol_name": None,
            "washes": [
                {
                    "wash_name": "Labeling",
                    "wash_type": None,
                    "start_time": "2026-09-17T16:00:00Z",
                    "end_time": "2026-09-18T16:00:00Z",
                    "modified_by": "Person One",
                    "reagents": [
                        {
                            "name": "anti-GFP",
                            "source": None,
                            "lot_number": None,
                        },
                        {"name": "DAPI", "source": None, "lot_number": None},
                    ],
                }
            ],
        } == body[0]
        kwargs = mock_get_histology_data.call_args.kwargs
        assert ("782745", datetime(2026, 9, 1), None) == (
            kwargs["subject_id"],
            kwargs["start_date_gte"],
            kwargs["end_date_lte"],
        )

    @pytest.mark.parametrize("params", [{}, {"subject_id": ""}])
    def test_get_histology_missing_subject_422(
        self, client: TestClient, params: dict
    ):
        """Tests a missing or empty subject_id is rejected"""
        response = client.get("/histology", params=params)
        assert 422 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
