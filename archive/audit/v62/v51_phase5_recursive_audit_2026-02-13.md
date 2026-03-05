# v5.1 Phase 5 Recursive Audit (P4 ETL Guard + C7 Observability)

- Date: 2026-02-13
- Source mandate: `audit/v51.md`
- Scope: `omega_core/omega_etl.py`, `parallel_trainer/run_parallel_backtest_v31.py`

## Recursive Check Against v51.md

1. P4 early-session projection floor raised: PASS  
   Evidence: `omega_core/omega_etl.py:237` uses `lower_bound=0.05`.
2. P4 rationale documented inline: PASS  
   Evidence: `omega_core/omega_etl.py:235` comment block.
3. C7 file-list observability fix: PASS  
   Evidence: `parallel_trainer/run_parallel_backtest_v31.py:689`~`parallel_trainer/run_parallel_backtest_v31.py:692`.
4. Syntax integrity: PASS  
   Evidence: `python3 -m py_compile` succeeded.

## Notes

- 回测报告在 manifest 模式下不再只展示 `data_roots`，避免“看起来用了多个根目录”的误读。
