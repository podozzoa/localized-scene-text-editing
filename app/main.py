from __future__ import annotations

import argparse
import os
from pathlib import Path

from app.config import AppConfig
from app.infra.image.inpainter import OpenCVInpainter
from app.infra.image.renderer import PILTextRenderer
from app.infra.image.style_estimator import HeuristicStyleEstimator
from app.infra.ocr.paddle_ocr_adapter import PaddleOCRAdapter
from app.infra.translate.localization_rewriter import SimpleLocalizationRewriter
from app.infra.translate.translator_adapter import TranslationSettings, TranslatorAdapter
from app.pipeline.engine import LocalizationEngine
from app.pipeline.quality_gate import OCRQualityValidator
from app.usecases.batch_runner import run_batch
from app.usecases.ste_dataset import STEDatasetExporter


def _load_dotenv_if_present(dotenv_path: str = ".env") -> None:
    env_file = Path(dotenv_path)
    if not env_file.exists() or not env_file.is_file():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Localized Scene Text Editing MVP")
    parser.add_argument("--input", help="입력 이미지 경로")
    parser.add_argument("--input-dir", help="입력 이미지 디렉터리")
    parser.add_argument("--target-lang", required=True, help="타겟 언어. 예: ko, en")
    parser.add_argument("--output-root", default="outputs", help="출력 루트 디렉터리")
    parser.add_argument("--font-path", default="assets/fonts/NotoSansKR-Regular.ttf", help="렌더링 폰트 경로")
    parser.add_argument("--ocr-lang", default="korean", help="PaddleOCR 언어 힌트")
    parser.add_argument("--translation-provider", default="auto", help="번역 백엔드. 예: auto, identity, openai, hf_local")
    parser.add_argument("--translation-model", default="gpt-4.1-mini", help="OpenAI-compatible 번역 모델명")
    parser.add_argument("--translation-local-model", default="facebook/nllb-200-distilled-600M", help="로컬 번역 모델명")
    parser.add_argument("--source-lang", default="ko", help="원문 언어 코드. 예: ko, en")
    parser.add_argument("--export-ste-dataset", action="store_true", help="STE 실험용 crop/mask/manifest를 추가로 저장")
    parser.add_argument("--ste-context-padding-ratio", type=float, default=0.18, help="STE export 시 텍스트 주변 컨텍스트 패딩 비율")
    return parser


def _build_engine(args: argparse.Namespace) -> tuple[LocalizationEngine, AppConfig]:
    config = AppConfig(
        output_root=Path(args.output_root),
        default_font_path=Path(args.font_path),
        ocr_language_hint=args.ocr_lang,
    )

    ocr_adapter = PaddleOCRAdapter(lang=config.ocr_language_hint)
    translator = TranslatorAdapter(
        TranslationSettings(
            provider=args.translation_provider,
            model=args.translation_model,
            source_lang=args.source_lang,
            local_model_name=args.translation_local_model,
        )
    )

    engine = LocalizationEngine(
        config=config,
        detector=ocr_adapter,
        recognizer=ocr_adapter,
        rewriter=SimpleLocalizationRewriter(translator=translator),
        restorer=OpenCVInpainter(inpaint_radius=config.inpaint_radius),
        style_estimator=HeuristicStyleEstimator(config=config),
        renderer=PILTextRenderer(config=config),
        validator=OCRQualityValidator(lang=config.ocr_language_hint),
    )
    return engine, config


def main() -> None:
    _load_dotenv_if_present()
    parser = build_parser()
    args = parser.parse_args()

    if not args.input and not args.input_dir:
        parser.error("--input 또는 --input-dir 중 하나는 필요합니다.")
    if args.input and args.input_dir:
        parser.error("--input 과 --input-dir 은 동시에 사용할 수 없습니다.")

    engine, config = _build_engine(args)
    ste_exporter = STEDatasetExporter(args.ste_context_padding_ratio) if args.export_ste_dataset else None

    if args.input_dir:
        summary = run_batch(
            engine=engine,
            input_dir=args.input_dir,
            target_lang=args.target_lang,
            output_root=config.output_root,
            ste_exporter=ste_exporter,
        )
        print("=== Batch Localization Result ===")
        print(f"input_dir: {summary.input_dir}")
        print(f"total_images: {summary.total_images}")
        print(f"succeeded: {summary.succeeded}")
        print(f"failed: {summary.failed}")
        print(f"average_quality_score: {summary.average_quality_score:.4f}")
        print(f"report_json: {config.output_root / '_batch_reports' / f'batch_{args.target_lang}.json'}")
        print(f"report_md: {config.output_root / '_batch_reports' / f'batch_{args.target_lang}.md'}")
        return

    if ste_exporter is not None:
        prepared = engine.prepare_edit_context(args.input, args.target_lang)
        ste_result = ste_exporter.export(prepared)
        result = engine.run_prepared(prepared)
        print("ste_dataset:")
        print(f" - export_dir: {ste_result.export_dir}")
        print(f" - manifest_path: {ste_result.manifest_path}")
        print(f" - item_count: {ste_result.item_count}")
    else:
        result = engine.run(args.input, args.target_lang)

    print("=== Localization Result ===")
    print(f"output_image_path: {result.output_image_path}")
    print(f"quality_score: {result.quality_score:.4f}")
    print(f"used_fallback: {result.used_fallback}")
    if result.warnings:
        print("warnings:")
        for warning in result.warnings:
            print(f" - {warning}")

    print("region_results:")
    for rr in result.region_results:
        print(
            f" - {rr.region_id}: '{rr.source_text}' -> '{rr.target_text}' "
            f"(score={rr.quality_score:.4f})"
        )


if __name__ == "__main__":
    main()
