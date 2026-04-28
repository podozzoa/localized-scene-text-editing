# Loop Plan

- loop_id: 2026-04-10-loop-001-harness-closure
- date: 2026-04-10
- owner: Codex
- theme: bootstrap a loop-scoped experiment folder from harness artifacts
- baseline_version: baseline
- benchmark_set: smoke-v1

## Problem Statement
- the repository had harness execution pieces, but not a single loop folder that naturally collects plan, summary, report, and promotion artifacts

## Hypothesis
- if the loop folder can be materialized directly from harness outputs, the repository can run repeated Ralph Wiggum loops with less manual drift

## Candidate Changes
- candidate_A: add loop bootstrap script
- candidate_B: instantiate the first loop folder with the narrow harness-closure theme

## Success Criteria
- the first loop folder exists under `experiments/`
- harness output can be copied or summarized into the loop folder
- the loop has plan, summary, report, and case directories

## Risks
- this loop improves operating discipline more than end-user image quality
