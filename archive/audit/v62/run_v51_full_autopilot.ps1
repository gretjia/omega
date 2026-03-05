param(
    [string]$Root = "C:\Omega_vNext",
    [string]$OutputDir = "D:\Omega_frames\v50\output",
    [string]$StageDir = "D:\Omega_frames\v50\stage",
    [string]$SourceDir = "E:\data\level2",
    [string]$ProfilePath = "configs/hardware/active_profile.yaml",
    [int]$TrainWorkers = 6,
    [int]$BacktestWorkers = 8,
    [double]$TrainMemoryThreshold = 98.0,
    [double]$BacktestMemoryThreshold = 98.0,
    [int]$MonitorIntervalSec = 300,
    [switch]$AllowAuditFailed = $true
)

$ErrorActionPreference = "Stop"

$runtimeRoot = Join-Path $Root "audit\v51_runtime\windows\full_autopilot"
$frameRuntime = Join-Path $runtimeRoot "frame_decjan"
$manifestDir = Join-Path $runtimeRoot "manifests"
$trainRuntime = Join-Path $runtimeRoot "train"
$backtestRuntime = Join-Path $runtimeRoot "backtest"

$masterLog = Join-Path $runtimeRoot "autopilot.log"
$statusPath = Join-Path $runtimeRoot "autopilot_status.json"
$summaryPath = Join-Path $runtimeRoot "autopilot_summary.json"
$exitPath = Join-Path $runtimeRoot "autopilot_exit_code.txt"
$pidPath = Join-Path $runtimeRoot "autopilot.pid"

$frameScript = Join-Path $frameRuntime "run_frame_202512_202601.py"
$frameStdout = Join-Path $frameRuntime "frame.stdout.log"
$frameStderr = Join-Path $frameRuntime "frame.stderr.log"
$frameReportPath = Join-Path $frameRuntime "frame_decjan_report.json"

$trainManifest = Join-Path $manifestDir "train_files.txt"
$backtestManifest = Join-Path $manifestDir "backtest_files.txt"
$manifestReportPath = Join-Path $manifestDir "manifest_report.json"

$trainStatus = Join-Path $trainRuntime "train_status.json"
$trainStdout = Join-Path $trainRuntime "train.stdout.log"
$trainStderr = Join-Path $trainRuntime "train.stderr.log"
$trainExitPath = Join-Path $trainRuntime "train_exit_code.txt"
$trainPolicyPath = Join-Path $trainRuntime "train_policy_path.txt"

$backtestStatus = Join-Path $backtestRuntime "backtest_status.json"
$backtestState = Join-Path $backtestRuntime "backtest_state.json"
$backtestStdout = Join-Path $backtestRuntime "backtest.stdout.log"
$backtestStderr = Join-Path $backtestRuntime "backtest.stderr.log"
$backtestExitPath = Join-Path $backtestRuntime "backtest_exit_code.txt"

$auditPath = Join-Path $Root "audit\v51_deep_audit.md"
$py = "C:\Python314\python.exe"

New-Item -ItemType Directory -Force -Path $runtimeRoot, $frameRuntime, $manifestDir, $trainRuntime, $backtestRuntime | Out-Null

foreach ($f in @($masterLog, $statusPath, $summaryPath, $exitPath, $frameStdout, $frameStderr, $frameReportPath, $manifestReportPath,
    $trainStdout, $trainStderr, $trainStatus, $trainExitPath, $trainPolicyPath,
    $backtestStdout, $backtestStderr, $backtestStatus, $backtestState, $backtestExitPath)) {
    if (Test-Path -LiteralPath $f) {
        Remove-Item -LiteralPath $f -Force -ErrorAction SilentlyContinue
    }
}

function Write-Log {
    param([string]$Text)
    $line = ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Text)
    $line | Tee-Object -FilePath $masterLog -Append | Out-Null
}

function Write-Status {
    param(
        [string]$Phase,
        [string]$State,
        [hashtable]$Extra
    )
    if ($null -eq $Extra) { $Extra = @{} }
    $obj = [ordered]@{
        timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        phase = $Phase
        state = $State
    }
    foreach ($k in $Extra.Keys) {
        $obj[$k] = $Extra[$k]
    }
    ($obj | ConvertTo-Json -Depth 12) | Set-Content -LiteralPath $statusPath -Encoding UTF8
}

function Invoke-TrackedProcess {
    param(
        [string]$Name,
        [string]$Phase,
        [string]$Exe,
        [string[]]$ArgList,
        [string]$StdoutPath,
        [string]$StderrPath,
        [string]$StepStatusPath = ""
    )

    foreach ($f in @($StdoutPath, $StderrPath)) {
        if (Test-Path -LiteralPath $f) {
            Remove-Item -LiteralPath $f -Force -ErrorAction SilentlyContinue
        }
    }

    if ($null -eq $ArgList) {
        Write-Log ("DEBUG {0} ArgList is NULL" -f $Name)
    } else {
        Write-Log ("DEBUG {0} ArgListCount={1}" -f $Name, $ArgList.Count)
    }

    $argLine = ($ArgList | ForEach-Object {
        if ($_ -match "\s") { '"' + $_ + '"' } else { $_ }
    }) -join " "

    Write-Log ("RUN {0} CMD={1} {2}" -f $Name, $Exe, $argLine)

    $start = Get-Date
    $proc = Start-Process -FilePath $Exe -ArgumentList $argLine -PassThru -WindowStyle Hidden -RedirectStandardOutput $StdoutPath -RedirectStandardError $StderrPath

    Write-Status -Phase $Phase -State "running" -Extra @{ step = $Name; pid = $proc.Id; start_time = ($start.ToString("yyyy-MM-dd HH:mm:ss")) }

    while (-not $proc.HasExited) {
        Start-Sleep -Seconds $MonitorIntervalSec
        $elapsed = [int]((Get-Date) - $start).TotalSeconds
        $extra = @{ step = $Name; pid = $proc.Id; elapsed_sec = $elapsed }

        if ($Phase -eq "frame") {
            try {
                $extra["dec_parquet_count"] = (Get-ChildItem -LiteralPath $OutputDir -Filter "202512*.parquet" -File -ErrorAction SilentlyContinue).Count
                $extra["jan_parquet_count"] = (Get-ChildItem -LiteralPath $OutputDir -Filter "202601*.parquet" -File -ErrorAction SilentlyContinue).Count
            } catch {}
        }

        if ((-not [string]::IsNullOrWhiteSpace($StepStatusPath)) -and (Test-Path -LiteralPath $StepStatusPath)) {
            try {
                $s = Get-Content -LiteralPath $StepStatusPath -Raw | ConvertFrom-Json
                foreach ($k in @("status", "phase", "files_processed_in_run", "total_tasks", "error_count", "total_rows", "total_trades", "total_pnl", "timestamp", "workers", "final_audit_status", "avg_align")) {
                    if ($s.PSObject.Properties.Name -contains $k) {
                        $extra[$k] = $s.$k
                    }
                }
            } catch {}
        }

        Write-Status -Phase $Phase -State "running" -Extra $extra
    }

    $proc.WaitForExit()
    $code = $proc.ExitCode
    Write-Log ("END {0} EXIT={1}" -f $Name, $code)
    return $code
}

function Get-UniqueDateTokensFromSource {
    param([string]$Needle)
    $items = Get-ChildItem -LiteralPath $SourceDir -Recurse -Filter "*.7z" -File -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -like ("*" + $Needle + "*") }
    $tokens = $items | ForEach-Object { $_.BaseName } | Where-Object { $_ -match "^\d{8}$" } | Sort-Object -Unique
    return @($tokens)
}

function Get-UniqueDateTokensFromOutput {
    param([string]$PrefixPattern)
    $items = Get-ChildItem -LiteralPath $OutputDir -Filter ($PrefixPattern + "*.parquet") -File -ErrorAction SilentlyContinue
    $tokens = $items | ForEach-Object { $_.BaseName } | Where-Object { $_ -match "^\d{8}$" } | Sort-Object -Unique
    return @($tokens)
}

function New-Manifest {
    param([string[]]$Prefixes, [string]$OutPath)
    $all = @()
    foreach ($p in $Prefixes) {
        $all += Get-ChildItem -LiteralPath $OutputDir -Filter ($p + "*.parquet") -File -ErrorAction SilentlyContinue
    }
    $sorted = $all | Sort-Object Name
    $sorted.FullName | Set-Content -LiteralPath $OutPath -Encoding UTF8
    return $sorted
}

function Append-AuditUpdate {
    param(
        [hashtable]$FrameReport,
        [hashtable]$ManifestReport,
        [hashtable]$TrainBrief,
        [hashtable]$BacktestBrief
    )

    if (-not (Test-Path -LiteralPath $auditPath)) {
        Set-Content -LiteralPath $auditPath -Value "# OMEGA v5.1 Deep Audit" -Encoding UTF8
    }

    $now = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $lines = @()
    $lines += ""
    $lines += "## Autonomous Full Pipeline Update ($now)"
    $lines += "- Trigger: unattended autopilot (frame 202512+202601 -> full train -> full backtest)."
    $lines += "- Runtime Root: $runtimeRoot"
    $lines += ""
    $lines += "### Frame (202512 + 202601)"
    $lines += ("- expected_dec_unique: {0}" -f $FrameReport.expected_dec_unique)
    $lines += ("- expected_jan_unique: {0}" -f $FrameReport.expected_jan_unique)
    $lines += ("- produced_dec_unique: {0}" -f $FrameReport.produced_dec_unique)
    $lines += ("- produced_jan_unique: {0}" -f $FrameReport.produced_jan_unique)
    $lines += ("- missing_unique_total: {0}" -f $FrameReport.missing_unique_total)
    if ($FrameReport.missing_unique_total -gt 0) {
        $missingStr = ($FrameReport.missing_tokens -join ",")
        $lines += ("- missing_tokens: {0}" -f $missingStr)
    }
    $lines += ""
    $lines += "### Manifests"
    $lines += ("- train_manifest: {0} files ({1})" -f $ManifestReport.train_count, $ManifestReport.train_years)
    $lines += ("- backtest_manifest: {0} files ({1})" -f $ManifestReport.backtest_count, $ManifestReport.backtest_years)
    $lines += ""
    $lines += "### Train"
    $lines += ("- exit_code: {0}" -f $TrainBrief.exit_code)
    $lines += ("- policy: {0}" -f $TrainBrief.policy)
    $lines += ("- total_rows: {0}" -f $TrainBrief.total_rows)
    $lines += ("- files_processed: {0}" -f $TrainBrief.files_processed)
    $lines += ""
    $lines += "### Backtest"
    $lines += ("- exit_code: {0}" -f $BacktestBrief.exit_code)
    $lines += ("- status: {0}" -f $BacktestBrief.status)
    $lines += ("- final_audit_status: {0}" -f $BacktestBrief.final_audit_status)
    $lines += ("- total_tasks: {0}" -f $BacktestBrief.total_tasks)
    $lines += ("- files_processed: {0}" -f $BacktestBrief.files_processed)
    $lines += ("- total_rows: {0}" -f $BacktestBrief.total_rows)
    $lines += ("- total_trades: {0}" -f $BacktestBrief.total_trades)
    $lines += ("- total_pnl: {0}" -f $BacktestBrief.total_pnl)
    $lines += ("- avg_snr: {0}" -f $BacktestBrief.avg_snr)
    $lines += ("- avg_orth: {0}" -f $BacktestBrief.avg_orth)
    $lines += ("- avg_align: {0}" -f $BacktestBrief.avg_align)

    Add-Content -LiteralPath $auditPath -Value ($lines -join "`r`n") -Encoding UTF8
}

Set-Content -LiteralPath $pidPath -Value $PID -Encoding UTF8
Write-Log "START v51 full autopilot"
Write-Log ("Root={0}" -f $Root)
Write-Log ("OutputDir={0}" -f $OutputDir)
Write-Log ("StageDir={0}" -f $StageDir)
Write-Log ("SourceDir={0}" -f $SourceDir)
Write-Log ("TrainWorkers={0}, BacktestWorkers={1}" -f $TrainWorkers, $BacktestWorkers)
Write-Log ("TrainMemoryThreshold={0}, BacktestMemoryThreshold={1}" -f $TrainMemoryThreshold, $BacktestMemoryThreshold)
Write-Log ("AllowAuditFailed={0}" -f $AllowAuditFailed)
Write-Status -Phase "init" -State "running" -Extra @{}

$frameReport = @{}
$manifestReport = @{}
$trainBrief = @{}
$backtestBrief = @{}

try {
    Set-Location $Root

    # Phase 1: Frame 202512 + 202601
    Write-Status -Phase "frame" -State "starting" -Extra @{}

    $decExpected = Get-UniqueDateTokensFromSource -Needle "202512"
    $janExpected = Get-UniqueDateTokensFromSource -Needle "202601"

    $removed = 0
    foreach ($pat in @("202512*.parquet", "202601*.parquet")) {
        $items = Get-ChildItem -LiteralPath $OutputDir -Filter $pat -File -ErrorAction SilentlyContinue
        foreach ($it in $items) {
            try {
                Remove-Item -LiteralPath $it.FullName -Force -ErrorAction Stop
                $removed += 1
            } catch {}
        }
    }
    Write-Log ("Frame pre-clean removed month parquet files: {0}" -f $removed)

    @'
import os
import sys

sys.path.append(os.getcwd())

from pipeline.config.loader import ConfigLoader
from pipeline.adapters.v3_adapter import OmegaCoreAdapter
from pipeline.engine.framer import Framer
from config import load_l2_pipeline_config


def main():
    root = os.environ.get("OMEGA_ROOT", "C:/Omega_vNext")
    profile_path = os.environ.get("OMEGA_PROFILE", "configs/hardware/active_profile.yaml")
    output_dir = os.environ.get("OMEGA_OUTPUT", "D:/Omega_frames/v50/output")
    stage_dir = os.environ.get("OMEGA_STAGE", "D:/Omega_frames/v50/stage")

    os.chdir(root)
    profile = ConfigLoader.load_hardware_profile(profile_path)
    profile.storage.output_root = output_dir
    profile.storage.stage_root = stage_dir

    cfg = load_l2_pipeline_config()
    core = OmegaCoreAdapter()
    core.initialize({"pipeline_cfg": cfg})

    def logger(msg: str):
        print(msg, flush=True)

    fr = Framer(profile, core, logger=logger)
    fr.run(year_filter="202512", limit=0)
    fr.run(year_filter="202601", limit=0)


if __name__ == "__main__":
    main()
'@ | Set-Content -LiteralPath $frameScript -Encoding UTF8

    $env:OMEGA_ROOT = $Root
    $env:OMEGA_PROFILE = $ProfilePath
    $env:OMEGA_OUTPUT = $OutputDir
    $env:OMEGA_STAGE = $StageDir

    Write-Log ("FrameScript={0}" -f $frameScript)
    Write-Log ("FrameScriptExists={0}" -f (Test-Path -LiteralPath $frameScript))
    $frameCode = Invoke-TrackedProcess -Name "frame_decjan" -Phase "frame" -Exe $py -ArgList @($frameScript) -StdoutPath $frameStdout -StderrPath $frameStderr
    if ($frameCode -ne 0) {
        throw "Frame step failed with exit code $frameCode"
    }

    $decProduced = Get-UniqueDateTokensFromOutput -PrefixPattern "202512"
    $janProduced = Get-UniqueDateTokensFromOutput -PrefixPattern "202601"

    $expectedAll = @($decExpected + $janExpected | Sort-Object -Unique)
    $producedAll = @($decProduced + $janProduced | Sort-Object -Unique)
    $producedSet = @{}
    foreach ($d in $producedAll) { $producedSet[$d] = $true }
    $missing = @()
    foreach ($d in $expectedAll) {
        if (-not $producedSet.ContainsKey($d)) { $missing += $d }
    }

    $frameReport = [ordered]@{
        expected_dec_unique = $decExpected.Count
        expected_jan_unique = $janExpected.Count
        produced_dec_unique = $decProduced.Count
        produced_jan_unique = $janProduced.Count
        expected_total_unique = $expectedAll.Count
        produced_total_unique = $producedAll.Count
        missing_unique_total = $missing.Count
        missing_tokens = $missing
    }
    ($frameReport | ConvertTo-Json -Depth 8) | Set-Content -LiteralPath $frameReportPath -Encoding UTF8

    if ($missing.Count -gt 0) {
        Write-Log ("Frame completed with missing tokens: {0}" -f ($missing -join ","))
    } else {
        Write-Log "Frame completed with full token coverage for 202512+202601."
    }

    # Phase 2: Regenerate manifests
    Write-Status -Phase "manifest" -State "running" -Extra @{}
    $trainFiles = New-Manifest -Prefixes @("2023", "2024") -OutPath $trainManifest
    $backtestFiles = New-Manifest -Prefixes @("2025", "202601") -OutPath $backtestManifest

    if ($trainFiles.Count -eq 0) {
        throw "Train manifest empty: $trainManifest"
    }
    if ($backtestFiles.Count -eq 0) {
        throw "Backtest manifest empty: $backtestManifest"
    }

    $trainYearSet = $trainFiles | ForEach-Object { $_.BaseName.Substring(0,4) } | Sort-Object -Unique
    $backtestYearSet = $backtestFiles | ForEach-Object { $_.BaseName.Substring(0,4) } | Sort-Object -Unique

    $manifestReport = [ordered]@{
        train_count = $trainFiles.Count
        backtest_count = $backtestFiles.Count
        train_years = ($trainYearSet -join ",")
        backtest_years = ($backtestYearSet -join ",")
        train_manifest = $trainManifest
        backtest_manifest = $backtestManifest
        train_first = $trainFiles[0].Name
        train_last = $trainFiles[$trainFiles.Count - 1].Name
        backtest_first = $backtestFiles[0].Name
        backtest_last = $backtestFiles[$backtestFiles.Count - 1].Name
    }
    ($manifestReport | ConvertTo-Json -Depth 8) | Set-Content -LiteralPath $manifestReportPath -Encoding UTF8
    Write-Log ("Manifest regenerated: train={0}, backtest={1}" -f $trainFiles.Count, $backtestFiles.Count)

    # Phase 3: Full training
    Write-Status -Phase "train" -State "starting" -Extra @{ manifest = $trainManifest }

    $trainStart = Get-Date
    $trainArgs = @(
        "parallel_trainer/run_parallel_v31.py",
        "--file-list", $trainManifest,
        "--workers", [string]$TrainWorkers,
        "--batch-rows", "750000",
        "--checkpoint-rows", "1500000",
        "--planning-progress-every-lines", "50000",
        "--memory-threshold", [string]$TrainMemoryThreshold,
        "--progress-every-files", "10",
        "--max-worker-errors", "500",
        "--stage-local",
        "--stage-dir", "D:/Omega_train_stage_v51_full",
        "--stage-chunk-files", "16",
        "--stage-copy-workers", "4",
        "--status-json", $trainStatus,
        "--no-resume"
    )

    $trainCode = Invoke-TrackedProcess -Name "train_full" -Phase "train" -Exe $py -ArgList $trainArgs -StdoutPath $trainStdout -StderrPath $trainStderr -StepStatusPath $trainStatus
    Set-Content -LiteralPath $trainExitPath -Value "$trainCode" -Encoding UTF8
    if ($trainCode -ne 0) {
        throw "Training failed with exit code $trainCode"
    }

    $newCkpt = Get-ChildItem -LiteralPath (Join-Path $Root "artifacts") -Filter "checkpoint_rows_*.pkl" -File -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -ge $trainStart } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($null -eq $newCkpt) {
        $newCkpt = Get-ChildItem -LiteralPath (Join-Path $Root "artifacts") -Filter "checkpoint_rows_*.pkl" -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        if ($null -eq $newCkpt) {
            throw "No checkpoint_rows_*.pkl found after training"
        }
        Write-Log "Warning: no strictly-new checkpoint found by timestamp; fallback to latest checkpoint."
    }

    $policyPath = $newCkpt.FullName
    Set-Content -LiteralPath $trainPolicyPath -Value $policyPath -Encoding UTF8
    Write-Log ("Selected policy: {0}" -f $policyPath)

    $trainStatusObj = $null
    if (Test-Path -LiteralPath $trainStatus) {
        try { $trainStatusObj = Get-Content -LiteralPath $trainStatus -Raw | ConvertFrom-Json } catch {}
    }

    $trainBrief = [ordered]@{
        exit_code = $trainCode
        policy = $policyPath
        total_rows = $(if ($trainStatusObj) { $trainStatusObj.total_rows } else { $null })
        files_processed = $(if ($trainStatusObj) { $trainStatusObj.files_processed_in_run } else { $null })
    }

    # Phase 4: Full backtest
    Write-Status -Phase "backtest" -State "starting" -Extra @{ manifest = $backtestManifest; policy = $policyPath }

    $backtestArgs = @(
        "parallel_trainer/run_parallel_backtest_v31.py",
        "--file-list", $backtestManifest,
        "--policy", $policyPath,
        "--workers", [string]$BacktestWorkers,
        "--save-every-files", "20",
        "--state-save-every-files", "50",
        "--planning-progress-every-lines", "50000",
        "--memory-threshold", [string]$BacktestMemoryThreshold,
        "--max-file-errors", "500",
        "--state-file", $backtestState,
        "--status-json", $backtestStatus,
        "--stage-local",
        "--stage-dir", "D:/Omega_backtest_stage_v51_full",
        "--stage-chunk-files", "16",
        "--stage-copy-workers", "4",
        "--no-resume"
    )

    if ($AllowAuditFailed) {
        $backtestArgs += "--allow-audit-failed"
    } else {
        $backtestArgs += "--fail-on-audit-failed"
    }

    $backtestCode = Invoke-TrackedProcess -Name "backtest_full" -Phase "backtest" -Exe $py -ArgList $backtestArgs -StdoutPath $backtestStdout -StderrPath $backtestStderr -StepStatusPath $backtestStatus
    Set-Content -LiteralPath $backtestExitPath -Value "$backtestCode" -Encoding UTF8

    $backtestStatusObj = $null
    if (Test-Path -LiteralPath $backtestStatus) {
        try { $backtestStatusObj = Get-Content -LiteralPath $backtestStatus -Raw | ConvertFrom-Json } catch {}
    }

    $backtestBrief = [ordered]@{
        exit_code = $backtestCode
        status = $(if ($backtestStatusObj) { $backtestStatusObj.status } else { $null })
        final_audit_status = $(if ($backtestStatusObj) { $backtestStatusObj.final_audit_status } else { $null })
        total_tasks = $(if ($backtestStatusObj) { $backtestStatusObj.total_tasks } else { $null })
        files_processed = $(if ($backtestStatusObj) { $backtestStatusObj.files_processed_in_run } else { $null })
        total_rows = $(if ($backtestStatusObj) { $backtestStatusObj.total_rows } else { $null })
        total_trades = $(if ($backtestStatusObj) { $backtestStatusObj.total_trades } else { $null })
        total_pnl = $(if ($backtestStatusObj) { $backtestStatusObj.total_pnl } else { $null })
        avg_snr = $(if ($backtestStatusObj) { $backtestStatusObj.avg_snr } else { $null })
        avg_orth = $(if ($backtestStatusObj) { $backtestStatusObj.avg_orth } else { $null })
        avg_align = $(if ($backtestStatusObj) { $backtestStatusObj.avg_align } else { $null })
    }

    if (($backtestCode -ne 0) -and (-not $AllowAuditFailed)) {
        throw "Backtest failed with exit code $backtestCode"
    }

    # Phase 5: Persist summary + update audit markdown
    Write-Status -Phase "audit_update" -State "running" -Extra @{}

    $summary = [ordered]@{
        timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        frame = $frameReport
        manifests = $manifestReport
        train = $trainBrief
        backtest = $backtestBrief
    }
    ($summary | ConvertTo-Json -Depth 12) | Set-Content -LiteralPath $summaryPath -Encoding UTF8

    Append-AuditUpdate -FrameReport $frameReport -ManifestReport $manifestReport -TrainBrief $trainBrief -BacktestBrief $backtestBrief

    Set-Content -LiteralPath $exitPath -Value "0" -Encoding UTF8
    Write-Status -Phase "complete" -State "completed" -Extra @{ exit_code = 0; summary = $summaryPath }
    Write-Log "END v51 full autopilot EXIT=0"
    exit 0
}
catch {
    $msg = $_ | Out-String
    Write-Log "[ERROR]"
    $msg | Tee-Object -FilePath $masterLog -Append | Out-Null

    $code = 1
    Set-Content -LiteralPath $exitPath -Value "$code" -Encoding UTF8
    Write-Status -Phase "failed" -State "failed" -Extra @{ exit_code = $code; error = $msg }
    Write-Log ("END v51 full autopilot EXIT={0}" -f $code)
    exit $code
}
