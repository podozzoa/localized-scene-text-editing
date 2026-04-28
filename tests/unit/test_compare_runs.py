from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from harness.comparators.compare_runs import compare_runs


class CompareRunsUnitTest(unittest.TestCase):
    def test_compare_runs_promotes_when_candidate_improves_without_new_failures(self) -> None:
        policy = {
            "policy_id": "test-policy",
            "description": "test",
            "thresholds": {
                "severe_regression_threshold": -0.05,
                "category_regression_threshold": -0.03,
                "block_on_average_regression": True,
                "block_on_candidate_failure_increase": True,
                "block_on_critical_average_regression": True,
                "block_on_critical_severe_regression": True,
                "block_on_item_severe_regression": True,
                "block_on_new_failure": True,
                "block_on_category_regression": True
            }
        }
        baseline = {
            "run_name": "baseline",
            "benchmark_items": [
                {"image_name": "sample1.png", "category_tags": ["smoke", "simple"], "critical": True, "expected_targets_status": "approved"},
                {"image_name": "sample2.jpg", "category_tags": ["smoke", "complex_background"], "critical": False, "expected_targets_status": "approved"},
            ],
            "summary": {"average_quality_score": 0.70, "failed": 0},
            "items": [
                {"input_path": "sample1.png", "quality_score": 0.70, "failed": False},
                {"input_path": "sample2.jpg", "quality_score": 0.70, "failed": False},
            ],
        }
        candidate = {
            "run_name": "candidate",
            "benchmark_items": baseline["benchmark_items"],
            "summary": {"average_quality_score": 0.76, "failed": 0},
            "items": [
                {"input_path": "sample1.png", "quality_score": 0.75, "failed": False},
                {"input_path": "sample2.jpg", "quality_score": 0.77, "failed": False},
            ],
        }

        comparison = compare_runs(baseline, candidate, policy)

        self.assertEqual(comparison["gate"]["status"], "promote")
        self.assertEqual(comparison["gate"]["blocking_reasons"], [])
        self.assertEqual(comparison["policy"]["policy_id"], "test-policy")
        self.assertEqual(comparison["critical_summary"]["item_count"], 1)
        self.assertTrue(any(item["category_tag"] == "simple" for item in comparison["category_summaries"]))
        self.assertTrue(comparison["benchmark_readiness"]["ready_for_promotion"])

    def test_compare_runs_rejects_on_severe_regression_and_new_failure(self) -> None:
        policy = {
            "policy_id": "test-policy",
            "description": "test",
            "thresholds": {
                "severe_regression_threshold": -0.05,
                "category_regression_threshold": -0.03,
                "block_on_average_regression": True,
                "block_on_candidate_failure_increase": True,
                "block_on_critical_average_regression": True,
                "block_on_critical_severe_regression": True,
                "block_on_item_severe_regression": True,
                "block_on_new_failure": True,
                "block_on_category_regression": True
            }
        }
        baseline = {
            "run_name": "baseline",
            "benchmark_items": [
                {"image_name": "sample1.png", "category_tags": ["smoke", "simple"], "critical": True, "expected_targets_status": "approved"},
                {"image_name": "sample2.jpg", "category_tags": ["smoke", "complex_background"], "critical": False, "expected_targets_status": "approved"},
            ],
            "summary": {"average_quality_score": 0.70, "failed": 0},
            "items": [
                {"input_path": "sample1.png", "quality_score": 0.70, "failed": False},
                {"input_path": "sample2.jpg", "quality_score": 0.70, "failed": False},
            ],
        }
        candidate = {
            "run_name": "candidate",
            "benchmark_items": baseline["benchmark_items"],
            "summary": {"average_quality_score": 0.60, "failed": 1},
            "items": [
                {"input_path": "sample1.png", "quality_score": 0.50, "failed": False},
                {"input_path": "sample2.jpg", "quality_score": 0.00, "failed": True},
            ],
        }

        comparison = compare_runs(baseline, candidate, policy)

        self.assertEqual(comparison["gate"]["status"], "reject")
        self.assertGreaterEqual(comparison["gate"]["severe_regression_count"], 1)
        self.assertGreaterEqual(comparison["gate"]["new_failure_count"], 1)
        self.assertGreaterEqual(comparison["gate"]["category_regression_count"], 1)
        self.assertLess(comparison["critical_summary"]["average_score_delta"], 0)

    def test_compare_runs_can_use_explore_policy_to_allow_item_regression(self) -> None:
        explore_policy = {
            "policy_id": "explore-policy",
            "description": "test",
            "thresholds": {
                "severe_regression_threshold": -0.08,
                "category_regression_threshold": -0.05,
                "block_on_average_regression": False,
                "block_on_candidate_failure_increase": True,
                "block_on_critical_average_regression": False,
                "block_on_critical_severe_regression": False,
                "block_on_item_severe_regression": False,
                "block_on_new_failure": True,
                "block_on_category_regression": False
            }
        }
        baseline = {
            "run_name": "baseline",
            "benchmark_items": [
                {"image_name": "sample1.png", "category_tags": ["smoke", "simple"], "critical": True, "expected_targets_status": "approved"},
            ],
            "summary": {"average_quality_score": 0.70, "failed": 0},
            "items": [
                {"input_path": "sample1.png", "quality_score": 0.70, "failed": False},
            ],
        }
        candidate = {
            "run_name": "candidate",
            "benchmark_items": baseline["benchmark_items"],
            "summary": {"average_quality_score": 0.64, "failed": 0},
            "items": [
                {"input_path": "sample1.png", "quality_score": 0.64, "failed": False},
            ],
        }

        comparison = compare_runs(baseline, candidate, explore_policy)

        self.assertEqual(comparison["policy"]["policy_id"], "explore-policy")
        self.assertEqual(comparison["gate"]["status"], "promote")

    def test_compare_runs_marks_benchmark_not_ready_when_targets_not_approved(self) -> None:
        policy = {
            "policy_id": "test-policy",
            "description": "test",
            "thresholds": {
                "severe_regression_threshold": -0.05,
                "category_regression_threshold": -0.03,
                "block_on_average_regression": True,
                "block_on_candidate_failure_increase": True,
                "block_on_critical_average_regression": True,
                "block_on_critical_severe_regression": True,
                "block_on_item_severe_regression": True,
                "block_on_new_failure": True,
                "block_on_category_regression": True
            }
        }
        baseline = {
            "run_name": "baseline",
            "benchmark_items": [
                {"image_name": "sample1.png", "category_tags": ["smoke"], "critical": True, "expected_targets_status": "draft"},
            ],
            "summary": {"average_quality_score": 0.70, "failed": 0},
            "items": [
                {"input_path": "sample1.png", "quality_score": 0.70, "failed": False},
            ],
        }
        candidate = {
            "run_name": "candidate",
            "benchmark_items": baseline["benchmark_items"],
            "summary": {"average_quality_score": 0.72, "failed": 0},
            "items": [
                {"input_path": "sample1.png", "quality_score": 0.72, "failed": False},
            ],
        }

        comparison = compare_runs(baseline, candidate, policy)

        self.assertFalse(comparison["benchmark_readiness"]["ready_for_promotion"])
        self.assertEqual(comparison["benchmark_readiness"]["non_approved_expected_target_count"], 1)

    def test_compare_runs_prefers_current_manifest_over_stale_run_snapshot(self) -> None:
        policy = {
            "policy_id": "test-policy",
            "description": "test",
            "thresholds": {
                "severe_regression_threshold": -0.05,
                "category_regression_threshold": -0.03,
                "block_on_average_regression": True,
                "block_on_candidate_failure_increase": True,
                "block_on_critical_average_regression": True,
                "block_on_critical_severe_regression": True,
                "block_on_item_severe_regression": True,
                "block_on_new_failure": True,
                "block_on_category_regression": True
            }
        }
        manifest_path = "benchmarks/manifests/test_manifest.json"
        manifest_payload = json.dumps(
            {
                "items": [
                    {
                        "image_path": "benchmarks/datasets/smoke/images/sample1.png",
                        "critical": False,
                        "expected_targets_status": "draft",
                        "category_tags": ["smoke", "headline"],
                        "expected_targets": ["SALE 50%"],
                    }
                ]
            }
        )
        baseline = {
            "run_name": "baseline",
            "benchmark_manifest": manifest_path,
            "benchmark_items": [
                {
                    "image_name": "sample1.png",
                    "category_tags": ["stale-tag"],
                    "critical": True,
                    "expected_targets": ["human approved target pending"],
                    "expected_targets_status": "approved",
                }
            ],
            "summary": {"average_quality_score": 0.70, "failed": 0},
            "items": [
                {"input_path": "sample1.png", "quality_score": 0.70, "failed": False},
            ],
        }
        candidate = {
            "run_name": "candidate",
            "benchmark_manifest": manifest_path,
            "benchmark_items": baseline["benchmark_items"],
            "summary": {"average_quality_score": 0.72, "failed": 0},
            "items": [
                {"input_path": "sample1.png", "quality_score": 0.72, "failed": False},
            ],
        }

        with patch("harness.comparators.compare_runs.Path.exists", return_value=True), patch(
            "harness.comparators.compare_runs.Path.read_text", return_value=manifest_payload
        ):
            comparison = compare_runs(baseline, candidate, policy)

        self.assertEqual(comparison["item_deltas"][0]["category_tags"], ["smoke", "headline"])
        self.assertFalse(comparison["item_deltas"][0]["critical"])
        self.assertEqual(comparison["benchmark_readiness"]["placeholder_expected_target_count"], 0)
        self.assertEqual(comparison["benchmark_readiness"]["non_approved_expected_target_count"], 1)

    def test_compare_runs_prefers_current_manifest_for_benchmark_readiness(self) -> None:
        policy = {
            "policy_id": "test-policy",
            "description": "test",
            "thresholds": {
                "severe_regression_threshold": -0.05,
                "category_regression_threshold": -0.03,
                "block_on_average_regression": True,
                "block_on_candidate_failure_increase": True,
                "block_on_critical_average_regression": True,
                "block_on_critical_severe_regression": True,
                "block_on_item_severe_regression": True,
                "block_on_new_failure": True,
                "block_on_category_regression": True,
            },
        }
        manifest_path = "benchmarks/manifests/test_manifest.json"
        manifest_payload = json.dumps(
            {
                "manifest_id": "smoke-v1",
                "dataset_root": "benchmarks/datasets/smoke/images",
                "items": [
                    {
                        "id": "sample1",
                        "image_path": "benchmarks/datasets/smoke/images/sample1.png",
                        "expected_targets": ["SALE 50%"],
                        "expected_targets_status": "draft",
                    }
                ],
            }
        )
        baseline = {
            "run_name": "baseline",
            "benchmark_manifest": manifest_path,
            "benchmark_items": [
                {
                    "image_name": "sample1.png",
                    "category_tags": ["smoke"],
                    "critical": True,
                    "expected_targets": ["human approved target pending"],
                    "expected_targets_status": "draft",
                }
            ],
            "summary": {"average_quality_score": 0.70, "failed": 0},
            "items": [
                {"input_path": "sample1.png", "quality_score": 0.70, "failed": False},
            ],
        }
        candidate = {
            "run_name": "candidate",
            "benchmark_manifest": manifest_path,
            "benchmark_items": baseline["benchmark_items"],
            "summary": {"average_quality_score": 0.72, "failed": 0},
            "items": [
                {"input_path": "sample1.png", "quality_score": 0.72, "failed": False},
            ],
        }

        with patch("harness.comparators.compare_runs.Path.exists", return_value=True), patch(
            "harness.comparators.compare_runs.Path.read_text", return_value=manifest_payload
        ):
            comparison = compare_runs(baseline, candidate, policy)

        self.assertEqual(comparison["benchmark_readiness"]["placeholder_expected_target_count"], 0)
        self.assertEqual(comparison["benchmark_readiness"]["non_approved_expected_target_count"], 1)
        self.assertFalse(comparison["benchmark_readiness"]["ready_for_promotion"])


if __name__ == "__main__":
    unittest.main()
