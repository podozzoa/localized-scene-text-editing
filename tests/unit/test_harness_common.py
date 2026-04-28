from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from app.usecases.batch_runner import BatchItemResult, BatchRunSummary
from harness.runners.common import (
    build_failure_summary,
    build_artifact_diagnosis,
    build_quality_diagnosis,
    execute_manifest,
    get_run_output_dir,
    get_code_version,
    get_translation_backend_status,
    HarnessRunConfig,
)


class HarnessCommonUnitTest(unittest.TestCase):
    def test_build_failure_summary_collects_failed_items(self) -> None:
        summary = BatchRunSummary(
            input_dir="inputs",
            target_lang="en",
            total_images=2,
            succeeded=1,
            failed=1,
            average_quality_score=0.5,
            items=[
                BatchItemResult(
                    input_path="sample1.png",
                    output_image_path="sample1.out.jpg",
                    quality_score=0.9,
                    warnings=[],
                    failed=False,
                    error=None,
                ),
                BatchItemResult(
                    input_path="sample2.jpg",
                    output_image_path="",
                    quality_score=0.0,
                    warnings=[],
                    failed=True,
                    error="stage crash",
                ),
            ],
        )

        failure_summary = build_failure_summary(summary)

        self.assertEqual(failure_summary["failed_item_count"], 1)
        self.assertEqual(failure_summary["failed_inputs"], ["sample2.jpg"])
        self.assertEqual(failure_summary["failure_reasons"][0]["error"], "stage crash")

    def test_get_code_version_handles_git_commands(self) -> None:
        rev_parse = Mock(stdout="abc123\n")
        status = Mock(stdout=" M README.md\n")
        with patch("harness.runners.common.subprocess.run", side_effect=[rev_parse, status]):
            version = get_code_version()

        self.assertEqual(version["git_commit"], "abc123")
        self.assertTrue(version["git_dirty"])

    def test_get_translation_backend_status_reads_rewriter_translator(self) -> None:
        class _Translator:
            def status_dict(self) -> dict:
                return {"active_provider": "identity", "backend_available": False}

        class _Rewriter:
            translator = _Translator()

        class _Engine:
            rewriter = _Rewriter()

        status = get_translation_backend_status(_Engine())

        self.assertEqual(status["active_provider"], "identity")
        self.assertFalse(status["backend_available"])

    def test_execute_manifest_loads_dotenv_before_building_engine(self) -> None:
        config = HarnessRunConfig(
            run_name="test",
            variant="baseline",
            target_lang="en",
            output_root="outputs/harness",
            translation_provider="auto",
            translation_model="model",
            translation_local_model="local",
            source_lang="ko",
            ocr_lang="korean",
            font_path="font.ttf",
            benchmark_manifest="benchmarks/manifests/smoke_manifest.json",
        )
        fake_summary = BatchRunSummary(
            input_dir="inputs",
            target_lang="en",
            total_images=0,
            succeeded=0,
            failed=0,
            average_quality_score=0.0,
            items=[],
        )

        class _Translator:
            def status_dict(self) -> dict:
                return {"active_provider": "openai_compatible", "backend_available": True}

        class _Rewriter:
            translator = _Translator()

        class _Engine:
            rewriter = _Rewriter()

        with patch("harness.runners.common._load_dotenv_if_present") as load_dotenv, patch(
            "harness.runners.common.load_manifest",
            return_value={"manifest_id": "smoke-v1", "dataset_root": "benchmarks/datasets/smoke/images", "items": []},
        ), patch("harness.runners.common._build_engine", return_value=(_Engine(), Mock(output_root=Path("outputs/harness")))), patch(
            "harness.runners.common.run_batch", return_value=fake_summary
        ):
            run_result = execute_manifest(config)

        load_dotenv.assert_called_once()
        self.assertEqual(run_result["translation_backend"]["active_provider"], "openai_compatible")

    def test_execute_manifest_uses_run_specific_output_root(self) -> None:
        config = HarnessRunConfig(
            run_name="isolated-run",
            variant="candidate",
            target_lang="en",
            output_root="outputs/harness",
            translation_provider="auto",
            translation_model="model",
            translation_local_model="local",
            source_lang="ko",
            ocr_lang="korean",
            font_path="font.ttf",
            benchmark_manifest="benchmarks/manifests/smoke_manifest.json",
        )
        fake_summary = BatchRunSummary(
            input_dir="inputs",
            target_lang="en",
            total_images=0,
            succeeded=0,
            failed=0,
            average_quality_score=0.0,
            items=[],
        )

        class _Translator:
            def status_dict(self) -> dict:
                return {"active_provider": "identity", "backend_available": False}

        class _Rewriter:
            translator = _Translator()

        class _Engine:
            rewriter = _Rewriter()

        with patch("harness.runners.common._load_dotenv_if_present"), patch(
            "harness.runners.common.load_manifest",
            return_value={"manifest_id": "smoke-v1", "dataset_root": "benchmarks/datasets/smoke/images", "items": []},
        ), patch("harness.runners.common._build_engine", return_value=(_Engine(), Mock(output_root=get_run_output_dir(config)))) as build_engine, patch(
            "harness.runners.common.run_batch", return_value=fake_summary
        ) as run_batch_mock:
            run_result = execute_manifest(config)

        engine_args = build_engine.call_args.args[0]
        self.assertEqual(Path(engine_args.output_root), Path("outputs/harness/isolated-run"))
        self.assertEqual(run_batch_mock.call_args.kwargs["output_root"], Path("outputs/harness/isolated-run"))
        self.assertEqual(Path(run_result["config_snapshot"]["output_root"]), Path("outputs/harness/isolated-run"))

    def test_build_quality_diagnosis_counts_zero_scores_and_region_warnings(self) -> None:
        output_dir = Path(".tmp_tests")
        output_dir.mkdir(exist_ok=True)
        (output_dir / "98_quality.json").write_text(
            """
            {
              "region_results": [
                {"quality_score": 0.0, "warning": "target text script mismatch"},
                {"quality_score": 0.9, "warning": "non-editable region skipped"}
              ]
            }
            """,
            encoding="utf-8",
        )
        summary = BatchRunSummary(
            input_dir="inputs",
            target_lang="en",
            total_images=1,
            succeeded=1,
            failed=0,
            average_quality_score=0.0,
            items=[
                BatchItemResult(
                    input_path="sample1.png",
                    output_image_path=str(output_dir / "99_final.jpg"),
                    quality_score=0.0,
                    warnings=["품질 점수가 임계값보다 낮습니다."],
                    failed=False,
                    error=None,
                )
            ],
        )

        diagnosis = build_quality_diagnosis(summary)

        self.assertEqual(diagnosis["zero_score_item_count"], 1)
        self.assertEqual(diagnosis["zero_score_region_count"], 1)
        self.assertEqual(diagnosis["region_warning_counts"]["target text script mismatch"], 1)
        self.assertEqual(diagnosis["region_warning_counts"]["non-editable region skipped"], 1)

    def test_build_artifact_diagnosis_reports_missing_required_files(self) -> None:
        summary = BatchRunSummary(
            input_dir="inputs",
            target_lang="en",
            total_images=1,
            succeeded=1,
            failed=0,
            average_quality_score=1.0,
            items=[
                BatchItemResult(
                    input_path="sample.png",
                    output_image_path="artifact_dir/99_final.jpg",
                    quality_score=1.0,
                    warnings=[],
                    failed=False,
                    error=None,
                )
            ],
        )

        with patch("harness.runners.common.Path.exists", new=lambda path: path.name == "99_final.jpg"), patch(
            "harness.runners.common.Path.glob", return_value=[]
        ):
            diagnosis = build_artifact_diagnosis(summary)

        self.assertEqual(diagnosis["checked_item_count"], 1)
        self.assertEqual(diagnosis["complete_item_count"], 0)
        self.assertEqual(diagnosis["missing_item_count"], 1)
        self.assertIn("98_quality.json", diagnosis["missing_items"][0]["missing_artifacts"])


if __name__ == "__main__":
    unittest.main()
