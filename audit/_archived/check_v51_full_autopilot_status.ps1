param(
    [string]$Root = "C:\Omega_vNext"
)

$runtimeRoot = Join-Path $Root "audit\v51_runtime\windows\full_autopilot"
$statusPath = Join-Path $runtimeRoot "autopilot_status.json"
$exitPath = Join-Path $runtimeRoot "autopilot_exit_code.txt"
$logPath = Join-Path $runtimeRoot "autopilot.log"
$frameOut = Join-Path $runtimeRoot "frame_decjan\frame.stdout.log"
$trainStatus = Join-Path $runtimeRoot "train\train_status.json"
$backtestStatus = Join-Path $runtimeRoot "backtest\backtest_status.json"

Write-Output "=== AUTOPILOT STATUS ==="
if (Test-Path -LiteralPath $statusPath) {
    Get-Content -LiteralPath $statusPath
} else {
    Write-Output "autopilot_status.json missing"
}

if (Test-Path -LiteralPath $exitPath) {
    Write-Output "=== EXIT CODE ==="
    Get-Content -LiteralPath $exitPath
}

Write-Output "=== AUTOPILOT LOG (tail 20) ==="
if (Test-Path -LiteralPath $logPath) {
    Get-Content -LiteralPath $logPath -Tail 20
}

Write-Output "=== FRAME LOG (tail 20) ==="
if (Test-Path -LiteralPath $frameOut) {
    Get-Content -LiteralPath $frameOut -Tail 20
}

Write-Output "=== TRAIN STATUS ==="
if (Test-Path -LiteralPath $trainStatus) {
    Get-Content -LiteralPath $trainStatus
} else {
    Write-Output "train_status.json not ready"
}

Write-Output "=== BACKTEST STATUS ==="
if (Test-Path -LiteralPath $backtestStatus) {
    Get-Content -LiteralPath $backtestStatus
} else {
    Write-Output "backtest_status.json not ready"
}
