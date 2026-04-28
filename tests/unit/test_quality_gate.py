from __future__ import annotations

import unittest
from unittest.mock import patch

from app.domain.models import RecognizedTextRegion, TextRegion
from app.pipeline.quality_gate import OCRQualityValidator


class _FakeOCR:
    def __init__(self, texts: list[str]) -> None:
        self._texts = texts

    def detect(self, image_path: str) -> list[TextRegion]:
        return [
            TextRegion(
                id=f"r{index}",
                polygon=[(0, 0), (10, 0), (10, 10), (0, 10)],
                bbox=(0, 0, 10, 10),
                rotation_deg=0.0,
            )
            for index, _ in enumerate(self._texts)
        ]

    def recognize(self, image_path: str, regions: list[TextRegion]) -> list[RecognizedTextRegion]:
        return [
            RecognizedTextRegion(
                region=region,
                text=text,
                confidence=0.99,
                source_lang="en",
            )
            for region, text in zip(regions, self._texts)
        ]


class OCRQualityValidatorUnitTest(unittest.TestCase):
    def test_resolve_ocr_lang_covers_documented_languages(self) -> None:
        self.assertEqual(OCRQualityValidator._resolve_ocr_lang("ja", "korean"), "japan")
        self.assertEqual(OCRQualityValidator._resolve_ocr_lang("zh", "korean"), "ch")
        self.assertEqual(OCRQualityValidator._resolve_ocr_lang("th", "korean"), "th")

    def test_validate_uses_token_counts_instead_of_duplicate_membership(self) -> None:
        validator = OCRQualityValidator(lang="en")
        with patch.object(validator, "_get_ocr", return_value=_FakeOCR(["sale"])):
            score = validator.validate("virtual.png", ["sale sale"], "en")

        self.assertEqual(score, 0.5)

    def test_validate_normalizes_accents_and_case(self) -> None:
        validator = OCRQualityValidator(lang="en")
        with patch.object(validator, "_get_ocr", return_value=_FakeOCR(["Cafe Promo"])):
            score = validator.validate("virtual.png", ["CAFÉ promo"], "en")

        self.assertEqual(score, 1.0)


if __name__ == "__main__":
    unittest.main()
