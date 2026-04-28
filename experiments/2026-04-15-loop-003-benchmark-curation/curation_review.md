# Benchmark Curation Review

- manifest_id: smoke-v1
- item_count: 2
- ready_for_promotion: True
- placeholder_expected_target_count: 0
- non_approved_expected_target_count: 0

## Reviewer Instruction
- Verify each expected target against the source image and intended target market copy.
- If the target is acceptable, change `expected_targets_status` from `draft` to `approved` in the manifest.
- Do not approve approximate marketing copy unless it is acceptable as benchmark evidence.

## Items

| id | image | critical | status | category_tags | expected_targets | reviewer_decision |
| --- | --- | ---: | --- | --- | --- | --- |
| sample1 | benchmarks/datasets/smoke/images/sample1.png | True | approved | smoke, simple, headline | SALE 50% | approved |
| sample2 | benchmarks/datasets/smoke/images/sample2.jpg | False | approved | smoke, complex_background, multi_region | Australia Golden Triangle 100% pure malt<br>This is what a clean lager tastes like!<br>Clean lager TERRA | approved |

## Validation Errors
- none

## Validation Warnings
- none