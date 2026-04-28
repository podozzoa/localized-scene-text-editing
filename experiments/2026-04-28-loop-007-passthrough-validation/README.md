# Experiment Loop

- loop_id: 2026-04-28-loop-007-passthrough-validation
- theme: validate target-script-compatible skipped text as pass-through only when no editable regions exist

This loop removes the false zero-score failure for already-localized headline text while keeping skipped non-editable brand fragments out of validation when editable regions are present.

Gate result: hold. The product behavior improved versus loop 006, but the current candidate run regressed against the baseline run on `sample2.jpg`, so it is not promotion-ready.
