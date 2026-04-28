from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or update an experiments/<loop_id>/ folder from harness artifacts.")
    parser.add_argument("--loop-id", required=True, help="Loop identifier, used as experiments/<loop_id>")
    parser.add_argument("--theme", required=True, help="Loop theme")
    parser.add_argument("--owner", default="Codex", help="Loop owner label")
    parser.add_argument("--date", default="2026-04-10", help="Loop date")
    parser.add_argument("--baseline-version", default="baseline", help="Baseline version label")
    parser.add_argument("--benchmark-set", default="smoke-v1", help="Benchmark set label")
    parser.add_argument("--comparison", help="Optional comparison JSON path")
    parser.add_argument("--report", help="Optional markdown report path")
    parser.add_argument("--recommendation", help="Optional recommendation JSON path")
    parser.add_argument("--root", default="experiments", help="Experiment root directory")
    return parser.parse_args()


def build_loop_plan_content(loop_id: str, date: str, owner: str, theme: str, baseline_version: str, benchmark_set: str) -> str:
    return "\n".join(
        [
            "# Loop Plan",
            "",
            f"- loop_id: {loop_id}",
            f"- date: {date}",
            f"- owner: {owner}",
            f"- theme: {theme}",
            f"- baseline_version: {baseline_version}",
            f"- benchmark_set: {benchmark_set}",
            "",
            "## Problem Statement",
            "- close the loop from harness execution to experiment-folder decision artifacts",
            "",
            "## Hypothesis",
            "- if baseline/candidate/report/recommendation artifacts land in one loop folder, the Ralph Wiggum loop becomes easier to run repeatedly",
            "",
            "## Candidate Changes",
            "- candidate_A: bootstrap experiment folder from harness artifacts",
            "- candidate_B: refine the loop summary after real comparison outputs exist",
            "",
            "## Success Criteria",
            "- loop folder exists with plan, report, summary, regression_cases, and winning_cases",
            "- comparison and recommendation artifacts can be copied in when available",
            "",
            "## Risks",
            "- this loop improves operational closure, not model quality directly",
        ]
    )


def build_run_summary(loop_id: str, comparison: dict | None, recommendation: dict | None) -> dict:
    gate = (comparison or {}).get("gate", {})
    critical = (comparison or {}).get("critical_summary", {})
    return {
        "loop_id": loop_id,
        "status": recommendation.get("promotion_status", "hold") if recommendation else "hold",
        "overall_score_delta": (comparison or {}).get("summary", {}).get("average_quality_delta", 0.0),
        "critical_failures": critical.get("severe_regression_count", 0),
        "regression_count": gate.get("severe_regression_count", 0),
        "manual_review_count": len(recommendation.get("required_followups", [])) if recommendation else 0,
        "decision": recommendation.get("promotion_status", "hold") if recommendation else "hold",
        "next_loop": "quality-targeted candidate loop" if recommendation and recommendation.get("promotion_status") == "promote" else "refine benchmark and candidate behavior",
    }


def build_report_content(loop_id: str, theme: str, comparison: dict | None, recommendation: dict | None) -> str:
    summary = (comparison or {}).get("summary", {})
    gate = (comparison or {}).get("gate", {})
    decision = recommendation.get("promotion_status", "hold") if recommendation else "hold"
    blocking_reasons = recommendation.get("blocking_reasons") if recommendation else None
    if blocking_reasons is None:
        blocking_reasons = gate.get("blocking_reasons", [])
    lines = [
        "# Loop Report",
        "",
        f"- loop_id: {loop_id}",
        f"- theme: {theme}",
        f"- decision: {decision}",
        "",
        "## Summary",
        "- bootstrap the loop folder and consolidate harness artifacts into one loop-scoped location",
        "",
        "## Evaluation",
        f"- overall score delta: {summary.get('average_quality_delta', 0.0):.4f}",
        f"- regressions: {gate.get('severe_regression_count', 0)}",
        f"- critical failures: {(comparison or {}).get('critical_summary', {}).get('severe_regression_count', 0)}",
        "",
        "## Blocking Reasons",
    ]
    if blocking_reasons:
        lines.extend([f"- {reason}" for reason in blocking_reasons])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Next Loop",
            f"- {build_run_summary(loop_id, comparison, recommendation)['next_loop']}",
        ]
    )
    return "\n".join(lines)


def _load_optional_json(path: str | None) -> dict | None:
    if not path:
        return None
    file_path = Path(path)
    if not file_path.exists():
        return None
    return json.loads(file_path.read_text(encoding="utf-8"))


def _copy_if_present(source: str | None, destination: Path) -> None:
    if not source:
        return
    source_path = Path(source)
    if source_path.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)


def main() -> None:
    args = parse_args()
    loop_dir = Path(args.root) / args.loop_id
    (loop_dir / "regression_cases").mkdir(parents=True, exist_ok=True)
    (loop_dir / "winning_cases").mkdir(parents=True, exist_ok=True)

    comparison = _load_optional_json(args.comparison)
    recommendation = _load_optional_json(args.recommendation)

    (loop_dir / "loop_plan.md").write_text(
        build_loop_plan_content(args.loop_id, args.date, args.owner, args.theme, args.baseline_version, args.benchmark_set),
        encoding="utf-8",
    )
    (loop_dir / "run_summary.json").write_text(
        json.dumps(build_run_summary(args.loop_id, comparison, recommendation), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (loop_dir / "report.md").write_text(
        build_report_content(args.loop_id, args.theme, comparison, recommendation),
        encoding="utf-8",
    )
    (loop_dir / "README.md").write_text(
        "\n".join(
            [
                "# Experiment Loop",
                "",
                f"- loop_id: {args.loop_id}",
                f"- theme: {args.theme}",
                "",
                "This folder stores the loop plan, summary, report, and selected regression/winning cases.",
            ]
        ),
        encoding="utf-8",
    )

    _copy_if_present(args.comparison, loop_dir / "comparison.json")
    _copy_if_present(args.report, loop_dir / "comparison_report.md")
    _copy_if_present(args.recommendation, loop_dir / "promotion_recommendation.json")

    print(f"loop_dir: {loop_dir}")


if __name__ == "__main__":
    main()
