# Loop 008 Report

## Outcome

The loop 007 candidate regression was caused by poor run reproducibility, not by a validated product improvement failure. Harness image artifacts were not fully isolated by run name, and OpenAI-compatible candidate generation used a high temperature that made identical baseline/candidate configs produce different localized candidates.

Loop 008 isolates product debug artifacts under `outputs/harness/<run_name>/...` and lowers OpenAI-compatible translation temperature to deterministic mode.

## Harness Result

- baseline average quality: 1.0000
- candidate average quality: 1.0000
- average delta: 0.0000
- zero-score items: 0
- target script mismatch warnings: 0
- gate status: promote
- promotion status: promote

## Interpretation

The approved smoke benchmark is now stable enough for the next Ralph Wiggum loop: runs are inspectable per variant, target-script validation remains strict, and baseline/candidate comparison no longer fails because of avoidable artifact overwrites or translation sampling noise.
