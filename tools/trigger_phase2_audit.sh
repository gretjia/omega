#!/bin/bash
# Trigger script for the PHASE 2 Executed Code Audit
# Verifies the Base_L1 extraction and Feature_L2 compute separation

echo "--- Dispatching Engineering Audit (Execution Codex) ---"
codex exec "As a Distributed Systems Engineer, review tools/stage1_linux_base_etl.py and tools/stage2_physics_compute.py. Have we properly decoupled raw IO (Stage 1) from CPU Physics (Stage 2)? Did we implement safe symbol-batch memory loading via pl.scan_parquet in Stage 2 to prevent OOM on 128GB node? Output PASS/FAIL and any memory leaks." --model=gpt-5.3-codex > audit/v62_phase2_eng_audit.log 2>&1

echo "Phase 2 Audit complete. Logs generated."
