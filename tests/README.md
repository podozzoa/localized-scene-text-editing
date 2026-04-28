# Tests

This directory holds repository tests split by intent:

- `unit/`: contract and pure logic checks
- `integration/`: low-cost workflow integration checks
- `regression/`: smoke tests that protect the baseline path

Keep research-only tests out of this tree unless they are intended to gate the product path.
