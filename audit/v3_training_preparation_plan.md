# OMEGA v3.1 Training Preparation Plan

**Status**: Draft
**Date**: 2026-02-05
**Ref**: `audit/20260205_handover.md`, `audit/v3_training_results_audit_artitecture.md`

## 1. Status Assessment
Current `omega_v3_core/trainer.py` is based on **v3.0 logic**. It lacks the critical "Recursive Patch" and "Robustness Fixes" required by the latest audit.
- **Missing**: Peace Protocol (Recursive Y updates), Dark Energy (Spoofing Ratio), Holographic Topology Normalization.
- **Issue**: Training treats all frames equally (Mean Reversion) and uses noisy labels (Random Walk).
- **Goal**: Upgrade to **v3.1** to capture "Rare Structural Alpha".

### Reviewer Notes (AI)
- 近期升级已完成在 `omega_v3_core/kernel.py` / `omega_etl.py` / `omega_math_core.py`（Map‑Reduce + Peace Protocol + Spoofing + Topology Normalization）。**trainer 仍未升级**，本计划必须补齐训练侧调用“Reduce”逻辑。
- 如果训练仍使用旧的 `level2_frames_*` Parquet（升级前生成），将**缺失 `trade_vol/cancel_vol/spoof_ratio`** 等字段，需**重新产出 frames**或在训练中重新计算。

## 2. Upgrade Requirements (The "Minimal Fix Set")

### A. Pipeline Architecture (Map-Reduce Integration)
*   **Current**: Loads Parquet -> Feeds Model.
*   **Required**: Load Parquet (Map Output) -> **Apply Recursive Physics (Reduce Step)** -> Feed Model.
*   **Why**: To ensure `srl_resid`, `adaptive_y`, and `is_signal` respect the "Peace Protocol" and new v3.1 math.
*   **Action**: Inject `kernel._apply_recursive_physics` into the training data loader.

**Reviewer Notes (AI)**:
- `_apply_recursive_physics` 当前为“内部函数”，建议增加一个**公开包装**（例如 `kernel.apply_recursive_physics(frames, cfg)`）避免训练端依赖私有实现。
- 训练侧应**严格基于 `build_l2_frames` 输出**再做 reduce；若直接读取旧 `level2_frames_*`，可能缺失新字段。

### B. Label Engineering ("Direction Definition")
*   **Current**: `close[t+h] > close[t]` (Binary).
*   **Required**: **Future K-Bar Return with Noise Filter**.
    *   Target: `ret_k = (close[t+k] - close[t]) / close[t]`
    *   Label: `sign(ret_k)` IF `abs(ret_k) > theta * sigma_eff` ELSE `0`.
*   **Why**: To stop the model from learning microstructure noise.

**Reviewer Notes (AI)**:
- 该标签是 **三类**（-1/0/+1）。若继续用 `SGDClassifier` 二分类，必须**丢弃 label=0** 或将其视为“忽略样本”（sample_weight=0）。
- `ret_k` 建议使用**volume-clock 帧**上的 forward return（当前 frames 已是 volume bucket）。  

### C. Structural Sampling ("Signal Focus")
*   **Current**: Random Sampling (`sample_frac`).
*   **Required**: **Importance Sampling**.
    *   **Hard Filter**: Keep frame IF `is_signal == True` (from kernel) OR `abs(net_ofi) > 90th percentile` OR `topo_snr > threshold`.
    *   **Soft Weighting**: Weight samples by `log(1 + Topo_SNR)`.
*   **Why**: Force the linear model to fit "Structure" instead of "Mean".

**Reviewer Notes (AI)**:
- `topo_snr` 是**全局审计指标**，不是帧级字段；此处过滤逻辑不可执行。应替换为帧级 proxy（如 `topo_energy` / `abs(topo_area)` / `epiplexity`）。
- 可优先使用 `is_signal` + `topo_energy` 进行 hard filter；soft weight 可用 `log1p(abs(topo_area))` 或 `log1p(topo_energy)`。

### D. Feature Robustness ("Math Guardrails")
*   **Current**: `StandardScaler` (Mean/Std).
*   **Required**: **Pre-scaling Transformations**.
    *   `log1p`: For `net_ofi`, `depth_eff`, `srl_resid` (Heavy Tails).
    *   `winsorize`: For `topo_area` (Outliers).
    *   `z-score`: Local (Rolling) or Per-Symbol normalization.
*   **Why**: Prevent single massive events from destroying SGD gradients.

**Reviewer Notes (AI)**:
- 对有符号特征（`net_ofi`, `srl_resid`, `topo_area`）应使用 **sign(x)*log1p(abs(x))**，避免符号丢失。
- `topo_area` 已在 kernel 侧标准化，但若训练加载旧 frames 仍需防护。

## 3. Implementation Plan

### Step 1: Modify `omega_v3_core/trainer.py`
1.  **Import Kernel**: `from omega_v3_core.kernel import _apply_recursive_physics`
2.  **Update `prepare_data`**:
    *   Add `apply_physics: bool = True` flag.
    *   Call `_apply_recursive_physics` if enabled.
    *   Implement new Label Logic (`future_return`, `neutral_zone`).
    *   Implement Robust Transforms (`np.log1p` wrapper).
3.  **Update `train` Loop**:
    *   Implement "Smart Sampling" (Filter rows where `label == 0` unless used as negative samples? No, `label=0` usually means "ignore" in binary classification, or we treat as Multiclass/Regression. For `SGDClassifier`, we might just drop `label=0` rows or use them as neutral if doing 3-class. *Audit suggests: "label=0 (Don't Trade/Learn)" -> Drop these rows for Binary Classifier*).

**Reviewer Notes (AI)**:
- 建议把 `_apply_recursive_physics` 改为公开接口后再调用，避免训练对私有实现强耦合。
- `is_signal` 过滤应在 **Reduce 完成后**再做，避免未来信息泄露。

### Step 2: Verification (Dry Run)
1.  Run `trainer.py` in Debug Mode (`max_files=10`).
2.  Check Logs:
    *   Are `srl_resid` values different? (Proof of Recursive Physics)
    *   Is `Vector_Alignment` **improving vs baseline**? (不强求 >0.5，需以历史口径对比)
    *   Are Feature Weights for `topo_area` non-zero?

### Step 3: Full Training
1.  Run on merged dataset (Windows 2023 + Mac 2024).
2.  Save Artifact: `omega_v3_1_policy.pkl`.

## 4. Request for Approval
I am ready to modify `omega_v3_core/trainer.py` to implement the above v3.1 upgrades.
**Do you approve this plan?**
