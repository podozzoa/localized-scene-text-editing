from __future__ import annotations

import unittest

from harness.reports.build_quality_diagnosis import build_markdown


class QualityDiagnosisReportUnitTest(unittest.TestCase):
    def test_build_markdown_lists_region_warning_counts(self) -> None:
        report = build_markdown(
            {
                "run_name": "candidate",
                "summary": {"average_quality_score": 0.0},
                "translation_backend": {"active_provider": "identity", "backend_available": False},
            },
            {
                "zero_score_item_count": 1,
                "zero_score_inputs": ["sample2.jpg"],
                "item_warning_counts": {"low score": 1},
                "region_count": 2,
                "zero_score_region_count": 1,
                "region_warning_counts": {"target text script mismatch": 1},
                "missing_quality_artifacts": [],
            },
            {
                "missing_item_count": 0,
                "missing_items": [],
                "render_artifact_counts": {"sample2.jpg": 2},
            },
        )

        self.assertIn("target text script mismatch: 1", report)
        self.assertIn("sample2.jpg", report)
        self.assertIn("translation_backend: identity", report)
        self.assertIn("missing_artifact_item_count: 0", report)
        self.assertIn("sample2.jpg: 2", report)


if __name__ == "__main__":
    unittest.main()
