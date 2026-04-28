# Loop Plan

- loop_id: 2026-04-28-loop-009-artifact-completeness
- owner: Codex
- date: 2026-04-28
- target: make missing debug/quality artifacts visible before renderer-quality work

## Scope

- Define the current required per-item artifact contract.
- Add harness-level artifact completeness aggregation.
- Include artifact completeness in run notes and diagnosis reports.
- Keep `05_rendered_*` as an observed count, not a required artifact, because some images have no editable regions.

## Validation Plan

- Compile `app`, `harness`, `tests`, `benchmarks`, and `experiments`.
- Run full unittest discovery.
- Validate approved smoke manifest.
- Run fresh approved smoke baseline and candidate executions.
- Build comparison, recommendation, and quality/artifact diagnosis outputs.

## Decision Rule

- Promote only if smoke score does not regress and required artifact missing count is zero.
