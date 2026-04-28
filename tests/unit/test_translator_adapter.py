from __future__ import annotations

import unittest
from unittest.mock import patch

from app.infra.translate.localization_rewriter import SimpleLocalizationRewriter
from app.infra.translate.translator_adapter import BaseTranslator, OpenAICompatibleTranslator, TranslationSettings, TranslatorAdapter


class _HangulTranslator(BaseTranslator):
    def translate(self, text: str, target_lang: str) -> str:
        return text

    def generate_candidates(self, text: str, target_lang: str, max_chars: int, role: str) -> list[str]:
        return [text]


class TranslatorAdapterUnitTest(unittest.TestCase):
    def test_auto_without_backend_does_not_return_hangul_for_english_target(self) -> None:
        translator = TranslatorAdapter(TranslationSettings(provider="auto", source_lang="ko"))

        self.assertEqual(translator.translate("청정라거", "en"), "")
        self.assertEqual(translator.generate_candidates("청정라거", "en", 20, "headline"), [])
        self.assertTrue(translator.status().fallback_active)
        self.assertFalse(translator.status().backend_available)

    def test_auto_without_backend_preserves_ascii_brandlike_tokens(self) -> None:
        translator = TranslatorAdapter(TranslationSettings(provider="auto", source_lang="ko"))

        self.assertEqual(translator.translate("TERRA", "en"), "TERRA")
        self.assertEqual(translator.generate_candidates("SALE 50%", "en", 20, "headline"), ["SALE 50%"])

    def test_rewriter_filters_script_incompatible_candidates(self) -> None:
        rewriter = SimpleLocalizationRewriter(translator=_HangulTranslator())

        candidates = rewriter.rewrite("청정라거", "en", 300, 80)

        self.assertEqual(candidates, [])

    def test_openai_candidate_generation_uses_deterministic_temperature(self) -> None:
        translator = OpenAICompatibleTranslator(TranslationSettings(provider="openai", api_key="test-key", source_lang="ko"))

        with patch.object(translator, "_post_chat", return_value="Clean Lager\nPure Lager\nFresh Lager") as post_chat:
            candidates = translator.generate_candidates("청정라거", "en", 30, "headline")

        self.assertEqual(candidates, ["Clean Lager", "Pure Lager", "Fresh Lager"])
        self.assertEqual(post_chat.call_args.kwargs["temperature"], 0.0)


if __name__ == "__main__":
    unittest.main()
