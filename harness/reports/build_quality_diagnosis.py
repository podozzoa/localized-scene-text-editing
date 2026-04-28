from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.usecases.batch_runner import BatchItemResult, BatchRunSummary
from harness.runners.common import build_artifact_diagnosis, build_quality_diagnosis


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a quality diagnosis report from a harness run_result.json.")
    parser.add_argument("--run-result", required=True, help="Harness run_result.json path")
    parser.add_argument("--output-json", required=True, help="Diagnosis JSON output path")
    parser.add_argument("--output-md", required=True, help="Diagnosis markdown output path")
    return parser.parse_args()


def _summary_from_run_result(run_result: dict) -> BatchRunSummary:
    summary = run_result["summary"]
    return BatchRunSummary(
        input_dir=summary["input_dir"],
        target_lang=summary["target_lang"],
        total_images=summary["total_images"],
        succeeded=summary["succeeded"],
        failed=summary["failed"],
        average_quality_score=summary["average_quality_score"],
        items=[
            BatchItemResult(
                input_path=item["input_path"],
                output_image_path=item["output_image_path"],
                quality_score=item["quality_score"],
                warnings=item.get("warnings", []),
                failed=item.get("failed", False),
                error=item.get("error"),
            )
            for item in summary.get("items", run_result.get("items", []))
        ],
    )


def build_markdown(run_result: dict, diagnosis: dict, artifact_diagnosis: dict | None = None) -> str:
    artifact_diagnosis = artifact_diagnosis or run_result.get("artifact_diagnosis", {})
    lines = [
        "# Quality Diagnosis",
        "",
        f"- run_name: {run_result.get('run_name')}",
        f"- average_quality_score: {run_result.get('summary', {}).get('average_quality_score', 0.0):.4f}",
        f"- translation_backend: {run_result.get('translation_backend', {}).get('active_provider', 'unknown')}",
        f"- translation_backend_available: {run_result.get('translation_backend', {}).get('backend_available', 'unknown')}",
        f"- zero_score_item_count: {diagnosis.get('zero_score_item_count', 0)}",
        f"- region_count: {diagnosis.get('region_count', 0)}",
        f"- zero_score_region_count: {diagnosis.get('zero_score_region_count', 0)}",
        f"- missing_artifact_item_count: {artifact_diagnosis.get('missing_item_count', 0)}",
        "",
        "## Zero Score Inputs",
    ]
    zero_score_inputs = diagnosis.get("zero_score_inputs", [])
    lines.extend([f"- {item}" for item in zero_score_inputs] if zero_score_inputs else ["- none"])

    lines.extend(["", "## Item Warning Counts"])
    item_warning_counts = diagnosis.get("item_warning_counts", {})
    lines.extend([f"- {warning}: {count}" for warning, count in sorted(item_warning_counts.items())] if item_warning_counts else ["- none"])

    lines.extend(["", "## Region Warning Counts"])
    region_warning_counts = diagnosis.get("region_warning_counts", {})
    lines.extend([f"- {warning}: {count}" for warning, count in sorted(region_warning_counts.items())] if region_warning_counts else ["- none"])

    missing_artifacts = diagnosis.get("missing_quality_artifacts", [])
    lines.extend(["", "## Missing Quality Artifacts"])
    lines.extend([f"- {item}" for item in missing_artifacts] if missing_artifacts else ["- none"])

    missing_items = artifact_diagnosis.get("missing_items", [])
    lines.extend(["", "## Missing Required Artifacts"])
    if missing_items:
        for item in missing_items:
            missing = ", ".join(item.get("missing_artifacts", []))
            lines.append(f"- {item.get('input_path')}: {missing}")
    else:
        lines.append("- none")

    render_counts = artifact_diagnosis.get("render_artifact_counts", {})
    lines.extend(["", "## Render Artifact Counts"])
    lines.extend([f"- {path}: {count}" for path, count in sorted(render_counts.items())] if render_counts else ["- none"])
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    run_result = json.loads(Path(args.run_result).read_text(encoding="utf-8"))
    summary = _summary_from_run_result(run_result)
    diagnosis = build_quality_diagnosis(summary)
    artifact_diagnosis = build_artifact_diagnosis(summary)
    report_payload = {
        **diagnosis,
        "artifact_diagnosis": artifact_diagnosis,
    }

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    output_md = Path(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(build_markdown(run_result, diagnosis, artifact_diagnosis), encoding="utf-8")
    print(f"quality_diagnosis_json: {output_json}")
    print(f"quality_diagnosis_md: {output_md}")


if __name__ == "__main__":
    main()
