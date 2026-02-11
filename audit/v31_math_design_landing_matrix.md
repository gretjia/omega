# OMEGA v31 Math Design Landing Matrix

Date: 2026-02-07  
Scope: v31 code path + v31 training artifacts only

## Source Lock

- `/Volumes/desktop-41jidl2/Omega_vNext/omega_v3_core/omega_math_core.py`
- `/Volumes/desktop-41jidl2/Omega_vNext/omega_v3_core/kernel.py`
- `/Volumes/desktop-41jidl2/Omega_vNext/omega_v3_core/trainer.py`
- `/Volumes/desktop-41jidl2/Omega_vNext/config.py`
- `/Volumes/desktop-41jidl2/Omega_vNext/audit/_v31_final_weight_snapshot.csv`
- `/Volumes/desktop-41jidl2/Omega_vNext/audit/_v31_checkpoint_coef_trace.csv`

## Summary Verdict

1. The v31 mathematical design is fully implemented at the computation layer.
2. Not all computed math states enter the model as trainable features.
3. Current model behavior is dominated by mean reversion, with SRL/Topology/Epiplexity as secondary contributors.
4. The local bottleneck is not "missing math"; it is "partial landing of math into learning channels."

## A. Formula -> Code -> Training -> Weight -> Action Matrix

| ID | Math module | Core formula or rule | Code anchor | Training landing | v31 evidence | Status | Minimal action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M1 | Inverse SRL residual | `R_t = dP - sign(Q) * Y_t * sigma_eff * sqrt(|Q|/D_eff)` | `omega_math_core.py:57-81`, `kernel.py:75-83` | In `feature_cols` | `srl_resid = -0.013993` | Effective | Keep; tune only thresholds, not formula |
| M2 | Adaptive Y recursion | If `epiplexity < peace_threshold` and `|Q| > Q_min`, update `Y` by EMA | `kernel.py:84-87` | Computed, not in `feature_cols` | No direct weight | Partial landing | Add optional feature flag experiment (not default) |
| M3 | Epiplexity (zlib) | `E = 4r(1-r)`, `r = |zlib(symbols)| / |symbols|` | `omega_math_core.py:17-35`, `kernel.py:72` | In gate + in `feature_cols` | `epiplexity = +0.013554`; sign positive in 57/57 checkpoints | Effective and stable | Keep zlib as baseline |
| M4 | Holographic topology area | Signed shoelace area in normalized `(price, cum_ofi)` path | `omega_math_core.py:124-154`, `kernel.py:73` | In gate + in `feature_cols` | `topo_area = +0.000045` (near zero) | Weak landing | P0: recover directional channel with minimal ablation |
| M5 | Holographic topology energy | Path length in normalized `(price, cum_ofi)` path | `omega_math_core.py:124-154`, `kernel.py:73` | In gate/filter + in `feature_cols` | `topo_energy = +0.017790`; sign positive in 89.5% checkpoints | Effective | Keep; use as topology backbone |
| M6 | Spoofing filter | `spoof_ratio = cancel / (trade + 1)` and require `< spoofing_ratio_max` | `kernel.py:88-90`, `kernel.py:116` | Gate only (not feature) | Enabled when columns exist; trainer warns when missing | Gate-only landing | Add fail-fast data schema check in production runs |
| M7 | Signal synthesis gate | Strict conjunction of 5 inequalities | `kernel.py:111-117` | Used by structural sampling | Directly affects sample composition | Effective | Keep strict form; tune thresholds only via config |
| M8 | Label engineering | `ret_k = fwd_change/close_abs`; label by `|ret_k| > k * sigma_ret` | `trainer.py:96-114` | Defines target `direction_label` | Full v31 run uses this label path | Effective | Keep as canonical label function |
| M9 | Robust transforms | Winsor + signed-log1p on selected heavy-tail features | `trainer.py:128-138`, `config.py:646-654` | Pre-feature transform | `topo_area` may be over-compressed | Possible over-regularization | P0 ablation on `topo_area` transform only |
| M10 | Sample weighting | `weight = log1p(abs(topo_area))` | `trainer.py:268-273` | Training loss weighting | Single-channel topology weighting | Narrow weighting channel | P1 compare with simple composite topology weight |
| M11 | DoD audit metrics | Topo_SNR, Orthogonality, Vector_Alignment thresholds | `trainer.py:401-436`, `config.py:616-627` | Audit/evaluation, not optimization objective | Works as validation gate | Audit-only landing | Keep as separate governance layer |
| M12 | Runtime parameter override | `TARGET_FRAMES_DAY`, `INITIAL_Y` from production config | `config.py:687-719` | Runtime adaptation | Applied if override file exists | Effective | Log override provenance into audit each run |

## B. Final v31 Feature Weights (Checkpoint `31793682`)

Source: `/Volumes/desktop-41jidl2/Omega_vNext/audit/_v31_final_weight_snapshot.csv`

| Rank | Feature | Weight | Interpretation |
| --- | --- | --- | --- |
| 1 | `price_change` | `-0.357560` | Strong mean-reversion dominance |
| 2 | `net_ofi` | `-0.055471` | Flow exhaustion / liquidity absorption effect |
| 3 | `sigma_eff` | `+0.032207` | Volatility regime expansion |
| 4 | `topo_energy` | `+0.017790` | Structural activity contributes positively |
| 5 | `bar_duration_ms` | `-0.017600` | Time-scale regime effect |
| 6 | `srl_resid` | `-0.013993` | Inverse SRL alignment is active |
| 7 | `epiplexity` | `+0.013554` | Complexity premium is active |
| 8 | `depth_eff` | `+0.008830` | Liquidity depth context is secondary |
| 9 | `topo_area` | `+0.000045` | Directional topology channel is almost inactive |

## C. Weight Sign Stability (57 checkpoints)

Source: `/Volumes/desktop-41jidl2/Omega_vNext/audit/_v31_weight_sign_stability.csv`

- `w_epiplexity`: positive ratio `1.000000`
- `w_price_change`: negative ratio `1.000000`
- `w_srl_resid`: negative ratio `0.877193`
- `w_topo_energy`: positive ratio `0.894737`

Interpretation:

1. Epiplexity and price-reversion directions are structurally stable, not random artifacts.
2. SRL residual and topology energy were noisy early, then converged toward final expected signs.
3. Topology "energy" is stable enough; topology "direction area" is the main weak point.

## D. Landing Coverage (Kernel Outputs)

Kernel outputs (`11`):  
`price_change`, `sigma_eff`, `depth_eff`, `epiplexity`, `topo_area`, `topo_energy`, `srl_resid`, `adaptive_y`, `spoof_ratio`, `is_signal`, `direction`

Directly used as model features (`7/11`):  
`price_change`, `sigma_eff`, `depth_eff`, `epiplexity`, `topo_area`, `topo_energy`, `srl_resid`

Gate/filter only (`2/11`):  
`spoof_ratio`, `is_signal`

Not in current training objective (`2/11`):  
`adaptive_y`, `direction`

Conclusion:

- The math system is implemented, but learning objective coverage is selective.
- v31 is mathematically valid and operational, while still leaving headroom for targeted local upgrades.

## E. Less-is-More Upgrade Plan

### P0 (keep system lean, high ROI)

1. Run a single-variable ablation for `topo_area` channel only.
2. Keep all formulas fixed; only test transform/weighting knobs in `config.py`.
3. Acceptance rule: improve `|w_topo_area|` from near-zero without degrading DoD metrics.

### P1 (optional feature landing)

1. Add config flags for `adaptive_y` and `spoof_ratio` as optional features.
2. Keep defaults off; enable only in controlled A/B runs.
3. Promote only if out-of-sample quality and DoD both improve.

### P2 (governance, not extra complexity)

1. Freeze this matrix as a release checkpoint artifact.
2. Require each future version to update only changed rows, not rewrite the framework.
3. This preserves creativity in model evolution while keeping mathematical traceability.

