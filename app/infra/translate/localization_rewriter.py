from __future__ import annotations

from app.domain.interfaces import ILocalizationRewriter
from app.domain.models import LocalizedCandidate
from app.infra.translate.translator_adapter import BaseTranslator, TranslatorAdapter


class SimpleLocalizationRewriter(ILocalizationRewriter):
    """
    1차 MVP:
    - 더미 번역
    - 길이 차이 기반 점수
    - 짧은 후보 우선
    """

    def __init__(self, translator: BaseTranslator | None = None) -> None:
        self.translator = translator or TranslatorAdapter()

    @staticmethod
    def _infer_role(width: int, height: int) -> str:
        area = width * height
        if width >= 420 or height >= 120 or area >= 80000:
            return "headline"
        if height <= 42:
            return "fineprint"
        return "caption"

    @staticmethod
    def _character_budget(width: int, height: int, role: str) -> int:
        scale = max(1.0, width / 42.0)
        if role == "headline":
            return max(10, min(26, int(scale)))
        if role == "caption":
            return max(12, min(34, int(scale * 1.25)))
        return max(10, min(42, int(scale * 1.4)))

    @staticmethod
    def _contains_script(text: str, start: int, end: int) -> bool:
        return any(start <= ord(char) <= end for char in text)

    @staticmethod
    def _script_penalty(text: str, target_lang: str) -> float:
        target = target_lang.lower()
        if target != "ko" and any(0xAC00 <= ord(char) <= 0xD7A3 for char in text):
            return 0.55
        if target != "th" and any(0x0E00 <= ord(char) <= 0x0E7F for char in text):
            return 0.65
        return 1.0

    @classmethod
    def _is_target_script_compatible(cls, text: str, target_lang: str) -> bool:
        target = target_lang.lower()
        if target != "ko" and cls._contains_script(text, 0xAC00, 0xD7A3):
            return False
        if target != "th" and cls._contains_script(text, 0x0E00, 0x0E7F):
            return False
        return True

    @staticmethod
    def _layout_fit_score(text: str, width: int, height: int) -> float:
        area = max(1, width * height)
        density = len(text) / max(1.0, area / 1800.0)
        score = 1.0 - min(1.0, abs(density - 1.0) * 0.35)
        return max(0.0, min(1.0, score))

    @staticmethod
    def _brevity_score(text: str) -> float:
        if len(text) <= 8:
            return 1.0
        if len(text) <= 16:
            return 0.8
        if len(text) <= 24:
            return 0.6
        return 0.4

    def rewrite(self, text: str, target_lang: str, width: int, height: int) -> list[LocalizedCandidate]:
        role = self._infer_role(width, height)
        budget = self._character_budget(width, height, role)
        generated = self.translator.generate_candidates(text, target_lang, budget, role)
        base = generated[0] if generated else self.translator.translate(text, target_lang)
        target = target_lang.lower()

        variants = list(generated) if generated else [base]

        contains_thai = self._contains_script(base, 0x0E00, 0x0E7F)
        preserve_spacing = target in {"vi", "th"}
        skip_truncation = preserve_spacing or contains_thai

        if len(base) > 10 and not skip_truncation:
            variants.append(base[:10])
        if " " in base and not contains_thai and not preserve_spacing:
            variants.append(base.replace(" ", ""))

        unique_variants: list[str] = []
        seen = set()
        for variant in variants:
            if not self._is_target_script_compatible(variant, target_lang):
                continue
            if variant not in seen and variant.strip():
                seen.add(variant)
                unique_variants.append(variant)

        candidates: list[LocalizedCandidate] = []
        for candidate_text in unique_variants:
            semantic_score = 0.92 if candidate_text in generated else 0.82
            layout_fit_score = self._layout_fit_score(candidate_text, width, height)
            brevity_score = self._brevity_score(candidate_text)
            if len(candidate_text) > budget:
                brevity_score *= max(0.2, budget / max(1, len(candidate_text)))
            script_penalty = self._script_penalty(candidate_text, target_lang)
            final_score = (semantic_score * 0.45 + layout_fit_score * 0.35 + brevity_score * 0.20) * script_penalty
            candidates.append(
                LocalizedCandidate(
                    text=candidate_text,
                    semantic_score=semantic_score,
                    layout_fit_score=layout_fit_score,
                    brevity_score=brevity_score,
                    final_score=final_score,
                )
            )

        candidates.sort(key=lambda x: x.final_score, reverse=True)
        return candidates
