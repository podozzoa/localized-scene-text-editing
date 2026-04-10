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

---

## 3. Repository Structure

```text
.
├─ AGENTS.md
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
```

### Layer roles

- `app/domain/`: pure models, value objects, interfaces, core contracts
- `app/infra/`: OCR, translation, image operations, rendering, style estimation
- `app/pipeline/`: orchestration and quality validation flow
- `app/usecases/`: batch execution, artifact export, auxiliary workflows
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

## 5. Runtime Requirements

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

## 6. Fonts

Font files are intentionally not bundled in this repository.

You must provide a TTF or OTF font and pass it through `--font-path`, or place an appropriate font under `assets/fonts/`.

Example Windows font paths often used during experiments:

- `C:\Windows\Fonts\malgun.ttf`
- `C:\Windows\Fonts\malgunbd.ttf`
- `C:\Windows\Fonts\arial.ttf`
- `C:\Windows\Fonts\arialbd.ttf`

---

## 7. Single Image Execution

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

## 8. Batch Execution

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

## 9. Translation Provider Behavior

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

## 10. Output Artifacts

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

## 11. STE Dataset Export

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

## 13. Practical Codex / Agent Guidance

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

## 14. Current Limitations

This baseline still has important limitations, including but not limited to:

- imperfect text removal in difficult backgrounds,
- imperfect typography preservation,
- visible render artifacts on complex posters,
- OCR sensitivity on low-quality regions,
- heuristic style estimation,
- bbox-oriented rendering limitations.

These are expected limitations of the current baseline. The harness structure exists to improve them without losing control of the project.

---

## 15. What Not To Optimize Prematurely

Unless explicitly required, do not prioritize:

- web UI,
- database integration,
- SaaS scaffolding,
- speculative GPU optimization,
- full-system rewrites.

The first priority is reliable quality improvement under measurable governance.

---

## 16. Next Recommended Steps

If continuing this project, the most reasonable next steps are:

1. add machine-readable harness policy files,
2. add benchmark datasets and split definitions,
3. formalize regression reports,
4. add maintenance-agent automation,
5. separate product-track adapters from STE research adapters more explicitly.

This repository should be treated as a baseline system entering long-term disciplined development, not as a throwaway prototype.
