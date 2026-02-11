param(
    [string]$Root = "",
    [string]$CondaExe = "conda",
    [string]$CondaEnv = "OMEGA",
    [string]$SmokeRoot = "C:/Omega_v40_smoke",
    [string]$FrameYear = "",
    [int]$FrameLimit = 1,
    [int]$FrameWorkers = 1,
    [int]$TrainWorkers = 2,
    [int]$BacktestWorkers = 2,
    [int]$SmokeFiles = 3,
    [double]$MemoryThreshold = 85.0,
    [switch]$NoCleanupStage
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

if ($SmokeFiles -lt 1) {
    throw "SmokeFiles must be >= 1."
}

try {
    $resolvedConda = (Get-Command $CondaExe -ErrorAction Stop).Source
}
catch {
    throw "Conda executable not found: $CondaExe"
}

function Write-Stamp {
    param([string]$Msg)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$ts] $Msg"
}

function Invoke-CondaPython {
    param(
        [string[]]$ScriptArguments,
        [string]$LogPath,
        [string]$WorkingDir
    )
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $LogPath) | Out-Null
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $cmdLine = "$resolvedConda run -n $CondaEnv python " + ($ScriptArguments -join " ")
    "[$ts] CMD: $cmdLine" | Tee-Object -FilePath $LogPath -Append
    Push-Location $WorkingDir
    try {
        & $resolvedConda run -n $CondaEnv python @ScriptArguments 2>&1 | ForEach-Object { $_.ToString() } | Tee-Object -FilePath $LogPath -Append
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed: $cmdLine"
        }
    }
    finally {
        Pop-Location
    }
}

$runId = Get-Date -Format "yyyyMMdd_HHmmss"
$runDir = Join-Path $SmokeRoot "run_$runId"
$frameOutputDir = Join-Path $runDir "frames_smoke"
$frameStageDir = Join-Path $runDir "frame_stage"
$manifestPath = Join-Path $runDir "train_files.txt"
$frameStatus = Join-Path $runDir "frame_status.json"
$trainStatus = Join-Path $runDir "train_status.json"
$backtestStatus = Join-Path $runDir "backtest_status.json"
$backtestState = Join-Path $runDir "backtest_state.json"
$frameLog = Join-Path $runDir "smoke_frame.log"
$trainLog = Join-Path $runDir "smoke_train.log"
$backtestLog = Join-Path $runDir "smoke_backtest.log"
$artifactsDir = Join-Path $runDir "artifacts"

New-Item -ItemType Directory -Force -Path $runDir | Out-Null

$frameScript = Join-Path $Root "tools/run_l2_audit_driver.py"
$trainScript = Join-Path $Root "parallel_trainer/run_parallel_v31.py"
$backtestScript = Join-Path $Root "parallel_trainer/run_parallel_backtest_v31.py"

Write-Stamp "Smoke run directory: $runDir"
Write-Stamp "Using conda: $resolvedConda (env=$CondaEnv)"

# 1) Real frame build from raw level2 archive(s)
$frameArgs = @(
    $frameScript,
    "--workers", "$FrameWorkers",
    "--limit", "$FrameLimit",
    "--output-dir", $frameOutputDir,
    "--copy-to-local",
    "--stage-dir", $frameStageDir,
    "--memory-threshold", "$MemoryThreshold",
    "--skip-report",
    "--status-json", $frameStatus
)
if (-not [string]::IsNullOrWhiteSpace($FrameYear)) {
    $frameArgs += "--year"
    $frameArgs += $FrameYear
}
if ($NoCleanupStage) {
    $frameArgs += "--no-cleanup-stage"
}

Write-Stamp "Step 1/4: frame smoke"
Invoke-CondaPython -ScriptArguments $frameArgs -LogPath $frameLog -WorkingDir $Root

# 2) Build tiny file-list for train/backtest smoke
$smokeParquets = @(
    Get-ChildItem -Path $frameOutputDir -Filter "*.parquet" -File |
        Sort-Object FullName |
        Select-Object -First $SmokeFiles
)
if ($smokeParquets.Count -le 0) {
    throw "No parquet files produced for smoke run: $frameOutputDir"
}
$smokeParquets.FullName | Set-Content -Path $manifestPath -Encoding UTF8
Write-Stamp "Step 2/4: manifest built at $manifestPath (files=$($smokeParquets.Count))"

# 3) Train smoke in isolated cwd (so artifacts do not pollute main workspace)
$trainArgs = @(
    $trainScript,
    "--file-list", $manifestPath,
    "--workers", "$TrainWorkers",
    "--batch-rows", "5000",
    "--checkpoint-rows", "10000",
    "--memory-threshold", "$MemoryThreshold",
    "--progress-every-files", "1",
    "--no-stage-local",
    "--status-json", $trainStatus,
    "--no-resume"
)
Write-Stamp "Step 3/4: train smoke"
Invoke-CondaPython -ScriptArguments $trainArgs -LogPath $trainLog -WorkingDir $runDir

$latestPolicy = Get-ChildItem -Path $artifactsDir -Filter "checkpoint_rows_*.pkl" -File -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if ($null -eq $latestPolicy) {
    throw "Smoke train produced no checkpoint under $artifactsDir"
}

# 4) Backtest smoke
$backtestArgs = @(
    $backtestScript,
    "--policy", $latestPolicy.FullName,
    "--file-list", $manifestPath,
    "--workers", "$BacktestWorkers",
    "--memory-threshold", "$MemoryThreshold",
    "--save-every-files", "1",
    "--no-stage-local",
    "--state-file", $backtestState,
    "--status-json", $backtestStatus,
    "--no-resume",
    "--allow-audit-failed"
)
Write-Stamp "Step 4/4: backtest smoke"
Invoke-CondaPython -ScriptArguments $backtestArgs -LogPath $backtestLog -WorkingDir $runDir

$trainObj = Get-Content -Raw $trainStatus | ConvertFrom-Json
$backtestObj = Get-Content -Raw $backtestStatus | ConvertFrom-Json

if ($trainObj.status -ne "completed") {
    throw "Train smoke did not complete: status=$($trainObj.status)"
}
if ($backtestObj.status -ne "completed") {
    throw "Backtest smoke did not complete: status=$($backtestObj.status)"
}

Write-Stamp "Smoke completed."
Write-Stamp "Frame status: $frameStatus"
Write-Stamp "Train status: $trainStatus"
Write-Stamp "Backtest status: $backtestStatus"
Write-Stamp "Policy: $($latestPolicy.FullName)"
