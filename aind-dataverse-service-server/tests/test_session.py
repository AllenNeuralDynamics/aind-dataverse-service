"""Tests session module"""

import unittest

from aind_dataverse_service_server.session import StaticTokenCredential


class TestStaticTokenCredential(unittest.TestCase):
    """Test methods in StaticTokenCredential class."""

    def test_get_token(self):
        """Tests get_token method"""
        static_token = StaticTokenCredential(
            access_token={"token": "abc", "expires_on": 0}
        )
        access_token = static_token.get_token()
        self.assertEqual("abc", access_token.token)
        self.assertEqual(0, access_token.expires_on)


if __name__ == "__main__":
    unittest.main()
