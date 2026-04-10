from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.config import AppConfig
from app.domain.interfaces import IRenderer
from app.domain.models import RecognizedTextRegion, StyleProfile


@dataclass
class LayoutCandidate:
    lines: list[str]
    font: ImageFont.FreeTypeFont
    text_size: tuple[int, int]
    line_height: int
    horizontal_scale: float = 1.0


class PILTextRenderer(IRenderer):
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    @staticmethod
    def _contains_range(text: str, start: int, end: int) -> bool:
        return any(start <= ord(char) <= end for char in text)

    def _contains_vietnamese_latin(self, text: str) -> bool:
        return (
            self._contains_range(text, 0x00C0, 0x024F)
            or self._contains_range(text, 0x1E00, 0x1EFF)
        )

    def _resolve_font_path(self, text: str, preferred_font_path: str) -> str:
        candidates: list[str] = []

        if self._contains_vietnamese_latin(text):
            candidates.extend(
                [
                    r"C:\Windows\Fonts\arialbd.ttf",
                    r"C:\Windows\Fonts\arial.ttf",
                    r"C:\Windows\Fonts\tahomabd.ttf",
                    r"C:\Windows\Fonts\tahoma.ttf",
                ]
            )
        if self._contains_range(text, 0x0E00, 0x0E7F):
            candidates.extend(
                [
                    r"C:\Windows\Fonts\LeelaUIb.ttf",
                    r"C:\Windows\Fonts\LeelawUI.ttf",
                    r"C:\Windows\Fonts\tahomabd.ttf",
                    r"C:\Windows\Fonts\tahoma.ttf",
                ]
            )
        if self._contains_range(text, 0xAC00, 0xD7A3):
            candidates.extend(
                [
                    r"C:\Windows\Fonts\malgunbd.ttf",
                    r"C:\Windows\Fonts\malgun.ttf",
                ]
            )

        if preferred_font_path:
            candidates.append(preferred_font_path)

        candidates.extend(self.config.fallback_font_paths)

        seen: set[str] = set()
        for candidate in candidates:
            normalized = str(Path(candidate))
            if normalized in seen:
                continue
            seen.add(normalized)
            if Path(normalized).exists():
                return normalized

        raise FileNotFoundError(f"사용 가능한 폰트 파일이 없습니다. preferred={preferred_font_path}")

    @staticmethod
    def _split_tokens(text: str) -> list[str]:
        text = text.strip()
        if " " in text:
            return [token for token in text.split(" ") if token]
        return list(text)

    @staticmethod
    def _measure_line(font: ImageFont.FreeTypeFont, text: str) -> tuple[int, int]:
        left, top, right, bottom = font.getbbox(text or " ")
        return (right - left, bottom - top)

    def _build_lines(self, tokens: list[str], target_lines: int) -> list[str]:
        if not tokens:
            return [""]

        if target_lines <= 1:
            return [" ".join(tokens) if len(tokens) > 1 and len("".join(tokens)) != len(tokens) else "".join(tokens)]

        lines: list[str] = []
        chunk_size = max(1, round(len(tokens) / target_lines))
        cursor = 0
        for line_index in range(target_lines):
            remaining = len(tokens) - cursor
            remaining_lines = target_lines - line_index
            take = max(1, round(remaining / remaining_lines))
            part = tokens[cursor : cursor + max(chunk_size, take) if line_index < target_lines - 1 else len(tokens)]
            cursor += len(part)
            if not part:
                continue
            separator = " " if len(tokens) != len("".join(tokens)) and all(len(token) > 1 for token in tokens) else ""
            lines.append(separator.join(part))

        if cursor < len(tokens):
            tail = "".join(tokens[cursor:])
            if lines:
                lines[-1] += tail
            else:
                lines.append(tail)
        return [line for line in lines if line]

    def _fit_text_layout(
        self,
        text: str,
        bbox: tuple[int, int, int, int],
        font_path: str,
        line_spacing: float,
        preferred_font_size: int | None = None,
    ) -> LayoutCandidate:
        _, _, width, height = bbox
        tokens = self._split_tokens(text)
        max_lines = min(3, max(1, len(tokens)))
        start_font_size = min(220, max(self.config.render_max_font_size, preferred_font_size or 0))

        for font_size in range(start_font_size, self.config.render_min_font_size - 1, -1):
            font = ImageFont.truetype(font_path, size=font_size)
            for target_lines in range(1, max_lines + 1):
                lines = self._build_lines(tokens, target_lines)
                line_sizes = [self._measure_line(font, line) for line in lines]
                text_width = max(line_width for line_width, _ in line_sizes)
                single_line_height = max(line_height for _, line_height in line_sizes)
                total_height = single_line_height * len(lines) + int(single_line_height * (line_spacing - 1.0) * max(0, len(lines) - 1))
                horizontal_scale = min(1.0, width / max(1, text_width))
                allow_scaled_fit = target_lines == 1 and horizontal_scale >= 0.82
                if (text_width <= width or allow_scaled_fit) and total_height <= height:
                    return LayoutCandidate(
                        lines=lines,
                        font=font,
                        text_size=(min(width, int(text_width * horizontal_scale)), total_height),
                        line_height=single_line_height,
                        horizontal_scale=horizontal_scale,
                    )

        font = ImageFont.truetype(font_path, size=self.config.render_min_font_size)
        line_size = self._measure_line(font, text)
        return LayoutCandidate(lines=[text], font=font, text_size=line_size, line_height=line_size[1], horizontal_scale=1.0)

    @staticmethod
    def _multiline_positions(
        bbox: tuple[int, int, int, int],
        candidate: LayoutCandidate,
        align: str,
        line_spacing: float,
    ) -> list[tuple[int, int, str]]:
        x, y, w, h = bbox
        text_width, text_height = candidate.text_size
        start_y = y + max(0, (h - text_height) // 2)

        positions: list[tuple[int, int, str]] = []
        for index, line in enumerate(candidate.lines):
            line_width, _ = PILTextRenderer._measure_line(candidate.font, line)
            if align == "left":
                tx = x
            elif align == "right":
                tx = x + w - line_width
            else:
                tx = x + (w - line_width) // 2
            ty = start_y + int(index * candidate.line_height * line_spacing)
            positions.append((tx, ty, line))
        return positions

    @staticmethod
    def _draw_scaled_text(
        overlay: Image.Image,
        position: tuple[int, int],
        text: str,
        font: ImageFont.FreeTypeFont,
        fill: tuple[int, int, int],
        stroke_fill: tuple[int, int, int] | None,
        stroke_width: int,
        horizontal_scale: float,
        shadow,
    ) -> None:
        left, top, right, bottom = font.getbbox(text)
        natural_width = max(1, right - left + stroke_width * 4)
        natural_height = max(1, bottom - top + stroke_width * 4)
        text_layer = Image.new("RGBA", (natural_width, natural_height), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        origin = (stroke_width * 2 - left, stroke_width * 2 - top)

        if shadow and shadow.enabled:
            text_draw.text(
                (origin[0] + shadow.dx, origin[1] + shadow.dy),
                text,
                font=font,
                fill=shadow.color + (120,),
            )

        text_draw.text(
            origin,
            text,
            font=font,
            fill=fill + (255,),
            stroke_fill=(stroke_fill + (255,)) if stroke_fill else None,
            stroke_width=stroke_width,
        )

        if horizontal_scale < 0.999:
            scaled_width = max(1, int(text_layer.width * horizontal_scale))
            text_layer = text_layer.resize((scaled_width, text_layer.height), Image.Resampling.LANCZOS)

        overlay.alpha_composite(text_layer, dest=position)

    def render(
        self,
        image_path: str,
        region: RecognizedTextRegion,
        text: str,
        style: StyleProfile,
        output_path: str,
    ) -> str:
        image = Image.open(image_path).convert("RGBA")
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))

        x, y, w, h = region.region.bbox
        padding_ratio = style.padding_ratio if style.padding_ratio is not None else self.config.render_padding_ratio
        padding_x = int(w * padding_ratio)
        padding_y = int(h * padding_ratio)
        padded_bbox = (
            x + padding_x,
            y + padding_y,
            max(1, w - padding_x * 2),
            max(1, h - padding_y * 2),
        )

        font_path = self._resolve_font_path(text, style.font_path or str(self.config.default_font_path))

        candidate = self._fit_text_layout(
            text,
            padded_bbox,
            font_path=font_path,
            line_spacing=style.line_spacing,
            preferred_font_size=style.preferred_font_size,
        )
        stroke_width = max(style.stroke_width, max(1, candidate.font.size // 18))
        positions = self._multiline_positions(padded_bbox, candidate, style.align, style.line_spacing)

        for tx, ty, line in positions:
            self._draw_scaled_text(
                overlay=overlay,
                position=(tx, ty),
                text=line,
                font=candidate.font,
                fill=style.fill_color,
                stroke_fill=style.stroke_color,
                stroke_width=stroke_width,
                horizontal_scale=candidate.horizontal_scale if len(candidate.lines) == 1 else 1.0,
                shadow=style.shadow,
            )

        composed = Image.alpha_composite(image, overlay).convert("RGB")
        composed.save(output_path)
        return output_path
