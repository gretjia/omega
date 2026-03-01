param(
    [string]$Root = "C:\Omega_vNext",
    [int]$PollSec = 600,
    [int]$MaxRestarts = 3
)

$ErrorActionPreference = "Continue"

$runtimeRoot = Join-Path $Root "audit\v51_runtime\windows\full_autopilot"
$statusPath = Join-Path $runtimeRoot "autopilot_status.json"
$exitPath = Join-Path $runtimeRoot "autopilot_exit_code.txt"
$watchLog = Join-Path $runtimeRoot "watchdog.log"
$launchScript = Join-Path $runtimeRoot "start_v51_full_autopilot_detached.ps1"
$postframeScript = Join-Path $runtimeRoot "run_v51_postframe_train_backtest.ps1"
$watchPid = Join-Path $runtimeRoot "watchdog.pid"

New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null
Set-Content -LiteralPath $watchPid -Value $PID -Encoding UTF8

function WLog {
    param([string]$Text)
    $line = ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Text)
    $line | Tee-Object -FilePath $watchLog -Append | Out-Null
}

function IsMainRunning {
    try {
        $procs = Get-CimInstance Win32_Process | Where-Object {
            ((($_.CommandLine -like "*run_v51_full_autopilot.ps1*") -or ($_.CommandLine -like "*run_v51_postframe_train_backtest.ps1*")) -and ($_.CommandLine -notlike "*watch_v51_full_autopilot.ps1*"))
        }
        return ($procs.Count -gt 0)
    } catch {
        return $false
    }
}

$restarts = 0
WLog "START watchdog"
WLog ("PollSec={0}, MaxRestarts={1}" -f $PollSec, $MaxRestarts)

while ($true) {
    $phase = ""
    $state = ""
    $exitCode = $null

    if (Test-Path -LiteralPath $statusPath) {
        try {
            $s = Get-Content -LiteralPath $statusPath -Raw | ConvertFrom-Json
            $phase = [string]$s.phase
            $state = [string]$s.state
        } catch {}
    }

    if (Test-Path -LiteralPath $exitPath) {
        try { $exitCode = [int](Get-Content -LiteralPath $exitPath -Raw).Trim() } catch {}
    }

    $running = IsMainRunning

    if ($phase -eq "complete" -and $state -eq "completed") {
        WLog "Main pipeline completed. Watchdog exiting."
        break
    }

    if (-not $running) {
        if ($restarts -ge $MaxRestarts) {
            WLog ("Main not running and restart budget exhausted ({0}). Watchdog exiting." -f $restarts)
            break
        }

        WLog ("Main not running. phase={0} state={1} exit={2}. Restarting..." -f $phase, $state, $exitCode)
        try {
            if (($phase -eq "failed") -and (Test-Path -LiteralPath $postframeScript)) {
                cmd /c "start \"\" /b powershell -NoProfile -ExecutionPolicy Bypass -File $postframeScript -Root $Root -TrainWorkers 6 -BacktestWorkers 8 -TrainMemoryThreshold 98 -BacktestMemoryThreshold 98 -AllowAuditFailed -MonitorIntervalSec 300" | Out-Null
                WLog "Postframe recovery launch issued."
            } else {
                & powershell -NoProfile -ExecutionPolicy Bypass -File $launchScript -Root $Root -AllowAuditFailed -TrainWorkers 6 -BacktestWorkers 8 -TrainMemoryThreshold 98 -BacktestMemoryThreshold 98 -MonitorIntervalSec 300
                WLog "Default autopilot launch issued."
            }
            $restarts += 1
            WLog ("Restart issued. total_restarts={0}" -f $restarts)
        } catch {
            WLog ("Restart command failed: {0}" -f ($_ | Out-String))
            $restarts += 1
        }
    } else {
        WLog ("Main running. phase={0} state={1}" -f $phase, $state)
    }

    Start-Sleep -Seconds $PollSec
}

WLog "END watchdog"
exit 0

