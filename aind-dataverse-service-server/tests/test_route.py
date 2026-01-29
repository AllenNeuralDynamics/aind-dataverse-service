"""Test routes"""

import pytest
from unittest.mock import MagicMock, patch, call
from starlette.testclient import TestClient
from azure.core.credentials import AccessToken

from aind_dataverse_service_server.route import get_access_token


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

    @patch(
        "aind_dataverse_service_server.route."
        "allen_powerplatform_client.DefaultApi"
    )
    @patch(
        "aind_dataverse_service_server.route."
        "allen_powerplatform_client.ApiClient"
    )
    @patch("aind_dataverse_service_server.route.get_access_token")
    def test_get_table_200_response(
        self,
        mock_get_token,
        mock_api_client,
        mock_default_api,
        client: TestClient,
        mock_table_data,
    ):
        """Tests a successful table data retrieval"""

        mock_get_token.return_value = "mock_token"
        mock_instance = MagicMock()
        mock_instance.get_table.return_value = mock_table_data
        mock_default_api.return_value = mock_instance
        mock_api_client.return_value.__enter__.return_value = MagicMock()

        response = client.get("/table/cr138_projects")
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
    def test_get_table_data_200_response(
        self,
        mock_get_token,
        mock_api_client,
        mock_default_api,
        client: TestClient,
        mock_entity_table_rows,
    ):
        """Tests a successful table data retrieval"""

        mock_get_token.return_value = "mock_token"
        mock_instance = MagicMock()
        mock_instance.fetch_table_names.return_value = mock_entity_table_rows
        mock_default_api.return_value = mock_instance
        mock_api_client.return_value.__enter__.return_value = MagicMock()

        response = client.get("/table_data")
        assert 200 == response.status_code
        assert isinstance(response.json(), list)
        assert len(response.json()) == 3
        assert response.json()[0]["entitysetname"] == "cr138_projects"


if __name__ == "__main__":
    pytest.main([__file__])
