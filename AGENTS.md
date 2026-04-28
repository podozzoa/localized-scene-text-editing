# AGENTS.md

## Mission

This repository is a **harness-first Localized Scene Text Editing project**.

The long-term target is not a one-off demo. The target is a repeatable service that can:

- localize poster or scene text into a target market language,
- preserve the original design as much as possible,
- validate output quality with explicit gates,
- evolve through repeated agent loops,
- separate product-track work from research-track work,
- stay maintainable over a long project horizon.

Codex must therefore optimize for **stable progress under harness control**, not for flashy one-shot rewrites.

---

## Product Goal

Build and ship a service that performs:

1. text detection,
2. OCR recognition,
3. localization / copy rewriting,
4. mask construction,
5. background restoration,
6. style-aware rendering,
7. validation and scoring,
8. optional STE research-track comparison.

The key success condition is:

> localized output improves target-market usability **without visibly damaging the original poster design**.

---

## Current Baseline

Current implemented baseline in this repo is a classical pipeline:

`detect -> recognize -> rewrite -> restore -> render -> validate`

Relevant modules:

- `app/domain/`: pure contracts, models, interfaces
- `app/infra/`: OCR, translation, rendering, inpainting, style estimation
- `app/pipeline/`: orchestration and quality validation
- `app/usecases/`: batch run, debug artifacts, STE dataset export
- `app/main.py`: CLI entrypoint

This baseline is the **reference path**. Do not casually break it.

---

## Non-Negotiable Rules

### 1. Preserve pipeline integrity
Do not reorder the main flow unless the task explicitly requires a controlled experiment.

Baseline order:

- detect
- recognize
- rewrite
- restore
- render
- validate

### 2. Product track and research track must stay separated
- Product-track code must remain stable and mergeable.
- Research-track code may experiment, but must not silently replace the product baseline.
- STE or diffusion experiments belong behind adapters, exporters, or explicit experiment paths.

### 3. Contracts are more important than convenience
Do not introduce ad-hoc dictionaries or hidden coupling where typed models or explicit payload schemas should exist.

Protect the meaning of:

- OCR region outputs
- prepared edit context
- style estimation outputs
- render instructions
- quality reports
- benchmark / harness manifests

### 4. Incremental changes only
Prefer small, testable, reversible changes.
Avoid “rewrite entire subsystem” behavior unless explicitly requested.

### 5. Maintain debug visibility
If a change makes diagnosis harder, it is probably the wrong change.
Prefer preserving or extending intermediate artifacts and diagnostics.

### 6. Never optimize away validation
This project only becomes trustworthy if changes stay measurable.
Do not remove checks, artifact outputs, or quality reports just to simplify execution.

---

## How Codex Must Operate

When working in this repo, Codex should follow this order:

1. Read `README.md`
2. Read `docs/ste_experiment_design.md`
3. Read the harness docs under `docs/harness/`
4. Inspect the affected modules only after understanding the harness constraints
5. Make the smallest viable change
6. Keep CLI behavior backward compatible unless the task explicitly changes it
7. Prefer adding tests, validation hooks, artifact logging, or structured outputs over silent logic changes

### Mandatory Work Logging
- `TASKS.md` and `DONE.md` are mandatory operating files at the repository root.
- Before starting any meaningful task, create or update an entry in `TASKS.md`.
- A task entry must include scope, status, plan, validation, and feedback/risks.
- While working, keep the task status current as `todo`, `in_progress`, `blocked`, or `done`.
- When a task is completed, update `TASKS.md` and append a completion note to `DONE.md`.
- Do not perform silent work that is not reflected in these files.
- If validation is skipped, the reason must be written explicitly in the task record.

---

## Required Harness Documents

These files define the intended operating model and should guide future changes:

- `docs/harness/01_requirements_and_target.md`
- `docs/harness/02_harness_engineering_blueprint.md`
- `docs/harness/03_ralph_wiggum_loop_guide.md`
- `docs/harness/04_benchmark_manifest_template.md`
- `docs/harness/05_agent_prompt_templates.md`
- `docs/harness/06_merge_gate_checklist.md`
- `docs/harness/07_maintenance_agent_blueprint.md`
- `docs/harness/08_code_convention_policy.md`
- `docs/harness/09_architecture_guard_rules.md`
- `docs/harness/10_autofix_policy.md`
- `docs/harness/11_repo_governance_schedule.md`
- `docs/harness/12_maintenance_gate_checklist.md`

If there is conflict between a quick hack and these documents, prefer the harness-aligned direction.

---

## Agent Roles

Codex should assume the repository will eventually run with multiple specialized agents.

### Conductor Agent
- decomposes work,
- decides which sub-agent should act,
- gathers results,
- applies merge gate logic.

### Feature Agent
- implements scoped improvements,
- avoids broad architectural drift,
- keeps output contracts stable.

### Validation Agent
- checks quality outputs,
- compares before/after behavior,
- flags regression risk.

### STE Research Agent
- works on research-track integrations,
- uses exporter / adapter style boundaries,
- must not overwrite baseline product flow.

### Maintenance Agent
- checks convention, architecture, drift, dead code, and autofix-safe issues,
- must respect protected paths and autofix policy.

---

## Protected Areas

Changes touching the following areas must be treated as high risk:

- domain contracts and core models
- validation logic and quality scoring meaning
- benchmark / golden / manifest semantics
- harness policies and merge gate rules
- CLI public behavior

Do not change these casually. When changes are required, document the reason and impact.

---

## Coding Direction

### Architecture
- Keep domain logic pure where possible.
- Do not leak infra concerns into domain models.
- Prefer explicit interfaces over hidden side effects.
- Keep product code readable and decomposable.

### Maintainability
- Keep functions focused.
- Avoid giant god-functions.
- Avoid silent fallback chains that hide failure reasons.
- Favor explicit warnings and structured result payloads.

### Image / localization specifics
- Do not hardcode text for specific posters.
- Do not assume axis-aligned perfect boxes only.
- Do not treat localization as literal translation only.
- Layout fit, readability, and design preservation matter more than literal word-by-word output.

---

## Change Priorities

Preferred improvements, in rough order:

1. validation reliability,
2. benchmark and harness integration,
3. renderer quality,
4. inpainting quality,
5. localization candidate quality,
6. style estimation quality,
7. batch and reporting robustness,
8. STE research adapters.

This priority order is intentional. Better governance beats unmeasured feature growth.

---

## What Not To Do

Unless explicitly requested, do **not**:

- build a web UI,
- add a database,
- rewrite the entire pipeline,
- replace typed structures with loose ad-hoc dict sprawl,
- mix research experiments directly into the baseline path,
- remove artifact outputs that help validation,
- perform speculative optimization before quality is controlled.

---

## Definition of Good Progress

A change is good if most of the following are true:

- baseline pipeline still runs,
- output artifacts remain inspectable,
- behavior is easier to validate than before,
- architecture drift did not increase,
- the change is reversible,
- the repo is closer to harness-driven iteration,
- product and research paths are clearer, not blurrier.

---

## Practical Execution Notes

### Environment
- Python 3.11 or 3.12 is the intended runtime.
- Python 3.13 is not the supported target for the current stack.

### Fonts
- Font files are intentionally not bundled.
- Use user-provided fonts through `--font-path`.

### CLI stability
Current public CLI entrypoint is:

```bash
python -m app.main
```

Maintain this unless a task explicitly requests a breaking change.

---

## Final Operating Principle

This repository should evolve by repeating a disciplined loop:

- define target,
- make scoped change,
- run harness,
- compare against baseline,
- accept or reject,
- repeat.

Codex should act like an engineer inside that loop, not like a demo generator.
