Write-Host "=== OMEGA v3 FULL SOLO CYCLE START ==="
$root = Get-Location

# 1. Rebuild 2023 Frames
Write-Host ">>> Step 1: Rebuilding 2023 Frames (Windows Node)..."
python tools/run_l2_audit_driver.py --year 2023 --limit 0 --workers 4 --output-dir data/level2_frames_2023 --skip-report --copy-to-local
if ($LASTEXITCODE -ne 0) { Write-Error "2023 Rebuild Failed"; exit 1 }

# 2. Rebuild 2024 Frames
Write-Host ">>> Step 2: Rebuilding 2024 Frames (Mac Node Data)..."
python tools/run_l2_audit_driver.py --year 2024 --limit 0 --workers 4 --output-dir data/level2_frames_2024 --skip-report --copy-to-local
if ($LASTEXITCODE -ne 0) { Write-Error "2024 Rebuild Failed"; exit 1 }

# 3. Generate Reports (Streaming)
Write-Host ">>> Step 3: Generating Streaming Audit Reports..."
python tools/generate_report_streaming.py --input-dir data/level2_frames_2023 --report audit/win2023_report_streaming.md
python tools/generate_report_streaming.py --input-dir data/level2_frames_2024 --report audit/mac2024_report_streaming.md

# 4. Run Training
Write-Host ">>> Step 4: Starting Full Training..."
python tools/run_v3_training.py
if ($LASTEXITCODE -ne 0) { Write-Error "Training Failed"; exit 1 }

Write-Host "=== OMEGA v3 FULL SOLO CYCLE COMPLETED SUCCESSFULLY ==="
