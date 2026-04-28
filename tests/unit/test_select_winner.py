from __future__ import annotations

import unittest

from harness.comparators.select_winner import build_recommendation


class SelectWinnerUnitTest(unittest.TestCase):
    def test_build_recommendation_promotes_clean_candidate(self) -> None:
        comparison = {
            "baseline_run": "baseline",
            "candidate_run": "candidate",
            "policy": {"policy_id": "gate-default-v1"},
            "benchmark_readiness": {"placeholder_expected_target_count": 0, "non_approved_expected_target_count": 0},
            "gate": {"status": "promote", "blocking_reasons": []},
        }

        recommendation = build_recommendation(comparison)

        self.assertEqual(recommendation["promotion_status"], "promote")
        self.assertEqual(recommendation["required_followups"], [])

    def test_build_recommendation_holds_when_gate_rejects(self) -> None:
        comparison = {
            "baseline_run": "baseline",
            "candidate_run": "candidate",
            "policy": {"policy_id": "gate-default-v1"},
            "benchmark_readiness": {"placeholder_expected_target_count": 0, "non_approved_expected_target_count": 0},
            "gate": {"status": "reject", "blocking_reasons": ["critical regression"]},
        }

        recommendation = build_recommendation(comparison)

        self.assertEqual(recommendation["promotion_status"], "hold")
        self.assertEqual(recommendation["blocking_reasons"], ["critical regression"])
        self.assertGreater(len(recommendation["required_followups"]), 0)

    def test_build_recommendation_holds_when_expected_targets_are_placeholders(self) -> None:
        comparison = {
            "baseline_run": "baseline",
            "candidate_run": "candidate",
            "policy": {"policy_id": "gate-default-v1"},
            "benchmark_readiness": {"placeholder_expected_target_count": 2, "non_approved_expected_target_count": 2},
            "gate": {"status": "promote", "blocking_reasons": []},
        }

        recommendation = build_recommendation(comparison)

        self.assertEqual(recommendation["promotion_status"], "hold")
        self.assertIn("benchmark expected targets still contain placeholder values", recommendation["blocking_reasons"])
        self.assertIn("replace placeholder expected targets with curated benchmark values", recommendation["required_followups"])

    def test_build_recommendation_holds_when_targets_are_only_draft(self) -> None:
        comparison = {
            "baseline_run": "baseline",
            "candidate_run": "candidate",
            "policy": {"policy_id": "gate-default-v1"},
            "benchmark_readiness": {"placeholder_expected_target_count": 0, "non_approved_expected_target_count": 1},
            "gate": {"status": "promote", "blocking_reasons": []},
        }

        recommendation = build_recommendation(comparison)

        self.assertEqual(recommendation["promotion_status"], "hold")
        self.assertIn("benchmark expected targets are not yet approved", recommendation["blocking_reasons"])
        self.assertNotIn("replace placeholder expected targets with curated benchmark values", recommendation["required_followups"])
        self.assertIn("mark benchmark expected targets as approved after human review", recommendation["required_followups"])


if __name__ == "__main__":
    unittest.main()
