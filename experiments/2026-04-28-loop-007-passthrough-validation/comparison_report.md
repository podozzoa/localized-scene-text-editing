# Harness Comparison Report

- baseline_run: loop007_baseline_passthrough_v2
- candidate_run: loop007_candidate_passthrough_v2
- policy_id: gate-default-v1
- baseline_average_quality_score: 1.0000
- candidate_average_quality_score: 0.9167
- average_quality_delta: -0.0833
- baseline_failed: 0
- candidate_failed: 0
- gate_status: reject
- severe_regression_count: 1
- new_failure_count: 0
- category_regression_count: 3
- benchmark_ready_for_promotion: True

## Gate

- candidate average quality score regressed below baseline
- candidate contains severe item-level regressions
- candidate regressed in one or more category averages

## Benchmark Readiness

- item_count: 2
- placeholder_expected_target_count: 0
- non_approved_expected_target_count: 0
- no placeholder expected targets
- all expected targets approved

## Critical Split

- item_count: 1
- baseline_average_score: 1.0000
- candidate_average_score: 1.0000
- average_score_delta: 0.0000

## Category Summary

| category | items | baseline | candidate | delta |
| --- | ---: | ---: | ---: | ---: |
| complex_background | 1 | 1.0000 | 0.8333 | -0.1667 |
| headline | 1 | 1.0000 | 1.0000 | 0.0000 |
| multi_region | 1 | 1.0000 | 0.8333 | -0.1667 |
| simple | 1 | 1.0000 | 1.0000 | 0.0000 |
| smoke | 2 | 1.0000 | 0.9167 | -0.0833 |

| item | baseline | candidate | delta |
| --- | ---: | ---: | ---: |
| sample1.png | 1.0000 | 1.0000 | 0.0000 |
| sample2.jpg | 1.0000 | 0.8333 | -0.1667 |