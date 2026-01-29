"""Tests methods in models module"""

import unittest
from aind_dataverse_service_server.models import (
    HealthCheck,
    EntityTableRow,
)


class TestHealthCheck(unittest.TestCase):
    """Tests for HealthCheck class"""

    def test_constructor(self):
        """Basic test for class constructor"""

        health_check = HealthCheck()
        self.assertEqual("OK", health_check.status)


class TestEntityTableRow(unittest.TestCase):
    """Tests for EntityTableRow class"""

    def test_constructor(self):
        """Test constructor with all fields provided"""

        entity_row = EntityTableRow(
            entityid="test-id-123",
            entitysetname="cr138_projects",
            name="cr138_Project",
            logicalname="cr138_project",
        )

        self.assertEqual("test-id-123", entity_row.entityid)
        self.assertEqual("cr138_projects", entity_row.entitysetname)
        self.assertEqual("cr138_Project", entity_row.name)
        self.assertEqual("cr138_project", entity_row.logicalname)


if __name__ == "__main__":
    unittest.main()
