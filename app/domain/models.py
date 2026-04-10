from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Optional

Point = tuple[int, int]
BBox = tuple[int, int, int, int]  # x, y, w, h


@dataclass
class TextRegion:
    id: str
    polygon: list[Point]
    bbox: BBox
    rotation_deg: float = 0.0


@dataclass
class RecognizedTextRegion:
    region: TextRegion
    text: str
    confidence: float
    source_lang: Optional[str] = None


@dataclass
class LocalizedCandidate:
    text: str
    semantic_score: float
    layout_fit_score: float
    brevity_score: float
    final_score: float


@dataclass
class ShadowStyle:
    enabled: bool = False
    dx: int = 0
    dy: int = 0
    blur: int = 0
    color: tuple[int, int, int] = (0, 0, 0)


@dataclass
class StyleProfile:
    fill_color: tuple[int, int, int] = (255, 255, 255)
    stroke_color: Optional[tuple[int, int, int]] = (0, 0, 0)
    stroke_width: int = 1
    font_weight: str = "regular"
    italic: bool = False
    align: str = "center"
    letter_spacing: float = 0.0
    line_spacing: float = 1.0
    shadow: Optional[ShadowStyle] = None
    font_path: Optional[str] = None
    preferred_font_size: Optional[int] = None
    padding_ratio: float = 0.04


@dataclass
class EditabilityAssessment:
    editable: bool
    risk_level: str
    reasons: list[str] = field(default_factory=list)


@dataclass
class PreparedRegionEdit:
    region: RecognizedTextRegion
    role: str
    style: StyleProfile
    candidates: list[LocalizedCandidate] = field(default_factory=list)
    chosen_candidate: Optional[LocalizedCandidate] = None


@dataclass
class PreparedEditContext:
    input_image_path: str
    target_lang: str
    job_dir: str
    restored_image_path: str
    original_image_shape: tuple[int, int, int]
    editable_regions: list[PreparedRegionEdit] = field(default_factory=list)
    skipped_regions: list[RecognizedTextRegion] = field(default_factory=list)


@dataclass
class RegionEditResult:
    region_id: str
    source_text: str
    target_text: str
    quality_score: float
    warning: Optional[str] = None


@dataclass
class EditJobResult:
    output_image_path: str
    quality_score: float
    used_fallback: bool
    warnings: list[str]
    region_results: list[RegionEditResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
