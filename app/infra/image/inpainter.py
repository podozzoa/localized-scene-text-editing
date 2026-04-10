from __future__ import annotations

import cv2
import numpy as np

from app.domain.interfaces import IBackgroundRestorer
from app.domain.models import RecognizedTextRegion
from app.infra.image.mask_builder import TextMaskBuilder


class OpenCVInpainter(IBackgroundRestorer):
    def __init__(self, inpaint_radius: int = 3) -> None:
        self.inpaint_radius = inpaint_radius
        self.mask_builder = TextMaskBuilder()

    @staticmethod
    def _refine_mask(mask: np.ndarray) -> np.ndarray:
        kernel = np.ones((7, 7), np.uint8)
        refined = cv2.dilate(mask, kernel, iterations=1)
        refined = cv2.morphologyEx(refined, cv2.MORPH_CLOSE, kernel, iterations=1)
        refined = cv2.medianBlur(refined, 5)
        refined = cv2.GaussianBlur(refined, (5, 5), 0)
        _, refined = cv2.threshold(refined, 10, 255, cv2.THRESH_BINARY)
        return refined

    @staticmethod
    def _score_candidate(original: np.ndarray, candidate: np.ndarray, mask: np.ndarray) -> float:
        ring_kernel = np.ones((9, 9), np.uint8)
        expanded = cv2.dilate(mask, ring_kernel, iterations=1)
        seam_ring = cv2.subtract(expanded, mask)
        if not np.any(seam_ring):
            return 0.0

        original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        candidate_gray = cv2.cvtColor(candidate, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(original_gray, candidate_gray)
        return float(diff[seam_ring > 0].mean())

    def restore(self, image_path: str, regions: list[RecognizedTextRegion], output_path: str) -> str:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"이미지를 열 수 없습니다: {image_path}")

        base_mask = self.mask_builder.build_mask(image.shape, regions)
        refined_mask = self._refine_mask(base_mask)

        telea = cv2.inpaint(image, refined_mask, self.inpaint_radius, cv2.INPAINT_TELEA)
        ns = cv2.inpaint(image, refined_mask, self.inpaint_radius + 1, cv2.INPAINT_NS)
        expanded_mask = cv2.dilate(refined_mask, np.ones((5, 5), np.uint8), iterations=1)
        telea = cv2.inpaint(telea, expanded_mask, max(1, self.inpaint_radius - 1), cv2.INPAINT_TELEA)
        ns = cv2.inpaint(ns, expanded_mask, self.inpaint_radius, cv2.INPAINT_NS)

        telea_score = self._score_candidate(image, telea, refined_mask)
        ns_score = self._score_candidate(image, ns, refined_mask)
        restored = telea if telea_score <= ns_score else ns

        ok = cv2.imwrite(output_path, restored)
        if not ok:
            raise RuntimeError(f"복원 이미지 저장 실패: {output_path}")

        return output_path
