"""Test routes"""

from unittest.mock import MagicMock, call, patch

import pytest
from allen_powerplatform_client.exceptions import NotFoundException
from azure.core.credentials import AccessToken
from starlette.testclient import TestClient

from aind_dataverse_service_server.route import (
    get_access_token,
    get_dataverse_access_token,
    get_funding_data,
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
        assert mock_funding_records == response

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
        assert mock_water_restriction_records == response

    @patch("aind_dataverse_service_server.route.get_funding_data")
    async def test_get_funding_200(
        self,
        mock_get_funding_data: MagicMock,
        client: TestClient,
        mock_funding_records: str,
    ):
        """Tests a good response when fetching funding info"""
        mock_get_funding_data.return_value = mock_funding_records

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
        mock_water_restriction_records: str,
    ):
        """Tests a good response when fetching water restriction info"""
        mock_get_water_restriction_data.return_value = (
            mock_water_restriction_records
        )
        response = client.get(
            "/water_restriction", params={"mouse_id": "858802"}
        )
        expected_response = [
            {
                "mouse_id": "858802",
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


if __name__ == "__main__":
    pytest.main([__file__])
