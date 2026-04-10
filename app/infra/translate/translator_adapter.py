from __future__ import annotations

import os
import re
from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class TranslationSettings:
    provider: str = "auto"
    model: str = "gpt-4.1-mini"
    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: int = 30
    source_lang: str = "ko"
    local_model_name: str = "facebook/nllb-200-distilled-600M"


class BaseTranslator:
    def translate(self, text: str, target_lang: str) -> str:
        raise NotImplementedError

    def generate_candidates(
        self,
        text: str,
        target_lang: str,
        max_chars: int,
        role: str,
    ) -> list[str]:
        translated = self.translate(text, target_lang)
        return [translated] if translated else []


class IdentityTranslator(BaseTranslator):
    """
    번역 백엔드가 없을 때의 안전한 fallback.
    특정 포스터/문구에 의존하지 않고 원문을 유지한다.
    """

    @staticmethod
    def _is_ascii_brandlike(text: str) -> bool:
        compact = re.sub(r"[^A-Za-z0-9%&+-]", "", text)
        if not compact:
            return False
        letters = re.sub(r"[^A-Za-z]", "", compact)
        return bool(letters) and letters.upper() == letters

    def translate(self, text: str, target_lang: str) -> str:
        text = text.strip()
        if not text:
            return text
        if self._is_ascii_brandlike(text):
            return text
        return text

    @staticmethod
    def _contains_hangul(text: str) -> bool:
        return any(0xAC00 <= ord(char) <= 0xD7A3 for char in text)

    @staticmethod
    def _contains_thai(text: str) -> bool:
        return any(0x0E00 <= ord(char) <= 0x0E7F for char in text)


class OpenAICompatibleTranslator(BaseTranslator):
    def __init__(self, settings: TranslationSettings) -> None:
        if not settings.api_key:
            raise ValueError("api_key is required for OpenAICompatibleTranslator")
        self.settings = settings

    def _post_chat(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        headers = {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.model,
            "messages": messages,
            "temperature": temperature,
        }

        response = requests.post(
            f"{self.settings.base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
            timeout=self.settings.timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        message = data["choices"][0]["message"]["content"]
        return str(message).strip()

    @staticmethod
    def _lang_label(target_lang: str) -> str:
        mapping = {
            "ko": "Korean",
            "en": "English",
            "vi": "Vietnamese",
            "th": "Thai",
            "ja": "Japanese",
            "zh": "Chinese",
        }
        return mapping.get(target_lang.lower(), target_lang)

    @staticmethod
    def _sanitize_candidate(text: str) -> str:
        sanitized = text.strip()
        sanitized = re.sub(r"^[\-\*\u2022\.\s]+", "", sanitized)
        sanitized = re.sub(r"^\[[A-Za-z]{2,5}\]\s*", "", sanitized)
        sanitized = re.sub(r"\s+", " ", sanitized)
        return sanitized.strip(" -\t\r\n")

    def translate(self, text: str, target_lang: str) -> str:
        text = text.strip()
        if not text:
            return text
        if IdentityTranslator._is_ascii_brandlike(text):
            return text

        return self._post_chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You localize short poster and marketing text. "
                        "Keep brand names unchanged. Preserve tone and brevity. "
                        "Return only the best localized line, with no quotes or explanations."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Localize the following text into {self._lang_label(target_lang)}. "
                        f"If the text is a brand or product token, keep it unchanged.\n\n{text}"
                    ),
                },
            ],
            temperature=0.3,
        )

    def generate_candidates(
        self,
        text: str,
        target_lang: str,
        max_chars: int,
        role: str,
    ) -> list[str]:
        text = text.strip()
        if not text:
            return []
        if IdentityTranslator._is_ascii_brandlike(text):
            return [text]

        lang_label = self._lang_label(target_lang)
        source_label = self._lang_label(self.settings.source_lang)
        role_guidance = {
            "headline": (
                "Write punchy slogan-like copy. Favor short, memorable phrasing and strong rhythm. "
                "Avoid literal wording."
            ),
            "caption": (
                "Write concise product-support copy. Keep informative meaning, but stay natural and marketable."
            ),
            "fineprint": (
                "Stay closer to the literal meaning. Do not over-market the copy."
            ),
        }.get(role, "Write concise localized poster copy.")
        prompt = (
            f"Source language: {source_label}\n"
            f"Target language: {lang_label}\n"
            f"Role: {role}\n"
            f"Max characters per candidate: {max_chars}\n"
            "Task: create 3 short localized ad-copy candidates for poster text.\n"
            "Requirements:\n"
            f"- {role_guidance}\n"
            "- Keep brand names and product tokens unchanged.\n"
            "- If a likely product name appears in Korean, transliterate it rather than inventing a different product name.\n"
            "- Preserve the core meaning, but prefer natural marketing copy over literal translation.\n"
            "- Make each option concise and visually suitable for a poster.\n"
            "- Write fully in the target language unless a token is clearly a brand name.\n"
            "- Do not leave Korean descriptive words untranslated.\n"
            "- Do not explain anything.\n"
            "- Output exactly 3 lines, one candidate per line, with no numbering.\n\n"
            f"Source text:\n{text}"
        )
        raw = self._post_chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You are an expert advertising copy localizer for poster headlines and captions. "
                        "You write natural, catchy localized copy that fits tight layouts."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        lines = [self._sanitize_candidate(line) for line in raw.splitlines()]
        candidates: list[str] = []
        seen: set[str] = set()
        for line in lines:
            compact = line.strip()
            if not compact or compact.lower().startswith("candidate"):
                continue
            if compact not in seen:
                seen.add(compact)
                candidates.append(compact)
        if target_lang.lower() != "ko" and candidates and all(IdentityTranslator._contains_hangul(candidate) for candidate in candidates):
            raw = self._post_chat(
                [
                    {
                        "role": "system",
                        "content": (
                            "You rewrite ad-copy candidates fully into the target language. "
                            "Do not leave any Korean characters in the output unless the source is an exact brand token written in Latin letters."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Rewrite the following poster copy into fully natural {lang_label}. "
                            "Do not keep any Korean characters. Keep meaning and brand tone concise.\n\n"
                            f"Source text:\n{text}"
                        ),
                    },
                ],
                temperature=0.4,
            )
            candidates = [self._sanitize_candidate(line) for line in raw.splitlines() if self._sanitize_candidate(line)]
        if not candidates:
            fallback = self.translate(text, target_lang)
            return [fallback] if fallback else []
        return candidates[:3]


class HuggingFaceLocalTranslator(BaseTranslator):
    NLLB_CODES = {
        "ko": "kor_Hang",
        "en": "eng_Latn",
        "vi": "vie_Latn",
        "th": "tha_Thai",
        "ja": "jpn_Jpan",
        "zh": "zho_Hans",
    }
    MBART50_CODES = {
        "ko": "ko_KR",
        "en": "en_XX",
        "vi": "vi_VN",
        "th": "th_TH",
        "ja": "ja_XX",
        "zh": "zh_CN",
    }
    M2M100_CODES = {
        "ko": "ko",
        "en": "en",
        "vi": "vi",
        "th": "th",
        "ja": "ja",
        "zh": "zh",
    }

    def __init__(self, settings: TranslationSettings) -> None:
        self.settings = settings
        try:
            import torch  # type: ignore
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("transformers, sentencepiece, and torch are required for hf_local translation backend") from exc

        self._torch = torch
        self._tokenizer = AutoTokenizer.from_pretrained(self.settings.local_model_name)
        self._model = AutoModelForSeq2SeqLM.from_pretrained(self.settings.local_model_name)
        self._model.to("cpu")
        self._model.eval()

    def _lang_kwargs(self, target_lang: str) -> dict[str, str]:
        model_name = self.settings.local_model_name.lower()
        source_lang = self.settings.source_lang.lower()
        target_lang = target_lang.lower()
        if "nllb" in model_name:
            src_code = self.NLLB_CODES.get(source_lang)
            tgt_code = self.NLLB_CODES.get(target_lang)
            return {"src_lang": src_code, "tgt_lang": tgt_code} if src_code and tgt_code else {}
        if "mbart" in model_name:
            src_code = self.MBART50_CODES.get(source_lang)
            tgt_code = self.MBART50_CODES.get(target_lang)
            return {"src_lang": src_code, "tgt_lang": tgt_code} if src_code and tgt_code else {}
        if "m2m100" in model_name:
            src_code = self.M2M100_CODES.get(source_lang)
            tgt_code = self.M2M100_CODES.get(target_lang)
            return {"src_lang": src_code, "tgt_lang": tgt_code} if src_code and tgt_code else {}
        return {}

    def _prepare_input(self, text: str, target_lang: str) -> str:
        model_name = self.settings.local_model_name.lower()
        if "t5" not in model_name:
            return text

        source_label = OpenAICompatibleTranslator._lang_label(self.settings.source_lang)
        target_label = OpenAICompatibleTranslator._lang_label(target_lang)
        return f"translate {source_label} to {target_label}: {text}"

    def _generate(self, text: str, target_lang: str) -> str:
        kwargs = self._lang_kwargs(target_lang)
        tokenizer = self._tokenizer
        model = self._model

        src_lang = kwargs.get("src_lang")
        tgt_lang = kwargs.get("tgt_lang")
        if src_lang and hasattr(tokenizer, "src_lang"):
            tokenizer.src_lang = src_lang

        encoded = tokenizer(self._prepare_input(text, target_lang), return_tensors="pt", truncation=True)
        generate_kwargs: dict[str, int] = {}

        if tgt_lang:
            lang_code_to_id = getattr(tokenizer, "lang_code_to_id", None)
            if isinstance(lang_code_to_id, dict) and tgt_lang in lang_code_to_id:
                generate_kwargs["forced_bos_token_id"] = int(lang_code_to_id[tgt_lang])
            else:
                convert = getattr(tokenizer, "convert_tokens_to_ids", None)
                if callable(convert):
                    token_id = convert(tgt_lang)
                    if isinstance(token_id, int) and token_id >= 0:
                        generate_kwargs["forced_bos_token_id"] = token_id

        with self._torch.inference_mode():
            output_ids = model.generate(**encoded, max_new_tokens=128, **generate_kwargs)
        return tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0].strip()

    def translate(self, text: str, target_lang: str) -> str:
        text = text.strip()
        if not text:
            return text
        if target_lang.lower() == self.settings.source_lang.lower():
            return text
        if IdentityTranslator._is_ascii_brandlike(text):
            return text
        translated = self._generate(text, target_lang)
        return translated or text


class TranslatorAdapter(BaseTranslator):
    def __init__(self, settings: TranslationSettings | None = None) -> None:
        env_settings = TranslationSettings(
            provider=os.getenv("TRANSLATION_PROVIDER", "auto"),
            model=os.getenv("TRANSLATION_MODEL", "gpt-4.1-mini"),
            api_key=os.getenv("OPENAI_API_KEY") or os.getenv("TRANSLATION_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", os.getenv("TRANSLATION_BASE_URL", "https://api.openai.com/v1")),
            timeout_seconds=int(os.getenv("TRANSLATION_TIMEOUT_SECONDS", "30")),
            source_lang=os.getenv("TRANSLATION_SOURCE_LANG", "ko"),
            local_model_name=os.getenv("TRANSLATION_LOCAL_MODEL", "facebook/nllb-200-distilled-600M"),
        )
        if settings is None:
            self.settings = env_settings
        else:
            self.settings = TranslationSettings(
                provider=settings.provider or env_settings.provider,
                model=settings.model or env_settings.model,
                api_key=settings.api_key or env_settings.api_key,
                base_url=settings.base_url or env_settings.base_url,
                timeout_seconds=settings.timeout_seconds or env_settings.timeout_seconds,
                source_lang=settings.source_lang or env_settings.source_lang,
                local_model_name=settings.local_model_name or env_settings.local_model_name,
            )
        self.fallback = IdentityTranslator()
        self.backend = self._build_backend()

    def _build_backend(self) -> BaseTranslator:
        provider = self.settings.provider.lower()

        if provider == "identity":
            return self.fallback

        if provider == "hf_local":
            try:
                return HuggingFaceLocalTranslator(self.settings)
            except Exception:
                return self.fallback

        if provider in {"auto", "openai", "openai_compatible"} and self.settings.api_key:
            return OpenAICompatibleTranslator(self.settings)

        return self.fallback

    def translate(self, text: str, target_lang: str) -> str:
        try:
            translated = self.backend.translate(text, target_lang)
        except Exception:
            translated = self.fallback.translate(text, target_lang)
        return translated.strip() or text.strip()

    def generate_candidates(
        self,
        text: str,
        target_lang: str,
        max_chars: int,
        role: str,
    ) -> list[str]:
        try:
            candidates = self.backend.generate_candidates(text, target_lang, max_chars, role)
        except Exception:
            candidates = self.fallback.generate_candidates(text, target_lang, max_chars, role)
        normalized: list[str] = []
        seen: set[str] = set()
        for candidate in candidates:
            item = candidate.strip()
            if not item or item in seen:
                continue
            seen.add(item)
            normalized.append(item)
        return normalized or [self.translate(text, target_lang)]
