from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from app.domain.models import (
    LocalizedCandidate,
    PreparedEditContext,
    PreparedRegionEdit,
    RecognizedTextRegion,
    StyleProfile,
    TextRegion,
)
from app.usecases.ste_dataset import STEDatasetExporter


class STEDatasetExporterUnitTest(unittest.TestCase):
    def test_export_manifest_preserves_adapter_contract_fields(self) -> None:
        source = np.zeros((20, 30, 3), dtype=np.uint8)
        restored = np.ones((20, 30, 3), dtype=np.uint8)
        region = RecognizedTextRegion(
            region=TextRegion(
                id="r1",
                bbox=(5, 4, 10, 6),
                polygon=[(5, 4), (15, 4), (15, 10), (5, 10)],
            ),
            text="청정라거",
            confidence=0.91,
            source_lang="ko",
        )
        candidate = LocalizedCandidate(
            text="Clean lager",
            semantic_score=0.9,
            layout_fit_score=0.8,
            brevity_score=0.7,
            final_score=0.85,
        )
        prepared = PreparedEditContext(
            input_image_path="input.jpg",
            target_lang="en",
            job_dir="outputs/job",
            restored_image_path="restored.jpg",
            original_image_shape=source.shape,
            editable_regions=[
                PreparedRegionEdit(
                    region=region,
                    role="headline",
                    style=StyleProfile(fill_color=(1, 2, 3), stroke_width=2),
                    candidates=[candidate],
                    chosen_candidate=candidate,
                )
            ],
        )
        written_text: dict[str, str] = {}
        written_images: list[str] = []

        def _capture_write_text(self: Path, text: str, encoding: str | None = None) -> int:
            written_text[self.name] = text
            return len(text)

        def _capture_imwrite(path: str, image) -> bool:
            written_images.append(Path(path).name)
            return True

        with patch("app.usecases.ste_dataset.cv2.imread", side_effect=[source, restored]), patch(
            "app.usecases.ste_dataset.cv2.imwrite", side_effect=_capture_imwrite
        ), patch("app.usecases.ste_dataset.Path.mkdir"), patch(
            "app.usecases.ste_dataset.Path.write_text", new=_capture_write_text
        ):
            result = STEDatasetExporter().export(prepared)

        manifest = json.loads(written_text["ste_manifest.json"])
        item = manifest["items"][0]

        self.assertEqual(result.item_count, 1)
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["target_lang"], "en")
        self.assertEqual(item["region_id"], "r1")
        self.assertEqual(item["role"], "headline")
        self.assertEqual(item["source_text"], "청정라거")
        self.assertEqual(item["target_text"], "Clean lager")
        self.assertEqual(item["candidate_texts"], ["Clean lager"])
        self.assertEqual(item["confidence"], 0.91)
        self.assertIn("style", item)
        self.assertEqual(
            set(item["artifacts"]),
            {"source_crop", "restored_crop", "mask_crop"},
        )
        self.assertIn("source_image.jpg", written_images)
        self.assertIn("restored_image.jpg", written_images)
        self.assertIn("full_mask.png", written_images)


if __name__ == "__main__":
    unittest.main()
