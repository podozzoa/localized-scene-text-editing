from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

from app.domain.models import RecognizedTextRegion, TextRegion


class DebugArtifactWriter:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write_boxes_image(self, image_path: str, regions: list[TextRegion], output_name: str) -> str:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(image_path)

        for region in regions:
            pts = np.array(region.polygon, np.int32).reshape((-1, 1, 2))
            cv2.polylines(image, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            x, y, w, h = region.bbox
            cv2.putText(
                image,
                region.id,
                (x, max(0, y - 5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )

        out_path = self.root / output_name
        cv2.imwrite(str(out_path), image)
        return str(out_path)

    def write_mask_image(self, mask: np.ndarray, output_name: str) -> str:
        out_path = self.root / output_name
        cv2.imwrite(str(out_path), mask)
        return str(out_path)

    def write_ocr_json(self, recognized: list[RecognizedTextRegion], output_name: str) -> str:
        serializable = []
        for r in recognized:
            serializable.append(
                {
                    "id": r.region.id,
                    "polygon": r.region.polygon,
                    "bbox": r.region.bbox,
                    "rotation_deg": r.region.rotation_deg,
                    "text": r.text,
                    "confidence": r.confidence,
                    "source_lang": r.source_lang,
                }
            )

        out_path = self.root / output_name
        out_path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(out_path)

    def write_quality_json(self, payload: dict, output_name: str) -> str:
        out_path = self.root / output_name
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(out_path)
