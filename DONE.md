# DONE.md

This file is the mandatory completion log for this repository.

## Rules

1. Every completed task must leave a record here.
2. Each entry must include:
   - task id
   - completion date
   - owner
   - summary of change
   - validation performed
   - follow-up items or residual risks
3. `DONE.md` is not a changelog for every line edit. It is the decision log for completed work.
4. If validation was not run, state that explicitly.

---

## Completed Tasks

### TASK-2026-04-28-002
- completion date: 2026-04-28
- owner: Codex
- summary of change:
  - updated harness execution so `.env` is loaded before engine construction
  - added test coverage proving harness execution calls dotenv loading before building the engine
  - ran fresh approved smoke baseline and candidate runs with OpenAI-compatible translation
  - generated loop 006 comparison, recommendation, and quality diagnosis artifacts
  - recorded loop 006 under `experiments/2026-04-28-loop-006-openai-smoke-run`
- validation performed:
  - ran `python -m compileall app harness tests benchmarks experiments`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
  - ran approved smoke manifest validation
  - ran `loop006_baseline_openai` and `loop006_candidate_openai`
  - generated comparison, recommendation, and diagnosis reports for loop 006
- follow-up items or residual risks:
  - average smoke quality improved to 0.5, but `sample1.png` still scores 0.0
  - `sample2.jpg` no longer reports `target text script mismatch`
  - next loop should focus on editability/role classification for skipped headline or brand-like text

### TASK-2026-04-28-001
- completion date: 2026-04-28
- owner: Codex
- summary of change:
  - added translation backend status reporting to `TranslatorAdapter` and harness run results
  - changed fallback behavior so Hangul source text that requires English translation no longer passes through as a valid candidate
  - kept ASCII brand-like tokens such as `TERRA` and `SALE 50%` as valid passthrough text
  - updated the rewriter to filter script-incompatible candidates before scoring
  - added loop 005 experiment artifacts under `experiments/2026-04-28-loop-005-translation-readiness`
  - added unit coverage for backend readiness, untranslated candidate blocking, and quality diagnosis markdown
- validation performed:
  - ran `python -m compileall app harness tests benchmarks experiments`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
  - ran approved smoke manifest validation with `harness/validators/benchmark_manifest.py --require-approved`
- follow-up items or residual risks:
  - this prevents silent untranslated candidates, but it does not create target-language text without a real backend
  - fresh OCR-backed harness execution is still required once the local runtime is stable
  - next loop should configure or verify OpenAI-compatible or local translation and rerun approved smoke artifacts

### TASK-2026-04-20-001
- completion date: 2026-04-20
- owner: Codex
- summary of change:
  - added harness quality diagnosis aggregation from per-image `98_quality.json` artifacts
  - added `harness/reports/build_quality_diagnosis.py` to generate machine-readable and markdown quality diagnosis reports from existing run results
  - generated loop 004 artifacts under `experiments/2026-04-20-loop-004-quality-zero-diagnosis`
  - recorded that baseline and candidate both have two zero-score smoke items, five skipped non-editable regions, and three target-script mismatches
  - added unit tests for diagnosis aggregation and markdown report generation
- validation performed:
  - ran `python -m compileall app harness tests benchmarks experiments`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
  - ran approved smoke manifest validation
  - generated baseline and candidate quality diagnosis artifacts
  - attempted a fresh approved baseline run, which exited with code 1 before writing a run bundle
- follow-up items or residual risks:
  - this loop diagnoses the zero-score failure mode but intentionally does not change product pipeline behavior
  - fresh baseline/candidate execution is still desirable once the local OCR runtime is stable
  - next loop should target rewrite/translation behavior so English runs do not silently keep Korean target text for editable regions

### TASK-2026-04-16-002
- completion date: 2026-04-16
- owner: Codex
- summary of change:
  - promoted the two smoke benchmark `expected_targets_status` values from `draft` to `approved` after user confirmation
  - regenerated loop 003 manifest validation and curation packet artifacts
  - regenerated loop 002 comparison, markdown report, promotion recommendation, and loop summary artifacts
  - updated the curation packet generator so approved items show `reviewer_decision` as `approved`
  - confirmed benchmark readiness is now open and loop 002 recommendation is `promote`
- validation performed:
  - ran `python -m compileall harness tests benchmarks experiments`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
  - ran `harness/validators/benchmark_manifest.py --require-approved` against the smoke manifest
  - inspected regenerated comparison, recommendation, and loop summaries
- follow-up items or residual risks:
  - approval only covers the two-item smoke set and should not be treated as a production benchmark
  - loop 002 promotes on governance/readiness criteria, but both baseline and candidate still score 0.0
  - the next loop should investigate why smoke quality scoring remains zero or rerun the harness with fresh approved-target bundles

### TASK-2026-04-16-001
- completion date: 2026-04-16
- owner: Codex
- summary of change:
  - added `harness/validators/benchmark_manifest.py` to semantically validate benchmark manifests and report promotion readiness
  - added `harness/reports/build_curation_packet.py` to generate reviewer-facing curation packets for loop folders
  - generated loop 003 curation artifacts under `experiments/2026-04-15-loop-003-benchmark-curation`
  - added unit tests for approved, draft, placeholder, and curation-packet behavior
  - documented the new validation and packet-generation commands in `benchmarks/CURATION.md`
- validation performed:
  - ran `python -m compileall harness tests benchmarks experiments`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
  - ran manifest validation against `benchmarks/manifests/smoke_manifest.json`
- follow-up items or residual risks:
  - smoke manifest is structurally valid but still not promotion-ready because both targets are `draft`
  - human review must decide whether to mark `sample1` and `sample2` expected targets as `approved`
  - after approval, baseline/candidate comparison and recommendation artifacts should be regenerated

### TASK-2026-04-15-003
- completion date: 2026-04-15
- owner: Codex
- summary of change:
  - opened loop 003 at `experiments/2026-04-15-loop-003-benchmark-curation` for smoke benchmark curation
  - replaced smoke manifest placeholder targets with draft expected targets and added explicit `expected_targets_status` metadata
  - updated comparator readiness logic to prefer current manifest curation metadata over stale run snapshots when assessing promotion readiness
  - regenerated loop 002 comparison, recommendation, and loop-folder artifacts so the loop now holds for draft benchmark approval instead of placeholder text
- validation performed:
  - ran `python -m compileall harness tests benchmarks experiments`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
  - regenerated `outputs/harness/comparisons/loop002_validation_comparison.json`
  - regenerated `outputs/harness/comparisons/loop002_validation_comparison.md`
  - regenerated `outputs/harness/comparisons/loop002_validation_recommendation.json`
  - regenerated loop 002 bootstrap artifacts under `experiments/2026-04-10-loop-002-validation-reliability`
- follow-up items or residual risks:
  - current smoke expected targets are still `draft`, so loop 002 remains correctly blocked from promotion
  - full rerun of baseline/candidate harness execution is still desirable once the local OCR runtime permission issue is resolved
  - benchmark trust still depends on human approval and likely broader dataset expansion beyond the two-item smoke set

### TASK-2026-04-15-002
- completion date: 2026-04-15
- owner: Codex
- summary of change:
  - added benchmark-readiness signals to comparison output
  - updated recommendation logic to hold when benchmark expected targets still use placeholder values
  - documented benchmark curation in `benchmarks/CURATION.md`
  - regenerated loop 002 comparison and recommendation artifacts with the new safety rule
- validation performed:
  - ran `python -m compileall harness tests benchmarks`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
  - regenerated `loop002_validation_comparison.json` and `loop002_validation_recommendation.json`
- follow-up items or residual risks:
  - placeholder detection is still string-based and should later become explicit benchmark metadata
  - loop 002 remains operationally complete but benchmark curation is still required before any meaningful promotion decision

### TASK-2026-04-13-001
- completion date: 2026-04-15
- owner: Codex
- summary of change:
  - installed the missing Paddle runtime so harness execution could run end to end
  - generated loop 002 baseline and candidate run artifacts
  - generated comparison, markdown report, recommendation, and bootstrapped them into the loop 002 experiment folder
  - updated the loop 002 summary/report to reflect that the correct interpretation is still `hold`
- validation performed:
  - ran the baseline and candidate harness runners successfully
  - generated comparison, report, recommendation, and experiment-folder artifacts for loop 002
- follow-up items or residual risks:
  - the current smoke manifest still uses placeholder expected targets, so zero scores do not yet support a meaningful promote decision
  - loop 002 proved the operational loop path, but not yet the quality uplift path

### TASK-2026-04-10-010
- completion date: 2026-04-10
- owner: Codex
- summary of change:
  - opened the first quality-targeted loop at `experiments/2026-04-10-loop-002-validation-reliability`
  - improved `OCRQualityValidator` so duplicate expected tokens are scored by token counts rather than simple presence
  - expanded validator OCR language mapping for documented `ja`, `zh`, and `th` targets
  - added focused unit tests for validation reliability behavior
- validation performed:
  - ran `python -m compileall app harness experiments tests`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
- follow-up items or residual risks:
  - this loop is still validated mainly by targeted unit coverage and should later be exercised through a real harness candidate comparison
  - OCR language aliases depend on installed backend support and may still need environment-level verification

### TASK-2026-04-10-009
- completion date: 2026-04-10
- owner: Codex
- summary of change:
  - added `bootstrap_loop.py` to materialize or update an `experiments/<loop_id>/` folder from harness artifacts
  - added unit coverage for loop bootstrap summary and report generation
  - instantiated the first concrete loop folder at `experiments/2026-04-10-loop-001-harness-closure`
- validation performed:
  - ran `python -m compileall harness experiments tests`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
- follow-up items or residual risks:
  - the first loop folder currently contains the plan/report scaffold and still needs real baseline/candidate comparison artifacts
  - the next meaningful loop should target measured quality change, not only operational closure

### TASK-2026-04-10-008
- completion date: 2026-04-10
- owner: Codex
- summary of change:
  - added run bundle snapshots so harness outputs keep copied config and benchmark inputs alongside result metadata
  - added `select_winner.py` so comparison results can be converted into a promotion recommendation artifact
  - incorporated experiment loop scaffolding under `experiments/` and reusable loop templates under `harness/templates/`
  - updated `README.md` so the run, compare, recommend, and experiment-folder workflow is documented end to end
- validation performed:
  - ran `python -m compileall harness experiments tests`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
- follow-up items or residual risks:
  - this now supports a minimum operational Ralph Wiggum loop, but benchmark scale and human-approved expected outputs are still small
  - full governance parity with the docs will still require more policy coverage, richer datasets, and stronger maintenance automation

### TASK-2026-04-10-007
- completion date: 2026-04-10
- owner: Codex
- summary of change:
  - added explicit gate policy files under `harness/policies`
  - updated the comparator to load thresholds and boolean gate behavior from policy JSON instead of hardcoded constants
  - added a policy schema and expanded comparator tests to cover alternate policy behavior
- validation performed:
  - ran `python -m compileall harness tests`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
- follow-up items or residual risks:
  - current policy files only drive the lightweight comparator and do not yet encode the full merge-gate checklist from the docs
  - stricter policy validation will be needed if policy files grow beyond the current threshold set

### TASK-2026-04-10-006
- completion date: 2026-04-10
- owner: Codex
- summary of change:
  - added `critical` metadata to the smoke benchmark manifest
  - carried benchmark item metadata into harness run results
  - extended the comparator and report builder with critical-split and category-level summaries and gate checks
  - expanded comparator unit tests to cover the new gate behavior
- validation performed:
  - ran `python -m compileall harness tests`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
- follow-up items or residual risks:
  - current gate logic is still lightweight and should not be treated as a final promotion policy
  - benchmark categories and critical flags still need human curation before they can carry stronger governance weight

### TASK-2026-04-10-005
- completion date: 2026-04-10
- owner: Codex
- summary of change:
  - added a lightweight local schema validator for the current harness JSON schema subset
  - updated run result and comparison write paths to validate payloads before writing files
  - aligned schema files with the richer run/comparison payloads and added validator unit tests
- validation performed:
  - ran `python -m compileall harness tests`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
- follow-up items or residual risks:
  - validator currently supports the schema subset used here and should be expanded or replaced if schema complexity grows
  - schema enforcement is structural today and does not yet validate semantic rules like threshold bounds or tag vocabularies

### TASK-2026-04-10-004
- completion date: 2026-04-10
- owner: Codex
- summary of change:
  - enriched harness `run_result.json` generation with config snapshot, benchmark snapshot, code version, and failure summary fields
  - added unit tests for failure summary aggregation and git metadata capture
  - updated `README.md` to document the new harness metadata
- validation performed:
  - ran `python -m compileall harness tests`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
- follow-up items or residual risks:
  - schema validation is still documentation-driven and should later be enforced automatically
  - current code version capture records git commit and dirty state, but not yet branch name or config file hash

### TASK-2026-04-10-003
- completion date: 2026-04-10
- owner: Codex
- summary of change:
  - promoted two real local sample images into the smoke benchmark dataset
  - replaced the placeholder smoke manifest entry with concrete dataset items
  - extended the harness comparator with simple promote/reject gate output and blocking reasons
  - added comparator unit tests and kept the smoke suite green
- validation performed:
  - verified benchmark image files exist under `benchmarks/datasets/smoke/images`
  - ran `python -m compileall harness tests`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
- follow-up items or residual risks:
  - expected target text in the smoke manifest is still provisional and needs human-approved benchmark values
  - comparator gate logic is intentionally simple and does not yet encode category-aware or critical-split policy

### TASK-2026-04-10-002
- completion date: 2026-04-10
- owner: Codex
- summary of change:
  - added concrete `benchmarks/` and `harness/` foundations
  - added baseline runner, candidate runner, run comparator, and markdown report builder
  - added `tests/unit`, `tests/integration`, and `tests/regression` with low-cost baseline safety checks
  - updated `README.md` with harness and test quick-start commands
- validation performed:
  - ran `python -m compileall harness tests`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
- follow-up items or residual risks:
  - the benchmark manifest currently points to placeholder smoke samples and still needs approved real benchmark images
  - the harness currently wraps the existing batch runner and does not yet implement category-aware scoring or merge-gate automation

### TASK-2026-04-10-001
- completion date: 2026-04-10
- owner: Codex
- summary of change:
  - added `TASKS.md` as the mandatory active work board
  - added `DONE.md` as the mandatory completion log
  - updated `AGENTS.md` and `README.md` so future work must be recorded before and after implementation
- validation performed:
  - verified both root tracking files exist
  - verified the logging rule is present in `AGENTS.md` and `README.md`
- follow-up items or residual risks:
  - enforcement is document-driven today and can later be strengthened with pre-commit or CI checks

### TASK-2026-04-10-000
- completion date: 2026-04-10
- owner: Codex
- summary of change:
  - initialized local Git repository
  - added repository hygiene files for Git publishing
  - created the first commit and pushed to GitHub
- validation performed:
  - checked tracked vs ignored files
  - verified initial commit creation
  - verified push to `origin/main`
- follow-up items or residual risks:
  - runtime target is still documented as Python 3.11/3.12 while the local machine currently has 3.13

---

### TASK-2026-04-28-003
- completion date: 2026-04-28
- owner: Codex
- summary of change:
  - added narrow pass-through validation for target-script-compatible skipped text when no editable regions exist
  - protected the behavior with regression tests for skipped `SALE 50%` style text and mixed editable/skipped regions
  - generated loop 007 comparison, recommendation, and quality diagnosis artifacts
  - recorded loop 007 under `experiments/2026-04-28-loop-007-passthrough-validation`
- validation performed:
  - ran `python -m compileall app harness tests benchmarks experiments`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
  - ran approved smoke baseline and candidate harness executions
- follow-up items or residual risks:
  - zero-score smoke items are removed, but candidate promotion is held because `sample2.jpg` regressed against baseline
  - the next loop should isolate candidate configuration effects before broader renderer or localization changes

---

### TASK-2026-04-28-004
- completion date: 2026-04-28
- owner: Codex
- summary of change:
  - made harness execution use run-specific output roots for engine artifacts and batch reports
  - updated baseline/candidate runner bundle destinations to avoid double-nesting run names
  - lowered OpenAI-compatible translation temperature to deterministic mode for repeatable comparisons
  - added unit coverage for run-specific output roots and deterministic candidate generation
  - recorded loop 008 under `experiments/2026-04-28-loop-008-run-isolation`
- validation performed:
  - ran `python -m compileall app harness tests benchmarks experiments`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
  - ran `.\\.venv\\Scripts\\python.exe -m harness.validators.benchmark_manifest --manifest benchmarks\\manifests\\smoke_manifest.json --require-approved`
  - ran fresh approved smoke baseline and candidate harness executions
  - generated loop 008 comparison, recommendation, and quality diagnosis artifacts
- follow-up items or residual risks:
  - future translation quality can still drift if the external provider/model changes behavior
  - the smoke benchmark is stable but still too small for production confidence; benchmark expansion should come before larger renderer changes

---

### TASK-2026-04-28-005
- completion date: 2026-04-28
- owner: Codex
- summary of change:
  - added required per-item artifact completeness diagnosis to harness run results
  - included missing artifact counts in run notes and run summaries
  - extended quality diagnosis JSON/Markdown with artifact completeness and render artifact counts
  - added unit tests for missing artifact detection and diagnosis report rendering
  - recorded loop 009 under `experiments/2026-04-28-loop-009-artifact-completeness`
- validation performed:
  - ran `python -m compileall app harness tests benchmarks experiments`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
  - ran `.\\.venv\\Scripts\\python.exe -m harness.validators.benchmark_manifest --manifest benchmarks\\manifests\\smoke_manifest.json --require-approved`
  - ran fresh approved smoke baseline and candidate harness executions
  - generated loop 009 comparison, recommendation, and quality/artifact diagnosis artifacts
- follow-up items or residual risks:
  - artifact completeness is now visible, but visual quality metrics still need deeper image-level checks
  - benchmark coverage remains small and should be expanded before accepting larger renderer changes

---

### TASK-2026-04-28-006
- completion date: 2026-04-28
- owner: Codex
- summary of change:
  - reviewed README, STE design, harness direction, tests, and recent loop artifacts against the intended generative STE direction
  - clarified in docs that the current runtime is classical baseline plus OCR/LLM components, not generative STE
  - documented the required STE adapter boundary and forbidden research-to-product shortcuts
  - added unit coverage for the STE dataset export manifest contract
  - recorded loop 010 under `experiments/2026-04-28-loop-010-ste-alignment`
- validation performed:
  - ran `python -m compileall app harness tests benchmarks experiments`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
  - ran `.\\.venv\\Scripts\\python.exe -m harness.validators.benchmark_manifest --manifest benchmarks\\manifests\\smoke_manifest.json --require-approved`
  - ran fresh approved smoke baseline and candidate harness executions
  - generated loop 010 comparison, recommendation, and quality/artifact diagnosis artifacts
- follow-up items or residual risks:
  - generative STE is still not implemented
  - next loop should add a research-track STE adapter skeleton that consumes `ste_manifest.json` and writes candidate artifacts outside the product baseline

---

## Entry Template

### TASK-YYYY-MM-DD-XXX
- completion date:
- owner:
- summary of change:
  - item 1
- validation performed:
  - check 1
- follow-up items or residual risks:
  - note 1
