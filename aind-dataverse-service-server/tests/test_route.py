"""Test routes"""

import pytest
from httpx import AsyncClient
from starlette.testclient import TestClient


class TestHealthcheckRoute:
    """Test healthcheck responses."""

    def test_get_health(self, client: TestClient):
        """Tests a good response"""
        response = client.get("/healthcheck")
        assert 200 == response.status_code
        assert "OK" == response.json()["status"]


@pytest.mark.asyncio
class TestAlleleInfoRoute:
    """Test responses for Allele Info."""

    async def test_get_200_response(
        self, client: TestClient, mock_async_client_get_pvalb: AsyncClient
    ):
        """Tests a good response"""
        response = client.get("/allele_info/Parvalbumin-IRES-Cre")
        assert 200 == response.status_code

    async def test_get_404_response(
        self, client: TestClient, mock_async_client_get_nothing: AsyncClient
    ):
        """Tests an empty response"""

        response = client.get("/allele_info/NOTHING")
        assert 200 == response.status_code
        assert [] == response.json()


if __name__ == "__main__":
    pytest.main([__file__])
