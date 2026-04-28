from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Produce a promotion recommendation from a harness comparison result.")
    parser.add_argument("--comparison", required=True, help="Path to comparison JSON")
    parser.add_argument("--output", required=True, help="Path to recommendation JSON")
    return parser.parse_args()


def build_recommendation(comparison: dict) -> dict:
    gate = comparison.get("gate", {})
    benchmark_readiness = comparison.get("benchmark_readiness", {})
    blocking_reasons = gate.get("blocking_reasons", [])
    status = gate.get("status", "reject")
    if benchmark_readiness.get("placeholder_expected_target_count", 0) > 0:
        blocking_reasons = list(blocking_reasons) + [
            "benchmark expected targets still contain placeholder values"
        ]
        status = "reject"
    if benchmark_readiness.get("non_approved_expected_target_count", 0) > 0:
        blocking_reasons = list(blocking_reasons) + [
            "benchmark expected targets are not yet approved"
        ]
        status = "reject"
    required_followups: list[str] = []
    if benchmark_readiness.get("placeholder_expected_target_count", 0) > 0:
        required_followups.append("replace placeholder expected targets with curated benchmark values")
    if benchmark_readiness.get("non_approved_expected_target_count", 0) > 0:
        required_followups.append("mark benchmark expected targets as approved after human review")
    if blocking_reasons:
        required_followups.extend(
            [
                "inspect regressed items in the comparison report",
                "review critical split summary before promotion",
            ]
        )
    return {
        "baseline_run": comparison.get("baseline_run"),
        "candidate_run": comparison.get("candidate_run"),
        "policy_id": comparison.get("policy", {}).get("policy_id"),
        "promotion_status": "promote" if status == "promote" else "hold",
        "blocking_reasons": blocking_reasons,
        "required_followups": required_followups,
    }


def main() -> None:
    args = parse_args()
    comparison = json.loads(Path(args.comparison).read_text(encoding="utf-8"))
    recommendation = build_recommendation(comparison)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(recommendation, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"promotion_recommendation: {output_path}")


if __name__ == "__main__":
    main()
