from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import cv2

from app.domain.interfaces import ITextDetector, ITextRecognizer
from app.domain.models import RecognizedTextRegion, TextRegion


class PaddleOCRAdapter(ITextDetector, ITextRecognizer):
    """
    PaddleOCR 단일 엔진에서 detect + recognize를 같이 수행한다.
    현재 MVP에서는 detect()도 내부적으로 OCR 전체 실행 결과에서 박스만 추출한다.
    """

    def __init__(self, lang: str = "korean") -> None:
        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise RuntimeError(
                "paddleocr 가 설치되어 있지 않습니다. "
                "requirements.txt 설치 후 다시 실행하세요."
            ) from exc

        self._ocr = PaddleOCR(use_doc_orientation_classify=False, lang=lang)
        self._result_cache: dict[str, list[Any]] = {}
        self._scale_cache: dict[str, tuple[float, float]] = {}
        self._ocr_max_side = 1400

    def _run_ocr(self, image_path: str) -> list[Any]:
        cache_key = str(Path(image_path).resolve())
        if cache_key in self._result_cache:
            return self._result_cache[cache_key]

        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"이미지를 읽지 못했습니다: {image_path}")

        height, width = image.shape[:2]
        scale_x = 1.0
        scale_y = 1.0
        input_path = image_path

        max_side = max(height, width)
        if max_side > self._ocr_max_side:
            resize_ratio = self._ocr_max_side / max_side
            resized = cv2.resize(
                image,
                (max(1, int(width * resize_ratio)), max(1, int(height * resize_ratio))),
                interpolation=cv2.INTER_AREA,
            )
            resized_height, resized_width = resized.shape[:2]
            scale_x = width / resized_width
            scale_y = height / resized_height

            with NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                input_path = temp_file.name
            cv2.imwrite(input_path, resized)

        result = self._ocr.predict(input_path)
        if input_path != image_path:
            Path(input_path).unlink(missing_ok=True)

        self._result_cache[cache_key] = result
        self._scale_cache[cache_key] = (scale_x, scale_y)
        return result

    @staticmethod
    def _polygon_to_bbox(polygon: list[list[float]]) -> tuple[int, int, int, int]:
        xs = [int(p[0]) for p in polygon]
        ys = [int(p[1]) for p in polygon]
        min_x = min(xs)
        min_y = min(ys)
        max_x = max(xs)
        max_y = max(ys)
        return (min_x, min_y, max_x - min_x, max_y - min_y)

    @staticmethod
    def _rotation_from_polygon(polygon: list[list[float]]) -> float:
        if len(polygon) < 2:
            return 0.0
        x1, y1 = polygon[0]
        x2, y2 = polygon[1]
        dx = x2 - x1
        dy = y2 - y1
        angle = cv2.fastAtan2(dy, dx)
        return float(angle)

    def detect(self, image_path: str) -> list[TextRegion]:
        result = self._run_ocr(image_path)
        cache_key = str(Path(image_path).resolve())
        scale_x, scale_y = self._scale_cache.get(cache_key, (1.0, 1.0))
        regions: list[TextRegion] = []

        for page_idx, page in enumerate(result):
            rec_polys = page.get("rec_polys", [])
            for idx, poly in enumerate(rec_polys):
                raw_poly = poly.tolist() if hasattr(poly, "tolist") else poly
                scaled_poly = [[float(p[0]) * scale_x, float(p[1]) * scale_y] for p in raw_poly]
                polygon = [(int(round(p[0])), int(round(p[1]))) for p in scaled_poly]
                bbox = self._polygon_to_bbox(scaled_poly)
                rotation_deg = self._rotation_from_polygon(scaled_poly)
                regions.append(
                    TextRegion(
                        id=f"p{page_idx}_r{idx}",
                        polygon=polygon,
                        bbox=bbox,
                        rotation_deg=rotation_deg,
                    )
                )

        return regions

    def recognize(self, image_path: str, regions: list[TextRegion]) -> list[RecognizedTextRegion]:
        result = self._run_ocr(image_path)

        recognized: list[RecognizedTextRegion] = []
        flat_idx = 0

        all_texts: list[str] = []
        all_scores: list[float] = []
        for page in result:
            rec_texts = page.get("rec_texts", [])
            rec_scores = page.get("rec_scores", [])
            all_texts.extend(rec_texts)
            all_scores.extend(rec_scores)

        for region in regions:
            if flat_idx >= len(all_texts):
                break
            text = str(all_texts[flat_idx])
            score = float(all_scores[flat_idx]) if flat_idx < len(all_scores) else 0.0
            recognized.append(
                RecognizedTextRegion(
                    region=region,
                    text=text,
                    confidence=score,
                    source_lang=None,
                )
            )
            flat_idx += 1

        return recognized
