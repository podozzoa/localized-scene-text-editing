# Loop Report

- loop_id: 2026-04-20-loop-004-quality-zero-diagnosis
- theme: diagnose approved-smoke zero quality scores before changing pipeline behavior
- decision: hold

## Summary
- Existing loop 002 baseline and candidate artifacts both score `0.0`.
- The score is not blocked by benchmark readiness anymore.
- Region artifacts show that the product path is not producing English target text for editable Korean regions.

## Evaluation
- zero_score_item_count: 2
- region_count: 8
- zero_score_region_count: 3
- non-editable region skipped: 5
- target text script mismatch: 3

## Diagnosis
- `sample1.png` contains only a skipped non-editable region, so item-level quality remains zero despite a high region confidence.
- `sample2.jpg` has three editable Korean regions whose `target_text` remains Korean during an English run, producing `target text script mismatch`.
- Baseline and candidate diagnosis are identical, so the validation reliability change did not create a new regression.

## Blocking Reasons
- approved smoke benchmark still has zero product-quality signal because translation/editability behavior is not producing target-language editable text.
- fresh approved baseline rerun exited with code 1 before writing a `loop004_baseline_approved` run bundle.

## Next Loop
- inspect rewrite/translation provider fallback behavior
- add a candidate fix that prevents target-lang runs from silently keeping source-script text for editable regions
- rerun fresh baseline and candidate artifacts after the local OCR runtime is stable
