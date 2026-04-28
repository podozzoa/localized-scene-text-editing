# Loop Plan

- loop_id: 2026-04-28-loop-005-translation-readiness
- date: 2026-04-28
- owner: Codex
- theme: prevent translation fallback from silently passing source-script text
- baseline_version: loop002_baseline
- benchmark_set: smoke-v1

## Problem Statement
- Approved smoke artifacts show `target text script mismatch` because Korean source text can survive as English target text.
- The identity fallback made missing translation backend look like a normal candidate generation path.

## Hypothesis
- If fallback translation returns no candidate for source-script text that requires real translation, the pipeline will expose translation backend unavailability earlier and stop scoring untranslated candidates as valid localization options.

## Candidate Changes
- expose translation backend status in harness run results
- make fallback translation preserve only same-language text and ASCII brand-like tokens
- filter script-incompatible candidates before rewriter scoring

## Success Criteria
- `auto` without a backend returns no English candidate for Hangul source copy
- ASCII brand-like tokens remain pass-through
- run metadata can report `translation_backend.active_provider` and backend availability
- tests protect fallback and candidate filtering behavior

## Risks
- this loop does not create a real translation backend
- fresh OCR-backed harness execution may still be blocked by local Paddle runtime behavior
