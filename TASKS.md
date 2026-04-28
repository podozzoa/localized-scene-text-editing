# TASKS.md

This file is the mandatory working board for this repository.

## Rules

1. Before starting any meaningful task, add or update an item in `TASKS.md`.
2. Each item must have:
   - id
   - date
   - owner
   - scope
   - status
   - plan
   - validation
   - feedback / risks
3. Status values must be one of:
   - `todo`
   - `in_progress`
   - `blocked`
   - `done`
4. When a task is finished:
   - update its final status here,
   - append a completion note to `DONE.md`,
   - record what changed, what was verified, and what remains open.
5. Do not start silent work that is not represented here.

---

## Active Tasks

### TASK-2026-04-28-006
- date: 2026-04-28
- owner: Codex
- scope: Implement Loop 010 STE direction alignment review, update docs/tests where needed, and rerun the Ralph Wiggum harness loop.
- status: done
- plan:
  - review README, STE experiment design, harness docs, current tests, and recent loop artifacts against the generated STE target direction
  - document the current gap between classical product baseline and future generative STE adapter path
  - add or update tests that enforce product/research separation and STE adapter/export contract readiness
  - rerun compile, unittest, approved manifest validation, and fresh smoke harness comparison
  - record loop 010 artifacts and completion logs
- validation:
  - ran `python -m compileall app harness tests benchmarks experiments`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
  - ran approved smoke manifest validation with `--require-approved`
  - ran fresh approved smoke baseline and candidate harness executions
  - generated comparison, recommendation, and baseline/candidate quality diagnosis artifacts
- feedback / risks:
  - docs now explicitly state that current runtime is not generative STE
  - STE export manifest contract is protected by a unit test
  - generated STE work should enter next through a research-track adapter/candidate path, not by replacing baseline

### TASK-2026-04-28-005
- date: 2026-04-28
- owner: Codex
- scope: Implement Loop 009 artifact completeness checks so harness runs expose missing per-item debug and quality artifacts before deeper renderer work.
- status: done
- plan:
  - inspect current harness run output and quality diagnosis structure
  - define required per-item artifact expectations without changing product pipeline behavior
  - add harness-level artifact completeness aggregation and report output
  - add unit coverage for complete and missing artifact cases
  - run compile, unittest, manifest validation, and smoke harness comparison if runtime allows
  - record loop 009 artifacts and task logs
- validation:
  - ran `python -m compileall app harness tests benchmarks experiments`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
  - ran approved smoke manifest validation with `--require-approved`
  - ran fresh approved smoke baseline and candidate harness executions
  - generated comparison, recommendation, and baseline/candidate quality diagnosis artifacts
- feedback / risks:
  - artifact checks do not replace quality scoring or weaken validation gates
  - required artifacts reflect the current baseline debug contract; `05_rendered_*` remains an observed count because no-edit images may skip rendering
  - fresh smoke comparison promoted with zero missing artifact items

### TASK-2026-04-28-004
- date: 2026-04-28
- owner: Codex
- scope: Implement Loop 008 candidate regression isolation so the approved smoke candidate no longer scores below baseline on `sample2.jpg`.
- status: done
- plan:
  - compare baseline and candidate harness configs and run artifacts
  - inspect `sample2.jpg` quality/debug artifacts for the scoring delta
  - make the smallest reversible change to remove candidate-only regression without weakening validation
  - add or update regression coverage for the observed cause
  - rerun compile, unittest, manifest validation, and fresh smoke harness comparison
  - record loop 008 artifacts and task logs
- validation:
  - ran `python -m compileall app harness tests benchmarks experiments`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
  - ran approved smoke manifest validation with `--require-approved`
  - ran fresh approved smoke baseline and candidate harness executions
  - generated comparison, recommendation, and baseline/candidate quality diagnosis artifacts
- feedback / risks:
  - candidate promotion was achieved without weakening gates or expected targets
  - harness debug artifacts are now run-isolated under `outputs/harness/<run_name>/...`
  - OpenAI-compatible translation is more deterministic, but external model/provider changes can still affect future copy quality

### TASK-2026-04-28-003
- date: 2026-04-28
- owner: Codex
- scope: Implement Loop 007 pass-through validation for target-script-compatible skipped regions so already-localized headline text does not force zero quality.
- status: done
- plan:
  - add a narrow engine helper for skipped text that should still be validated as pass-through target text
  - include target-script-compatible skipped text in validation expected texts without rendering it
  - add regression coverage for skipped `SALE 50%` style text contributing to final quality
  - rerun approved smoke baseline/candidate after the change
  - record loop 007 artifacts and task logs
- validation:
  - ran `python -m compileall app harness tests benchmarks experiments`
  - ran `.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_*.py" -v`
  - ran approved smoke baseline and candidate harness executions with OpenAI-compatible translation
  - generated comparison, recommendation, and baseline/candidate quality diagnosis artifacts
- feedback / risks:
  - pass-through validation is intentionally limited to target-script-compatible skipped text when no editable regions exist
  - the change removed zero-score smoke items, but the current candidate still regresses against baseline on `sample2.jpg`
  - promotion remains held until candidate-vs-baseline behavior is isolated

### TASK-2026-04-28-002
- date: 2026-04-28
- owner: Codex
- scope: Implement Loop 006 backend readiness wiring so harness runners load `.env` and can use configured OpenAI-compatible translation instead of identity fallback.
- status: done
- plan:
  - load `.env` before harness engine construction
  - verify backend status can reflect configured translation provider during harness runs
  - add tests for harness dotenv loading behavior
  - attempt an approved smoke run if network/runtime permissions allow it
  - record loop 006 artifacts and validation
- validation:
  - run compile validation for app/harness/tests/benchmarks/experiments
  - run unittest discovery
  - run approved smoke manifest validation
- feedback / risks:
  - `.env` contains translation configuration, but external API/network execution may require approval
  - local OCR runtime may still prevent fresh full harness artifacts
  - approved smoke now runs through OpenAI-compatible translation, but sample1 remains blocked by editability/skipped-region behavior

### TASK-2026-04-28-001
- date: 2026-04-28
- owner: Codex
- scope: Implement Loop 005 translation backend readiness and untranslated candidate blocking so target-language runs do not silently keep source-script text.
- status: done
- plan:
  - expose translator backend status in harness run results
  - make identity/fallback translation return no candidate when source-script text requires translation into a different target language
  - filter untranslated/script-incompatible candidates before rewriter scoring
  - add unit and regression coverage for fallback readiness and untranslated candidate blocking
  - run compile, unittest, and manifest validation
- validation:
  - run compile validation for app/harness/tests/benchmarks/experiments
  - run unittest discovery
  - run approved smoke manifest validation
- feedback / risks:
  - this loop improves failure visibility and candidate safety, but it does not provide a real translation backend by itself
  - actual target-language output still requires OpenAI-compatible or local translation backend availability
  - next loop should configure or verify a real backend and regenerate approved smoke run artifacts

### TASK-2026-04-20-001
- date: 2026-04-20
- owner: Codex
- scope: Open a quality diagnosis loop for approved smoke benchmark runs and make harness reports expose zero-score causes.
- status: done
- plan:
  - inspect current quality artifacts and summary generation
  - add harness-level quality diagnosis aggregation for skipped regions and script mismatches
  - regenerate comparison/report outputs with clearer zero-score evidence
  - open loop 004 experiment artifacts for quality diagnosis
  - validate with unit tests and smoke manifest validation
- validation:
  - run compile validation for app/harness/tests/benchmarks/experiments
  - run unittest discovery
  - inspect regenerated diagnosis artifacts
- feedback / risks:
  - this loop diagnoses the zero-score failure mode before changing translation or editability behavior
  - fresh baseline/candidate execution may still depend on local OCR model cache permissions
  - baseline and candidate diagnosis are identical, so the next candidate loop should target rewrite/translation behavior rather than comparator logic

### TASK-2026-04-16-002
- date: 2026-04-16
- owner: Codex
- scope: Promote smoke benchmark draft expected targets to approved after user confirmation and regenerate readiness-dependent harness artifacts.
- status: done
- plan:
  - update smoke manifest target statuses from `draft` to `approved`
  - regenerate manifest validation and reviewer packet artifacts
  - regenerate loop 002 comparison, report, recommendation, and loop bootstrap artifacts
  - verify tests and manifest readiness
  - update task completion logs
- validation:
  - run manifest validation with approval required
  - run compile validation for harness/tests/benchmarks/experiments
  - run unittest discovery again
  - inspect regenerated recommendation and loop summaries
- feedback / risks:
  - approval only covers the two-item smoke benchmark, not a broader production benchmark
  - actual quality score remains dependent on pipeline behavior and may still be 0.0 until model/candidate improvements land
  - loop 002 now promotes on governance criteria, but the zero quality scores still require the next quality-targeted loop

### TASK-2026-04-16-001
- date: 2026-04-16
- owner: Codex
- scope: Strengthen loop 003 benchmark curation by adding manifest validation and reviewer-ready curation artifacts without falsely marking draft targets as approved.
- status: done
- plan:
  - inspect benchmark and harness schema conventions
  - add a smoke manifest validation script that enforces target status and required item metadata
  - add tests for approved, draft, and invalid benchmark manifest states
  - generate reviewer-facing loop 003 curation artifacts from the current manifest
  - rerun comparison/recommendation artifacts if validation metadata affects loop outputs
- validation:
  - run manifest validation against the current smoke manifest
  - run compile validation for harness/tests/benchmarks/experiments
  - run unittest discovery again
- feedback / risks:
  - Codex must not mark targets as human-approved without user review
  - this improves curation governance but does not replace the human approval decision
  - current smoke manifest is valid but remains blocked from promotion until both draft targets are approved

### TASK-2026-04-15-003
- date: 2026-04-15
- owner: Codex
- scope: Open loop 003 for benchmark curation, replace smoke manifest placeholder expected targets with draft values, and distinguish draft vs approved benchmark readiness.
- status: done
- plan:
  - inspect smoke sample OCR/debug artifacts to understand current source text
  - draft concrete expected targets for the smoke manifest
  - add explicit benchmark target-status metadata so draft values do not count as promotion-ready
  - open a loop 003 experiment folder for benchmark curation
  - update curation docs and task records after verification
- validation:
  - verify manifest no longer contains placeholder targets
  - run compile validation for harness/tests/benchmarks
  - run unittest discovery again
- feedback / risks:
  - expected targets may still need later human refinement for marketing nuance
  - small smoke benchmark curation improves gate trust but does not replace larger benchmark expansion
  - loop 002 artifacts now reflect draft benchmark readiness correctly, but a real approved target set is still the next hard dependency

### TASK-2026-04-15-002
- date: 2026-04-15
- owner: Codex
- scope: Prevent false promotion when benchmark expected targets are placeholders and document the benchmark curation workflow.
- status: done
- plan:
  - enrich comparison output with benchmark readiness signals
  - make promotion recommendation hold when expected targets are still placeholders
  - document how smoke benchmark expected targets should be curated
  - run validation and update task records
- validation:
  - run compile validation for harness and tests
  - run unittest discovery again
- feedback / risks:
  - this adds a safety guard, but it does not replace actual benchmark curation
  - placeholder detection is string-based and should eventually become explicit benchmark metadata
  - loop 002 recommendation is now correctly blocked, but benchmark curation is the real next dependency

### TASK-2026-04-13-001
- date: 2026-04-13
- owner: Codex
- scope: Close loop 002 with real harness baseline/candidate/comparison artifacts and attach them to the loop folder.
- status: done
- plan:
  - inspect current harness configs and benchmark readiness
  - run baseline and candidate on the smoke benchmark
  - build comparison, report, and recommendation artifacts
  - bootstrap loop 002 with the generated artifacts
  - verify outputs and update task logs
- validation:
  - run the harness commands end to end
  - confirm the loop folder contains comparison and recommendation artifacts
- feedback / risks:
  - runtime success depends on the local OCR/backend environment
  - the smoke benchmark is still small, so loop conclusions remain lightweight
  - loop 002 artifacts now exist, but the correct human interpretation is still `hold`, not automatic promotion, because the current benchmark targets are placeholders

### TASK-2026-04-10-010
- date: 2026-04-10
- owner: Codex
- scope: Start the first quality-targeted Ralph Wiggum loop on validation reliability by tightening low-cost validation behavior and protecting it with tests.
- status: done
- plan:
  - inspect the current quality validator and nearby contracts
  - open a new loop folder for validation reliability
  - implement one small measurable reliability improvement
  - add or expand tests around the changed validation behavior
  - update loop records and task logs after verification
- validation:
  - run compile validation for app, harness, experiments, and tests
  - run unittest discovery again
- feedback / risks:
  - this first quality loop should stay narrow and avoid dragging renderer or translation logic into the same change
  - without larger benchmark data, gains here are still protected mainly by targeted tests and smoke harness behavior
  - validation reliability improved in code and tests, but a real harness baseline/candidate comparison is still needed to quantify loop-level uplift

### TASK-2026-04-10-009
- date: 2026-04-10
- owner: Codex
- scope: Start the first actual Ralph Wiggum loop by adding a bootstrap that materializes an `experiments/<loop_id>/` folder from harness outputs and records the loop plan.
- status: done
- plan:
  - inspect current experiment template files and harness outputs expected by a loop
  - add a bootstrap script that creates a loop folder and copies/summarizes harness artifacts into it
  - instantiate the first loop folder with a narrow theme around harness-driven execution
  - validate the new script and update task records
- validation:
  - run compile validation for harness, experiments, and tests
  - run unittest discovery again
- feedback / risks:
  - this first loop focuses on operational closure, not yet a model-quality uplift
  - later loops should target measured quality improvements on renderer, validation, or localization behavior
  - the first loop is now instantiated, but it still needs real baseline/candidate comparison outputs attached

### TASK-2026-04-10-008
- date: 2026-04-10
- owner: Codex
- scope: Bring the repository to a minimum operational Ralph Wiggum loop preparation state by closing the remaining harness and experiment-ops gaps.
- status: done
- plan:
  - identify the remaining loop-preparation gaps against the harness docs
  - strengthen run outputs with reproducibility snapshots
  - add experiment folder and loop artifact scaffolding
  - add selection/promotion helper scripts for loop decisions
  - update docs and task records after validation
- validation:
  - run compile validation for harness and tests
  - run unittest discovery again
  - sanity-check the new loop scaffolding paths
- feedback / risks:
  - this targets minimum operational readiness, not full production governance completeness
  - final benchmark quality still depends on human-curated expected outputs and dataset expansion
  - minimum loop readiness is in place; remaining work is now quality/depth expansion rather than missing operating primitives

### TASK-2026-04-10-007
- date: 2026-04-10
- owner: Codex
- scope: Move harness gate thresholds into policy files so comparator behavior is driven by explicit repository policy instead of hardcoded constants.
- status: done
- plan:
  - add baseline harness policy files under `harness/policies`
  - update comparator CLI and internals to load thresholds from policy files
  - update tests to cover policy-driven gate behavior
  - refresh README/task records after verification
- validation:
  - run compile validation for harness and tests
  - run unittest discovery again
- feedback / risks:
  - initial policy schema will stay simple and focused on current comparator thresholds
  - later policy growth may require tighter schema coverage
  - current policies cover threshold tuning, not the full merge-gate logic described in the governance docs

### TASK-2026-04-10-006
- date: 2026-04-10
- owner: Codex
- scope: Make the harness comparator category-aware and add critical-split style gate checks using benchmark manifest metadata.
- status: done
- plan:
  - enrich benchmark manifest items with explicit critical flags and make them available in run results
  - carry benchmark item metadata into run results for comparator use
  - extend comparator summary and gate logic with critical-item and category-level checks
  - add unit coverage for the new gate behavior
  - update task logs after verification
- validation:
  - run compile validation for harness and tests
  - run unittest discovery again
- feedback / risks:
  - current smoke benchmark is still too small for strong product decisions, so this remains a lightweight gate
  - category-aware gating depends on benchmark metadata quality
  - critical/category checks are now wired, but the benchmark taxonomy itself still needs deliberate curation

### TASK-2026-04-10-005
- date: 2026-04-10
- owner: Codex
- scope: Enforce schema validation for harness run and comparison outputs so result formats are checked at generation time.
- status: done
- plan:
  - add a lightweight local schema validator for the current JSON schema subset
  - validate `run_result.json` before writing it
  - validate comparison output before writing it
  - add unit tests for valid and invalid payload cases
  - update task logs after verification
- validation:
  - run compile validation for harness and tests
  - run unittest discovery again
- feedback / risks:
  - validator will intentionally support the subset of JSON schema currently used in this repository
  - future schema complexity may require a dedicated validator library
  - current schema checks focus on structure, not semantic constraints such as score ranges or allowed enum values

### TASK-2026-04-10-004
- date: 2026-04-10
- owner: Codex
- scope: Enrich harness run results with config snapshot, code version, and failure summaries so they are usable as merge-gate inputs.
- status: done
- plan:
  - inspect current run result structure and reusable metadata sources
  - add code version capture and config snapshot details to harness run output
  - add structured failure summary fields derived from batch results
  - add unit coverage for the new run result metadata shape
  - update task records after verification
- validation:
  - run compile validation for harness and tests
  - run unittest discovery again
- feedback / risks:
  - git metadata capture should fail soft when the repo state is unavailable
  - this will improve run observability, not yet full schema validation
  - run result metadata is richer now, but schema enforcement and commit-to-run reproducibility checks are still future work

### TASK-2026-04-10-003
- date: 2026-04-10
- owner: Codex
- scope: Populate the smoke benchmark with real local sample inputs and add basic regression gate logic to the harness comparator.
- status: done
- plan:
  - inspect local sample images that can be promoted into benchmark assets
  - copy a small approved smoke set into `benchmarks/datasets/smoke/images`
  - replace placeholder manifest entries with real sample metadata
  - extend harness comparison output with simple promotion/rejection gate signals
  - add or update tests for comparator behavior and update task logs
- validation:
  - verify benchmark image files and manifest paths exist
  - run compile validation for harness and tests
  - run unittest discovery again
- feedback / risks:
  - benchmark expected target text is still provisional until a human-approved golden set is curated
  - current gating will be intentionally simple and should not be mistaken for the final merge gate
  - current smoke benchmark is useful for harness wiring, but it is still too small for promotion-quality decisions

### TASK-2026-04-10-002
- date: 2026-04-10
- owner: Codex
- scope: Create concrete `harness/`, `benchmarks/`, and `tests/` foundations with baseline/candidate/compare/report scripts and initial smoke tests.
- status: done
- plan:
  - inspect current pipeline entrypoints and reusable batch execution pieces
  - add minimal benchmark manifest and harness config/schema/report structure
  - add baseline runner, candidate runner, compare script, and report builder
  - add unit, integration, and regression test skeletons with core contract and pipeline smoke coverage
  - update task records and summarize residual gaps
- validation:
  - verify new directories and scripts exist
  - run lightweight syntax or compile validation
  - run tests that do not require external OCR/model downloads when feasible
- feedback / risks:
  - current runtime depends on heavy OCR/image dependencies, so smoke tests should avoid requiring full external model execution
  - this step creates the operating skeleton first, not a full benchmark automation system
  - benchmark manifests are wired, but real approved smoke images still need to be populated under `benchmarks/datasets/smoke/images/`

### TASK-2026-04-10-001
- date: 2026-04-10
- owner: Codex
- scope: Add mandatory repository work logging with `TASKS.md` and `DONE.md`, and wire the rule into repository guidance.
- status: done
- plan:
  - add root tracking files with a stable template
  - update `AGENTS.md` to require task logging before and after work
  - update `README.md` so human contributors follow the same flow
- validation:
  - confirm the new files exist
  - confirm the workflow is documented in both root guidance files
- feedback / risks:
  - this enforces process by repository convention, not by executable hook
  - future automation can read these files to build stricter gates

---

## Backlog Template

### TASK-YYYY-MM-DD-XXX
- date:
- owner:
- scope:
- status: todo
- plan:
  - item 1
  - item 2
- validation:
  - check 1
  - check 2
- feedback / risks:
  - note 1
