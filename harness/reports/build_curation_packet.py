from __future__ import annotations

import argparse
import json
from pathlib import Path

from harness.validators.benchmark_manifest import validate_manifest_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a reviewer-facing benchmark curation packet.")
    parser.add_argument("--manifest", required=True, help="Benchmark manifest JSON path")
    parser.add_argument("--loop-dir", required=True, help="Experiment loop directory")
    parser.add_argument("--output-name", default="curation_review.md", help="Markdown file name inside the loop directory")
    parser.add_argument("--report-name", default="manifest_validation.json", help="Validation JSON file name inside the loop directory")
    return parser.parse_args()


def _format_targets(targets: list[str]) -> str:
    return "<br>".join(targets)


def _reviewer_decision_for_status(status: str) -> str:
    return "approved" if status == "approved" else "pending"


def build_curation_packet(manifest: dict, validation_report: dict) -> str:
    lines = [
        "# Benchmark Curation Review",
        "",
        f"- manifest_id: {manifest.get('manifest_id', 'unknown')}",
        f"- item_count: {validation_report.get('item_count', 0)}",
        f"- ready_for_promotion: {validation_report.get('ready_for_promotion', False)}",
        f"- placeholder_expected_target_count: {validation_report.get('placeholder_expected_target_count', 0)}",
        f"- non_approved_expected_target_count: {validation_report.get('non_approved_expected_target_count', 0)}",
        "",
        "## Reviewer Instruction",
        "- Verify each expected target against the source image and intended target market copy.",
        "- If the target is acceptable, change `expected_targets_status` from `draft` to `approved` in the manifest.",
        "- Do not approve approximate marketing copy unless it is acceptable as benchmark evidence.",
        "",
        "## Items",
        "",
        "| id | image | critical | status | category_tags | expected_targets | reviewer_decision |",
        "| --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for item in manifest.get("items", []):
        status = item.get("expected_targets_status", "")
        lines.append(
            "| {id} | {image} | {critical} | {status} | {tags} | {targets} | {decision} |".format(
                id=item.get("id", ""),
                image=item.get("image_path", ""),
                critical=item.get("critical", False),
                status=status,
                tags=", ".join(item.get("category_tags", [])),
                targets=_format_targets([str(target) for target in item.get("expected_targets", [])]),
                decision=_reviewer_decision_for_status(status),
            )
        )

    errors = validation_report.get("errors", [])
    warnings = validation_report.get("warnings", [])
    lines.extend(["", "## Validation Errors"])
    lines.extend([f"- {error}" for error in errors] if errors else ["- none"])
    lines.extend(["", "## Validation Warnings"])
    lines.extend([f"- {warning}" for warning in warnings] if warnings else ["- none"])
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validation_report = validate_manifest_file(manifest_path)
    loop_dir = Path(args.loop_dir)
    loop_dir.mkdir(parents=True, exist_ok=True)
    (loop_dir / args.report_name).write_text(json.dumps(validation_report, ensure_ascii=False, indent=2), encoding="utf-8")
    (loop_dir / args.output_name).write_text(build_curation_packet(manifest, validation_report), encoding="utf-8")
    print(f"curation_packet: {loop_dir / args.output_name}")
    print(f"manifest_validation: {loop_dir / args.report_name}")


if __name__ == "__main__":
    main()
