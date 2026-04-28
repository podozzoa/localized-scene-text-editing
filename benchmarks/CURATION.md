# Benchmark Curation

This repository now blocks automatic promotion when benchmark items still use placeholder expected targets or when expected targets are not yet approved.

## Why

If `expected_targets` contain placeholder text such as `human approved target pending`, the harness can execute, but the resulting scores are not trustworthy enough for promotion decisions.

## Required Curation Steps

1. Open the target benchmark manifest under `benchmarks/manifests/`.
2. Replace placeholder `expected_targets` with human-reviewed target text for each benchmark item.
3. Set `expected_targets_status` for each item.
   - use `draft` while targets are still under review
   - use `approved` only after a human reviewer accepts them
4. Keep category tags and `critical` flags aligned with the intended merge-gate weight of the sample.
5. Re-run baseline and candidate harness comparisons after curation.

## Validation Commands

Generate a machine-readable manifest validation report:

```bash
python harness/validators/benchmark_manifest.py \
  --manifest benchmarks/manifests/smoke_manifest.json \
  --output experiments/2026-04-15-loop-003-benchmark-curation/manifest_validation.json
```

Build a reviewer-facing curation packet:

```bash
python harness/reports/build_curation_packet.py \
  --manifest benchmarks/manifests/smoke_manifest.json \
  --loop-dir experiments/2026-04-15-loop-003-benchmark-curation
```

## Practical Rule

- Placeholder benchmark entries are acceptable for wiring and smoke execution.
- Draft benchmark targets are acceptable for iteration and review.
- Only approved benchmark targets are acceptable evidence for promotion.
