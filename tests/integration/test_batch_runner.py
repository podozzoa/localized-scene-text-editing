from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from app.domain.models import EditJobResult
from app.usecases.batch_runner import collect_input_images, run_batch


class _FakeEngine:
    def run(self, image_path: str, target_lang: str) -> EditJobResult:
        return EditJobResult(
            output_image_path=f"{image_path}.{target_lang}.jpg",
            quality_score=0.9,
            used_fallback=False,
            warnings=[],
            region_results=[],
        )


class BatchRunnerIntegrationTest(unittest.TestCase):
    def test_collect_input_images_filters_supported_extensions(self) -> None:
        fake_root = Path("virtual-inputs")
        fake_paths = [
            Path("virtual-inputs/a.png"),
            Path("virtual-inputs/b.jpg"),
            Path("virtual-inputs/ignore.txt"),
        ]

        with patch("app.usecases.batch_runner.Path.exists", return_value=True), patch(
            "app.usecases.batch_runner.Path.is_dir", return_value=True
        ), patch("app.usecases.batch_runner.Path.iterdir", return_value=fake_paths), patch(
            "pathlib.Path.is_file", return_value=True
        ):
            images = collect_input_images(str(fake_root))

        self.assertEqual([path.name for path in images], ["a.png", "b.jpg"])

    def test_run_batch_writes_summary_files(self) -> None:
        output_dir = Path("virtual-outputs")
        fake_images = [Path("virtual-inputs/sample.png")]
        mkdir_calls: list[tuple[tuple, dict]] = []
        written_payloads: list[str] = []

        def _record_mkdir(*args, **kwargs) -> None:
            mkdir_calls.append((args, kwargs))

        def _record_write_text(self: Path, text: str, encoding: str | None = None) -> int:
            written_payloads.append(text)
            return len(text)

        with patch("app.usecases.batch_runner.collect_input_images", return_value=fake_images), patch(
            "app.usecases.batch_runner.Path.mkdir", new=_record_mkdir
        ), patch("app.usecases.batch_runner.Path.write_text", new=_record_write_text):
            summary = run_batch(
                engine=_FakeEngine(),
                input_dir="virtual-inputs",
                target_lang="en",
                output_root=output_dir,
            )

        self.assertEqual(summary.succeeded, 1)
        self.assertEqual(len(mkdir_calls), 1)
        self.assertEqual(len(written_payloads), 2)


if __name__ == "__main__":
    unittest.main()
