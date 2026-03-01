#!/bin/bash
# Trigger script for the PHASE 3 Executed Code Audit
# Verifies the GIL Eradication and Numba optimization

echo "--- Dispatching Engineering Audit (Execution Codex) ---"
codex exec "As a Compiler Engineer, review omega_core/kernel.py and omega_core/omega_math_rolling.py. Have we eradicated list-based Polars/Python iterations for Epiplexity and Topology? Are we successfully using sliding_window_view and @njit(parallel=True) for GIL-free computation? Output PASS/FAIL and any GIL contention risks." --model=gpt-5.3-codex > audit/v62_phase3_eng_audit.log 2>&1

echo "Phase 3 Audit complete. Logs generated."
