# Loop Template

Copy this folder to create a new loop run folder named after the `loop_id`.

Example:

```text
experiments/2026-04-10-render-overflow-01/
```

Template contents:

- `loop_plan.md`: problem statement, hypothesis, candidate changes
- `config_snapshot.json`: runtime, dataset, policy, and version snapshot
- `run_summary.json`: metrics, regressions, decision, and next step
- `report.md`: human-readable summary
- `regression_cases/`: failing cases to preserve
- `winning_cases/`: improved cases to preserve

Keep each loop focused on one problem theme.
