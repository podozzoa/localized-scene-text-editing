from __future__ import annotations

import argparse
import json
from pathlib import Path


ALLOWED_TARGET_STATUSES = {"draft", "approved"}
PLACEHOLDER_TARGET = "human approved target pending"


class BenchmarkManifestValidationError(ValueError):
    pass


def load_manifest(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_manifest(payload: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    items = payload.get("items")

    if not payload.get("manifest_id"):
        errors.append("manifest_id is required")
    if not payload.get("dataset_root"):
        errors.append("dataset_root is required")
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty array")
        items = []

    item_ids: set[str] = set()
    placeholder_items: list[str] = []
    non_approved_items: list[str] = []
    missing_image_items: list[str] = []

    for index, item in enumerate(items):
        item_label = str(item.get("id") or f"items[{index}]")
        image_path = item.get("image_path")
        expected_targets = item.get("expected_targets")
        target_status = item.get("expected_targets_status")

        if not item.get("id"):
            errors.append(f"{item_label}: id is required")
        elif item["id"] in item_ids:
            errors.append(f"{item_label}: duplicate id")
        else:
            item_ids.add(item["id"])

        if not image_path:
            errors.append(f"{item_label}: image_path is required")
        elif not Path(image_path).exists():
            errors.append(f"{item_label}: image_path does not exist: {image_path}")
            missing_image_items.append(item_label)

        if not isinstance(item.get("critical"), bool):
            errors.append(f"{item_label}: critical must be boolean")
        if not isinstance(item.get("category_tags"), list) or not item.get("category_tags"):
            errors.append(f"{item_label}: category_tags must be a non-empty array")
        if not item.get("source_lang"):
            errors.append(f"{item_label}: source_lang is required")
        if not item.get("target_lang"):
            errors.append(f"{item_label}: target_lang is required")

        if target_status not in ALLOWED_TARGET_STATUSES:
            errors.append(f"{item_label}: expected_targets_status must be draft or approved")
        elif target_status != "approved":
            non_approved_items.append(item_label)

        if not isinstance(expected_targets, list) or not expected_targets:
            errors.append(f"{item_label}: expected_targets must be a non-empty array")
        else:
            normalized_targets = [str(target).strip() for target in expected_targets]
            if any(not target for target in normalized_targets):
                errors.append(f"{item_label}: expected_targets cannot contain blank strings")
            if any(target.lower() == PLACEHOLDER_TARGET for target in normalized_targets):
                warnings.append(f"{item_label}: expected_targets contain placeholder text")
                placeholder_items.append(item_label)

    return {
        "manifest_id": payload.get("manifest_id"),
        "item_count": len(items),
        "valid": not errors,
        "ready_for_promotion": not errors and not placeholder_items and not non_approved_items,
        "placeholder_expected_target_count": len(placeholder_items),
        "placeholder_expected_target_items": placeholder_items,
        "non_approved_expected_target_count": len(non_approved_items),
        "non_approved_expected_target_items": non_approved_items,
        "missing_image_count": len(missing_image_items),
        "missing_image_items": missing_image_items,
        "errors": errors,
        "warnings": warnings,
    }


def validate_manifest_file(path: str | Path) -> dict:
    return validate_manifest(load_manifest(path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a benchmark manifest for harness promotion readiness.")
    parser.add_argument("--manifest", required=True, help="Benchmark manifest JSON path")
    parser.add_argument("--output", help="Optional JSON report path")
    parser.add_argument("--require-approved", action="store_true", help="Exit non-zero unless all expected targets are approved")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = validate_manifest_file(args.manifest)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["valid"] or (args.require_approved and not report["ready_for_promotion"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
