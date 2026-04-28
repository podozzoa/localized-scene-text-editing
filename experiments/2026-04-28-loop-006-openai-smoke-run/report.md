# Loop Report

- loop_id: 2026-04-28-loop-006-openai-smoke-run
- theme: verify approved smoke benchmark with configured OpenAI-compatible translation
- decision: promote

## Summary
- Harness runners now load `.env` before engine construction.
- Both approved smoke runs selected `openai_compatible` translation.
- Average quality improved from the prior known `0.0` state to `0.5`.
- `sample2.jpg` now scores `1.0` and no longer reports `target text script mismatch`.

## Evaluation
- baseline_average_quality_score: 0.5000
- candidate_average_quality_score: 0.5000
- average_quality_delta: 0.0000
- benchmark_ready_for_promotion: true
- zero_score_item_count: 1
- target text script mismatch: 0
- non-editable region skipped: 5

## Blocking Reasons
- none for translation readiness
- `sample1.png` still scores `0.0` because the detected `SALE 50%` region is skipped as non-editable

## Next Loop
- inspect editability and role classification for `SALE 50%`
- preserve brand-like text while allowing benchmark-relevant headline text to contribute to quality
- rerun approved smoke artifacts after the editability fix
