"""Tests configs module"""

import os
import unittest
from unittest.mock import patch

from aind_dataverse_service_server.configs import Settings


class TestSettings(unittest.TestCase):
    """Test methods in Settings Class"""

    @patch.dict(
        os.environ,
        {
            "DATAVERSE_HOST": "http://example.com",
            "DATAVERSE_TENANT_ID": "example_tenant_id",
            "DATAVERSE_CLIENT_ID": "example_client_id",
            "DATAVERSE_CLIENT_SECRET": "example_client_secret",
            "DATAVERSE_ENVIRONMENT_URL": "http://example.com",
        },
        clear=True,
    )
    def test_get_settings(self):
        """Tests settings can be set via env vars"""
        settings = Settings()
        expected_settings = Settings(
            host="http://example.com",
            tenant_id="example_tenant_id",
            client_id="example_client_id",
            client_secret="example_client_secret",
            environment_url="http://example.com",
        )
        computed_dataverse_scope_url = settings.dataverse_api_scope_url
        expected_dataverse_scope_url = "http://example.com/.default"
        self.assertEqual(expected_settings, settings)
        self.assertEqual(
            expected_dataverse_scope_url, computed_dataverse_scope_url
        )


if __name__ == "__main__":
    unittest.main()
