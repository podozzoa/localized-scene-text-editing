# Loop Plan

- loop_id: 2026-04-28-loop-006-openai-smoke-run
- date: 2026-04-28
- owner: Codex
- theme: verify approved smoke benchmark with configured OpenAI-compatible translation
- baseline_version: loop006_baseline_openai
- benchmark_set: smoke-v1

## Problem Statement
- Loop 005 made fallback behavior explicit, but the app still needed a real target-language candidate path.
- Harness runners previously did not load `.env`, so configured translation credentials were not guaranteed to affect benchmark runs.

## Hypothesis
- Loading `.env` before harness engine construction will allow `translation_provider=auto` to select OpenAI-compatible translation and eliminate Korean-to-English script mismatches in editable smoke regions.

## Candidate Changes
- load `.env` in harness `execute_manifest`
- run approved smoke baseline and candidate with OpenAI-compatible backend
- compare and diagnose the refreshed artifacts

## Success Criteria
- run results show `translation_backend.active_provider = openai_compatible`
- `sample2.jpg` has no `target text script mismatch`
- approved smoke average quality improves from the previous 0.0 baseline

## Risks
- smoke benchmark still has only two items
- `sample1.png` remains blocked by editability/skipped-region behavior
