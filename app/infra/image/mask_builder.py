from __future__ import annotations

import cv2
import numpy as np

from app.domain.models import RecognizedTextRegion


class TextMaskBuilder:
    def __init__(self, dilation_kernel_size: int = 5) -> None:
        self.dilation_kernel_size = dilation_kernel_size

    @staticmethod
    def _padded_rect(
        bbox: tuple[int, int, int, int],
        image_shape: tuple[int, int, int],
    ) -> tuple[int, int, int, int]:
        x, y, w, h = bbox
        image_h, image_w = image_shape[:2]
        pad_x = max(3, int(w * 0.08))
        pad_y = max(3, int(h * 0.18))
        return (
            max(0, x - pad_x),
            max(0, y - pad_y),
            min(image_w, x + w + pad_x),
            min(image_h, y + h + pad_y),
        )

    def build_mask(self, image_shape: tuple[int, int, int], regions: list[RecognizedTextRegion]) -> np.ndarray:
        height, width = image_shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)

        for r in regions:
            polygon = np.array(r.region.polygon, dtype=np.int32)
            cv2.fillPoly(mask, [polygon], 255)
            x, y, w, h = r.region.bbox
            area_ratio = (w * h) / max(1, width * height)
            if h < height * 0.07 or area_ratio < 0.002:
                rx1, ry1, rx2, ry2 = self._padded_rect(r.region.bbox, image_shape)
                cv2.rectangle(mask, (rx1, ry1), (rx2, ry2), 255, thickness=-1)

        kernel = np.ones((self.dilation_kernel_size, self.dilation_kernel_size), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)
        return mask
