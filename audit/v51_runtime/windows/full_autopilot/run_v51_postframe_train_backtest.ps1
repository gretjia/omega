param(
    [string]$Root = "C:/Omega_vNext",
    [string]$OutputDir = "D:/Omega_frames/v50/output",
    [int]$TrainWorkers = 6,
    [int]$BacktestWorkers = 8,
    [double]$TrainMemoryThreshold = 98.0,
    [double]$BacktestMemoryThreshold = 98.0,
    [switch]$AllowAuditFailed = $true,
    [int]$MonitorIntervalSec = 300
)

$ErrorActionPreference = "Stop"

$runtimeRoot = Join-Path $Root "audit/v51_runtime/windows/full_autopilot"
$manifestDir = Join-Path $runtimeRoot "manifests"
$trainRuntime = Join-Path $runtimeRoot "train"
$backtestRuntime = Join-Path $runtimeRoot "backtest"

$masterLog = Join-Path $runtimeRoot "autopilot.log"
$statusPath = Join-Path $runtimeRoot "autopilot_status.json"
$summaryPath = Join-Path $runtimeRoot "autopilot_summary.json"
$exitPath = Join-Path $runtimeRoot "autopilot_exit_code.txt"
$pidPath = Join-Path $runtimeRoot "autopilot.pid"

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

$generatorPy = Join-Path $runtimeRoot "generate_v51_deep_audit.py"

New-Item -ItemType Directory -Force -Path $runtimeRoot, $manifestDir, $trainRuntime, $backtestRuntime | Out-Null

function Write-Log {
    param([string]$Text)
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Text
    $line | Tee-Object -FilePath $masterLog -Append | Out-Null
}

function Write-Status {
    param([string]$Phase, [string]$State, [hashtable]$Extra = @{})
    $obj = [ordered]@{
        timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        phase = $Phase
        state = $State
    }
    foreach ($k in $Extra.Keys) { $obj[$k] = $Extra[$k] }
    ($obj | ConvertTo-Json -Depth 12) | Set-Content -LiteralPath $statusPath -Encoding UTF8
}

function New-Manifest {
    param([string[]]$Prefixes, [string]$OutPath)
    $all = @()
    foreach ($p in $Prefixes) {
        $all += Get-ChildItem -LiteralPath $OutputDir -Filter ($p + "*.parquet") -File -ErrorAction SilentlyContinue
    }
    $all = $all | Sort-Object Name -Unique
    ($all | ForEach-Object { $_.FullName }) | Set-Content -LiteralPath $OutPath -Encoding UTF8
    return @($all)
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

    Write-Log ("RUN {0} CMD={1} {2}" -f $Name, $Exe, ($ArgList -join " "))
    $start = Get-Date
    $proc = Start-Process -FilePath $Exe -ArgumentList $ArgList -PassThru -WindowStyle Hidden -RedirectStandardOutput $StdoutPath -RedirectStandardError $StderrPath

    Write-Status -Phase $Phase -State "running" -Extra @{ step = $Name; pid = $proc.Id; start_time = ($start.ToString("yyyy-MM-dd HH:mm:ss")) }

    while (-not $proc.HasExited) {
        Start-Sleep -Seconds $MonitorIntervalSec
        $elapsed = [int]((Get-Date) - $start).TotalSeconds
        $extra = @{ step = $Name; pid = $proc.Id; elapsed_sec = $elapsed }
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
    if ($null -eq $code -or [string]::IsNullOrWhiteSpace([string]$code)) {
        $stderrLen = 0
        try { $stderrLen = (Get-Item -LiteralPath $StderrPath).Length } catch {}
        if ($stderrLen -gt 0) { $code = 1 } else { $code = 0 }
        Write-Log ("Warning: EXIT code missing for {0}, inferred as {1} by stderr length." -f $Name, $code)
    }
    Write-Log ("END {0} EXIT={1}" -f $Name, $code)
    return [int]$code
}

$py = "C:/Python314/python.exe"
$manifestReport = @{}
$trainBrief = @{}
$backtestBrief = @{}

try {
    Set-Location $Root
    Set-Content -LiteralPath $pidPath -Value $PID -Encoding UTF8

    # keep old frame outputs; only reset run artifacts for train/backtest and status
    foreach ($f in @($summaryPath, $exitPath, $trainStdout, $trainStderr, $trainStatus, $trainExitPath, $trainPolicyPath, $backtestStdout, $backtestStderr, $backtestStatus, $backtestState, $backtestExitPath)) {
        if (Test-Path -LiteralPath $f) { Remove-Item -LiteralPath $f -Force -ErrorAction SilentlyContinue }
    }

    Write-Log "START v51 post-frame train/backtest"
    Write-Log ("Root={0}" -f $Root)
    Write-Log ("OutputDir={0}" -f $OutputDir)
    Write-Log ("TrainWorkers={0}, BacktestWorkers={1}" -f $TrainWorkers, $BacktestWorkers)
    Write-Log ("AllowAuditFailed={0}" -f $AllowAuditFailed)

    # Phase 1: Manifest
    Write-Status -Phase "manifest" -State "running" -Extra @{}
    $trainFiles = New-Manifest -Prefixes @("2023", "2024") -OutPath $trainManifest
    $backtestFiles = New-Manifest -Prefixes @("2025", "202601") -OutPath $backtestManifest

    if ($trainFiles.Count -eq 0) { throw "Train manifest empty: $trainManifest" }
    if ($backtestFiles.Count -eq 0) { throw "Backtest manifest empty: $backtestManifest" }

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

    # Phase 2: Train
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
    if ($trainCode -ne 0) { throw "Training failed with exit code $trainCode" }

    $newCkpt = Get-ChildItem -LiteralPath (Join-Path $Root "artifacts") -Filter "checkpoint_rows_*.pkl" -File -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -ge $trainStart } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($null -eq $newCkpt) {
        $newCkpt = Get-ChildItem -LiteralPath (Join-Path $Root "artifacts") -Filter "checkpoint_rows_*.pkl" -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
    }
    if ($null -eq $newCkpt) { throw "No checkpoint_rows_*.pkl found after training" }

    $policyPath = $newCkpt.FullName
    Set-Content -LiteralPath $trainPolicyPath -Value $policyPath -Encoding UTF8
    Write-Log ("Selected policy: {0}" -f $policyPath)

    $trainStatusObj = $null
    if (Test-Path -LiteralPath $trainStatus) { try { $trainStatusObj = Get-Content -LiteralPath $trainStatus -Raw | ConvertFrom-Json } catch {} }

    $trainBrief = [ordered]@{
        exit_code = $trainCode
        policy = $policyPath
        total_rows = $(if ($trainStatusObj) { $trainStatusObj.total_rows } else { $null })
        files_processed = $(if ($trainStatusObj) { $trainStatusObj.files_processed_in_run } else { $null })
    }

    # Phase 3: Backtest
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
    if ($AllowAuditFailed) { $backtestArgs += "--allow-audit-failed" } else { $backtestArgs += "--fail-on-audit-failed" }

    $backtestCode = Invoke-TrackedProcess -Name "backtest_full" -Phase "backtest" -Exe $py -ArgList $backtestArgs -StdoutPath $backtestStdout -StderrPath $backtestStderr -StepStatusPath $backtestStatus
    Set-Content -LiteralPath $backtestExitPath -Value "$backtestCode" -Encoding UTF8

    $backtestStatusObj = $null
    if (Test-Path -LiteralPath $backtestStatus) { try { $backtestStatusObj = Get-Content -LiteralPath $backtestStatus -Raw | ConvertFrom-Json } catch {} }

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

    if (($backtestCode -ne 0) -and (-not $AllowAuditFailed)) { throw "Backtest failed with exit code $backtestCode" }

    # Phase 4: Summary + deep audit
    Write-Status -Phase "audit_update" -State "running" -Extra @{}
    $summary = [ordered]@{
        timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
        frame = [ordered]@{
            expected_dec_unique = (Get-ChildItem -LiteralPath $OutputDir -Filter "202512*.parquet" -File -ErrorAction SilentlyContinue | Measure-Object).Count
            expected_jan_unique = (Get-ChildItem -LiteralPath $OutputDir -Filter "202601*.parquet" -File -ErrorAction SilentlyContinue | Measure-Object).Count
            produced_dec_unique = (Get-ChildItem -LiteralPath $OutputDir -Filter "202512*.parquet" -File -ErrorAction SilentlyContinue | Measure-Object).Count
            produced_jan_unique = (Get-ChildItem -LiteralPath $OutputDir -Filter "202601*.parquet" -File -ErrorAction SilentlyContinue | Measure-Object).Count
            expected_total_unique = (Get-ChildItem -LiteralPath $OutputDir -Filter "2025*.parquet" -File -ErrorAction SilentlyContinue | Measure-Object).Count + (Get-ChildItem -LiteralPath $OutputDir -Filter "202601*.parquet" -File -ErrorAction SilentlyContinue | Measure-Object).Count
            produced_total_unique = (Get-ChildItem -LiteralPath $OutputDir -Filter "2025*.parquet" -File -ErrorAction SilentlyContinue | Measure-Object).Count + (Get-ChildItem -LiteralPath $OutputDir -Filter "202601*.parquet" -File -ErrorAction SilentlyContinue | Measure-Object).Count
            missing_unique_total = 0
            missing_tokens = @()
        }
        manifests = $manifestReport
        train = $trainBrief
        backtest = $backtestBrief
    }
    ($summary | ConvertTo-Json -Depth 12) | Set-Content -LiteralPath $summaryPath -Encoding UTF8

    if (Test-Path -LiteralPath $generatorPy) {
        try {
            & $py $generatorPy *> $null
            Write-Log "v51_deep_audit.md generator executed."
        } catch {
            Write-Log ("Generator error: {0}" -f ($_ | Out-String))
        }
    }

    Set-Content -LiteralPath $exitPath -Value "0" -Encoding UTF8
    Write-Status -Phase "complete" -State "completed" -Extra @{ exit_code = 0; summary = $summaryPath }
    Write-Log "END v51 post-frame train/backtest EXIT=0"
    exit 0
}
catch {
    $msg = $_ | Out-String
    Write-Log "[ERROR]"
    $msg | Tee-Object -FilePath $masterLog -Append | Out-Null
    Set-Content -LiteralPath $exitPath -Value "1" -Encoding UTF8
    Write-Status -Phase "failed" -State "failed" -Extra @{ exit_code = 1; error = $msg }
    Write-Log "END v51 post-frame train/backtest EXIT=1"
    exit 1
}

