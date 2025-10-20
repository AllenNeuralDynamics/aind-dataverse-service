"""Module to test main app"""

import pytest
from httpx import AsyncClient
from starlette.testclient import TestClient


class TestMain:
    """Tests app endpoints"""

    def test_get_healthcheck(self, client: TestClient):
        """Tests healthcheck"""
        response = client.get("/healthcheck")
        assert 200 == response.status_code

    def test_get_allele_info(
        self, client: TestClient, mock_async_client_get_pvalb: AsyncClient
    ):
        """Tests content route length"""
        response = client.get("/allele_info/Parvalbumin-IRES-Cre")
        assert 1 == len(response.json())
        assert 200 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
