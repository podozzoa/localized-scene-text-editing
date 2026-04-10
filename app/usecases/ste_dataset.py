from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2

from app.domain.models import PreparedEditContext, PreparedRegionEdit
from app.infra.image.mask_builder import TextMaskBuilder


@dataclass
class STEDatasetExportResult:
    export_dir: str
    manifest_path: str
    item_count: int


class STEDatasetExporter:
    def __init__(self, context_padding_ratio: float = 0.18) -> None:
        self.context_padding_ratio = max(0.05, context_padding_ratio)
        self.mask_builder = TextMaskBuilder()

    @staticmethod
    def _style_to_dict(prepared_region: PreparedRegionEdit) -> dict:
        style = asdict(prepared_region.style)
        if style.get("shadow") is None:
            style["shadow"] = {}
        return style

    def _expand_bbox(
        self,
        bbox: tuple[int, int, int, int],
        image_shape: tuple[int, int, int],
        role: str,
    ) -> tuple[int, int, int, int]:
        x, y, w, h = bbox
        image_height, image_width = image_shape[:2]
        role_multiplier = 1.35 if role == "headline" else 1.0
        pad_x = int(w * self.context_padding_ratio * role_multiplier)
        pad_y = int(h * self.context_padding_ratio * role_multiplier)
        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(image_width, x + w + pad_x)
        y2 = min(image_height, y + h + pad_y)
        return x1, y1, x2 - x1, y2 - y1

    def export(self, prepared: PreparedEditContext) -> STEDatasetExportResult:
        source_image = cv2.imread(prepared.input_image_path)
        restored_image = cv2.imread(prepared.restored_image_path)
        if source_image is None:
            raise FileNotFoundError(prepared.input_image_path)
        if restored_image is None:
            raise FileNotFoundError(prepared.restored_image_path)

        export_dir = Path(prepared.job_dir) / "ste_dataset"
        region_dir = export_dir / "regions"
        export_dir.mkdir(parents=True, exist_ok=True)
        region_dir.mkdir(parents=True, exist_ok=True)

        cv2.imwrite(str(export_dir / "source_image.jpg"), source_image)
        cv2.imwrite(str(export_dir / "restored_image.jpg"), restored_image)

        full_mask = self.mask_builder.build_mask(
            source_image.shape,
            [item.region for item in prepared.editable_regions],
        )
        cv2.imwrite(str(export_dir / "full_mask.png"), full_mask)

        manifest_items: list[dict] = []
        for index, item in enumerate(prepared.editable_regions, start=1):
            region_mask = self.mask_builder.build_mask(source_image.shape, [item.region])
            crop_bbox = self._expand_bbox(item.region.region.bbox, source_image.shape, item.role)
            x, y, w, h = crop_bbox

            source_crop = source_image[y : y + h, x : x + w]
            restored_crop = restored_image[y : y + h, x : x + w]
            mask_crop = region_mask[y : y + h, x : x + w]

            stem = f"region_{index:02d}"
            source_crop_path = region_dir / f"{stem}_source.png"
            restored_crop_path = region_dir / f"{stem}_restored.png"
            mask_crop_path = region_dir / f"{stem}_mask.png"

            cv2.imwrite(str(source_crop_path), source_crop)
            cv2.imwrite(str(restored_crop_path), restored_crop)
            cv2.imwrite(str(mask_crop_path), mask_crop)

            chosen = item.chosen_candidate.text if item.chosen_candidate else item.region.text
            manifest_items.append(
                {
                    "region_index": index,
                    "region_id": item.region.region.id,
                    "role": item.role,
                    "source_text": item.region.text,
                    "target_text": chosen,
                    "candidate_texts": [candidate.text for candidate in item.candidates[:5]],
                    "region_bbox": item.region.region.bbox,
                    "crop_bbox": crop_bbox,
                    "polygon": item.region.region.polygon,
                    "confidence": item.region.confidence,
                    "style": self._style_to_dict(item),
                    "artifacts": {
                        "source_crop": str(source_crop_path.relative_to(export_dir)),
                        "restored_crop": str(restored_crop_path.relative_to(export_dir)),
                        "mask_crop": str(mask_crop_path.relative_to(export_dir)),
                    },
                }
            )

        manifest = {
            "schema_version": 1,
            "input_image_path": prepared.input_image_path,
            "target_lang": prepared.target_lang,
            "restored_image_path": prepared.restored_image_path,
            "full_artifacts": {
                "source_image": "source_image.jpg",
                "restored_image": "restored_image.jpg",
                "full_mask": "full_mask.png",
            },
            "items": manifest_items,
        }

        manifest_path = export_dir / "ste_manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        markdown_lines = [
            "# STE Dataset Export",
            "",
            f"- input_image_path: {prepared.input_image_path}",
            f"- restored_image_path: {prepared.restored_image_path}",
            f"- item_count: {len(manifest_items)}",
            "",
            "| idx | role | source | target | crop |",
            "| --- | --- | --- | --- | --- |",
        ]
        for manifest_item in manifest_items:
            markdown_lines.append(
                f"| {manifest_item['region_index']} | {manifest_item['role']} | "
                f"{manifest_item['source_text']} | {manifest_item['target_text']} | "
                f"{manifest_item['artifacts']['source_crop']} |"
            )
        (export_dir / "README.md").write_text("\n".join(markdown_lines), encoding="utf-8")

        return STEDatasetExportResult(
            export_dir=str(export_dir),
            manifest_path=str(manifest_path),
            item_count=len(manifest_items),
        )
