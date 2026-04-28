from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a markdown summary from a harness comparison result.")
    parser.add_argument("--comparison", required=True, help="Path to comparison JSON")
    parser.add_argument("--output", required=True, help="Path to markdown output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    comparison = json.loads(Path(args.comparison).read_text(encoding="utf-8"))
    summary = comparison["summary"]
    policy = comparison.get("policy", {})
    gate = comparison.get("gate", {})
    critical = comparison.get("critical_summary", {})
    benchmark_readiness = comparison.get("benchmark_readiness", {})
    lines = [
        "# Harness Comparison Report",
        "",
        f"- baseline_run: {comparison['baseline_run']}",
        f"- candidate_run: {comparison['candidate_run']}",
        f"- policy_id: {policy.get('policy_id', 'unknown')}",
        f"- baseline_average_quality_score: {summary['baseline_average_quality_score']:.4f}",
        f"- candidate_average_quality_score: {summary['candidate_average_quality_score']:.4f}",
        f"- average_quality_delta: {summary['average_quality_delta']:.4f}",
        f"- baseline_failed: {summary['baseline_failed']}",
        f"- candidate_failed: {summary['candidate_failed']}",
        f"- gate_status: {gate.get('status', 'unknown')}",
        f"- severe_regression_count: {gate.get('severe_regression_count', 0)}",
        f"- new_failure_count: {gate.get('new_failure_count', 0)}",
        f"- category_regression_count: {gate.get('category_regression_count', 0)}",
        f"- benchmark_ready_for_promotion: {benchmark_readiness.get('ready_for_promotion', False)}",
        "",
        "## Gate",
        "",
    ]
    blocking_reasons = gate.get("blocking_reasons", [])
    if blocking_reasons:
        lines.extend([f"- {reason}" for reason in blocking_reasons])
    else:
        lines.append("- no blocking reasons")

    lines.extend([
        "",
        "## Benchmark Readiness",
        "",
        f"- item_count: {benchmark_readiness.get('item_count', 0)}",
        f"- placeholder_expected_target_count: {benchmark_readiness.get('placeholder_expected_target_count', 0)}",
        f"- non_approved_expected_target_count: {benchmark_readiness.get('non_approved_expected_target_count', 0)}",
    ])
    placeholder_items = benchmark_readiness.get("placeholder_expected_target_items", [])
    if placeholder_items:
        lines.extend([f"- placeholder: {item}" for item in placeholder_items])
    else:
        lines.append("- no placeholder expected targets")
    non_approved_items = benchmark_readiness.get("non_approved_expected_target_items", [])
    if non_approved_items:
        lines.extend([f"- non-approved: {item}" for item in non_approved_items])
    else:
        lines.append("- all expected targets approved")

    lines.extend([
        "",
        "## Critical Split",
        "",
        f"- item_count: {critical.get('item_count', 0)}",
        f"- baseline_average_score: {critical.get('baseline_average_score', 0.0):.4f}",
        f"- candidate_average_score: {critical.get('candidate_average_score', 0.0):.4f}",
        f"- average_score_delta: {critical.get('average_score_delta', 0.0):.4f}",
        "",
        "## Category Summary",
        "",
        "| category | items | baseline | candidate | delta |",
        "| --- | ---: | ---: | ---: | ---: |",
    ])
    for item in comparison.get("category_summaries", []):
        lines.append(
            f"| {item['category_tag']} | {item['item_count']} | {item['baseline_average_score']:.4f} | {item['candidate_average_score']:.4f} | {item['average_score_delta']:.4f} |"
        )

    lines.extend([
        "",
        "| item | baseline | candidate | delta |",
        "| --- | ---: | ---: | ---: |",
    ])
    for item in comparison["item_deltas"]:
        lines.append(
            f"| {item['item_name']} | {item['baseline_score']:.4f} | {item['candidate_score']:.4f} | {item['score_delta']:.4f} |"
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"comparison_report: {output_path}")


if __name__ == "__main__":
    main()
