from __future__ import annotations

import cv2
import numpy as np

from app.config import AppConfig
from app.domain.interfaces import IStyleEstimator
from app.domain.models import RecognizedTextRegion, ShadowStyle, StyleProfile
from app.infra.image.color_utils import clamp_color, color_distance, contrast_ratio, dominant_color, luminance, safe_mean_color
from app.infra.image.geometry import clamp_bbox


class HeuristicStyleEstimator(IStyleEstimator):
    """
    포스터용 개선판:
    - 전경/배경 색을 분리해 원문 색감에 더 가깝게 추정
    - 전경 외곽 링에서 stroke 색을 따로 뽑아 원본 외곽선 느낌을 복원
    - bbox 높이를 기준으로 원본에 가까운 글자 크기를 유도
    """

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    @staticmethod
    def _build_local_masks(
        polygon: list[tuple[int, int]],
        bbox: tuple[int, int, int, int],
    ) -> tuple[np.ndarray, np.ndarray]:
        x, y, w, h = bbox
        local_poly = np.array([[(px - x), (py - y)] for px, py in polygon], dtype=np.int32)

        text_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(text_mask, [local_poly], 255)

        outer_kernel = np.ones((9, 9), dtype=np.uint8)
        expanded = cv2.dilate(text_mask, outer_kernel, iterations=2)
        outer_ring = cv2.subtract(expanded, text_mask)
        return text_mask, outer_ring

    @staticmethod
    def _foreground_mask(crop_rgb: np.ndarray, text_mask: np.ndarray, background_color: tuple[int, int, int]) -> np.ndarray:
        gray = cv2.cvtColor(crop_rgb, cv2.COLOR_RGB2GRAY)
        masked_gray = gray[text_mask > 0]
        if masked_gray.size == 0:
            return np.zeros_like(text_mask)

        otsu_threshold, _ = cv2.threshold(masked_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        bg_luma = luminance(background_color)

        dark_mask = ((gray <= otsu_threshold) & (text_mask > 0)).astype(np.uint8) * 255
        light_mask = ((gray >= otsu_threshold) & (text_mask > 0)).astype(np.uint8) * 255

        pixels = crop_rgb[text_mask > 0]
        distances = color_distance(pixels, background_color)
        distance_mask = np.zeros_like(text_mask)
        distance_mask[text_mask > 0] = (distances > max(18.0, np.percentile(distances, 55))).astype(np.uint8) * 255

        candidate_masks = [cv2.bitwise_and(dark_mask, distance_mask), cv2.bitwise_and(light_mask, distance_mask)]
        best_mask = candidate_masks[0]
        best_score = -1.0

        for candidate in candidate_masks:
            candidate_pixels = crop_rgb[candidate > 0]
            if candidate_pixels.size == 0:
                continue
            color = dominant_color(candidate_pixels, fallback=safe_mean_color(candidate_pixels))
            score = contrast_ratio(color, background_color) * max(1.0, candidate_pixels.shape[0] / 24.0)
            if bg_luma > 170 and luminance(color) > bg_luma:
                score *= 0.6
            if bg_luma < 80 and luminance(color) < bg_luma:
                score *= 0.6
            if score > best_score:
                best_score = score
                best_mask = candidate

        if not np.any(best_mask):
            best_mask = distance_mask

        kernel = np.ones((3, 3), dtype=np.uint8)
        return cv2.morphologyEx(best_mask, cv2.MORPH_OPEN, kernel, iterations=1)

    @staticmethod
    def _stroke_mask(foreground_mask: np.ndarray, text_mask: np.ndarray) -> np.ndarray:
        kernel = np.ones((5, 5), dtype=np.uint8)
        expanded = cv2.dilate(foreground_mask, kernel, iterations=1)
        stroke_ring = cv2.subtract(expanded, foreground_mask)
        return cv2.bitwise_and(stroke_ring, text_mask)

    def estimate(self, image_path: str, region: RecognizedTextRegion) -> StyleProfile:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"이미지를 열 수 없습니다: {image_path}")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_height, image_width = image_rgb.shape[:2]
        x, y, w, h = clamp_bbox(region.region.bbox, image_width, image_height)
        crop = image_rgb[y : y + h, x : x + w]

        if crop.size == 0:
            return StyleProfile(font_path=str(self.config.default_font_path))

        text_mask, outer_ring = self._build_local_masks(region.region.polygon, (x, y, w, h))
        background_pixels = crop[outer_ring > 0]
        background_color = dominant_color(background_pixels, fallback=safe_mean_color(crop.reshape(-1, 3)))

        foreground_mask = self._foreground_mask(crop, text_mask, background_color)
        foreground_pixels = crop[foreground_mask > 0]
        fill_color = dominant_color(foreground_pixels, fallback=safe_mean_color(crop[text_mask > 0], fallback=(32, 32, 32)))

        if contrast_ratio(fill_color, background_color) < 2.1:
            fill_color = (250, 250, 250) if luminance(background_color) < 128 else (18, 18, 18)

        stroke_mask = self._stroke_mask(foreground_mask, text_mask)
        stroke_pixels = crop[stroke_mask > 0]
        stroke_color = dominant_color(stroke_pixels, fallback=(255, 255, 255) if luminance(fill_color) < 120 else (20, 20, 20))

        stroke_width = 1
        if stroke_pixels.size > 0 and contrast_ratio(stroke_color, fill_color) > 1.2:
            stroke_width = 2 if min(w, h) >= 70 else 1
        elif contrast_ratio(fill_color, background_color) < 3.0:
            stroke_color = (255, 255, 255) if luminance(fill_color) < 120 else (18, 18, 18)
            stroke_width = 2 if min(w, h) >= 70 else 1
        else:
            stroke_color = None

        source_text = region.text.strip()
        preferred_font_size = int(round(h * (0.86 if len(source_text) <= 8 else 0.76)))
        preferred_font_size = max(self.config.render_min_font_size, min(preferred_font_size, 220))

        shadow_enabled = contrast_ratio(fill_color, background_color) < 2.2
        shadow_color = (0, 0, 0) if luminance(background_color) > 150 else (255, 255, 255)
        padding_ratio = 0.02 if len(source_text) <= 6 else 0.035

        return StyleProfile(
            fill_color=clamp_color(fill_color),
            stroke_color=clamp_color(stroke_color) if stroke_color is not None else None,
            stroke_width=stroke_width,
            font_weight="regular",
            italic=False,
            align="center",
            letter_spacing=0.0,
            line_spacing=0.96,
            shadow=ShadowStyle(
                enabled=shadow_enabled,
                dx=1,
                dy=2,
                blur=0,
                color=shadow_color,
            ),
            font_path=str(self.config.default_font_path),
            preferred_font_size=preferred_font_size,
            padding_ratio=padding_ratio,
        )
