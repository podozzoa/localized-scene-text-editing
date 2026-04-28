from __future__ import annotations

from collections import Counter
import re
import unicodedata

from app.domain.interfaces import IQualityValidator
from app.infra.ocr.paddle_ocr_adapter import PaddleOCRAdapter


class OCRQualityValidator(IQualityValidator):
    """
    개선판:
    - target language 에 맞는 OCR 모델 선택
    - 완전 일치 대신 토큰 포함률 기반으로 부분 성공을 반영
    """

    def __init__(self, lang: str = "korean") -> None:
        self.default_lang = lang
        self._ocr_cache: dict[str, PaddleOCRAdapter] = {}

    @staticmethod
    def _normalize_tokens(text: str) -> list[str]:
        normalized = unicodedata.normalize("NFKD", text)
        normalized = "".join(char for char in normalized if not unicodedata.combining(char))
        normalized = re.sub(r"[^\w%]+", " ", normalized.lower(), flags=re.UNICODE)
        return [token for token in normalized.split() if token]

    @staticmethod
    def _resolve_ocr_lang(target_lang: str, fallback: str) -> str:
        mapping = {
            "ko": "korean",
            "kr": "korean",
            "en": "en",
            "vi": "en",
            "ja": "japan",
            "jp": "japan",
            "zh": "ch",
            "cn": "ch",
            "th": "th",
        }
        return mapping.get(target_lang.lower(), fallback)

    def _get_ocr(self, target_lang: str) -> PaddleOCRAdapter:
        ocr_lang = self._resolve_ocr_lang(target_lang, self.default_lang)
        if ocr_lang not in self._ocr_cache:
            self._ocr_cache[ocr_lang] = PaddleOCRAdapter(lang=ocr_lang)
        return self._ocr_cache[ocr_lang]

    def validate(self, image_path: str, expected_texts: list[str], target_lang: str) -> float:
        if not expected_texts:
            return 0.0

        ocr = self._get_ocr(target_lang)
        regions = ocr.detect(image_path)
        recognized = ocr.recognize(image_path, regions)
        actual_tokens = self._normalize_tokens(" ".join(r.text for r in recognized))
        if not actual_tokens:
            return 0.0

        scores: list[float] = []
        for expected in expected_texts:
            expected_tokens = self._normalize_tokens(expected)
            if not expected_tokens:
                continue
            actual_counts = Counter(actual_tokens)
            expected_counts = Counter(expected_tokens)
            matched = sum(min(actual_counts[token], count) for token, count in expected_counts.items())
            scores.append(matched / sum(expected_counts.values()))

        if not scores:
            return 0.0

        return sum(scores) / len(scores)
