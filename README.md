# Localized Scene Text Editing MVP

## 1. Project Intent

This repository is an MVP baseline for a **Localized Scene Text Editing** system.

The long-term goal is larger than OCR-based translation. The intended product is a service that can:

- detect and understand text regions in posters or scene images,
- generate localized target-market copy,
- preserve original design structure as much as possible,
- validate output quality with explicit scoring and review gates,
- support both a stable product track and an STE research track,
- evolve through harness-driven iteration and multi-agent execution.

Current repository status is still **baseline / MVP**, but the operating direction is now **harness-first**.

---

## 2. What Is Implemented Right Now

Current baseline pipeline:

`OCR -> localization -> inpaint -> render -> validate`

Important current-state clarification:

- This is **not yet a generative STE runtime**.
- OCR/detection uses deep-learning components, and localization can use an LLM backend.
- Background restoration is currently OpenCV inpainting.
- Final text synthesis is currently font/PIL rendering, not diffusion or end-to-end scene text editing.
- Generative STE work must enter through an explicit adapter/export/candidate path before it can affect the product baseline.

Implemented capabilities include:

- PaddleOCR-based text detection and recognition
- polygon-based masking
- OpenCV inpainting-based background restoration
- pluggable translation / localization backend
- local Hugging Face translation backend support (`hf_local`)
- bbox-based text re-rendering
- OCR re-check based quality scoring
- debug artifact export
- batch run support
- STE dataset export for later research-track comparison

This is a baseline path, not the final poster-localization quality target.

The current baseline exists so that future generative STE candidates can be measured against a stable reference rather than replacing the product path silently.

---

## 3. Repository Structure

```text
.
├─ AGENTS.md
├─ TASKS.md
├─ DONE.md
├─ README.md
├─ requirements.txt
├─ app/
│  ├─ config.py
│  ├─ main.py
│  ├─ domain/
│  ├─ infra/
│  ├─ pipeline/
│  └─ usecases/
├─ assets/
│  └─ fonts/
├─ benchmarks/
│  ├─ datasets/
│  ├─ manifests/
│  └─ golden/
└─ docs/
   ├─ ste_experiment_design.md
   └─ harness/
      ├─ 01_requirements_and_target.md
      ├─ 02_harness_engineering_blueprint.md
      ├─ 03_ralph_wiggum_loop_guide.md
      ├─ 04_benchmark_manifest_template.md
      ├─ 05_agent_prompt_templates.md
      ├─ 06_merge_gate_checklist.md
      ├─ 07_maintenance_agent_blueprint.md
      ├─ 08_code_convention_policy.md
      ├─ 09_architecture_guard_rules.md
      ├─ 10_autofix_policy.md
      ├─ 11_repo_governance_schedule.md
      └─ 12_maintenance_gate_checklist.md
├─ harness/
│  ├─ configs/
│  ├─ policies/
│  ├─ runners/
│  ├─ comparators/
│  ├─ reports/
│  ├─ schemas/
│  └─ templates/
├─ experiments/
│  └─ loop_template/
└─ tests/
   ├─ unit/
   ├─ integration/
   └─ regression/
```

### Layer roles

- `app/domain/`: pure models, value objects, interfaces, core contracts
- `app/infra/`: OCR, translation, image operations, rendering, style estimation
- `app/pipeline/`: orchestration and quality validation flow
- `app/usecases/`: batch execution, artifact export, auxiliary workflows
- `benchmarks/`: benchmark datasets, manifests, and golden references
- `harness/`: baseline/candidate execution wiring, comparison scripts, and reports
- `experiments/`: loop-scoped working folders and reusable experiment scaffolds
- `tests/`: low-cost unit, integration, and regression safety checks
- `docs/`: design intent, harness policy, governance, loop guidance

---

## 4. Recommended Reading Order

If you are joining the project or using Codex/CLI agents, read in this order:

1. `AGENTS.md`
2. `README.md`
3. `docs/ste_experiment_design.md`
4. `docs/harness/01_requirements_and_target.md`
5. `docs/harness/02_harness_engineering_blueprint.md`
6. `docs/harness/03_ralph_wiggum_loop_guide.md`
7. the rest of `docs/harness/`

This order matters because the repository is now intended to be operated with explicit harness and governance constraints.

---

## 5. Mandatory Task Logging

All meaningful repository work must be tracked through the two root files below:

- `TASKS.md`: active work board, plan, status, validation plan, feedback, and risks
- `DONE.md`: completion log with summary, verification, and follow-up notes

Required workflow:

1. Before starting work, add or update the task in `TASKS.md`.
2. Keep task status current while implementing.
3. When the task finishes, mark it in `TASKS.md` and append the result to `DONE.md`.
4. If verification was skipped or partial, state that explicitly.

This is a repository rule, not an optional habit. The goal is to keep every change inspectable and reviewable under the harness-first operating model.

---

## 6. Runtime Requirements

### Python

Recommended:

- Python 3.11
- Python 3.12

Not the current target:

- Python 3.13

### Main dependencies

- PaddleOCR
- OpenCV
- Pillow

Install baseline requirements:

```bash
pip install -r requirements.txt
```

If you want local Hugging Face translation, also install:

```bash
pip install transformers>=4.51.0 sentencepiece>=0.2.0
```

If your environment already has a separate requirement file for local translation, you may also use that.

---

## 7. Fonts

Font files are intentionally not bundled in this repository.

You must provide a TTF or OTF font and pass it through `--font-path`, or place an appropriate font under `assets/fonts/`.

Example Windows font paths often used during experiments:

- `C:\Windows\Fonts\malgun.ttf`
- `C:\Windows\Fonts\malgunbd.ttf`
- `C:\Windows\Fonts\arial.ttf`
- `C:\Windows\Fonts\arialbd.ttf`

---

## 8. Single Image Execution

```bash
python -m app.main \
  --input ./sample.jpg \
  --target-lang ko \
  --source-lang ko \
  --output-root ./outputs \
  --font-path ./assets/fonts/NotoSansKR-Regular.ttf \
  --ocr-lang korean \
  --translation-provider auto \
  --translation-model gpt-4.1-mini
```

### Notes

- `--target-lang` is required.
- Use either `--input` or `--input-dir`.
- Do not pass both at the same time.

---

## 9. Batch Execution

```bash
python -m app.main \
  --input-dir ./samples \
  --target-lang vi \
  --source-lang ko \
  --output-root ./outputs \
  --font-path C:\Windows\Fonts\arialbd.ttf \
  --translation-provider auto
```

Batch mode writes a summary under:

```text
outputs/_batch_reports/
  ├─ batch_<target_lang>.json
  └─ batch_<target_lang>.md
```

---

## 10. Translation Provider Behavior

### `auto`
If `OPENAI_API_KEY` or `TRANSLATION_API_KEY` is available, the app tries an OpenAI-compatible translation backend.
If not, it falls back to keeping the source text.

### `hf_local`
Example:

```bash
set HF_HOME=D:\hf-cache
python -m app.main \
  --input ./sample.jpg \
  --target-lang vi \
  --source-lang ko \
  --translation-provider hf_local \
  --translation-local-model facebook/m2m100_418M \
  --font-path C:\Windows\Fonts\arialbd.ttf
```

Notes:

- first run may download the model,
- CPU execution can be slow,
- on Windows, moving `HF_HOME` to a larger drive is often safer.

Currently referenced language codes in this repo include:

- `ko`
- `en`
- `vi`
- `th`
- `ja`
- `zh`

---

## 11. Output Artifacts

For a single input image, outputs are written under:

```text
outputs/{input_stem}/
```

Typical artifacts:

- `01_detected_boxes.jpg`
- `02_ocr.json`
- `03_mask.png`
- `04_restored.jpg`
- `05_rendered_XX.jpg`
- `98_quality.json`
- `99_final.jpg`

These artifacts are important. They are not just debug leftovers; they are part of the inspection and validation workflow.

---

## 12. STE Dataset Export

You can export an STE-oriented dataset package while preserving the existing baseline path.

Example:

```bash
python -m app.main \
  --input ./sample.jpg \
  --target-lang vi \
  --source-lang ko \
  --font-path C:\Windows\Fonts\arialbd.ttf \
  --translation-provider auto \
  --export-ste-dataset
```

Additional outputs:

```text
outputs/<job_name>/ste_dataset/
  ├─ source_image.jpg
  ├─ restored_image.jpg
  ├─ full_mask.png
  ├─ ste_manifest.json
  ├─ README.md
  └─ regions/
     ├─ region_01_source.png
     ├─ region_01_restored.png
     ├─ region_01_mask.png
     └─ ...
```

The manifest records information such as:

- source text
- target text
- candidate texts
- role classification
- bbox / polygon
- style estimate
- crop artifact paths

This export is the bridge between the stable baseline and later STE model experimentation.

Current status:

- implemented: crop/mask/context export for editable regions
- implemented: target text, candidate text, region geometry, confidence, and style metadata in `ste_manifest.json`
- not implemented yet: a production generative STE model adapter
- not implemented yet: diffusion/AnyText-style output selection in the baseline path

Expected next integration shape:

1. Keep the classical baseline as the reference path.
2. Add a research-track STE adapter that consumes `ste_manifest.json`.
3. Store STE-generated candidates beside baseline artifacts.
4. Compare baseline renderer output vs STE output under the same harness policy.
5. Promote only after text correctness, visual preservation, artifact completeness, and benchmark gates pass.

See also:

- `docs/ste_experiment_design.md`

---

## 12. Harness-First Development Direction

This repository should now be developed under the following discipline:

1. define the target or hypothesis,
2. make a scoped change,
3. run the baseline and collect artifacts,
4. compare results under a harness,
5. reject or accept by gate,
6. repeat.

The harness and governance documents under `docs/harness/` define the intended long-term operating model.

Key themes:

- explicit benchmark manifests,
- repeatable loop execution,
- merge gates,
- maintenance agent governance,
- architecture drift control,
- product-track / research-track separation.

---

## 13. Harness Quick Start

Example baseline run wiring:

```bash
python harness/runners/run_baseline.py --config harness/configs/baseline.json
```

Example candidate run wiring:

```bash
python harness/runners/run_candidate.py --config harness/configs/candidate.example.json --run-name candidate_smoke
```

Compare two completed runs:

```bash
python harness/comparators/compare_runs.py \
  --baseline outputs/harness/baseline/run_result.json \
  --candidate outputs/harness/candidate_smoke/run_result.json \
  --output outputs/harness/comparisons/baseline_vs_candidate.json \
  --policy harness/policies/gate_default.json
```

Build a markdown report:

```bash
python harness/reports/build_report.py \
  --comparison outputs/harness/comparisons/baseline_vs_candidate.json \
  --output outputs/harness/comparisons/baseline_vs_candidate.md
```

Build a promotion recommendation:

```bash
python harness/comparators/select_winner.py \
  --comparison outputs/harness/comparisons/baseline_vs_candidate.json \
  --output outputs/harness/comparisons/baseline_vs_candidate.recommendation.json
```

Each harness run now records:

- config snapshot
- benchmark snapshot
- git commit / dirty state when available
- failure summary derived from batch execution
- schema validation before writing run and comparison artifacts

Available gate policy examples:

- `harness/policies/gate_default.json`
- `harness/policies/gate_explore.json`

Each run directory also stores a `_snapshots/` folder with copied config and benchmark manifest inputs.

---

## 14. Test Quick Start

Run the current lightweight safety tests:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Current test focus:

- domain contract stability
- low-cost batch runner integration behavior
- fake-based pipeline regression smoke

---

## 15. Experiment Loop Scaffold

Use `experiments/loop_template/` as the starting point for a new loop folder.

Recommended flow:

1. create `experiments/<loop_id>/`
2. copy the template files into that folder
3. record the loop plan before implementation
4. run baseline and candidate through the harness
5. attach comparison, report, and recommendation outputs to the loop folder
6. record regressions and winning cases before promotion decisions

---

## 16. Practical Codex / Agent Guidance

When using Codex or a CLI coding agent on this repo:

- start from `AGENTS.md`,
- preserve the current CLI entrypoint,
- avoid broad rewrites,
- prefer small reversible changes,
- keep output artifacts inspectable,
- do not mix research shortcuts into the product baseline,
- treat contracts, quality scoring semantics, and harness policies as high-risk areas.

The repository is intentionally moving toward a multi-agent model including:

- Conductor Agent
- Feature Agent
- Validation Agent
- STE Research Agent
- Maintenance Agent

The repo is not fully automated yet, but the document structure is prepared for that direction.

---

## 17. Current Limitations

This baseline still has important limitations, including but not limited to:

- imperfect text removal in difficult backgrounds,
- imperfect typography preservation,
- visible render artifacts on complex posters,
- OCR sensitivity on low-quality regions,
- heuristic style estimation,
- bbox-oriented rendering limitations.

These are expected limitations of the current baseline. The harness structure exists to improve them without losing control of the project.

---

## 18. What Not To Optimize Prematurely

Unless explicitly required, do not prioritize:

- web UI,
- database integration,
- SaaS scaffolding,
- speculative GPU optimization,
- full-system rewrites.

The first priority is reliable quality improvement under measurable governance.

---

## 19. Next Recommended Steps

If continuing this project, the most reasonable next steps are:

1. expand benchmark datasets and split definitions beyond the initial smoke set,
2. add a research-track STE adapter that consumes exported crop/mask/target-text packages,
3. add visual comparison metrics for background cleanliness, typography fit, and design preservation,
4. compare baseline renderer output vs STE candidate output under the harness,
5. add policy coverage for more of the merge-gate checklist,
6. add maintenance-agent automation.

This repository should be treated as a baseline system entering long-term disciplined development, not as a throwaway prototype.
