# Loop Plan

- loop_id: 2026-04-10-loop-002-validation-reliability
- date: 2026-04-10
- owner: Codex
- theme: improve validation reliability with duplicate-safe token scoring and broader OCR language mapping
- baseline_version: baseline
- benchmark_set: smoke-v1

## Problem Statement
- close the loop from harness execution to experiment-folder decision artifacts

## Hypothesis
- if baseline/candidate/report/recommendation artifacts land in one loop folder, the Ralph Wiggum loop becomes easier to run repeatedly

## Candidate Changes
- candidate_A: bootstrap experiment folder from harness artifacts
- candidate_B: refine the loop summary after real comparison outputs exist

## Success Criteria
- loop folder exists with plan, report, summary, regression_cases, and winning_cases
- comparison and recommendation artifacts can be copied in when available

## Risks
- this loop improves operational closure, not model quality directly