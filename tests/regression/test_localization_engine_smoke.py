from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from app.config import AppConfig
from app.domain.models import (
    LocalizedCandidate,
    PreparedEditContext,
    PreparedRegionEdit,
    RecognizedTextRegion,
    StyleProfile,
    TextRegion,
)
from app.pipeline.engine import LocalizationEngine


class _FakeRewriter:
    def rewrite(self, text: str, target_lang: str, width: int, height: int) -> list[LocalizedCandidate]:
        return [
            LocalizedCandidate(
                text="localized text",
                semantic_score=0.9,
                layout_fit_score=0.9,
                brevity_score=0.9,
                final_score=0.9,
            )
        ]


class _FakeRestorer:
    def restore(self, image_path: str, regions: list[RecognizedTextRegion], output_path: str) -> str:
        return output_path


class _FakeStyleEstimator:
    def estimate(self, image_path: str, region: RecognizedTextRegion) -> StyleProfile:
        return StyleProfile()


class _FakeRenderer:
    def render(self, image_path: str, region: RecognizedTextRegion, text: str, style: StyleProfile, output_path: str) -> str:
        return output_path


class _FakeValidator:
    def validate(self, image_path: str, expected_texts: list[str], target_lang: str) -> float:
        return 0.95 if expected_texts else 0.0


class LocalizationEngineRegressionSmokeTest(unittest.TestCase):
    def test_engine_run_prepared_path_produces_expected_result_contract(self) -> None:
        region = TextRegion(
            id="r1",
            polygon=[(20, 20), (180, 20), (180, 80), (20, 80)],
            bbox=(20, 20, 160, 60),
            rotation_deg=0.0,
        )
        recognized = RecognizedTextRegion(
            region=region,
            text="원문 텍스트",
            confidence=0.99,
            source_lang="ko",
        )
        chosen = _FakeRewriter().rewrite("원문 텍스트", "en", 160, 60)[0]
        prepared = PreparedEditContext(
            input_image_path="virtual-input.png",
            target_lang="en",
            job_dir="virtual-job",
            restored_image_path="virtual-job/04_restored.jpg",
            original_image_shape=(200, 300, 3),
            editable_regions=[
                PreparedRegionEdit(
                    region=recognized,
                    role="headline",
                    style=StyleProfile(),
                    candidates=[chosen],
                    chosen_candidate=chosen,
                )
            ],
            skipped_regions=[],
        )

        engine = LocalizationEngine(
            config=AppConfig(output_root=Path("outputs")),
            detector=None,
            recognizer=None,
            rewriter=_FakeRewriter(),
            restorer=_FakeRestorer(),
            style_estimator=_FakeStyleEstimator(),
            renderer=_FakeRenderer(),
            validator=_FakeValidator(),
        )

        quality_payloads: list[tuple[dict, str]] = []

        class _FakeDebugWriter:
            def __init__(self, job_dir) -> None:
                self.job_dir = job_dir

            def write_quality_json(self, payload: dict, filename: str) -> None:
                quality_payloads.append((payload, filename))

        with patch("app.pipeline.engine.cv2.imread", return_value=object()), patch(
            "app.pipeline.engine.cv2.imwrite", return_value=True
        ), patch("app.pipeline.engine.DebugArtifactWriter", _FakeDebugWriter):
            result = engine.run_prepared(prepared)

        self.assertEqual(Path(result.output_image_path), Path("virtual-job/99_final.jpg"))
        self.assertGreater(result.quality_score, 0.0)
        self.assertEqual(result.region_results[0].target_text, "localized text")
        self.assertEqual(quality_payloads[0][1], "98_quality.json")

    def test_engine_validates_target_script_skipped_text_as_passthrough(self) -> None:
        region = TextRegion(
            id="r1",
            polygon=[(20, 20), (180, 20), (180, 80), (20, 80)],
            bbox=(20, 20, 160, 60),
            rotation_deg=0.0,
        )
        recognized = RecognizedTextRegion(
            region=region,
            text="SALE 50%",
            confidence=0.99,
            source_lang="en",
        )
        prepared = PreparedEditContext(
            input_image_path="virtual-input.png",
            target_lang="en",
            job_dir="virtual-job",
            restored_image_path="virtual-job/04_restored.jpg",
            original_image_shape=(200, 300, 3),
            editable_regions=[],
            skipped_regions=[recognized],
        )
        validator = _FakeValidator()
        engine = LocalizationEngine(
            config=AppConfig(output_root=Path("outputs")),
            detector=None,
            recognizer=None,
            rewriter=_FakeRewriter(),
            restorer=_FakeRestorer(),
            style_estimator=_FakeStyleEstimator(),
            renderer=_FakeRenderer(),
            validator=validator,
        )

        with patch("app.pipeline.engine.cv2.imread", return_value=object()), patch(
            "app.pipeline.engine.cv2.imwrite", return_value=True
        ), patch("app.pipeline.engine.DebugArtifactWriter"):
            result = engine.run_prepared(prepared)

        self.assertGreater(result.quality_score, 0.0)
        self.assertEqual(result.region_results[0].warning, "non-editable region skipped")

    def test_engine_does_not_mix_skipped_text_into_validation_when_editable_regions_exist(self) -> None:
        editable_region = TextRegion(
            id="editable",
            polygon=[(20, 20), (180, 20), (180, 80), (20, 80)],
            bbox=(20, 20, 160, 60),
            rotation_deg=0.0,
        )
        skipped_region = TextRegion(
            id="skipped",
            polygon=[(200, 20), (260, 20), (260, 60), (200, 60)],
            bbox=(200, 20, 60, 40),
            rotation_deg=0.0,
        )
        chosen = _FakeRewriter().rewrite("원문 텍스트", "en", 160, 60)[0]
        prepared = PreparedEditContext(
            input_image_path="virtual-input.png",
            target_lang="en",
            job_dir="virtual-job",
            restored_image_path="virtual-job/04_restored.jpg",
            original_image_shape=(200, 300, 3),
            editable_regions=[
                PreparedRegionEdit(
                    region=RecognizedTextRegion(editable_region, "원문 텍스트", 0.99, "ko"),
                    role="headline",
                    style=StyleProfile(),
                    candidates=[chosen],
                    chosen_candidate=chosen,
                )
            ],
            skipped_regions=[
                RecognizedTextRegion(skipped_region, "TERRA", 0.99, "en"),
            ],
        )
        observed_expected_texts: list[str] = []

        class _RecordingValidator:
            def validate(self, image_path: str, expected_texts: list[str], target_lang: str) -> float:
                observed_expected_texts.extend(expected_texts)
                return 1.0

        engine = LocalizationEngine(
            config=AppConfig(output_root=Path("outputs")),
            detector=None,
            recognizer=None,
            rewriter=_FakeRewriter(),
            restorer=_FakeRestorer(),
            style_estimator=_FakeStyleEstimator(),
            renderer=_FakeRenderer(),
            validator=_RecordingValidator(),
        )

        with patch("app.pipeline.engine.cv2.imread", return_value=object()), patch(
            "app.pipeline.engine.cv2.imwrite", return_value=True
        ), patch("app.pipeline.engine.DebugArtifactWriter"):
            engine.run_prepared(prepared)

        self.assertEqual(observed_expected_texts, ["localized text"])


if __name__ == "__main__":
    unittest.main()
