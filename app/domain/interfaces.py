from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models import (
    LocalizedCandidate,
    RecognizedTextRegion,
    StyleProfile,
    TextRegion,
)


class ITextDetector(ABC):
    @abstractmethod
    def detect(self, image_path: str) -> list[TextRegion]:
        raise NotImplementedError


class ITextRecognizer(ABC):
    @abstractmethod
    def recognize(self, image_path: str, regions: list[TextRegion]) -> list[RecognizedTextRegion]:
        raise NotImplementedError


class ILocalizationRewriter(ABC):
    @abstractmethod
    def rewrite(self, text: str, target_lang: str, width: int, height: int) -> list[LocalizedCandidate]:
        raise NotImplementedError


class IBackgroundRestorer(ABC):
    @abstractmethod
    def restore(self, image_path: str, regions: list[RecognizedTextRegion], output_path: str) -> str:
        raise NotImplementedError


class IStyleEstimator(ABC):
    @abstractmethod
    def estimate(self, image_path: str, region: RecognizedTextRegion) -> StyleProfile:
        raise NotImplementedError


class IRenderer(ABC):
    @abstractmethod
    def render(
        self,
        image_path: str,
        region: RecognizedTextRegion,
        text: str,
        style: StyleProfile,
        output_path: str,
    ) -> str:
        raise NotImplementedError


class IQualityValidator(ABC):
    @abstractmethod
    def validate(self, image_path: str, expected_texts: list[str], target_lang: str) -> float:
        raise NotImplementedError
