"""Tests handler module"""

import unittest
from datetime import datetime, timedelta, timezone
from typing import List
from xml.etree import ElementTree

from PowerPlatform.Dataverse.models import Record

from aind_dataverse_service_server.handler import (
    delipidation_fetchxml,
    group_delipidation_rows,
    labeling_fetchxml,
    labeling_rows_to_histology,
    water_restriction_sql_query,
)


class TestHandler(unittest.TestCase):
    """Test methods in handler module"""

    def test_water_restriction_sql_query(self):
        """Tests water_restriction_sql_query method"""
        sql_query = water_restriction_sql_query("12345")
        self.assertIn("WHERE m.aibs_mouse_id = '12345'", sql_query)


class TestHistologyHandler:
    """Test the histology queries and grouping."""

    def test_delipidation_fetchxml_without_dates(self):
        """Tests the query is well-formed and has no date filter by default."""
        root = ElementTree.fromstring(delipidation_fetchxml("782745"))
        assert (
            root.find("entity/link-entity[@name='aibs_wholebrainimaging']")
            is not None
        )
        assert "aibs_reagentwashid" == root.find("entity/order").get(
            "attribute"
        )
        assert ["782745"] == [
            c.get("value") for c in root.findall("entity/filter/condition")
        ]
        assert root.find(".//link-entity[@name='cr138_batch']/filter") is None

    def test_delipidation_fetchxml_with_filters(self):
        """Tests the subject filter is escaped and dates are converted to
        UTC."""
        subject_id = '1" /><condition attribute="x'
        root = ElementTree.fromstring(
            delipidation_fetchxml(
                subject_id=subject_id,
                start_date_gte=datetime(2026, 9, 1),
                end_date_lte=datetime(
                    2026, 10, 1, tzinfo=timezone(timedelta(hours=-7))
                ),
            )
        )
        subject_conditions = root.findall("entity/filter/condition")
        assert [subject_id] == [c.get("value") for c in subject_conditions]
        date_conditions = root.findall(
            ".//link-entity[@name='cr138_batch']/filter/condition"
        )
        assert [
            ("ge", "2026-09-01T00:00:00+00:00"),
            ("le", "2026-10-01T07:00:00+00:00"),
        ] == [(c.get("operator"), c.get("value")) for c in date_conditions]

    def test_labeling_fetchxml(self):
        """Tests the labeling query filters on the subject and an end date."""
        root = ElementTree.fromstring(
            labeling_fetchxml(
                subject_id="782745", end_date_lte=datetime(2026, 10, 1)
            )
        )
        assert (
            root.find("entity/link-entity[@name='aibs_wholebrainimaging']")
            is not None
        )
        conditions = root.findall("entity/filter/condition")
        assert [
            ("cr138_aibsmouseregistry", "782745"),
            ("createdon", "2026-10-01T00:00:00+00:00"),
        ] == [(c.get("attribute"), c.get("value")) for c in conditions]

    def test_group_delipidation_rows(
        self, mock_delipidation_records: List[Record]
    ):
        """Tests rows collapse per specimen and procedure, honoring step
        participants."""
        records = group_delipidation_rows(
            [r.data for r in mock_delipidation_records]
        )
        active = {
            "wash_name": "Active Delipidation",
            "wash_type": "Active Delipidation",
            "start_time": "2026-09-16T22:23:00Z",
            "end_time": "2026-09-16T22:24:00Z",
            "modified_by": "Person One",
            "reagents": [
                {
                    "name": "Conduction Buffer",
                    "source": None,
                    "lot_number": "K08S108",
                },
                {
                    "name": "Delipidation Buffer",
                    "source": None,
                    "lot_number": "DBBP0825",
                },
            ],
        }
        created_on = "2026-09-16T21:20:51Z"
        assert [
            {
                "procedure_name": "SmartSPIM Delipidation",
                "experiment_run_created_on": created_on,
                "subject_id": "782745",
                "specimen_id": "782745",
                "washes": [active],
            },
            {
                "procedure_name": "SmartSPIM Refractive Index Matching",
                "experiment_run_created_on": created_on,
                "subject_id": "782745",
                "specimen_id": "782745",
                "washes": [
                    {
                        "wash_name": "Refractive Index Wash #1",
                        "wash_type": "Refractive Index Wash #1",
                        "start_time": "2026-09-16T22:23:00Z",
                        "end_time": "2026-09-16T22:23:30Z",
                        "modified_by": "Person One",
                        "reagents": [
                            {
                                "name": "EasyIndex",
                                "source": "LifeCanvas",
                                "lot_number": "EIEI90",
                            }
                        ],
                    },
                    {
                        "wash_name": "Embedding (Neural Dynamics)",
                        "wash_type": "Embedding",
                        "start_time": None,
                        "end_time": None,
                        "modified_by": "Person One",
                        "reagents": [],
                    },
                ],
            },
            {
                "procedure_name": "SmartSPIM Delipidation",
                "experiment_run_created_on": created_on,
                "subject_id": "614177",
                "specimen_id": "614177",
                "washes": [active],
            },
        ] == records

    def test_group_delipidation_rows_edge_cases(self):
        """Tests batches without steps are dropped and unknown wash types
        keep their code."""
        base = {
            "reagent_wash_id": "w",
            "subject_id": "1",
            "batch_id": "b",
            "batch_number": "B",
            "batch_created_on": "2026-09-16T21:20:51Z",
        }
        assert [] == group_delipidation_rows([base])
        records = group_delipidation_rows(
            [
                {**base, "step_id": "s1", "wash_type": 99},
                {**base, "step_id": "s2", "batch_id": "b2"},
            ]
        )
        assert [("99", None, None), (None, None, None)] == [
            (
                r["washes"][0]["wash_type"],
                r["washes"][0]["wash_name"],
                r["specimen_id"],
            )
            for r in records
        ]

    def test_labeling_rows_to_histology(
        self, mock_labeling_records: List[Record]
    ):
        """Tests each labeling row becomes one record with one wash."""
        assert [
            {
                "procedure_name": "SmartSPIM Labeling",
                "experiment_run_created_on": "2026-09-16T21:16:37Z",
                "subject_id": "782745",
                "specimen_id": "782745",
                "washes": [
                    {
                        "wash_name": "Labeling",
                        "start_time": "2026-09-17T16:00:00Z",
                        "end_time": "2026-09-18T16:00:00Z",
                        "modified_by": "Person One",
                        "reagents": [{"name": "anti-GFP"}, {"name": "DAPI"}],
                    }
                ],
            }
        ] == labeling_rows_to_histology(
            [r.data for r in mock_labeling_records]
        )


if __name__ == "__main__":
    unittest.main()
