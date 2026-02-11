param(
    [ValidateSet("frame", "train", "backtest", "all")]
    [string]$Stage = "all",
    [string]$Root = "",
    [string]$FrameYear = "",
    [string]$FrameOutputDir = "data/level2_frames_v40_win",
    [int]$FrameWorkers = 12,
    [int]$FrameIoSlots = 4,
    [int]$FrameSevenZipThreads = 1,
    [string]$FrameStageDir = "C:/Omega_level2_stage",
    [switch]$NoCleanupFrameStage,
    [switch]$FrameExtractAll,
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
    [switch]$FrameGenerateReport,
    [string]$FrameReportPath = "audit/level2_v3_audit_report.md",
    [switch]$SkipFrameCompatibilityCheck,
    [int]$FrameCompatibilitySampleFiles = 96,
    [int]$FrameCompatibilityPrepareSmokeFiles = 3,
    [switch]$NoResume
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

$runtimeRoot = Join-Path $Root "audit\v40_runtime\windows"
$frameDir = Join-Path $runtimeRoot "frame"
$trainDir = Join-Path $runtimeRoot "train"
$backtestDir = Join-Path $runtimeRoot "backtest"
$manifestDir = Join-Path $runtimeRoot "manifests"

New-Item -ItemType Directory -Force -Path $frameDir | Out-Null
New-Item -ItemType Directory -Force -Path $trainDir | Out-Null
New-Item -ItemType Directory -Force -Path $backtestDir | Out-Null
New-Item -ItemType Directory -Force -Path $manifestDir | Out-Null

Push-Location $Root
try {

function Write-Stamp {
    param([string]$Msg)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$ts] $Msg"
}

function Assert-RepoPathExists {
    param([string]$RelativePath)
    $abs = Join-Path $Root $RelativePath
    if (-not (Test-Path $abs)) {
        throw "Required pipeline dependency not found: $RelativePath (resolved=$abs)"
    }
}

function Invoke-LoggedPython {
    param(
        [string[]]$ScriptArguments,
        [string]$LogPath
    )
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $LogPath) | Out-Null
    $cmdLine = "python " + ($ScriptArguments -join " ")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$ts] CMD: $cmdLine" | Tee-Object -FilePath $LogPath -Append
    $exitCode = $null
    $prevErrorAction = $ErrorActionPreference
    try {
        # Keep live stdout/stderr streaming to console+log, but do not let native stderr
        # warnings (e.g. sklearn InconsistentVersionWarning) terminate the PowerShell script.
        $ErrorActionPreference = "Continue"
        & python @ScriptArguments 2>&1 | ForEach-Object { $_.ToString() } | Tee-Object -FilePath $LogPath -Append
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $prevErrorAction
    }
    if ($exitCode -ne 0) {
        throw "Command failed: $cmdLine"
    }
}

function Resolve-LatestPolicy {
    param([string]$RootPath)
    $artifacts = Join-Path $RootPath "artifacts"
    $latest = Get-ChildItem -Path $artifacts -Filter "checkpoint_rows_*.pkl" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($null -eq $latest) {
        throw "No checkpoint_rows_*.pkl found under $artifacts"
    }
    return $latest.FullName
}

function Resolve-AbsPath {
    param([string]$PathLike)
    if ([System.IO.Path]::IsPathRooted($PathLike)) {
        return $PathLike
    }
    return (Join-Path $Root $PathLike)
}

function Resolve-ManifestEntryAbsPath {
    param(
        [string]$ManifestPath,
        [string]$Entry
    )
    $s = $Entry.Trim().Trim([char]0xFEFF)
    if ([string]::IsNullOrWhiteSpace($s)) {
        return ""
    }
    if ([System.IO.Path]::IsPathRooted($s)) {
        return [System.IO.Path]::GetFullPath($s)
    }
    $baseDir = Split-Path -Parent $ManifestPath
    if ([string]::IsNullOrWhiteSpace($baseDir)) {
        $baseDir = $Root
    }
    return [System.IO.Path]::GetFullPath((Join-Path $baseDir $s))
}

function Build-RoleManifest {
    param(
        [string]$InputDir,
        [string]$OutFile,
        [string]$Role,
        [string]$StatusPath,
        [string]$LogPath,
        [string]$DisallowOverlapWith = ""
    )
    $absInput = Resolve-AbsPath -PathLike $InputDir
    if (-not (Test-Path $absInput)) {
        throw "Input directory not found: $absInput"
    }

    $cmdArgs = @(
        "tools/build_dataset_manifest_v40.py",
        "--input-dir", $absInput,
        "--out-file", $OutFile,
        "--role", $Role,
        "--status-json", $StatusPath
    )
    if (-not [string]::IsNullOrWhiteSpace($TrainYears)) {
        $cmdArgs += "--train-years"
        $cmdArgs += $TrainYears
    }
    if (-not [string]::IsNullOrWhiteSpace($BacktestYears)) {
        $cmdArgs += "--backtest-years"
        $cmdArgs += $BacktestYears
    }
    if (-not [string]::IsNullOrWhiteSpace($BacktestYearMonths)) {
        $cmdArgs += "--backtest-year-months"
        $cmdArgs += $BacktestYearMonths
    }
    if ($AllowUnparsedFrameDatePrefix) {
        $cmdArgs += "--allow-unparsed-date-prefix"
    }
    if (-not [string]::IsNullOrWhiteSpace($DisallowOverlapWith) -and -not $AllowTrainBacktestOverlap) {
        $cmdArgs += "--disallow-overlap-with"
        $cmdArgs += $DisallowOverlapWith
    }

    Invoke-LoggedPython -ScriptArguments $cmdArgs -LogPath $LogPath

    $count = (Get-Content $OutFile | Measure-Object -Line).Lines
    if ($count -le 0) {
        throw "Manifest is empty for role=${Role}: $OutFile"
    }
    Write-Stamp "Manifest built: role=${Role} path=$OutFile files=$count"
}

function Assert-NoManifestOverlap {
    param(
        [string]$TrainManifestPath,
        [string]$BacktestManifestPath
    )
    if ($AllowTrainBacktestOverlap) {
        Write-Stamp "Overlap guard disabled by flag: AllowTrainBacktestOverlap"
        return
    }
    if (-not (Test-Path $TrainManifestPath)) {
        throw "Train manifest not found: $TrainManifestPath"
    }
    if (-not (Test-Path $BacktestManifestPath)) {
        throw "Backtest manifest not found: $BacktestManifestPath"
    }
    $trainSet = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($line in Get-Content $TrainManifestPath) {
        $s = Resolve-ManifestEntryAbsPath -ManifestPath $TrainManifestPath -Entry $line
        if (-not [string]::IsNullOrWhiteSpace($s)) {
            [void]$trainSet.Add($s)
        }
    }
    $overlap = New-Object System.Collections.Generic.List[string]
    foreach ($line in Get-Content $BacktestManifestPath) {
        $s = Resolve-ManifestEntryAbsPath -ManifestPath $BacktestManifestPath -Entry $line
        if ([string]::IsNullOrWhiteSpace($s)) {
            continue
        }
        if ($trainSet.Contains($s)) {
            [void]$overlap.Add($s)
            if ($overlap.Count -ge 20) {
                break
            }
        }
    }
    if ($overlap.Count -gt 0) {
        $examples = $overlap -join "; "
        throw "Train/Backtest manifest overlap detected (sample <=20): $examples"
    }
    Write-Stamp "Overlap check passed: train/backtest manifests are disjoint."
}

function Invoke-FrameCompatibilityCheck {
    param(
        [string]$InputDir,
        [string]$StatusPath,
        [string]$LogPath
    )
    if ($SkipFrameCompatibilityCheck) {
        Write-Stamp "Frame compatibility check skipped by flag."
        return
    }
    Write-Stamp "Frame compatibility preflight start"
    $cmdArgs = @(
        "tools/check_frame_train_backtest_compat.py",
        "--input-dir", $InputDir,
        "--sample-files", "$FrameCompatibilitySampleFiles",
        "--prepare-smoke-files", "$FrameCompatibilityPrepareSmokeFiles",
        "--status-json", $StatusPath
    )
    Invoke-LoggedPython -ScriptArguments $cmdArgs -LogPath $LogPath
    Write-Stamp "Frame compatibility preflight complete"
}

function Invoke-DatasetSplitPreflight {
    param(
        [string]$InputDir,
        [string]$StatusPath,
        [string]$LogPath
    )
    if ($SkipDatasetSplitPreflight) {
        Write-Stamp "Dataset split preflight skipped by flag."
        return
    }
    $absInput = Resolve-AbsPath -PathLike $InputDir
    Write-Stamp "Dataset split preflight start"
    $cmdArgs = @(
        "tools/preflight_dataset_split_v40.py",
        "--input-dir", $absInput,
        "--status-json", $StatusPath
    )
    if (-not [string]::IsNullOrWhiteSpace($TrainYears)) {
        $cmdArgs += "--train-years"
        $cmdArgs += $TrainYears
    }
    if (-not [string]::IsNullOrWhiteSpace($BacktestYears)) {
        $cmdArgs += "--backtest-years"
        $cmdArgs += $BacktestYears
    }
    if (-not [string]::IsNullOrWhiteSpace($BacktestYearMonths)) {
        $cmdArgs += "--backtest-year-months"
        $cmdArgs += $BacktestYearMonths
    }
    if ($AllowUnparsedFrameDatePrefix) {
        $cmdArgs += "--allow-unparsed-date-prefix"
    }
    Invoke-LoggedPython -ScriptArguments $cmdArgs -LogPath $LogPath
    Write-Stamp "Dataset split preflight complete"
}

$frameLog = Join-Path $frameDir "frame.log"
$frameStatus = Join-Path $frameDir "frame_status.json"
$frameCompatStatus = Join-Path $frameDir "frame_compat_status.json"
$frameCompatLog = Join-Path $frameDir "frame_compat.log"
$trainLog = Join-Path $trainDir "train.log"
$trainStatus = Join-Path $trainDir "train_status.json"
$backtestLog = Join-Path $backtestDir "backtest.log"
$backtestStatus = Join-Path $backtestDir "backtest_status.json"
$backtestState = Join-Path $backtestDir "backtest_state.json"

$trainManifest = Join-Path $manifestDir "train_files.txt"
$backtestManifest = Join-Path $manifestDir "backtest_files.txt"
$trainManifestStatus = Join-Path $manifestDir "train_manifest_status.json"
$backtestManifestStatus = Join-Path $manifestDir "backtest_manifest_status.json"
$splitPreflightStatus = Join-Path $manifestDir "split_preflight_status.json"
$splitPreflightLog = Join-Path $manifestDir "split_preflight.log"
$frameCompatChecked = $false
$splitPreflightChecked = $false

Assert-RepoPathExists -RelativePath "tools/build_dataset_manifest_v40.py"
Assert-RepoPathExists -RelativePath "tools/check_frame_train_backtest_compat.py"
Assert-RepoPathExists -RelativePath "parallel_trainer/run_parallel_v31.py"
Assert-RepoPathExists -RelativePath "parallel_trainer/run_parallel_backtest_v31.py"
if (-not $SkipDatasetSplitPreflight) {
    Assert-RepoPathExists -RelativePath "tools/preflight_dataset_split_v40.py"
}

if ([string]::IsNullOrWhiteSpace($TrainYears) -and [string]::IsNullOrWhiteSpace($BacktestYears) -and [string]::IsNullOrWhiteSpace($BacktestYearMonths)) {
    Write-Stamp "Dataset split policy: using config.py -> SplitConfig(train_years/test_years/test_year_months)."
}
else {
    Write-Stamp "Dataset split policy override: train_years='$TrainYears' backtest_years='$BacktestYears' backtest_year_months='$BacktestYearMonths'"
}

Write-Stamp (
    "Hardware profile defaults: " +
    "FrameWorkers=$FrameWorkers, " +
    "FrameIoSlots=$FrameIoSlots, " +
    "Frame7zThreads=$FrameSevenZipThreads, " +
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

if ($Stage -eq "frame" -or $Stage -eq "all") {
    Write-Stamp "Stage=frame start"
    $cmdArgs = @(
        "tools/run_l2_audit_driver.py",
        "--workers", "$FrameWorkers",
        "--io-slots", "$FrameIoSlots",
        "--seven-zip-threads", "$FrameSevenZipThreads",
        "--limit", "999999",
        "--output-dir", $FrameOutputDir,
        "--copy-to-local",
        "--stage-dir", "$FrameStageDir",
        "--memory-threshold", "$MemoryThreshold",
        "--status-json", $frameStatus
    )
    if ($FrameExtractAll) {
        $cmdArgs += "--extract-all"
    }
    else {
        $cmdArgs += "--extract-csv-only"
    }
    if (-not [string]::IsNullOrWhiteSpace($FrameYear)) {
        $cmdArgs += "--year"
        $cmdArgs += $FrameYear
    }
    if ($NoCleanupFrameStage) {
        $cmdArgs += "--no-cleanup-stage"
    }
    if ($FrameGenerateReport) {
        $cmdArgs += "--report"
        $cmdArgs += $FrameReportPath
    }
    else {
        # Report generation does a full collect() and can stall frame tail on large datasets.
        # Keep chain-safe default; run report explicitly when needed.
        $cmdArgs += "--skip-report"
    }
    Invoke-LoggedPython -ScriptArguments $cmdArgs -LogPath $frameLog
    Write-Stamp "Stage=frame complete"
}

if ($Stage -eq "train" -or $Stage -eq "all") {
    Write-Stamp "Stage=train start"
    Invoke-FrameCompatibilityCheck -InputDir $FrameOutputDir -StatusPath $frameCompatStatus -LogPath $frameCompatLog
    $frameCompatChecked = $true
    Invoke-DatasetSplitPreflight -InputDir $FrameOutputDir -StatusPath $splitPreflightStatus -LogPath $splitPreflightLog
    $splitPreflightChecked = $true
    Build-RoleManifest -InputDir $FrameOutputDir -OutFile $trainManifest -Role "train" -StatusPath $trainManifestStatus -LogPath $trainLog
    $cmdArgs = @(
        "parallel_trainer/run_parallel_v31.py",
        "--file-list", $trainManifest,
        "--workers", "$TrainWorkers",
        "--batch-rows", "$TrainBatchRows",
        "--checkpoint-rows", "$TrainCheckpointRows",
        "--planning-progress-every-lines", "$TrainPlanningProgressEveryLines",
        "--memory-threshold", "$MemoryThreshold",
        "--progress-every-files", "20",
        "--max-worker-errors", "500",
        "--stage-local",
        "--stage-dir", "$TrainStageDir",
        "--stage-chunk-files", "$TrainStageChunkFiles",
        "--stage-copy-workers", "$TrainStageCopyWorkers",
        "--status-json", $trainStatus
    )
    if ($NoCleanupTrainStage) {
        $cmdArgs += "--no-cleanup-stage"
    }
    if ($NoResume) {
        $cmdArgs += "--no-resume"
    }
    Invoke-LoggedPython -ScriptArguments $cmdArgs -LogPath $trainLog
    Write-Stamp "Stage=train complete"
}

if ($Stage -eq "backtest" -or $Stage -eq "all") {
    Write-Stamp "Stage=backtest start"
    if ([string]::IsNullOrWhiteSpace($BacktestFileList) -and -not $frameCompatChecked) {
        Invoke-FrameCompatibilityCheck -InputDir $FrameOutputDir -StatusPath $frameCompatStatus -LogPath $frameCompatLog
        $frameCompatChecked = $true
    }

    $resolvedPolicy = $PolicyPath
    if ([string]::IsNullOrWhiteSpace($resolvedPolicy)) {
        $resolvedPolicy = Resolve-LatestPolicy -RootPath $Root
    }

    $resolvedBacktestList = $BacktestFileList
    if ([string]::IsNullOrWhiteSpace($resolvedBacktestList)) {
        if (-not $splitPreflightChecked) {
            Invoke-DatasetSplitPreflight -InputDir $FrameOutputDir -StatusPath $splitPreflightStatus -LogPath $splitPreflightLog
            $splitPreflightChecked = $true
        }
        if (-not (Test-Path $trainManifest)) {
            Build-RoleManifest -InputDir $FrameOutputDir -OutFile $trainManifest -Role "train" -StatusPath $trainManifestStatus -LogPath $trainLog
        }
        Build-RoleManifest -InputDir $FrameOutputDir -OutFile $backtestManifest -Role "backtest" -StatusPath $backtestManifestStatus -LogPath $backtestLog -DisallowOverlapWith $trainManifest
        $resolvedBacktestList = $backtestManifest
    }
    else {
        $resolvedBacktestList = Resolve-AbsPath -PathLike $resolvedBacktestList
        if (-not (Test-Path $resolvedBacktestList)) {
            throw "Backtest file list not found: $resolvedBacktestList"
        }
        if (-not (Test-Path $trainManifest)) {
            Build-RoleManifest -InputDir $FrameOutputDir -OutFile $trainManifest -Role "train" -StatusPath $trainManifestStatus -LogPath $trainLog
        }
        Assert-NoManifestOverlap -TrainManifestPath $trainManifest -BacktestManifestPath $resolvedBacktestList
        Write-Stamp "Using custom backtest file list: $resolvedBacktestList"
    }

    $cmdArgs = @(
        "parallel_trainer/run_parallel_backtest_v31.py",
        "--policy", $resolvedPolicy,
        "--file-list", $resolvedBacktestList,
        "--workers", "$BacktestWorkers",
        "--planning-progress-every-lines", "$BacktestPlanningProgressEveryLines",
        "--memory-threshold", "$MemoryThreshold",
        "--max-file-errors", "0",
        "--fail-on-audit-failed",
        "--save-every-files", "20",
        "--state-save-every-files", "$BacktestStateSaveEveryFiles",
        "--stage-local",
        "--stage-dir", "$BacktestStageDir",
        "--stage-chunk-files", "$BacktestStageChunkFiles",
        "--stage-copy-workers", "$BacktestStageCopyWorkers",
        "--state-file", $backtestState,
        "--status-json", $backtestStatus
    )
    if ($NoCleanupBacktestStage) {
        $cmdArgs += "--no-cleanup-stage"
    }
    if ($NoResume) {
        $cmdArgs += "--no-resume"
    }
    Invoke-LoggedPython -ScriptArguments $cmdArgs -LogPath $backtestLog
    Write-Stamp "Stage=backtest complete"
}

Write-Stamp "Pipeline done. Logs root: $runtimeRoot"
}
finally {
    Pop-Location
}
