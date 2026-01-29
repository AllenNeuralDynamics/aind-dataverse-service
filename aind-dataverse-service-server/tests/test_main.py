"""Module to test main app"""

import pytest


class TestMain:
    """Tests app endpoints"""

    def test_get_healthcheck(self, client):
        """Tests healthcheck"""
        response = client.get("/healthcheck")
        assert 200 == response.status_code

    def test_get_table(self, client):
        """Tests retrieval of table data"""
        response = client.get("/table/cr138_projects")
        assert 200 == response.status_code
        assert isinstance(response.json(), list)

    def test_get_table_names(self, client):
        """Tests retrieval of table names"""
        response = client.get("/table_names")
        assert 200 == response.status_code
        assert isinstance(response.json(), list)


if __name__ == "__main__":
    pytest.main([__file__])
