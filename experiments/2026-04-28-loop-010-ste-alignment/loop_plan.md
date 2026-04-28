# Loop Plan

- loop_id: 2026-04-28-loop-010-ste-alignment
- owner: Codex
- date: 2026-04-28
- target: make the current repository state honest and ready for a future generative STE adapter

## Scope

- Review current docs and tests against the desired generative STE direction.
- Clarify that current runtime is classical baseline plus OCR/LLM components, not diffusion/AnyText-style STE.
- Strengthen the STE export manifest contract with a unit test.
- Rerun the Ralph Wiggum smoke harness loop.

## Validation Plan

- Compile `app`, `harness`, `tests`, `benchmarks`, and `experiments`.
- Run full unittest discovery.
- Validate approved smoke manifest.
- Run fresh approved smoke baseline and candidate executions.
- Build comparison, recommendation, and quality/artifact diagnosis outputs.

## Decision Rule

- Promote if docs/tests align with the STE direction and the smoke harness gate still passes.
