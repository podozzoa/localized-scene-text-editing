# Experiment Loop

- loop_id: 2026-04-28-loop-008-run-isolation
- theme: isolate harness run artifacts and reduce translation nondeterminism

This loop fixes the candidate regression observed in loop 007 by making harness runs write image artifacts into run-specific output directories and by lowering OpenAI-compatible translation temperature to deterministic mode.

Gate result: promote.
