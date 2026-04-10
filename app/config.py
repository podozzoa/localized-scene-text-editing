from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    output_root: Path = Path("outputs")
    debug_save_boxes: bool = True
    debug_save_masks: bool = True
    debug_save_restored: bool = True
    debug_save_ocr_json: bool = True
    debug_save_quality_json: bool = True
    default_font_path: Path = Path("assets/fonts/NotoSansKR-Regular.ttf")
    default_font_size: int = 24
    quality_pass_threshold: float = 0.60
    inpaint_radius: int = 3
    ocr_language_hint: str = "korean"
    render_padding_ratio: float = 0.08
    render_min_font_size: int = 10
    render_max_font_size: int = 160
    min_region_confidence: float = 0.45
    min_region_area_ratio: float = 0.0007
    max_render_regions: int = 12
    fallback_font_paths: tuple[str, ...] = (
        r"C:\Windows\Fonts\malgunbd.ttf",
        r"C:\Windows\Fonts\malgun.ttf",
        r"C:\Windows\Fonts\LeelaUIb.ttf",
        r"C:\Windows\Fonts\LeelawUI.ttf",
        r"C:\Windows\Fonts\tahomabd.ttf",
        r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    )
