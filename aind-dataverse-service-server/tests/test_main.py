"""Module to test main app"""

import pytest
from starlette.testclient import TestClient


class TestMain:
    """Tests app endpoints"""

    def test_get_healthcheck(self, client: TestClient):
        """Tests healthcheck"""
        response = client.get("/healthcheck")
        assert 200 == response.status_code

    def test_app_with_redis(self, client_with_redis: TestClient):
        """Tests client is instantiated correctly when redis_url set."""
        response = client_with_redis.get("/healthcheck")
        assert 200 == response.status_code

    def test_app_with_in_memory_cache(self, client: TestClient):
        """Tests client is instantiated correctly when redis_url None."""
        response = client.get("/healthcheck")
        assert 200 == response.status_code


if __name__ == "__main__":
    pytest.main([__file__])
