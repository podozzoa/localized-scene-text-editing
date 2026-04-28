from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from harness.reports.build_curation_packet import build_curation_packet
from harness.validators.benchmark_manifest import validate_manifest


class BenchmarkManifestValidatorUnitTest(unittest.TestCase):
    def test_validate_manifest_accepts_approved_items(self) -> None:
        payload = {
            "manifest_id": "smoke-v1",
            "dataset_root": "benchmarks/datasets/smoke/images",
            "items": [
                {
                    "id": "sample1",
                    "image_path": "benchmarks/datasets/smoke/images/sample1.png",
                    "critical": True,
                    "expected_targets_status": "approved",
                    "source_lang": "ko",
                    "target_lang": "en",
                    "category_tags": ["smoke"],
                    "expected_targets": ["SALE 50%"],
                }
            ],
        }

        with patch.object(Path, "exists", return_value=True):
            report = validate_manifest(payload)

        self.assertTrue(report["valid"])
        self.assertTrue(report["ready_for_promotion"])
        self.assertEqual(report["non_approved_expected_target_count"], 0)

    def test_validate_manifest_valid_but_not_ready_for_draft_items(self) -> None:
        payload = {
            "manifest_id": "smoke-v1",
            "dataset_root": "benchmarks/datasets/smoke/images",
            "items": [
                {
                    "id": "sample1",
                    "image_path": "benchmarks/datasets/smoke/images/sample1.png",
                    "critical": True,
                    "expected_targets_status": "draft",
                    "source_lang": "ko",
                    "target_lang": "en",
                    "category_tags": ["smoke"],
                    "expected_targets": ["SALE 50%"],
                }
            ],
        }

        with patch.object(Path, "exists", return_value=True):
            report = validate_manifest(payload)

        self.assertTrue(report["valid"])
        self.assertFalse(report["ready_for_promotion"])
        self.assertEqual(report["non_approved_expected_target_items"], ["sample1"])

    def test_validate_manifest_flags_placeholder_targets(self) -> None:
        payload = {
            "manifest_id": "smoke-v1",
            "dataset_root": "benchmarks/datasets/smoke/images",
            "items": [
                {
                    "id": "sample1",
                    "image_path": "benchmarks/datasets/smoke/images/sample1.png",
                    "critical": True,
                    "expected_targets_status": "draft",
                    "source_lang": "ko",
                    "target_lang": "en",
                    "category_tags": ["smoke"],
                    "expected_targets": ["human approved target pending"],
                }
            ],
        }

        with patch.object(Path, "exists", return_value=True):
            report = validate_manifest(payload)

        self.assertTrue(report["valid"])
        self.assertEqual(report["placeholder_expected_target_count"], 1)
        self.assertFalse(report["ready_for_promotion"])

    def test_build_curation_packet_lists_pending_reviewer_decisions(self) -> None:
        manifest = {
            "manifest_id": "smoke-v1",
            "items": [
                {
                    "id": "sample1",
                    "image_path": "benchmarks/datasets/smoke/images/sample1.png",
                    "critical": True,
                    "expected_targets_status": "draft",
                    "category_tags": ["smoke"],
                    "expected_targets": ["SALE 50%"],
                }
            ],
        }
        report = {
            "item_count": 1,
            "ready_for_promotion": False,
            "placeholder_expected_target_count": 0,
            "non_approved_expected_target_count": 1,
            "errors": [],
            "warnings": [],
        }

        packet = build_curation_packet(manifest, report)

        self.assertIn("sample1", packet)
        self.assertIn("SALE 50%", packet)
        self.assertIn("pending", packet)

    def test_build_curation_packet_marks_approved_reviewer_decisions(self) -> None:
        manifest = {
            "manifest_id": "smoke-v1",
            "items": [
                {
                    "id": "sample1",
                    "image_path": "benchmarks/datasets/smoke/images/sample1.png",
                    "critical": True,
                    "expected_targets_status": "approved",
                    "category_tags": ["smoke"],
                    "expected_targets": ["SALE 50%"],
                }
            ],
        }
        report = {
            "item_count": 1,
            "ready_for_promotion": True,
            "placeholder_expected_target_count": 0,
            "non_approved_expected_target_count": 0,
            "errors": [],
            "warnings": [],
        }

        packet = build_curation_packet(manifest, report)

        self.assertIn("| sample1 |", packet)
        self.assertIn("| approved | smoke | SALE 50% | approved |", packet)


if __name__ == "__main__":
    unittest.main()
