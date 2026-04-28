# Loop 007 Report

## Outcome

The pass-through validation change fixed the `sample1.png` false zero-score case. A target-script-compatible skipped headline such as `SALE 50%` can now satisfy validation when the image has no editable regions.

The rule is intentionally narrow: skipped text is only added to expected validation text when there are no editable regions. This prevents non-editable brand fragments in mixed images from diluting the expected target list.

## Harness Result

- baseline average quality: 1.0000
- candidate average quality: 0.9167
- average delta: -0.0833
- zero-score items: 0
- target script mismatch warnings: 0
- gate status: reject
- promotion status: hold

## Interpretation

This loop improves product validation behavior compared with loop 006, where `sample1.png` scored `0.0`. It does not promote the current candidate variant because `sample2.jpg` regressed against baseline.

The next loop should isolate the candidate-vs-baseline difference for `sample2.jpg` before attempting renderer or localization-quality changes.
