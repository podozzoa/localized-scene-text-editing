# Loop Plan

- loop_id: 2026-04-28-loop-008-run-isolation
- owner: Codex
- date: 2026-04-28
- target: remove candidate-only smoke regression without weakening validation or benchmark gates

## Scope

- Compare baseline and candidate config/run artifacts.
- Isolate run output directories so debug images and `98_quality.json` files are not overwritten.
- Reduce translation nondeterminism in OpenAI-compatible candidate generation.
- Keep benchmark expected targets and gate policy unchanged.

## Validation Plan

- Compile `app`, `harness`, `tests`, `benchmarks`, and `experiments`.
- Run full unittest discovery.
- Validate the approved smoke manifest.
- Run fresh baseline and candidate smoke harness runs.
- Build comparison, recommendation, and quality diagnosis artifacts.

## Decision Rule

- Promote only if the candidate no longer regresses on `sample2.jpg` and the default comparator gate passes.
