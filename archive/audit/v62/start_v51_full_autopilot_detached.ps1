param(
    [string]$Root = "C:\Omega_vNext",
    [switch]$AllowAuditFailed = $true,
    [int]$TrainWorkers = 6,
    [int]$BacktestWorkers = 8,
    [double]$TrainMemoryThreshold = 98.0,
    [double]$BacktestMemoryThreshold = 98.0,
    [int]$MonitorIntervalSec = 300
)

$ErrorActionPreference = "Stop"

$runtimeRoot = Join-Path $Root "audit\v51_runtime\windows\full_autopilot"
$mainScript = Join-Path $runtimeRoot "run_v51_full_autopilot.ps1"
$launcherLog = Join-Path $runtimeRoot "launcher.log"
$pidPath = Join-Path $runtimeRoot "autopilot.pid"
$exitPath = Join-Path $runtimeRoot "autopilot_exit_code.txt"

New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null

function Write-Launch {
    param([string]$Text)
    $line = ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Text)
    $line | Tee-Object -FilePath $launcherLog -Append | Out-Null
}

if (-not (Test-Path -LiteralPath $mainScript)) {
    throw "Main script not found: $mainScript"
}

if (Test-Path -LiteralPath $pidPath) {
    try {
        $oldPid = [int](Get-Content -LiteralPath $pidPath -Raw).Trim()
        if ($oldPid -gt 0) {
            $oldProc = Get-Process -Id $oldPid -ErrorAction SilentlyContinue
            if ($null -ne $oldProc) {
                Write-Launch ("Autopilot already running with PID={0}. Skip new launch." -f $oldPid)
                exit 0
            }
        }
    } catch {}
}

if (Test-Path -LiteralPath $exitPath) {
    Remove-Item -LiteralPath $exitPath -Force -ErrorAction SilentlyContinue
}

$args = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", $mainScript,
    "-Root", $Root,
    "-TrainWorkers", [string]$TrainWorkers,
    "-BacktestWorkers", [string]$BacktestWorkers,
    "-TrainMemoryThreshold", [string]$TrainMemoryThreshold,
    "-BacktestMemoryThreshold", [string]$BacktestMemoryThreshold,
    "-MonitorIntervalSec", [string]$MonitorIntervalSec
)

if ($AllowAuditFailed) {
    $args += "-AllowAuditFailed"
}

Write-Launch ("START detached v51 full autopilot")
Write-Launch ("MainScript={0}" -f $mainScript)
Write-Launch ("AllowAuditFailed={0}" -f $AllowAuditFailed)
Write-Launch ("TrainWorkers={0}, BacktestWorkers={1}" -f $TrainWorkers, $BacktestWorkers)
Write-Launch ("MonitorIntervalSec={0}" -f $MonitorIntervalSec)

$quoted = @()
foreach ($a in $args) {
    if ($a -match "\s") { $quoted += ('"' + $a + '"') } else { $quoted += $a }
}
$cmdLine = "start "" /b powershell " + ($quoted -join " ")
cmd /c $cmdLine | Out-Null
Start-Sleep -Seconds 2

if (Test-Path -LiteralPath $pidPath) {
    $mainPid = (Get-Content -LiteralPath $pidPath -Raw).Trim()
    Write-Launch ("LAUNCHED PID={0}" -f $mainPid)
} else {
    Write-Launch "LAUNCHED (pid pending; check autopilot.pid)"
}

exit 0
