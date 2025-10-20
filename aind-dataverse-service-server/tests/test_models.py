"""Tests methods in models module"""

import json
import os
import unittest
from pathlib import Path

from aind_dataverse_service_server.models import (
    HealthCheck,
    MgiContent,
)

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


class TestHealthCheck(unittest.TestCase):
    """Tests for HealthCheck class"""

    def test_constructor(self):
        """Basic test for class constructor"""

        health_check = HealthCheck()
        self.assertEqual("OK", health_check.status)


class TestMgiContent(unittest.TestCase):
    """Tests for HealthCheck class"""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up class by loading resource files."""
        with open(RESOURCES_DIR / "example_response.json", "r") as f:
            contents = json.load(f)
        cls.contents = contents

    def test_constructor(self):
        """Basic test for class constructor"""

        content = MgiContent(**self.contents)
        self.assertEqual(1, len(content.summaryRows))
        self.assertEqual(1, content.totalCount)
        self.assertIsNone(content.meta)


if __name__ == "__main__":
    unittest.main()
