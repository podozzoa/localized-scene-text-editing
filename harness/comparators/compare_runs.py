from __future__ import annotations

import argparse
import json
from datetime import datetime, UTC
from pathlib import Path

from harness.schemas.validator import validate_payload_from_schema_file


DEFAULT_POLICY_PATH = Path("harness/policies/gate_default.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare baseline and candidate harness run results.")
    parser.add_argument("--baseline", required=True, help="Path to baseline run_result.json")
    parser.add_argument("--candidate", required=True, help="Path to candidate run_result.json")
    parser.add_argument("--output", required=True, help="Path to comparison result JSON")
    parser.add_argument("--policy", default=str(DEFAULT_POLICY_PATH), help="Gate policy JSON path")
    return parser.parse_args()


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_policy(path: str | Path) -> dict:
    policy_path = Path(path)
    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    validate_payload_from_schema_file(payload, Path("harness/schemas/gate_policy.schema.json"))
    return payload


def _index_items(run_result: dict) -> dict[str, dict]:
    return {Path(item["input_path"]).name: item for item in run_result.get("items", [])}


def _index_benchmark_items(run_result: dict) -> dict[str, dict]:
    return {item["image_name"]: item for item in run_result.get("benchmark_items", [])}


def _load_manifest_items(run_result: dict) -> list[dict] | None:
    manifest_path = run_result.get("benchmark_manifest")
    if not manifest_path:
        return None
    candidate_path = Path(manifest_path)
    if not candidate_path.exists():
        return None
    payload = json.loads(candidate_path.read_text(encoding="utf-8"))
    items = payload.get("items")
    if not isinstance(items, list):
        return None
    return items


def _normalize_manifest_item(item: dict) -> dict:
    return {
        "image_name": Path(item["image_path"]).name,
        "category_tags": item.get("category_tags", []),
        "critical": item.get("critical", False),
        "expected_targets": item.get("expected_targets", []),
        "expected_targets_status": item.get("expected_targets_status"),
    }


def _build_benchmark_readiness(run_result: dict) -> dict:
    manifest_items = _load_manifest_items(run_result)
    benchmark_items = (
        [_normalize_manifest_item(item) for item in manifest_items]
        if manifest_items is not None
        else run_result.get("benchmark_items", [])
    )
    placeholder_items = []
    non_approved_items = []
    for item in benchmark_items:
        expected_targets = item.get("expected_targets", [])
        if any(str(target).strip().lower() == "human approved target pending" for target in expected_targets):
            placeholder_items.append(item["image_name"])
        if item.get("expected_targets_status") != "approved":
            non_approved_items.append(item["image_name"])

    return {
        "item_count": len(benchmark_items),
        "placeholder_expected_target_count": len(placeholder_items),
        "placeholder_expected_target_items": placeholder_items,
        "non_approved_expected_target_count": len(non_approved_items),
        "non_approved_expected_target_items": non_approved_items,
        "ready_for_promotion": len(placeholder_items) == 0 and len(non_approved_items) == 0,
    }


def _build_category_summaries(item_deltas: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for item in item_deltas:
        tags = item.get("category_tags", [])
        for tag in tags:
            grouped.setdefault(tag, []).append(item)

    summaries = []
    for tag, items in sorted(grouped.items()):
        baseline_avg = sum(item["baseline_score"] for item in items) / len(items)
        candidate_avg = sum(item["candidate_score"] for item in items) / len(items)
        summaries.append(
            {
                "category_tag": tag,
                "item_count": len(items),
                "baseline_average_score": baseline_avg,
                "candidate_average_score": candidate_avg,
                "average_score_delta": candidate_avg - baseline_avg,
            }
        )
    return summaries


def _build_critical_summary(item_deltas: list[dict], severe_regression_threshold: float) -> dict:
    critical_items = [item for item in item_deltas if item.get("critical", False)]
    if not critical_items:
        return {
            "item_count": 0,
            "baseline_average_score": 0.0,
            "candidate_average_score": 0.0,
            "average_score_delta": 0.0,
            "severe_regression_count": 0,
        }

    baseline_avg = sum(item["baseline_score"] for item in critical_items) / len(critical_items)
    candidate_avg = sum(item["candidate_score"] for item in critical_items) / len(critical_items)
    severe_count = sum(1 for item in critical_items if item["score_delta"] <= severe_regression_threshold)
    return {
        "item_count": len(critical_items),
        "baseline_average_score": baseline_avg,
        "candidate_average_score": candidate_avg,
        "average_score_delta": candidate_avg - baseline_avg,
        "severe_regression_count": severe_count,
    }


def _summarize_gate(
    item_deltas: list[dict],
    baseline_failed: int,
    candidate_failed: int,
    average_quality_delta: float,
    category_summaries: list[dict],
    critical_summary: dict,
    thresholds: dict,
) -> dict:
    severe_regression_threshold = thresholds["severe_regression_threshold"]
    category_regression_threshold = thresholds["category_regression_threshold"]

    severe_regressions = [item for item in item_deltas if item["score_delta"] <= severe_regression_threshold]
    new_failures = [item for item in item_deltas if (not item["baseline_failed"]) and item["candidate_failed"]]
    category_regressions = [item for item in category_summaries if item["average_score_delta"] <= category_regression_threshold]

    blocking_reasons: list[str] = []
    if thresholds["block_on_candidate_failure_increase"] and candidate_failed > baseline_failed:
        blocking_reasons.append("candidate introduced more failed items than baseline")
    if thresholds["block_on_average_regression"] and average_quality_delta < 0:
        blocking_reasons.append("candidate average quality score regressed below baseline")
    if thresholds["block_on_critical_average_regression"] and critical_summary.get("average_score_delta", 0.0) < 0:
        blocking_reasons.append("candidate critical split average score regressed below baseline")
    if thresholds["block_on_critical_severe_regression"] and critical_summary.get("severe_regression_count", 0) > 0:
        blocking_reasons.append("candidate contains severe regressions in critical items")
    if thresholds["block_on_item_severe_regression"] and severe_regressions:
        blocking_reasons.append("candidate contains severe item-level regressions")
    if thresholds["block_on_new_failure"] and new_failures:
        blocking_reasons.append("candidate introduced new per-item failures")
    if thresholds["block_on_category_regression"] and category_regressions:
        blocking_reasons.append("candidate regressed in one or more category averages")

    return {
        "status": "promote" if not blocking_reasons else "reject",
        "policy_id": thresholds.get("policy_id"),
        "severe_regression_threshold": severe_regression_threshold,
        "category_regression_threshold": category_regression_threshold,
        "severe_regression_count": len(severe_regressions),
        "new_failure_count": len(new_failures),
        "category_regression_count": len(category_regressions),
        "blocking_reasons": blocking_reasons,
    }


def compare_runs(baseline: dict, candidate: dict, policy: dict | None = None) -> dict:
    policy_payload = policy or _load_policy(DEFAULT_POLICY_PATH)
    thresholds = dict(policy_payload["thresholds"])
    thresholds["policy_id"] = policy_payload["policy_id"]
    baseline_items = _index_items(baseline)
    candidate_items = _index_items(candidate)
    manifest_items = _load_manifest_items(candidate if candidate.get("benchmark_manifest") else baseline)
    benchmark_items = (
        {item["image_name"]: item for item in [_normalize_manifest_item(item) for item in manifest_items]}
        if manifest_items is not None
        else _index_benchmark_items(candidate if candidate.get("benchmark_items") else baseline)
    )
    names = sorted(set(baseline_items) | set(candidate_items))

    item_deltas = []
    for name in names:
        base_item = baseline_items.get(name)
        cand_item = candidate_items.get(name)
        benchmark_item = benchmark_items.get(name, {})
        base_score = base_item["quality_score"] if base_item else 0.0
        cand_score = cand_item["quality_score"] if cand_item else 0.0
        item_deltas.append(
            {
                "item_name": name,
                "baseline_score": base_score,
                "candidate_score": cand_score,
                "score_delta": cand_score - base_score,
                "baseline_failed": base_item["failed"] if base_item else True,
                "candidate_failed": cand_item["failed"] if cand_item else True,
                "category_tags": benchmark_item.get("category_tags", []),
                "critical": benchmark_item.get("critical", False),
            }
        )

    baseline_avg = baseline["summary"]["average_quality_score"]
    candidate_avg = candidate["summary"]["average_quality_score"]
    category_summaries = _build_category_summaries(item_deltas)
    critical_summary = _build_critical_summary(item_deltas, thresholds["severe_regression_threshold"])
    benchmark_readiness = _build_benchmark_readiness(candidate if candidate.get("benchmark_items") else baseline)
    summary = {
        "baseline_average_quality_score": baseline_avg,
        "candidate_average_quality_score": candidate_avg,
        "average_quality_delta": candidate_avg - baseline_avg,
        "baseline_failed": baseline["summary"]["failed"],
        "candidate_failed": candidate["summary"]["failed"],
    }
    gate = _summarize_gate(
        item_deltas,
        summary["baseline_failed"],
        summary["candidate_failed"],
        summary["average_quality_delta"],
        category_summaries,
        critical_summary,
        thresholds,
    )

    return {
        "baseline_run": baseline["run_name"],
        "candidate_run": candidate["run_name"],
        "created_at": datetime.now(UTC).isoformat(),
        "policy": {
          "policy_id": policy_payload["policy_id"],
          "description": policy_payload["description"],
        },
        "summary": summary,
        "gate": gate,
        "benchmark_readiness": benchmark_readiness,
        "category_summaries": category_summaries,
        "critical_summary": critical_summary,
        "item_deltas": item_deltas,
    }


def main() -> None:
    args = parse_args()
    comparison = compare_runs(_load(args.baseline), _load(args.candidate), _load_policy(args.policy))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    validate_payload_from_schema_file(comparison, Path("harness/schemas/comparison.schema.json"))
    output_path.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"comparison_result: {output_path}")


if __name__ == "__main__":
    main()
