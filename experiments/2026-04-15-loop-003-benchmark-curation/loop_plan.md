# Loop Plan

- loop_id: 2026-04-15-loop-003-benchmark-curation
- date: 2026-04-15
- owner: Codex
- theme: replace placeholder smoke benchmark targets with draft values and distinguish draft vs approved readiness
- baseline_version: baseline
- benchmark_set: smoke-v1

## Problem Statement
- smoke benchmark targets were placeholders, so loop 002 could execute operationally but could not support a trustworthy promotion decision

## Hypothesis
- replacing placeholders with draft targets and explicitly marking them as non-approved will make benchmark state more honest and safer for future loops

## Candidate Changes
- candidate_A: curate draft English expected targets for the smoke benchmark
- candidate_B: add explicit benchmark target approval status to readiness logic

## Success Criteria
- smoke manifest contains no placeholder expected targets
- readiness logic still blocks promotion until targets are approved

## Risks
- sample2 expected text is still approximate and needs human approval
