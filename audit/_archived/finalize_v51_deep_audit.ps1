param(
    [string]$Root = "C:/Omega_vNext",
    [int]$PollSec = 300
)

$ErrorActionPreference = "Continue"
$runtime = Join-Path $Root "audit/v51_runtime/windows/full_autopilot"
$statusPath = Join-Path $runtime "autopilot_status.json"
$summaryPath = Join-Path $runtime "autopilot_summary.json"
$exitPath = Join-Path $runtime "autopilot_exit_code.txt"
$pyScript = Join-Path $runtime "generate_v51_deep_audit.py"
$logPath = Join-Path $runtime "finalizer.log"
$pidPath = Join-Path $runtime "finalizer.pid"

Set-Content -LiteralPath $pidPath -Value $PID -Encoding UTF8

function FLog {
    param([string]$Text)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Text
    $line | Tee-Object -FilePath $logPath -Append | Out-Null
}

FLog "START finalizer"
FLog ("PollSec={0}" -f $PollSec)

while ($true) {
    $phase = ""
    $state = ""
    $exitCode = ""

    if (Test-Path -LiteralPath $statusPath) {
        try {
            $s = Get-Content -LiteralPath $statusPath -Raw | ConvertFrom-Json
            $phase = [string]$s.phase
            $state = [string]$s.state
        } catch {}
    }

    if (Test-Path -LiteralPath $exitPath) {
        try { $exitCode = (Get-Content -LiteralPath $exitPath -Raw).Trim() } catch {}
    }

    $done = (($phase -eq "complete" -and $state -eq "completed") -or ($phase -eq "failed"))

    if ($done -and (Test-Path -LiteralPath $pyScript)) {
        FLog ("Pipeline terminal state detected: phase={0}, state={1}, exit={2}" -f $phase, $state, $exitCode)
        try {
            & C:/Python314/python.exe $pyScript 2>&1 | Tee-Object -FilePath $logPath -Append | Out-Null
            FLog "Generated audit/v51_deep_audit.md"
            break
        } catch {
            FLog ("Generator failed: {0}" -f ($_ | Out-String))
            break
        }
    }

    FLog ("Waiting... phase={0}, state={1}, exit={2}" -f $phase, $state, $exitCode)
    Start-Sleep -Seconds $PollSec
}

FLog "END finalizer"
exit 0

