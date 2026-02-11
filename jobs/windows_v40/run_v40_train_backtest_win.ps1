param(
    [string]$Root = "",
    [string]$FrameOutputDir = "data/level2_frames_v40_win",
    [int]$TrainWorkers = 26,
    [int]$BacktestWorkers = 20,
    [int]$TrainBatchRows = 1000000,
    [int]$TrainCheckpointRows = 2000000,
    [int]$TrainPlanningProgressEveryLines = 50000,
    [int]$BacktestPlanningProgressEveryLines = 50000,
    [double]$MemoryThreshold = 88.0,
    [string]$TrainStageDir = "C:/Omega_train_stage",
    [int]$TrainStageChunkFiles = 48,
    [int]$TrainStageCopyWorkers = 4,
    [string]$BacktestStageDir = "C:/Omega_backtest_stage",
    [int]$BacktestStageChunkFiles = 48,
    [int]$BacktestStageCopyWorkers = 4,
    [int]$BacktestStateSaveEveryFiles = 200,
    [switch]$NoCleanupTrainStage,
    [switch]$NoCleanupBacktestStage,
    [string]$PolicyPath = "",
    [string]$BacktestFileList = "",
    [string]$TrainYears = "",
    [string]$BacktestYears = "",
    [string]$BacktestYearMonths = "",
    [switch]$AllowTrainBacktestOverlap,
    [switch]$AllowUnparsedFrameDatePrefix,
    [switch]$SkipDatasetSplitPreflight,
    [switch]$SkipFrameCompatibilityCheck,
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

$entry = Join-Path $Root "jobs/windows_v40/start_v40_pipeline_win.ps1"
if (-not (Test-Path $entry)) {
    throw "Pipeline entry not found: $entry"
}

$commonArgs = @{
    Root = $Root
    FrameOutputDir = $FrameOutputDir
    TrainWorkers = $TrainWorkers
    BacktestWorkers = $BacktestWorkers
    TrainBatchRows = $TrainBatchRows
    TrainCheckpointRows = $TrainCheckpointRows
    TrainPlanningProgressEveryLines = $TrainPlanningProgressEveryLines
    BacktestPlanningProgressEveryLines = $BacktestPlanningProgressEveryLines
    MemoryThreshold = $MemoryThreshold
    TrainStageDir = $TrainStageDir
    TrainStageChunkFiles = $TrainStageChunkFiles
    TrainStageCopyWorkers = $TrainStageCopyWorkers
    BacktestStageDir = $BacktestStageDir
    BacktestStageChunkFiles = $BacktestStageChunkFiles
    BacktestStageCopyWorkers = $BacktestStageCopyWorkers
    BacktestStateSaveEveryFiles = $BacktestStateSaveEveryFiles
    TrainYears = $TrainYears
    BacktestYears = $BacktestYears
    BacktestYearMonths = $BacktestYearMonths
}

if ($NoCleanupTrainStage) {
    $commonArgs.NoCleanupTrainStage = $true
}
if ($NoCleanupBacktestStage) {
    $commonArgs.NoCleanupBacktestStage = $true
}
if ($SkipFrameCompatibilityCheck) {
    $commonArgs.SkipFrameCompatibilityCheck = $true
}
if ($NoResume) {
    $commonArgs.NoResume = $true
}
if ($AllowTrainBacktestOverlap) {
    $commonArgs.AllowTrainBacktestOverlap = $true
}
if ($AllowUnparsedFrameDatePrefix) {
    $commonArgs.AllowUnparsedFrameDatePrefix = $true
}
if ($SkipDatasetSplitPreflight) {
    $commonArgs.SkipDatasetSplitPreflight = $true
}
if (-not [string]::IsNullOrWhiteSpace($PolicyPath)) {
    $commonArgs.PolicyPath = $PolicyPath
}
if (-not [string]::IsNullOrWhiteSpace($BacktestFileList)) {
    $commonArgs.BacktestFileList = $BacktestFileList
}

Write-Stamp "v40 train+backtest pipeline start"
Write-Stamp (
    "Hardware profile defaults: " +
    "TrainWorkers=$TrainWorkers, " +
    "BacktestWorkers=$BacktestWorkers, " +
    "TrainBatchRows=$TrainBatchRows, " +
    "TrainCheckpointRows=$TrainCheckpointRows, " +
    "TrainStageChunkFiles=$TrainStageChunkFiles, " +
    "TrainStageCopyWorkers=$TrainStageCopyWorkers, " +
    "BacktestStageChunkFiles=$BacktestStageChunkFiles, " +
    "BacktestStageCopyWorkers=$BacktestStageCopyWorkers, " +
    "BacktestStateSaveEveryFiles=$BacktestStateSaveEveryFiles, " +
    "MemoryThreshold=$MemoryThreshold"
)
Write-Stamp "Train stage"
& $entry -Stage train @commonArgs

Write-Stamp "Backtest stage"
& $entry -Stage backtest @commonArgs

Write-Stamp "v40 train+backtest pipeline complete"
Write-Stamp "Runtime root: $Root\\audit\\v40_runtime\\windows"
