# Loop Plan

- loop_id: 2026-04-28-loop-007-passthrough-validation
- owner: Codex
- date: 2026-04-28
- target: fix false zero-score validation for target-script-compatible skipped text

## Scope

- Add narrow pass-through validation for skipped text that is already compatible with the target language.
- Do not render skipped text.
- Do not include skipped text in validation when editable regions exist in the same image.
- Preserve the product baseline pipeline order.

## Validation Plan

- Compile `app`, `harness`, `tests`, `benchmarks`, and `experiments`.
- Run full unittest discovery.
- Run approved smoke baseline and candidate harness executions.
- Build comparison, recommendation, and quality diagnosis artifacts.

## Decision Rule

- Accept the code change if zero-score smoke failures are removed without reintroducing target-script mismatch.
- Promote the candidate only if the comparator gate passes.
