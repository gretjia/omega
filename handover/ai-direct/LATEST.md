# Latest Status

Current Phase: Vertex Train Running (Evidence Package Ready, Backtest Takeover Armed)
Last Update: 2026-02-19 19:50:18 +0800
Active Train Job: projects/269018079180/locations/us-central1/customJobs/4026903526469795840
Backtest Watcher: running (/tmp/backtest_takeover_aa8abb7.sh)

## Recent Handover Entries
- [20260219_195018_v60_training_audit_package.md](entries/20260219_195018_v60_training_audit_package.md) - Submit-ready v60 training evidence package with raw sources/logs.
- [20260219_155539_flexible_load_audited_design.md](entries/20260219_155539_flexible_load_audited_design.md) - Audited flexible-load contract and rollout status.
- [20260218_084500_migration_to_central1.md](entries/20260218_084500_migration_to_central1.md) - Migration and quota fixes.

## Approved Flexible-Load Contract
- Worker policy: workers=0, workers_min=2, workers_cpu_frac=0.75, cpu low/high=55/88, mem headroom=24GB, est mem=3GB.
- Backtest machine ladder: n2-standard-80 -> n2-standard-64 -> n2-standard-48 -> n2-standard-32.
- Governance: dual recursive audit required before promoting new defaults.

## Immediate Action Required
- Continue watcher until train succeeds and takeover submits backtest.
- After train/backtest completion, append evidence delta into a new handover entry for auditor handoff.
