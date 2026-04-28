# Loop Plan

- loop_id: 2026-04-20-loop-004-quality-zero-diagnosis
- date: 2026-04-20
- owner: Codex
- theme: diagnose approved-smoke zero quality scores before changing pipeline behavior
- baseline_version: loop002_baseline
- benchmark_set: smoke-v1

## Problem Statement
- The smoke benchmark is now approved, but both baseline and candidate still report `average_quality_score: 0.0`.
- Promotion readiness is no longer blocked by benchmark governance, so the next blocker is product-quality behavior.

## Hypothesis
- The zero-score result is caused by unchanged Korean target text for English runs and skipped non-editable regions, not by harness comparison logic.

## Candidate Changes
- candidate_A: add harness quality diagnosis aggregation for `98_quality.json` artifacts
- candidate_B: record a loop-level diagnosis before changing translation or editability policy

## Success Criteria
- zero-score causes are visible in machine-readable and markdown artifacts
- diagnosis distinguishes item warnings from region-level warnings
- no product pipeline behavior is changed in this loop

## Risks
- existing artifacts may be stale until a fresh harness run succeeds
- this loop identifies causes but does not yet fix translation or editability behavior
