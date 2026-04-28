from __future__ import annotations

import unittest

from app.domain.models import EditJobResult, RegionEditResult, StyleProfile, TextRegion


class DomainModelsTest(unittest.TestCase):
    def test_text_region_preserves_contract_shape(self) -> None:
        region = TextRegion(
            id="r1",
            polygon=[(0, 0), (10, 0), (10, 10), (0, 10)],
            bbox=(0, 0, 10, 10),
            rotation_deg=0.0,
        )
        self.assertEqual(region.id, "r1")
        self.assertEqual(region.bbox, (0, 0, 10, 10))

    def test_edit_job_result_to_dict_keeps_region_results(self) -> None:
        result = EditJobResult(
            output_image_path="outputs/sample/99_final.jpg",
            quality_score=0.75,
            used_fallback=False,
            warnings=["warn"],
            region_results=[
                RegionEditResult(
                    region_id="r1",
                    source_text="source",
                    target_text="target",
                    quality_score=0.8,
                )
            ],
        )
        payload = result.to_dict()
        self.assertEqual(payload["quality_score"], 0.75)
        self.assertEqual(payload["region_results"][0]["target_text"], "target")

    def test_style_profile_has_defaults(self) -> None:
        profile = StyleProfile()
        self.assertEqual(profile.fill_color, (255, 255, 255))
        self.assertEqual(profile.align, "center")


if __name__ == "__main__":
    unittest.main()
