"""Tests handler module"""

import unittest

from aind_dataverse_service_server.handler import water_restriction_sql_query


class TestHandler(unittest.TestCase):
    """Test methods in handler module"""

    def test_water_restriction_sql_query(self):
        """Tests water_restriction_sql_query method"""
        sql_query = water_restriction_sql_query("12345")
        self.assertIn("WHERE m.aibs_mouse_id = '12345'", sql_query)


if __name__ == "__main__":
    unittest.main()
