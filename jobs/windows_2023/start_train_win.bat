@echo off
REM ================================================================
REM OMEGA Level-2 Training Starter (Windows)
REM Year: 2023
REM Hardware Target: AMD Ryzen AI MAX+ PRO 395 (128G RAM)
REM ================================================================

echo [OMEGA] Starting Windows Training Job (2023)...

REM 1. Kill Idle Python Processes (Safety)
echo [OMEGA] Cleaning up idle python processes...
taskkill /F /IM python.exe >nul 2>&1

REM 2. Configure Environment
set WORKERS=16
set LIMIT=9999
set YEAR=2023
set OUTPUT_DIR=data/level2_frames_win2023

echo [OMEGA] Configuration:
echo   - Year: %YEAR%
echo   - Workers: %WORKERS%
echo   - Output: %OUTPUT_DIR%

REM 3. Run Driver
echo [OMEGA] Launching Driver...
python tools/run_l2_audit_driver.py --limit %LIMIT% --workers %WORKERS% --year %YEAR% --output-dir %OUTPUT_DIR%

echo [OMEGA] Job Complete.
pause
