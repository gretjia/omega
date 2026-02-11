param(
    [string]$Root = "",
    [switch]$NoResume
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

function Write-Stamp {
    param([string]$Msg)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$ts] $Msg"
}

$entry = Join-Path $Root "jobs/windows_v40/run_v40_train_backtest_win.ps1"
if (-not (Test-Path $entry)) {
    throw "Pipeline wrapper not found: $entry"
}

$args = @{
    Root = $Root
    TrainYears = "2023,2024"
    BacktestYears = "2025"
    BacktestYearMonths = "202601"
}

if ($NoResume) {
    $args.NoResume = $true
}

Write-Stamp "Run v40 train+backtest with fixed split: train=2023,2024 backtest=2025,202601"
& $entry @args

