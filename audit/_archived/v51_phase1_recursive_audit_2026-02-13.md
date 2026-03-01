# v5.1 Phase 1 Recursive Audit (P0 Kernel)

- Date: 2026-02-13
- Source mandate: `audit/v51.md`
- Scope: `omega_core/kernel.py`

## Recursive Check Against v51.md

1. P0 symmetric SRL gate: PASS  
   Evidence: `omega_core/kernel.py:205` uses `pl.col("srl_resid").abs() > ...`.
2. P0 symmetric topology gate: PASS  
   Evidence: `omega_core/kernel.py:206` uses `pl.col("topo_area").abs() > ...`.
3. P0 damper direction semantics: PASS  
   Evidence: `omega_core/kernel.py:211` sets `direction = -sign(srl_resid)`.
4. Runtime smoke for direction sign: PASS  
   Evidence: one-row smoke run returned positive residual with `direction=-1.0`.

## Notes

- `omega_core/trainer.py` remains file-locked (system-level permission anomaly) and is handled in subsequent phases via compatible module redirection.
