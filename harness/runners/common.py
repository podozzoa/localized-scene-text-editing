from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, replace
from datetime import datetime, UTC
from pathlib import Path

from app.main import _build_engine, _load_dotenv_if_present
from app.usecases.batch_runner import BatchRunSummary, run_batch
from harness.schemas.validator import validate_payload_from_schema_file


@dataclass(frozen=True)
class HarnessRunConfig:
    run_name: str
    variant: str
    target_lang: str
    output_root: str
    translation_provider: str
    translation_model: str
    translation_local_model: str
    source_lang: str
    ocr_lang: str
    font_path: str
    benchmark_manifest: str


def parse_runner_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a harness benchmark variant.")
    parser.add_argument("--config", required=True, help="Harness config JSON path")
    parser.add_argument("--benchmark-manifest", help="Optional benchmark manifest override path")
    parser.add_argument("--run-name", help="Optional run name override")
    parser.add_argument("--output-root", help="Optional output root override")
    return parser.parse_args()


def load_run_config(config_path: str, benchmark_manifest: str | None = None, run_name: str | None = None, output_root: str | None = None) -> HarnessRunConfig:
    payload = json.loads(Path(config_path).read_text(encoding="utf-8"))
    if benchmark_manifest is not None:
        payload["benchmark_manifest"] = benchmark_manifest
    if run_name is not None:
        payload["run_name"] = run_name
    if output_root is not None:
        payload["output_root"] = output_root
    return HarnessRunConfig(**payload)


def load_manifest(manifest_path: str) -> dict:
    return json.loads(Path(manifest_path).read_text(encoding="utf-8"))


def build_engine_args(config: HarnessRunConfig) -> argparse.Namespace:
    return argparse.Namespace(
        input=None,
        input_dir=None,
        target_lang=config.target_lang,
        output_root=config.output_root,
        font_path=config.font_path,
        ocr_lang=config.ocr_lang,
        translation_provider=config.translation_provider,
        translation_model=config.translation_model,
        translation_local_model=config.translation_local_model,
        source_lang=config.source_lang,
        export_ste_dataset=False,
        ste_context_padding_ratio=0.18,
    )


def get_run_output_dir(config: HarnessRunConfig) -> Path:
    return Path(config.output_root) / config.run_name


def get_code_version() -> dict:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status_output = subprocess.run(
            ["git", "status", "--short"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return {
            "git_commit": commit,
            "git_dirty": bool(status_output),
        }
    except Exception as exc:
        return {
            "git_commit": None,
            "git_dirty": None,
            "git_error": str(exc),
        }


def build_failure_summary(summary: BatchRunSummary) -> dict:
    failed_items = [item for item in summary.items if item.failed]
    return {
        "failed_item_count": len(failed_items),
        "failed_inputs": [item.input_path for item in failed_items],
        "failure_reasons": [
            {
                "input_path": item.input_path,
                "error": item.error,
            }
            for item in failed_items
        ],
    }


def build_quality_diagnosis(summary: BatchRunSummary) -> dict:
    zero_score_inputs: list[str] = []
    warning_counts: dict[str, int] = {}
    region_warning_counts: dict[str, int] = {}
    region_count = 0
    zero_score_region_count = 0
    missing_quality_artifacts: list[str] = []

    for item in summary.items:
        if item.quality_score == 0.0:
            zero_score_inputs.append(item.input_path)
        for warning in item.warnings:
            warning_counts[warning] = warning_counts.get(warning, 0) + 1

        if item.failed or not item.output_image_path:
            continue
        quality_path = Path(item.output_image_path).parent / "98_quality.json"
        if not quality_path.exists():
            missing_quality_artifacts.append(item.input_path)
            continue
        quality_payload = json.loads(quality_path.read_text(encoding="utf-8"))
        for region in quality_payload.get("region_results", []):
            region_count += 1
            if region.get("quality_score") == 0.0:
                zero_score_region_count += 1
            warning = region.get("warning")
            if warning:
                region_warning_counts[warning] = region_warning_counts.get(warning, 0) + 1

    return {
        "zero_score_item_count": len(zero_score_inputs),
        "zero_score_inputs": zero_score_inputs,
        "item_warning_counts": warning_counts,
        "region_count": region_count,
        "zero_score_region_count": zero_score_region_count,
        "region_warning_counts": region_warning_counts,
        "missing_quality_artifacts": missing_quality_artifacts,
    }


REQUIRED_ITEM_ARTIFACTS = (
    "01_detected_boxes.jpg",
    "02_ocr.json",
    "03_mask.png",
    "04_restored.jpg",
    "98_quality.json",
    "99_final.jpg",
)


def build_artifact_diagnosis(summary: BatchRunSummary) -> dict:
    checked_items = 0
    complete_item_count = 0
    missing_items: list[dict[str, object]] = []
    render_artifact_counts: dict[str, int] = {}

    for item in summary.items:
        if item.failed or not item.output_image_path:
            continue
        checked_items += 1
        item_dir = Path(item.output_image_path).parent
        missing = [name for name in REQUIRED_ITEM_ARTIFACTS if not (item_dir / name).exists()]
        render_count = len(list(item_dir.glob("05_rendered_*.jpg")))
        render_artifact_counts[item.input_path] = render_count
        if missing:
            missing_items.append(
                {
                    "input_path": item.input_path,
                    "artifact_dir": str(item_dir),
                    "missing_artifacts": missing,
                }
            )
        else:
            complete_item_count += 1

    return {
        "required_artifacts": list(REQUIRED_ITEM_ARTIFACTS),
        "checked_item_count": checked_items,
        "complete_item_count": complete_item_count,
        "missing_item_count": len(missing_items),
        "missing_items": missing_items,
        "render_artifact_counts": render_artifact_counts,
    }


def get_translation_backend_status(engine) -> dict:
    translator = getattr(getattr(engine, "rewriter", None), "translator", None)
    status_fn = getattr(translator, "status_dict", None)
    if callable(status_fn):
        return status_fn()
    return {
        "requested_provider": None,
        "active_provider": None,
        "fallback_active": None,
        "backend_available": None,
        "backend_error": "translator status unavailable",
    }


def execute_manifest(config: HarnessRunConfig) -> dict:
    _load_dotenv_if_present()
    manifest = load_manifest(config.benchmark_manifest)
    dataset_root = Path(manifest["dataset_root"])
    run_output_root = get_run_output_dir(config)
    effective_config = replace(config, output_root=str(run_output_root))
    engine, app_config = _build_engine(build_engine_args(effective_config))
    summary: BatchRunSummary = run_batch(
        engine=engine,
        input_dir=str(dataset_root),
        target_lang=config.target_lang,
        output_root=Path(app_config.output_root),
    )
    summary_dict = summary.to_dict()
    return {
        "run_name": config.run_name,
        "variant": config.variant,
        "benchmark_manifest": config.benchmark_manifest,
        "created_at": datetime.now(UTC).isoformat(),
        "code_version": get_code_version(),
        "translation_backend": get_translation_backend_status(engine),
        "config_snapshot": asdict(effective_config),
        "benchmark_snapshot": {
            "manifest_id": manifest.get("manifest_id"),
            "dataset_root": manifest.get("dataset_root"),
            "item_count": len(manifest.get("items", [])),
        },
        "benchmark_items": [
            {
                "id": item.get("id"),
                "image_name": Path(item.get("image_path", "")).name,
                "category_tags": item.get("category_tags", []),
                "critical": item.get("critical", False),
                "expected_targets_status": item.get("expected_targets_status", "unknown"),
                "expected_targets": item.get("expected_targets", []),
            }
            for item in manifest.get("items", [])
        ],
        "summary": summary_dict,
        "failure_summary": build_failure_summary(summary),
        "quality_diagnosis": build_quality_diagnosis(summary),
        "artifact_diagnosis": build_artifact_diagnosis(summary),
        "items": summary_dict["items"],
    }


def write_run_bundle(run_result: dict, destination_dir: str, config_path: str | None = None) -> Path:
    output_dir = Path(destination_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir = output_dir / "_snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    if config_path is not None:
        source_config = Path(config_path)
        if source_config.exists():
            (snapshots_dir / "config_snapshot.json").write_text(source_config.read_text(encoding="utf-8"), encoding="utf-8")

    benchmark_manifest = Path(run_result["benchmark_manifest"])
    if benchmark_manifest.exists():
        (snapshots_dir / "benchmark_manifest.json").write_text(
            benchmark_manifest.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    (snapshots_dir / "run_metadata.json").write_text(
        json.dumps(
            {
                "run_name": run_result["run_name"],
                "variant": run_result["variant"],
                "created_at": run_result["created_at"],
                "code_version": run_result["code_version"],
                "translation_backend": run_result.get("translation_backend"),
                "config_snapshot": run_result["config_snapshot"],
                "benchmark_snapshot": run_result["benchmark_snapshot"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    run_notes = {
        "run_name": run_result["run_name"],
        "variant": run_result["variant"],
        "created_at": run_result["created_at"],
        "benchmark_manifest": run_result["benchmark_manifest"],
        "git_commit": run_result["code_version"].get("git_commit"),
        "git_dirty": run_result["code_version"].get("git_dirty"),
        "translation_backend": run_result.get("translation_backend"),
        "benchmark_item_count": run_result["benchmark_snapshot"].get("item_count"),
        "failed_item_count": run_result["failure_summary"].get("failed_item_count"),
        "zero_score_item_count": run_result.get("quality_diagnosis", {}).get("zero_score_item_count"),
        "missing_artifact_item_count": run_result.get("artifact_diagnosis", {}).get("missing_item_count"),
        "region_warning_counts": run_result.get("quality_diagnosis", {}).get("region_warning_counts", {}),
    }
    (output_dir / "run_notes.json").write_text(json.dumps(run_notes, ensure_ascii=False, indent=2), encoding="utf-8")

    summary_lines = [
        f"# {run_result['variant'].title()} Run Summary",
        "",
        f"- run_name: {run_result['run_name']}",
        f"- benchmark_manifest: {run_result['benchmark_manifest']}",
        f"- average_quality_score: {run_result['summary']['average_quality_score']:.4f}",
        f"- succeeded: {run_result['summary']['succeeded']}",
        f"- failed: {run_result['summary']['failed']}",
        f"- zero_score_items: {run_result.get('quality_diagnosis', {}).get('zero_score_item_count', 0)}",
        f"- missing_artifact_items: {run_result.get('artifact_diagnosis', {}).get('missing_item_count', 0)}",
        f"- translation_backend: {run_result.get('translation_backend', {}).get('active_provider')}",
        f"- translation_backend_available: {run_result.get('translation_backend', {}).get('backend_available')}",
        f"- git_commit: {run_result['code_version'].get('git_commit')}",
    ]
    region_warning_counts = run_result.get("quality_diagnosis", {}).get("region_warning_counts", {})
    if region_warning_counts:
        summary_lines.extend(["", "## Region Warning Counts", ""])
        summary_lines.extend([f"- {warning}: {count}" for warning, count in sorted(region_warning_counts.items())])
    (output_dir / "candidate_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")

    return write_run_result(run_result, destination_dir)


def write_run_result(run_result: dict, destination_dir: str) -> Path:
    output_dir = Path(destination_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    validate_payload_from_schema_file(run_result, Path("harness/schemas/run_result.schema.json"))
    path = output_dir / "run_result.json"
    path.write_text(json.dumps(run_result, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
