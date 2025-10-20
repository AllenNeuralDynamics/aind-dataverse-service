"""Tests configs module"""

import os
import unittest
from unittest.mock import patch

from aind_dataverse_service_server.configs import Settings


class TestSettings(unittest.TestCase):
    """Test methods in Settings Class"""

    @patch.dict(os.environ, {"MGI_HOST": "http://example.com"}, clear=True)
    def test_get_settings(self):
        """Tests settings can be set via env vars"""
        settings = Settings()
        expected_settings = Settings(host="http://example.com")
        self.assertEqual(expected_settings, settings)


if __name__ == "__main__":
    unittest.main()
