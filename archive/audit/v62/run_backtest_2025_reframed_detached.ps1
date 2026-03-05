param(
    [string]$Root = "C:\Omega_vNext",
    [string]$OutputDir = "D:\Omega_frames\v50\output",
    [string]$PolicyPath = "",
    [string]$ReframeStart = "2026-02-13 11:10:10",
    [int]$Workers = 8,
    [double]$MemoryThreshold = 98.0,
    [switch]$FailOnAuditFailed = $false
)

$ErrorActionPreference = "Continue"

$runtimeRoot = Join-Path $Root "audit\v51_runtime\windows\backtest_patch_2025_reframed"
$manifestDir = Join-Path $runtimeRoot "manifests"
$logPath = Join-Path $runtimeRoot "backtest.log"
$statusPath = Join-Path $runtimeRoot "backtest_status.json"
$statePath = Join-Path $runtimeRoot "backtest_state.json"
$exitPath = Join-Path $runtimeRoot "backtest_exit_code.txt"
$manifestPath = Join-Path $manifestDir "backtest_files_2025_reframed.txt"
$launcherLog = Join-Path $runtimeRoot "launcher.log"
$policyRecord = Join-Path $runtimeRoot "policy_path.txt"
$py = "C:\Python314\python.exe"
$stageDir = "D:/Omega_backtest_stage_v51_reframed_2025"

New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null
New-Item -ItemType Directory -Force -Path $manifestDir | Out-Null

foreach ($f in @($logPath, $statusPath, $statePath, $exitPath, $manifestPath, $launcherLog, $policyRecord)) {
    if (Test-Path -LiteralPath $f) {
        Remove-Item -LiteralPath $f -Force -ErrorAction SilentlyContinue
    }
}

function Write-LaunchLog {
    param([string]$Text)
    $line = ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Text)
    $line | Tee-Object -FilePath $launcherLog -Append | Out-Null
}

function Resolve-PolicyPath {
    param(
        [string]$RootDir,
        [string]$Preferred
    )
    if (-not [string]::IsNullOrWhiteSpace($Preferred)) {
        if (Test-Path -LiteralPath $Preferred) {
            return $Preferred
        }
        throw "PolicyPath does not exist: $Preferred"
    }

    $pipelinePolicy = Join-Path $RootDir "audit\v5_runtime\windows\pipeline\full_noresume_policy.txt"
    if (Test-Path -LiteralPath $pipelinePolicy) {
        $candidate = (Get-Content -LiteralPath $pipelinePolicy -TotalCount 1).Trim()
        if (-not [string]::IsNullOrWhiteSpace($candidate) -and (Test-Path -LiteralPath $candidate)) {
            return $candidate
        }
    }

    $latest = Get-ChildItem -LiteralPath (Join-Path $RootDir "artifacts") -Filter "checkpoint_rows_*.pkl" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($null -ne $latest) {
        return $latest.FullName
    }
    throw "No usable policy checkpoint found."
}

Set-Location $Root
Write-LaunchLog "START v51 backtest patch (2025 reframed subset)"
Write-LaunchLog ("Root={0}" -f $Root)
Write-LaunchLog ("OutputDir={0}" -f $OutputDir)
Write-LaunchLog ("ReframeStart={0}" -f $ReframeStart)
Write-LaunchLog ("Workers={0}" -f $Workers)
Write-LaunchLog ("MemoryThreshold={0}" -f $MemoryThreshold)
Write-LaunchLog ("FailOnAuditFailed={0}" -f $FailOnAuditFailed)

try {
    $startTs = [datetime]::ParseExact($ReframeStart, "yyyy-MM-dd HH:mm:ss", $null)
    $subset = Get-ChildItem -LiteralPath $OutputDir -Filter "2025*.parquet" -File -ErrorAction Stop |
        Where-Object { $_.LastWriteTime -ge $startTs } |
        Sort-Object Name

    if ($null -eq $subset -or $subset.Count -eq 0) {
        throw "No 2025 reframed parquet files found since $ReframeStart."
    }

    $subset.FullName | Set-Content -LiteralPath $manifestPath -Encoding UTF8
    Write-LaunchLog ("Manifest={0}" -f $manifestPath)
    Write-LaunchLog ("ManifestFiles={0}" -f $subset.Count)
    Write-LaunchLog ("FirstFile={0}" -f $subset[0].Name)
    Write-LaunchLog ("LastFile={0}" -f $subset[$subset.Count - 1].Name)

    $resolvedPolicy = Resolve-PolicyPath -RootDir $Root -Preferred $PolicyPath
    Set-Content -LiteralPath $policyRecord -Value $resolvedPolicy -Encoding UTF8
    Write-LaunchLog ("Policy={0}" -f $resolvedPolicy)

    $args = @(
        "parallel_trainer/run_parallel_backtest_v31.py",
        "--file-list", $manifestPath,
        "--policy", $resolvedPolicy,
        "--workers", [string]$Workers,
        "--save-every-files", "20",
        "--state-save-every-files", "50",
        "--planning-progress-every-lines", "50000",
        "--memory-threshold", [string]$MemoryThreshold,
        "--max-file-errors", "500",
        "--state-file", $statePath,
        "--status-json", $statusPath,
        "--stage-local",
        "--stage-dir", $stageDir,
        "--stage-chunk-files", "16",
        "--stage-copy-workers", "4",
        "--no-resume"
    )

    if ($FailOnAuditFailed) {
        $args += "--fail-on-audit-failed"
    }
    else {
        $args += "--allow-audit-failed"
    }

    Write-LaunchLog ("RUN CMD={0} {1}" -f $py, ($args -join " "))
    & $py @args 2>&1 | Tee-Object -FilePath $logPath -Append
    $code = $LASTEXITCODE

    Write-LaunchLog ("END v51 backtest patch EXIT={0}" -f $code)
    Set-Content -LiteralPath $exitPath -Value "$code" -Encoding UTF8
    exit $code
}
catch {
    $_ | Out-String | Tee-Object -FilePath $launcherLog -Append | Out-Null
    Write-LaunchLog "END v51 backtest patch EXIT=1"
    Set-Content -LiteralPath $exitPath -Value "1" -Encoding UTF8
    exit 1
}
