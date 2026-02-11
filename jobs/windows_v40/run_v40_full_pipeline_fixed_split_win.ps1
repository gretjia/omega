param(
    [string]$Root = "",
    [switch]$NoResume,
    [switch]$PurgeFrameOutput,
    [switch]$SkipRuntimeClean,
    [switch]$SkipStageClean
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

function Clear-DirectoryContent {
    param([string]$Path)
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
    Get-ChildItem -LiteralPath $Path -Force -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction Stop
    }
}

$entry = Join-Path $Root "jobs/windows_v40/start_v40_pipeline_win.ps1"
if (-not (Test-Path $entry)) {
    throw "Pipeline entry not found: $entry"
}

$winnerExtractor = Join-Path $Root "tools/extract_v40_race_winner.py"
if (-not (Test-Path $winnerExtractor)) {
    throw "Winner extractor not found: $winnerExtractor"
}

$runtimeRoot = Join-Path $Root "audit\v40_runtime\windows"
$frameOutputRel = "data/level2_frames_v40_win"
$frameOutputAbs = Join-Path $Root $frameOutputRel

if (-not $SkipRuntimeClean) {
    Write-Stamp "Cleaning runtime artifacts under audit/v40_runtime/windows"
    foreach ($leaf in @("frame", "train", "backtest", "manifests", "frame_bench")) {
        Clear-DirectoryContent -Path (Join-Path $runtimeRoot $leaf)
    }
    foreach ($f in @(
        "pipeline_launcher.err.log",
        "pipeline_launcher.out.log",
        "_py_path_test_err.log",
        "_py_path_test_out.log",
        "_sp_test_err.log",
        "_sp_test_out.log"
    )) {
        $p = Join-Path $runtimeRoot $f
        if (Test-Path $p) {
            Remove-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
        }
    }
}
else {
    Write-Stamp "SkipRuntimeClean=true, keeping existing runtime artifacts."
}

if (-not $SkipStageClean) {
    Write-Stamp "Cleaning local stage directories (C:/Omega_*_stage)"
    foreach ($stageDir in @("C:/Omega_level2_stage", "C:/Omega_train_stage", "C:/Omega_backtest_stage")) {
        if (Test-Path $stageDir) {
            Remove-Item -LiteralPath $stageDir -Recurse -Force -ErrorAction Stop
        }
        New-Item -ItemType Directory -Force -Path $stageDir | Out-Null
    }
}
else {
    Write-Stamp "SkipStageClean=true, keeping existing C: stage directories."
}

if ($PurgeFrameOutput) {
    Write-Stamp "PurgeFrameOutput=true, removing frame output: $frameOutputAbs"
    if (Test-Path $frameOutputAbs) {
        Remove-Item -LiteralPath $frameOutputAbs -Recurse -Force -ErrorAction Stop
    }
    New-Item -ItemType Directory -Force -Path $frameOutputAbs | Out-Null
}
elseif (-not (Test-Path $frameOutputAbs)) {
    New-Item -ItemType Directory -Force -Path $frameOutputAbs | Out-Null
}

$args = @{
    Stage = "all"
    Root = $Root
    FrameOutputDir = $frameOutputRel
    FrameWorkers = 22
    FrameIoSlots = 4
    FrameSevenZipThreads = 1
    FrameStageDir = "C:/Omega_level2_stage"
    TrainWorkers = 26
    BacktestWorkers = 20
    TrainBatchRows = 1000000
    TrainCheckpointRows = 2000000
    TrainPlanningProgressEveryLines = 50000
    BacktestPlanningProgressEveryLines = 50000
    MemoryThreshold = 88.0
    TrainStageDir = "C:/Omega_train_stage"
    TrainStageChunkFiles = 48
    TrainStageCopyWorkers = 4
    BacktestStageDir = "C:/Omega_backtest_stage"
    BacktestStageChunkFiles = 48
    BacktestStageCopyWorkers = 4
    BacktestStateSaveEveryFiles = 200
    TrainYears = "2023,2024"
    BacktestYears = "2025"
    BacktestYearMonths = "202601"
}
if ($NoResume) {
    $args.NoResume = $true
}

Write-Stamp "v40 full pipeline start (fixed split + optimized defaults)."
Write-Stamp (
    "Params: " +
    "FrameWorkers=12 FrameIoSlots=4 Frame7zThreads=1 " +
    "TrainWorkers=26 BacktestWorkers=20 " +
    "TrainBatchRows=1000000 TrainCheckpointRows=2000000 " +
    "TrainStageChunkFiles=48 BacktestStageChunkFiles=48 " +
    "MemoryThreshold=88.0 " +
    "Split(train=2023,2024; backtest=2025,202601)"
)
& $entry @args

$winnerJson = Join-Path $runtimeRoot "backtest\race_winner_summary.json"
$winnerMd = Join-Path $runtimeRoot "backtest\race_winner_summary.md"
Write-Stamp "Extracting race winner summary from latest checkpoint"
$winnerExitCode = $null
$prevErrorAction = $ErrorActionPreference
try {
    $ErrorActionPreference = "Continue"
    & python "tools/extract_v40_race_winner.py" --out-json $winnerJson --out-md $winnerMd
    $winnerExitCode = $LASTEXITCODE
}
finally {
    $ErrorActionPreference = $prevErrorAction
}
if ($winnerExitCode -ne 0) {
    throw "Race winner extraction failed."
}

Write-Stamp "v40 full pipeline complete."
Write-Stamp "Runtime root: $runtimeRoot"
Write-Stamp "Race summary: $winnerMd"
