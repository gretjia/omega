@echo off
setlocal enableextensions
cd /d D:\work\Omega_vNext
set PYTHONNOUSERSITE=1
set OMEGA_DISABLE_NUMBA=1
set OMEGA_STAGE2_ALLOW_RISKY_RUNTIME=1
set OMEGA_WINDOWS_WMI_MACHINE_BYPASS=1
set OMEGA_STAGE2_FORCE_SCAN_FALLBACK=1
set OMEGA_STAGE2_ISOLATE_SYMBOL_BATCH=1
set OMEGA_STAGE2_SYMBOL_BATCH_SIZE=20
set OMEGA_STAGE2_POLARS_THREADS=1
set OMEGA_STAGE2_DIAG_EVERY_BATCHES=10
set STAGE2_PY=D:\work\Omega_vNext\.venv_stage2_win\Scripts\python.exe
if not exist "%STAGE2_PY%" (
  echo [FATAL] missing python: %STAGE2_PY%
  exit /b 2
)
"%STAGE2_PY%" -u tools\stage2_targeted_resume.py --input-dir D:\Omega_frames\v62_base_l1\host=windows1 --output-dir D:\Omega_frames\v62_feature_l2\host=windows1 --timeout-sec 21600 --log-file audit\stage2_targeted_resume_isolated_v2.log --fail-file audit\stage2_targeted_failed_isolated_v2.txt --reset-fail-file --pending-file audit\stage2_pending_isolated_v2.txt --python-bin "%STAGE2_PY%" --files-per-process 1
exit /b %errorlevel%
