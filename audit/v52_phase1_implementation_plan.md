# OMEGA v5.2 Supplementary Implementation Plan (Phase 1)

**Goal**: Execute the "Code Engineering" recommendations from `v52_supplementary_review.md`.

## User Review Required

> [!IMPORTANT]
> **Numba Dependency**: We are adding `numba` to `requirements.txt`. This requires a C compiler environment on the target machine (usually present on standard dev setups, but good to note).
> **CLI Entry Points**: We are making `trainer_v51.py` executable via `python -m`.

## Proposed Changes

### 1. Optimization: `omega_core/kernel.py`

We will replace the Python `for` loop in `_apply_recursive_physics` with a JIT-compiled function.

#### [MODIFY] [kernel.py](file:///Volumes/desktop-41jidl2/Omega_vNext/omega_core/kernel.py)

- Import `numba`.
- Extract the loop body (SRL + Adaptive Y + Spoofing) into `_calc_recursive_physics_loop_numba`.
- Decorate with `@numba.njit(cache=True, fastmath=True)`.
- In `_apply_recursive_physics`, prepare numpy arrays (float64) and call the JIT function.
- Fallback to Python loop if `numba` is not installed (soft dependency for compatibility, though `requirements.txt` will enforce it).

### 2. Dependency Management

#### [MODIFY] [requirements.txt](file:///Volumes/desktop-41jidl2/Omega_vNext/requirements.txt)

- Add `numba>=0.59.0`.

### 3. Reliability: `omega_core/trainer_v51.py`

We will prevent silent failures and add observability.

#### [MODIFY] [trainer_v51.py](file:///Volumes/desktop-41jidl2/Omega_vNext/omega_core/trainer_v51.py)

- Add `argparse` block in `if __name__ == "__main__":`.
- Add `error_count` and `MAX_ERROR_RATE = 0.05`.
- Add `training_errors.jsonl` logging.
- Catch specific exceptions in `get_latest_model`.

## Verification Plan

### Automated Tests

We will create a specific performance and correctness test for the new kernel.

#### [NEW] [tests/test_kernel_srl_numba.py](file:///Volumes/desktop-41jidl2/Omega_vNext/tests/test_kernel_srl_numba.py)

- **Correctness**: Generate random input arrays (N=1000). Run both Python implementation (extracted from current kernel) and Numba implementation. Assert `np.allclose`.
- **Benchmark**: Run both on N=100,000. Report speedup factor (expect >50x).

### Manual Verification

- Run `python -m omega_core.trainer_v51 --help` to verify CLI.
- Run the smoke test `python tests/test_kernel_srl_numba.py`.
