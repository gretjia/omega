#!/bin/bash
# ================================================================
# OMEGA Level-2 Training Starter (Mac Studio)
# Year: 2024
# Hardware Target: M4 Max (32G Unified Memory)
# ================================================================

echo "[OMEGA] Starting Mac Training Job (2024)..."

# 1. Kill Idle Python Processes (Safety)
echo "[OMEGA] Cleaning up idle python processes..."
pkill -9 python > /dev/null 2>&1

# 2. Configure Environment
# Mac M4 Max has fewer performance cores than Threadripper/Ryzen usually,
# and 32G RAM is tight. Lower workers to prevent OOM.
WORKERS=3
LIMIT=9999
YEAR=2024
OUTPUT_DIR="data/level2_frames_mac2024"

echo "[OMEGA] Configuration:"
echo "  - Year: $YEAR"
echo "  - Workers: $WORKERS"
echo "  - Output: $OUTPUT_DIR"
echo "  - Strategy: Network Copy-To-Local (Optimization)"

# 3. Run Driver
echo "[OMEGA] Launching Driver..."
python3 tools/run_l2_audit_driver.py --limit $LIMIT --workers $WORKERS --year $YEAR --output-dir $OUTPUT_DIR --copy-to-local

echo "[OMEGA] Job Complete."
