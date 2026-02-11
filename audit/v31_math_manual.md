# OMEGA v31 Mathematical Manual (Machine-Precise)

## 0. Scope and Source Lock

This document is derived **only** from:

1. `omega_v3_core/kernel.py`
2. `omega_v3_core/omega_math_core.py`
3. `config.py` (L2/v3 sections)

No formula, threshold, or execution step is introduced from external text.

Source line anchors:

- Kernel recursion and signal gate: `omega_v3_core/kernel.py:23-121`
- Public kernel API: `omega_v3_core/kernel.py:124-170`
- Math kernels: `omega_v3_core/omega_math_core.py:17-183`
- L2 config classes and runtime override: `config.py:519-718`

---

## 1. Deterministic Execution Order (Exact)

For each file path `path`, `run_l2_kernel(path, cfg, initial_y, target_frames)` executes:

1. `frames = build_l2_frames(path, cfg, target_frames)`
2. `frames = _apply_recursive_physics(frames, cfg, initial_y)`
3. `signals = frames.filter(is_signal == True)`
4. return `(frames, signals)`

Inside `_apply_recursive_physics` for each row:

1. read `trace`, `ofi_list`, `open`, `close`, `sigma`, `depth`, `net_ofi`, `trade_vol`, `cancel_vol`
2. compute `price_change = close - open`
3. robustify `sigma`, `depth` to `sigma_eff`, `depth_eff`
4. compute `epiplexity = calc_epiplexity(trace, cfg.epiplexity)`
5. compute `(topo_area, topo_energy) = calc_holographic_topology(trace, ofi_list)`
6. compute `(srl_resid, implied_y) = calc_physics_state(...)`
7. if update condition holds, recursively update `current_y`
8. compute `spoof_ratio = cancel_vol / (trade_vol + 1.0)`
9. write augmented row fields
10. after loop, vectorized signal predicate generates `is_signal`, `direction`

---

## 2. Symbols and Data Mapping

- $p_t$ := `trace[t]`
- $o_t$ := `ofi_list[t]`
- $q_t$ := cumulative OFI, $q_t = \sum_{i=1}^{t} o_i$
- $\Delta P$ := `close - open`
- $\sigma$ := `sigma`
- $\sigma_{eff}$ := $\max(\sigma, \sigma_{floor})$
- $D$ := `depth`
- $D_{eff}$ := $\max(D, D_{floor})$
- $Q$ := `net_ofi`
- $Y_t$ := current recursive SRL coefficient (`current_y`)
- $\hat Y_t$ := implied SRL coefficient from inverse mapping (`implied_y`)
- $R_t$ := SRL residual (`srl_resid`)
- $A_t$ := signed topology area (`topo_area`)
- $E_t$ := topology path energy (`topo_energy`)
- $\rho_t$ := spoof ratio (`spoof_ratio`)

---

## 3. Mathematical Operators (Exact from Code)

### 3.1 Epiplexity

From `calc_epiplexity(trace, cfg)`:

Given array $\mathbf p=(p_1,\dots,p_n)$.

If $n < n_{min}$ (`min_trace_len`), return fallback $f_0$ (`fallback_value`).

1. Difference sequence:

$$
\Delta p_t = p_t - p_{t-1},\quad t=2,\dots,n.
$$

2. Scale:

$$
s = \max\left(\operatorname{std}(\Delta p),\ \varepsilon_s\right).
$$

3. Threshold:

$$
\tau = c_{sax} \cdot s.
$$

4. 3-state symbolization:

$$
z_t=
\begin{cases}
1, & \Delta p_t > \tau\\
-1, & \Delta p_t < -\tau\\
0, & \text{otherwise}
\end{cases}
$$

5. Byte serialization of $\mathbf z$; if byte length $< b_{min}$ (`min_bytes`), return $f_0$.

6. Compression ratio:

$$
r = \frac{|\operatorname{zlib}(\mathbf z;\ \text{level}=\ell)|}{|\mathbf z|}.
$$

7. Output:

$$
\mathcal E = 4r(1-r).
$$

No additional normalization or clipping is applied.

---

### 3.2 SRL residual (vector form)

From `calc_srl_residual(net_ofi, price_change, depth, sigma, cfg)`:

$$
D_{eff} = \max(D, D_{floor}),\quad \sigma_{eff}=\max(\sigma,\sigma_{floor}),\quad q=|Q|.
$$

Predicted impact:

$$
I_{pred} = Y \cdot \sigma_{eff} \cdot \sqrt{\frac{q}{D_{eff}}} \cdot \operatorname{sign}(Q).
$$

Residual:

$$
R = \Delta P - I_{pred}.
$$

Here $Y$ is `cfg.y_coeff` in this vector helper.

---

### 3.3 Physics state (scalar recursive form)

From `calc_physics_state(price_change, sigma, net_ofi, depth, current_y, cfg)`:

$$
D_{eff}=\max(D,D_{floor}),\quad \sigma_{eff}=\max(\sigma,\sigma_{floor}).
$$

Raw impact scale:

$$
I_{raw} = \sigma_{eff}\sqrt{\frac{|Q|}{D_{eff}}}.
$$

Theoretical impact under current recursion state $Y_t$:

$$
I_{theory} = \operatorname{sign}(Q)\cdot Y_t\cdot I_{raw}.
$$

Residual:

$$
R_t = \Delta P - I_{theory}.
$$

Implied $Y$:

$$
\hat Y_t=
\begin{cases}
\dfrac{|\Delta P|}{I_{raw}}, & I_{raw}>10^{-9}\\
Y_t, & I_{raw}\le 10^{-9}
\end{cases}
$$

Output tuple is `(R_t, \hat Y_t)`.

---

### 3.4 Holographic topology

From `calc_holographic_topology(trace, ofi_list)`:

If length $<2$, return $(0,0)$.

1. Build cumulative OFI trajectory:

$$
q_t = \sum_{i=1}^t o_i.
$$

2. Construct 2D path $(x_t,y_t)=(p_t,q_t)$ and truncate to common length $n$.

3. Standardization:

$$
x_t \leftarrow \frac{x_t-\mu_x}{\sigma_x+10^{-9}},\quad
y_t \leftarrow \frac{y_t-\mu_y}{\sigma_y+10^{-9}}.
$$

4. Signed area:

$$
A = \frac{1}{2}\sum_{t=1}^{n-1}\left(x_t y_{t+1}-x_{t+1}y_t\right).
$$

5. Energy (path length):

$$
E = \sum_{t=1}^{n-1}\sqrt{(x_{t+1}-x_t)^2+(y_{t+1}-y_t)^2}.
$$

Output tuple is `(A, E)`.

---

### 3.5 Topo-SNR from traces

From `topo_snr_from_traces(traces, cfg, epi_cfg)`:

Given trace set $\mathcal T = \{T_i\}_{i=1}^N$.

1. Real epiplexity values:

$$
\mathcal E_i^{real} = \operatorname{Epiplexity}(T_i).
$$

2. Shuffled null values:

For each shuffle round $k=1..K$ (`n_shuffle`) and each trace $T_i$, randomly permute indices to get $\pi_k(T_i)$ and compute:

$$
\mathcal E_{ik}^{shuf} = \operatorname{Epiplexity}(\pi_k(T_i)).
$$

3. If number of shuffled values $< m_{min}$ (`min_shuffles`), return NaN.

4. Z-score:

$$
\text{TopoSNR} = \frac{\mu_{real}-\mu_{shuf}}{\max(\sigma_{shuf},\epsilon_{std})}.
$$

---

## 4. Recursive Kernel Dynamics

### 4.1 Input sanitization

For each row in `_apply_recursive_physics`:

- if `sigma` not finite: set to `0.0`
- if `depth` not finite: set to `0.0`
- then floor:

$$
\sigma_{eff}=\max(\sigma,\sigma_{floor}),\quad D_{eff}=\max(D,D_{floor}).
$$

### 4.2 Adaptive $Y$ update

Update trigger:

$$
\mathcal E_t < \theta_{peace} \quad \land \quad |Q_t| > Q_{min}.
$$

If triggered:

$$
\tilde Y_t = \operatorname{clip}(\hat Y_t, Y_{min}, Y_{max}),
$$

$$
Y_{t+1} = (1-\alpha)Y_t + \alpha\tilde Y_t.
$$

Else:

$$
Y_{t+1}=Y_t.
$$

`adaptive_y` stored in row is the post-update `current_y`.

### 4.3 Spoof ratio

$$
\rho_t = \frac{V^{cancel}_t}{V^{trade}_t + 1}.
$$

---

## 5. Final Signal Predicate (Exact Kernel Boolean)

Vectorized predicate in `kernel.py:111-117`:

$$
\text{is\_signal}_t = \mathbf 1\Big[
(\mathcal E_t > \theta_{peace})
\land (R_t < -k_\sigma\sigma_{eff,t})
\land (A_t > A_{min})
\land (E_t > k_E\sigma_{eff,t})
\land (\rho_t < \rho_{max})
\Big].
$$

Direction column:

$$
\text{direction}_t = \operatorname{sign}(A_t).
$$

Important code fact: gate uses `A_t > A_min` (not $|A_t| > A_{min}$).

---

## 6. Parameterization from `config.py` (Used in Above Equations)

### 6.1 `L2SRLConfig`

- `y_coeff = 0.75`
- `sigma_floor = 1e-12`
- `depth_floor = 1.0`
- `y_min = 0.1`
- `y_max = 5.0`
- `y_ema_alpha = 0.05`

### 6.2 `L2EpiplexityConfig`

- `min_trace_len = 10`
- `sax_scale_mult = 0.5`
- `scale_eps = 1e-9`
- `compress_level = 6`
- `min_bytes = 8`
- `fallback_value = 0.0`

### 6.3 `L2SignalConfig`

- `epiplexity_min = 0.4` (not directly used in boolean gate if `peace_threshold` exists)
- `peace_threshold = 0.35`
- `srl_resid_sigma_mult = 2.0`
- `topo_area_min_abs = 1e-9`
- `topo_energy_sigma_mult = 10.0`
- `spoofing_ratio_max = 2.5`
- `min_ofi_for_y_update = 100.0`

### 6.4 `L2TopoSNRConfig`

- `n_shuffle = 100`
- `seed = 1337`
- `std_floor = 1e-12`
- `min_shuffles = 10`

### 6.5 Runtime override (`load_l2_pipeline_config`)

From `model_audit/production_config.json`, key `AUTO_LEARNED_PARAMS`:

- if `TARGET_FRAMES_DAY` exists:
  - set `volume_clock.daily_volume_proxy_div = TARGET_FRAMES_DAY`
  - force `volume_clock.dynamic_bucket_size = True`
- if `INITIAL_Y` exists:
  - set `srl.y_coeff = INITIAL_Y`

No other mathematical parameter is overridden in this loader.

---

## 7. Full Derivation Chain for One Row

Given row state at step $t$ and current $Y_t$:

1. $\Delta P_t = close_t - open_t$
2. $\sigma_{eff,t}=\max(\sigma_t,\sigma_{floor})$
3. $D_{eff,t}=\max(D_t,D_{floor})$
4. $\mathcal E_t=\operatorname{Epiplexity}(trace_t)$
5. $(A_t,E_t)=\operatorname{HoloTopo}(trace_t, ofi\_list_t)$
6. $(R_t,\hat Y_t)=\operatorname{PhysicsState}(\Delta P_t,\sigma_{eff,t},Q_t,D_{eff,t},Y_t)$
7. $Y_{t+1}$ by update rule in Section 4.2
8. $\rho_t=V^{cancel}_t/(V^{trade}_t+1)$
9. apply Section 5 predicate to get `is_signal_t`
10. `direction_t = sign(A_t)`

The row output stored by kernel is:

- `price_change = ΔP_t`
- `sigma_eff = σ_eff,t`
- `depth_eff = D_eff,t`
- `epiplexity = \mathcal E_t` (epiplexity scalar)
- `topo_area = A_t`
- `topo_energy = E_t` (topology energy symbol, not epiplexity)
- `srl_resid = R_t`
- `adaptive_y = Y_{t+1}`
- `spoof_ratio = ρ_t`
- `is_signal`, `direction`

---

## 8. Non-ambiguous Edge Conditions

1. `frames.height == 0` returns immediately.
2. Non-finite `sigma` or `depth` are set to `0.0` before floor operation.
3. For epiplexity:
   - short trace or short byte sequence returns fallback.
4. For inverse SRL:
   - if $I_{raw}\le10^{-9}$, implied Y reuses current Y.
5. Signal gate is strict conjunction (`&`) of five inequalities.

---

## 9. Machine Assertions (for automated recursive check)

```json
{
  "source_lock": {
    "kernel": "omega_v3_core/kernel.py",
    "math_core": "omega_v3_core/omega_math_core.py",
    "config": "config.py"
  },
  "constants": {
    "L2SRLConfig": {
      "y_coeff": 0.75,
      "sigma_floor": 1e-12,
      "depth_floor": 1.0,
      "y_min": 0.1,
      "y_max": 5.0,
      "y_ema_alpha": 0.05
    },
    "L2EpiplexityConfig": {
      "min_trace_len": 10,
      "sax_scale_mult": 0.5,
      "scale_eps": 1e-9,
      "compress_level": 6,
      "min_bytes": 8,
      "fallback_value": 0.0
    },
    "L2SignalConfig": {
      "epiplexity_min": 0.4,
      "peace_threshold": 0.35,
      "srl_resid_sigma_mult": 2.0,
      "topo_area_min_abs": 1e-9,
      "topo_energy_sigma_mult": 10.0,
      "spoofing_ratio_max": 2.5,
      "min_ofi_for_y_update": 100.0
    },
    "L2TopoSNRConfig": {
      "n_shuffle": 100,
      "seed": 1337,
      "std_floor": 1e-12,
      "min_shuffles": 10
    }
  },
  "kernel_gate_clauses": [
    "epiplexity > peace_threshold",
    "srl_resid < -srl_resid_sigma_mult * sigma_eff",
    "topo_area > topo_area_min_abs",
    "topo_energy > sigma_eff * topo_energy_sigma_mult",
    "spoof_ratio < spoofing_ratio_max"
  ],
  "adaptive_y_update_condition": "epiplexity < peace_threshold and abs(net_ofi) > min_ofi_for_y_update"
}
```
