from __future__ import annotations

import unittest

from harness.reports.bootstrap_loop import build_loop_plan_content, build_report_content, build_run_summary


class BootstrapLoopUnitTest(unittest.TestCase):
    def test_build_run_summary_uses_recommendation_when_present(self) -> None:
        comparison = {
            "summary": {"average_quality_delta": 0.12},
            "gate": {"severe_regression_count": 0},
            "critical_summary": {"severe_regression_count": 0},
        }
        recommendation = {"promotion_status": "promote", "required_followups": []}

        summary = build_run_summary("loop-001", comparison, recommendation)

        self.assertEqual(summary["decision"], "promote")
        self.assertEqual(summary["overall_score_delta"], 0.12)

    def test_build_loop_plan_contains_loop_identity(self) -> None:
        plan = build_loop_plan_content("loop-001", "2026-04-10", "Codex", "theme", "baseline", "smoke-v1")

        self.assertIn("loop-001", plan)
        self.assertIn("theme", plan)

    def test_build_report_content_handles_empty_inputs(self) -> None:
        report = build_report_content("loop-001", "theme", None, None)

        self.assertIn("decision: hold", report)
        self.assertIn("Blocking Reasons", report)

    def test_build_report_content_prefers_recommendation_blocking_reasons(self) -> None:
        comparison = {"gate": {"blocking_reasons": []}}
        recommendation = {"promotion_status": "hold", "blocking_reasons": ["placeholder benchmark"]}

        report = build_report_content("loop-001", "theme", comparison, recommendation)

        self.assertIn("placeholder benchmark", report)


if __name__ == "__main__":
    unittest.main()
