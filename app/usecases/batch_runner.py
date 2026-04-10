from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from app.domain.models import EditJobResult


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


@dataclass
class BatchItemResult:
    input_path: str
    output_image_path: str
    quality_score: float
    warnings: list[str]
    failed: bool = False
    error: str | None = None


@dataclass
class BatchRunSummary:
    input_dir: str
    target_lang: str
    total_images: int
    succeeded: int
    failed: int
    average_quality_score: float
    items: list[BatchItemResult]

    def to_dict(self) -> dict:
        return asdict(self)


def collect_input_images(input_dir: str) -> list[Path]:
    root = Path(input_dir)
    if not root.exists():
        raise FileNotFoundError(f"입력 디렉터리가 없습니다: {input_dir}")
    if not root.is_dir():
        raise NotADirectoryError(f"입력 경로가 디렉터리가 아닙니다: {input_dir}")
    return sorted(path for path in root.iterdir() if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS)


def run_batch(
    engine,
    input_dir: str,
    target_lang: str,
    output_root: Path,
    ste_exporter=None,
) -> BatchRunSummary:
    images = collect_input_images(input_dir)
    items: list[BatchItemResult] = []
    succeeded = 0
    score_total = 0.0

    for image_path in images:
        try:
            if ste_exporter is not None:
                prepared = engine.prepare_edit_context(str(image_path), target_lang)
                ste_exporter.export(prepared)
                result: EditJobResult = engine.run_prepared(prepared)
            else:
                result = engine.run(str(image_path), target_lang)
            items.append(
                BatchItemResult(
                    input_path=str(image_path),
                    output_image_path=result.output_image_path,
                    quality_score=result.quality_score,
                    warnings=result.warnings,
                )
            )
            succeeded += 1
            score_total += result.quality_score
        except Exception as exc:
            items.append(
                BatchItemResult(
                    input_path=str(image_path),
                    output_image_path="",
                    quality_score=0.0,
                    warnings=[],
                    failed=True,
                    error=str(exc),
                )
            )

    summary = BatchRunSummary(
        input_dir=str(Path(input_dir)),
        target_lang=target_lang,
        total_images=len(images),
        succeeded=succeeded,
        failed=len(images) - succeeded,
        average_quality_score=(score_total / succeeded) if succeeded else 0.0,
        items=items,
    )

    report_dir = output_root / "_batch_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    summary_path = report_dir / f"batch_{target_lang}.json"
    summary_path.write_text(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    markdown_lines = [
        f"# Batch Summary ({target_lang})",
        "",
        f"- input_dir: {summary.input_dir}",
        f"- total_images: {summary.total_images}",
        f"- succeeded: {summary.succeeded}",
        f"- failed: {summary.failed}",
        f"- average_quality_score: {summary.average_quality_score:.4f}",
        "",
        "| image | score | status | output |",
        "| --- | ---: | --- | --- |",
    ]
    for item in items:
        status = "failed" if item.failed else ("warning" if item.warnings else "ok")
        output = item.error if item.failed else item.output_image_path
        markdown_lines.append(f"| {Path(item.input_path).name} | {item.quality_score:.4f} | {status} | {output} |")

    markdown_path = report_dir / f"batch_{target_lang}.md"
    markdown_path.write_text("\n".join(markdown_lines), encoding="utf-8")

    return summary
