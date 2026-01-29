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

    def test_constructor_with_all_fields(self):
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

    def test_constructor_with_optional_fields(self):
        """Test constructor with optional fields as None"""

        entity_row = EntityTableRow()

        self.assertIsNone(entity_row.entityid)
        self.assertIsNone(entity_row.entitysetname)
        self.assertIsNone(entity_row.name)
        self.assertIsNone(entity_row.logicalname)

    def test_extra_fields_ignored(self):
        """Test that extra fields are ignored due to ConfigDict"""

        entity_row = EntityTableRow(
            entityid="test-id-123",
            entitysetname="cr138_projects",
            extra_field="should_be_ignored",
        )

        self.assertEqual("test-id-123", entity_row.entityid)
        self.assertEqual("cr138_projects", entity_row.entitysetname)
        self.assertFalse(hasattr(entity_row, "extra_field"))


if __name__ == "__main__":
    unittest.main()
