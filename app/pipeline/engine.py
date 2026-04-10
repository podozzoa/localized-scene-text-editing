from __future__ import annotations

import re
from pathlib import Path

import cv2

from app.config import AppConfig
from app.domain.models import (
    EditJobResult,
    PreparedEditContext,
    PreparedRegionEdit,
    RecognizedTextRegion,
    RegionEditResult,
    TextRegion,
)
from app.infra.image.mask_builder import TextMaskBuilder
from app.usecases.debug_artifacts import DebugArtifactWriter


class LocalizationEngine:
    def __init__(
        self,
        config: AppConfig,
        detector,
        recognizer,
        rewriter,
        restorer,
        style_estimator,
        renderer,
        validator,
    ) -> None:
        self.config = config
        self.detector = detector
        self.recognizer = recognizer
        self.rewriter = rewriter
        self.restorer = restorer
        self.style_estimator = style_estimator
        self.renderer = renderer
        self.validator = validator

    @staticmethod
    def _normalize_text(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip())

    @staticmethod
    def _is_ascii_upper_token(text: str) -> bool:
        compact = re.sub(r"[^A-Za-z]", "", text)
        return bool(compact) and compact.upper() == compact

    @staticmethod
    def _contains_hangul(text: str) -> bool:
        return any(0xAC00 <= ord(char) <= 0xD7A3 for char in text)

    @staticmethod
    def _contains_thai(text: str) -> bool:
        return any(0x0E00 <= ord(char) <= 0x0E7F for char in text)

    @staticmethod
    def _contains_placeholder_tag(text: str) -> bool:
        return bool(re.match(r"^\[[A-Za-z]{2,5}\]\s*", text.strip()))

    def _is_target_script_compatible(self, text: str, target_lang: str) -> bool:
        target = target_lang.lower()
        if target != "ko" and self._contains_hangul(text):
            return False
        if target != "th" and self._contains_thai(text):
            return False
        return True

    def _should_render_candidate(self, source_text: str, target_text: str, target_lang: str) -> tuple[bool, str | None]:
        normalized_source = self._normalize_text(source_text)
        normalized_target = self._normalize_text(target_text)
        if not normalized_target:
            return False, "empty target text"
        if self._contains_placeholder_tag(target_text):
            return False, "placeholder-like target text"
        if not self._is_target_script_compatible(target_text, target_lang):
            return False, "target text script mismatch"
        if target_lang.lower() != "ko" and normalized_source == normalized_target and self._contains_hangul(source_text):
            return False, "untranslated source text"
        return True, None

    def _classify_role(self, item: RecognizedTextRegion, image_shape: tuple[int, int, int]) -> str:
        image_height, image_width = image_shape[:2]
        x, y, w, h = item.region.bbox
        area_ratio = (w * h) / max(1, image_height * image_width)
        text = self._normalize_text(item.text)
        compact = text.replace(" ", "")

        if item.confidence < self.config.min_region_confidence or area_ratio < self.config.min_region_area_ratio:
            return "fineprint"

        if self._is_ascii_upper_token(text) and len(compact) <= 8:
            return "brand"

        if compact in {"TERR", "TERI", "TERRA", "FROMA", "FROMAGT", "GOLDEN"}:
            return "brand"

        if x > image_width * 0.88 and w < image_width * 0.12:
            return "brand"

        if (x + w) > image_width * 0.93 and area_ratio < 0.004:
            return "brand"

        if h < image_height * 0.02 and area_ratio < 0.0015:
            return "fineprint"

        if y > image_height * 0.74 and h < image_height * 0.055:
            return "caption"

        if area_ratio < 0.0015 and y > image_height * 0.78:
            return "fineprint"

        if w > image_width * 0.18 or h > image_height * 0.045:
            return "headline"

        return "caption"

    def _filter_regions(self, recognized: list[RecognizedTextRegion], image_shape: tuple[int, int, int]) -> list[RecognizedTextRegion]:
        image_area = image_shape[0] * image_shape[1]
        min_area = image_area * self.config.min_region_area_ratio

        filtered = []
        for item in recognized:
            _, _, w, h = item.region.bbox
            area = w * h
            if item.confidence < self.config.min_region_confidence:
                continue
            if area < min_area:
                continue
            filtered.append(item)

        if not filtered:
            return recognized

        filtered.sort(key=lambda item: (item.region.bbox[1], item.region.bbox[0]))
        if len(filtered) > self.config.max_render_regions:
            filtered = sorted(
                filtered,
                key=lambda item: item.region.bbox[2] * item.region.bbox[3],
                reverse=True,
            )[: self.config.max_render_regions]
            filtered.sort(key=lambda item: (item.region.bbox[1], item.region.bbox[0]))
        return filtered

    def _should_merge(
        self,
        left: RecognizedTextRegion,
        right: RecognizedTextRegion,
        left_role: str,
        right_role: str,
        image_shape: tuple[int, int, int],
    ) -> bool:
        if left_role != right_role:
            return False
        if left_role not in {"headline", "caption"}:
            return False

        image_height, image_width = image_shape[:2]
        lx, ly, lw, lh = left.region.bbox
        rx, ry, rw, rh = right.region.bbox

        left_center_x = lx + lw / 2
        right_center_x = rx + rw / 2
        center_delta = abs(left_center_x - right_center_x)
        vertical_gap = ry - (ly + lh)
        horizontal_overlap = max(0, min(lx + lw, rx + rw) - max(lx, rx))
        horizontal_overlap_ratio = horizontal_overlap / max(1, min(lw, rw))
        width_ratio = max(lw, rw) / max(1, min(lw, rw))

        if vertical_gap < -min(lh, rh) * 0.25:
            return False
        if vertical_gap > max(lh, rh) * 1.35:
            return False
        if center_delta > image_width * 0.16:
            return False
        if horizontal_overlap_ratio < 0.18 and center_delta > min(lw, rw) * 0.55:
            return False
        if width_ratio > 4.0:
            return False

        if self._is_ascii_upper_token(left.text) or self._is_ascii_upper_token(right.text):
            return False

        return True

    def _merge_group(self, group: list[RecognizedTextRegion]) -> RecognizedTextRegion:
        ordered = sorted(group, key=lambda item: (item.region.bbox[1], item.region.bbox[0]))
        xs = [item.region.bbox[0] for item in ordered]
        ys = [item.region.bbox[1] for item in ordered]
        x2s = [item.region.bbox[0] + item.region.bbox[2] for item in ordered]
        y2s = [item.region.bbox[1] + item.region.bbox[3] for item in ordered]
        min_x = min(xs)
        min_y = min(ys)
        max_x = max(x2s)
        max_y = max(y2s)

        merged_text = " ".join(self._normalize_text(item.text) for item in ordered if self._normalize_text(item.text))
        merged_confidence = sum(item.confidence for item in ordered) / len(ordered)
        merged_region = TextRegion(
            id="+".join(item.region.id for item in ordered),
            polygon=[(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)],
            bbox=(min_x, min_y, max_x - min_x, max_y - min_y),
            rotation_deg=ordered[0].region.rotation_deg,
        )
        return RecognizedTextRegion(
            region=merged_region,
            text=merged_text,
            confidence=merged_confidence,
            source_lang=ordered[0].source_lang,
        )

    def _build_editable_regions(
        self,
        recognized: list[RecognizedTextRegion],
        image_shape: tuple[int, int, int],
    ) -> tuple[list[tuple[RecognizedTextRegion, str]], list[RecognizedTextRegion]]:
        annotated = [(item, self._classify_role(item, image_shape)) for item in recognized]
        editable_candidates = [(item, role) for item, role in annotated if role in {"headline", "caption"}]
        passthrough = [item for item, role in annotated if role not in {"headline", "caption"}]

        editable_candidates.sort(key=lambda pair: (pair[0].region.bbox[1], pair[0].region.bbox[0]))
        merged: list[tuple[RecognizedTextRegion, str]] = []
        used: set[int] = set()

        for index, (item, role) in enumerate(editable_candidates):
            if index in used:
                continue

            group = [item]
            used.add(index)
            for next_index in range(index + 1, len(editable_candidates)):
                if next_index in used:
                    continue
                candidate, candidate_role = editable_candidates[next_index]
                if self._should_merge(group[-1], candidate, role, candidate_role, image_shape):
                    group.append(candidate)
                    used.add(next_index)

            merged.append(((self._merge_group(group) if len(group) > 1 else item), role))

        merged.sort(key=lambda pair: (pair[0].region.bbox[1], pair[0].region.bbox[0]))
        return merged, passthrough

    def prepare_edit_context(self, image_path: str, target_lang: str) -> PreparedEditContext:
        input_path = Path(image_path)
        if not input_path.exists():
            raise FileNotFoundError(f"입력 이미지가 없습니다: {image_path}")

        job_dir = self.config.output_root / input_path.stem
        job_dir.mkdir(parents=True, exist_ok=True)

        debug_writer = DebugArtifactWriter(job_dir)

        regions = self.detector.detect(str(input_path))
        recognized = self.recognizer.recognize(str(input_path), regions)

        if self.config.debug_save_boxes:
            debug_writer.write_boxes_image(
                str(input_path),
                regions,
                "01_detected_boxes.jpg",
            )

        if self.config.debug_save_ocr_json:
            debug_writer.write_ocr_json(recognized, "02_ocr.json")

        original_image = cv2.imread(str(input_path))
        if original_image is None:
            raise FileNotFoundError(f"이미지를 읽지 못했습니다: {input_path}")

        recognized = self._filter_regions(recognized, original_image.shape)
        editable_regions, skipped_regions = self._build_editable_regions(recognized, original_image.shape)

        mask_builder = TextMaskBuilder()
        mask = mask_builder.build_mask(original_image.shape, [region for region, _role in editable_regions])

        if self.config.debug_save_masks:
            debug_writer.write_mask_image(mask, "03_mask.png")

        restored_path = str(job_dir / "04_restored.jpg")
        current_image_path = self.restorer.restore(
            str(input_path),
            [region for region, _role in editable_regions],
            restored_path,
        )

        prepared_regions: list[PreparedRegionEdit] = []
        for region, role in editable_regions:
            x, y, w, h = region.region.bbox
            candidates = self.rewriter.rewrite(region.text, target_lang, w, h)
            style = self.style_estimator.estimate(str(input_path), region)
            prepared_regions.append(
                PreparedRegionEdit(
                    region=region,
                    role=role,
                    style=style,
                    candidates=candidates,
                    chosen_candidate=candidates[0] if candidates else None,
                )
            )

        return PreparedEditContext(
            input_image_path=str(input_path),
            target_lang=target_lang,
            job_dir=str(job_dir),
            restored_image_path=current_image_path,
            original_image_shape=original_image.shape,
            editable_regions=prepared_regions,
            skipped_regions=skipped_regions,
        )

    def run_prepared(self, prepared: PreparedEditContext) -> EditJobResult:
        current_image_path = prepared.restored_image_path
        job_dir = Path(prepared.job_dir)
        region_results: list[RegionEditResult] = []
        expected_texts: list[str] = []

        for skipped in prepared.skipped_regions:
            region_results.append(
                RegionEditResult(
                    region_id=skipped.region.id,
                    source_text=skipped.text,
                    target_text=skipped.text,
                    quality_score=skipped.confidence,
                    warning="non-editable region skipped",
                )
            )

        for index, prepared_region in enumerate(prepared.editable_regions, start=1):
            region = prepared_region.region
            chosen = prepared_region.chosen_candidate
            if chosen is None:
                region_results.append(
                    RegionEditResult(
                        region_id=region.region.id,
                        source_text=region.text,
                        target_text=region.text,
                        quality_score=0.0,
                        warning="localized candidate 없음",
                    )
                )
                continue

            should_render, warning = self._should_render_candidate(region.text, chosen.text, prepared.target_lang)
            if not should_render:
                region_results.append(
                    RegionEditResult(
                        region_id=region.region.id,
                        source_text=region.text,
                        target_text=region.text,
                        quality_score=0.0,
                        warning=warning,
                    )
                )
                continue

            next_output_path = str(job_dir / f"05_rendered_{index:02d}.jpg")
            current_image_path = self.renderer.render(
                current_image_path,
                region,
                chosen.text,
                prepared_region.style,
                next_output_path,
            )

            expected_texts.append(chosen.text)
            region_results.append(
                RegionEditResult(
                    region_id=region.region.id,
                    source_text=region.text,
                    target_text=chosen.text,
                    quality_score=chosen.final_score,
                )
            )

        final_score = self.validator.validate(current_image_path, expected_texts, prepared.target_lang)

        final_output_path = str(job_dir / "99_final.jpg")
        if current_image_path != final_output_path:
            image = cv2.imread(current_image_path)
            if image is None:
                raise RuntimeError("최종 이미지를 읽지 못했습니다.")
            cv2.imwrite(final_output_path, image)

        warnings: list[str] = []
        if final_score < self.config.quality_pass_threshold:
            warnings.append("품질 점수가 임계값보다 낮습니다.")

        result = EditJobResult(
            output_image_path=final_output_path,
            quality_score=final_score,
            used_fallback=False,
            warnings=warnings,
            region_results=region_results,
        )

        if self.config.debug_save_quality_json:
            debug_writer = DebugArtifactWriter(job_dir)
            debug_writer.write_quality_json(result.to_dict(), "98_quality.json")

        return result

    def run(self, image_path: str, target_lang: str) -> EditJobResult:
        prepared = self.prepare_edit_context(image_path, target_lang)
        return self.run_prepared(prepared)
