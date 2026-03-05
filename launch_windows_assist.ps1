$env:OMEGA_STAGE2_FORCE_SCAN_FALLBACK='0'
$env:OMEGA_DISABLE_NUMBA='0'
$env:OMEGA_STAGE2_ISOLATE_SYMBOL_BATCH='0'

$pythonExe = "D:\work\Omega_vNext\.venv\Scripts\python.exe"
$scriptPath = "D:\work\Omega_vNext\tools\stage2_targeted_supervisor.py"
$inDir = "D:\Omega_frames\v63_subset_l1_assist_w1\host=windows1"
$outDir = "D:\Omega_frames\v63_feature_l2_assist_w1\host=windows1"
$logFile = "D:\work\Omega_vNext\audit\stage2_assist_windows.log"
$failFile = "D:\work\Omega_vNext\audit\stage2_assist_windows_fail.txt"
$pendingFile = "D:\work\Omega_vNext\audit\stage2_assist_windows_pending.txt"
$stateLog = "D:\work\Omega_vNext\audit\stage2_assist_windows_state.log"

& $pythonExe $scriptPath --input-dir $inDir --output-dir $outDir --timeout-sec 10800 --max-iterations 0 --log-file $logFile --fail-file $failFile --pending-file $pendingFile --state-log $stateLog --allow-user-slice
