# Loop Report

- loop_id: 2026-04-28-loop-005-translation-readiness
- theme: prevent translation fallback from silently passing source-script text
- decision: hold

## Summary
- Translation backend status is now available to harness run results.
- `auto` or `identity` fallback no longer returns Hangul text as an English candidate when real translation is required.
- ASCII brand-like text such as `TERRA` and `SALE 50%` still passes through.
- Rewriter scoring now ignores script-incompatible candidates instead of merely penalizing them.

## Evaluation
- fallback Hangul to English candidates: blocked
- ASCII brand-like passthrough: preserved
- unit/regression tests: passing
- approved smoke manifest: valid and promotion-ready

## Blocking Reasons
- this loop improves failure visibility and candidate safety, but does not provide a real translation backend
- fresh OCR-backed harness execution still needs a stable local runtime

## Next Loop
- configure OpenAI-compatible or local translation backend
- rerun approved smoke baseline/candidate artifacts
- verify `sample2.jpg` no longer reports `target text script mismatch` for editable Korean regions
