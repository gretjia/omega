param(
    [int]$Workers = 22,
    [int]$IoSlots = 4,
    [int]$SevenZipThreads = 1,
    [double]$MemoryThreshold = 88.0,
    [string]$OutputDir = "D:/Omega_frames/v50/output",
    [string]$StageDir = "D:/Omega_frames/v50/stage",
    [string]$Root = "C:\Omega_vNext",
    [string]$ProfilePath = "configs/hardware/active_profile.yaml",
    [switch]$NoResume = $false,
    [switch]$UseLegacyDriver = $false
)

$ErrorActionPreference = "Continue"

if (-not $UseLegacyDriver) {
    $pipelineScript = Join-Path $PSScriptRoot "run_reframe_backtest_interval_pipeline_detached.ps1"
    if (-not (Test-Path -LiteralPath $pipelineScript)) {
        throw "Pipeline reframe entry not found: $pipelineScript"
    }

    Write-Host "[INFO] Legacy frame driver disabled by default; forwarding to pipeline entry."
    & powershell -NoProfile -ExecutionPolicy Bypass -File $pipelineScript `
        -Root $Root `
        -OutputDir $OutputDir `
        -StageDir $StageDir `
        -ProfilePath $ProfilePath `
        -NoResume:$NoResume
    exit $LASTEXITCODE
}

$root = $Root
$runtimeRoot = Join-Path $root "audit\v51_runtime\windows\frame"
$logPath = Join-Path $runtimeRoot "reframe_backtest_interval.log"
$exitPath = Join-Path $runtimeRoot "reframe_backtest_interval_exit_code.txt"
$status2025 = Join-Path $runtimeRoot "frame_status_2025.json"
$status202601 = Join-Path $runtimeRoot "frame_status_202601.json"
$manifestPath = Join-Path $root "audit\v5_runtime\windows\manifests\backtest_files.txt"
$stateFile = Join-Path $OutputDir "_audit_state.jsonl"
$py = "C:\Python314\python.exe"

New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null

foreach ($f in @($logPath, $exitPath, $status2025, $status202601)) {
    if (Test-Path $f) {
        Remove-Item -LiteralPath $f -Force -ErrorAction SilentlyContinue
    }
}

function Write-Log {
    param([string]$Text)
    $line = ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Text)
    $line | Tee-Object -FilePath $logPath -Append | Out-Null
}

function Invoke-FrameYear {
    param(
        [string]$YearToken,
        [string]$StatusPath
    )
    $args = @(
        "tools/run_l2_audit_driver.py",
        "--workers", [string]$Workers,
        "--io-slots", [string]$IoSlots,
        "--seven-zip-threads", [string]$SevenZipThreads,
        "--limit", "999999",
        "--output-dir", $OutputDir,
        "--copy-to-local",
        "--stage-dir", $StageDir,
        "--memory-threshold", [string]$MemoryThreshold,
        "--status-json", $StatusPath,
        "--extract-csv-only",
        "--skip-report",
        "--year", $YearToken
    )

    Write-Log ("FRAME YEAR={0} CMD={1} {2}" -f $YearToken, $py, ($args -join " "))
    & $py @args 2>&1 | Tee-Object -FilePath $logPath -Append
    $code = $LASTEXITCODE
    Write-Log ("FRAME YEAR={0} EXIT={1}" -f $YearToken, $code)
    if ($code -ne 0) {
        throw "Frame year $YearToken failed with exit code $code"
    }
}

Set-Location $root
Write-Log "START reframe backtest interval (2025 + 202601)"
Write-Log ("OutputDir={0}" -f $OutputDir)
Write-Log ("StageDir={0}" -f $StageDir)
Write-Log ("Workers={0}, IoSlots={1}, SevenZipThreads={2}, MemoryThreshold={3}" -f $Workers, $IoSlots, $SevenZipThreads, $MemoryThreshold)

try {
    if (-not (Test-Path $manifestPath)) {
        throw "Backtest manifest not found: $manifestPath"
    }

    # 1) Delete existing backtest parquet files only (strictly from manifest)
    $toDelete = @()
    foreach ($line in Get-Content -LiteralPath $manifestPath) {
        $s = $line.Trim().Trim([char]0xFEFF)
        if ([string]::IsNullOrWhiteSpace($s)) { continue }
        $toDelete += $s
    }
    Write-Log ("Manifest entries to refresh: {0}" -f $toDelete.Count)

    $deleted = 0
    foreach ($p in $toDelete) {
        if (Test-Path -LiteralPath $p) {
            Remove-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
            if (-not (Test-Path -LiteralPath $p)) {
                $deleted += 1
            }
        }
    }
    Write-Log ("Deleted existing backtest parquet files: {0}" -f $deleted)

    # 2) Reset frame state to force re-processing under new P4 ETL rules.
    if (Test-Path -LiteralPath $stateFile) {
        Remove-Item -LiteralPath $stateFile -Force -ErrorAction SilentlyContinue
        Write-Log ("Removed state file: {0}" -f $stateFile)
    }
    else {
        Write-Log ("State file not found (skip): {0}" -f $stateFile)
    }

    # 3) Rebuild backtest years only
    Invoke-FrameYear -YearToken "2025" -StatusPath $status2025
    Invoke-FrameYear -YearToken "202601" -StatusPath $status202601

    Write-Log "END reframe backtest interval EXIT=0"
    Set-Content -LiteralPath $exitPath -Value "0" -Encoding UTF8
    exit 0
}
catch {
    $_ | Out-String | Tee-Object -FilePath $logPath -Append | Out-Null
    Write-Log "END reframe backtest interval EXIT=1"
    Set-Content -LiteralPath $exitPath -Value "1" -Encoding UTF8
    exit 1
}
