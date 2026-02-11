param(
    [string]$Root = "",
    [string]$FrameYear = "",
    [int]$Limit = 800,
    [string]$Workers = "12,16,20,22",
    [int]$IoSlots = 4,
    [int]$FrameSevenZipThreads = 1,
    [string]$FrameOutputRoot = "data/level2_frames_v40_bench",
    [string]$FrameStageDir = "C:/Omega_level2_stage",
    [double]$MemoryThreshold = 88.0,
    [switch]$ExtractAll,
    [switch]$NoCleanupFrameStage,
    [switch]$ContinueOnError
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

function Parse-Workers {
    param([string]$Text)
    $vals = @()
    foreach ($token in ($Text -split ",")) {
        $s = $token.Trim()
        if ([string]::IsNullOrWhiteSpace($s)) { continue }
        $n = 0
        if ([int]::TryParse($s, [ref]$n)) {
            if ($n -gt 0) { $vals += $n }
        }
    }
    if ($vals.Count -eq 0) {
        throw "Workers list is empty or invalid: '$Text'"
    }
    return $vals
}

$runtimeRoot = Join-Path $Root "audit\v40_runtime\windows\frame_bench"
New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null

Push-Location $Root
try {
    $workerList = Parse-Workers -Text $Workers
    Write-Stamp "Frame benchmark start: workers=$($workerList -join ',') limit=$Limit year='$FrameYear' ioSlots=$IoSlots 7zThreads=$FrameSevenZipThreads"

    $results = New-Object System.Collections.Generic.List[object]
    foreach ($w in $workerList) {
        $runTag = "w$w"
        $outputDir = Join-Path $FrameOutputRoot $runTag
        $statusPath = Join-Path $runtimeRoot "${runTag}_status.json"
        $logPath = Join-Path $runtimeRoot "${runTag}.log"

        if (Test-Path $outputDir) {
            Remove-Item -Recurse -Force $outputDir
        }
        if (Test-Path $statusPath) {
            Remove-Item -Force $statusPath
        }
        if (Test-Path $logPath) {
            Remove-Item -Force $logPath
        }

        $cmdArgs = @(
            "tools/run_l2_audit_driver.py",
            "--workers", "$w",
            "--io-slots", "$IoSlots",
            "--seven-zip-threads", "$FrameSevenZipThreads",
            "--limit", "$Limit",
            "--output-dir", $outputDir,
            "--copy-to-local",
            "--stage-dir", $FrameStageDir,
            "--memory-threshold", "$MemoryThreshold",
            "--status-json", $statusPath,
            "--skip-report"
        )
        if ($ExtractAll) {
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

        $cmdLine = "python " + ($cmdArgs -join " ")
        Write-Stamp "Run $runTag start: $cmdLine"
        "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] CMD: $cmdLine" | Tee-Object -FilePath $logPath -Append | Out-Null

        $started = Get-Date
        $ok = $true
        & python @cmdArgs 2>&1 | ForEach-Object { $_.ToString() } | Tee-Object -FilePath $logPath -Append | Out-Null
        if ($LASTEXITCODE -ne 0) {
            $ok = $false
            Write-Stamp "Run $runTag failed with exit code $LASTEXITCODE"
            if (-not $ContinueOnError) {
                throw "Benchmark run failed for $runTag"
            }
        }
        $ended = Get-Date
        $elapsedSec = [math]::Max(0.0, ($ended - $started).TotalSeconds)

        $status = $null
        if (Test-Path $statusPath) {
            try {
                $status = Get-Content $statusPath -Raw | ConvertFrom-Json
            } catch {
                $status = $null
            }
        }

        $archivesDone = 0
        $parquetOut = 0
        $aph = 0.0
        if ($status -ne $null) {
            if ($status.PSObject.Properties.Name -contains "archives_completed_in_run") {
                $archivesDone = [int]$status.archives_completed_in_run
            }
            if ($status.PSObject.Properties.Name -contains "parquet_files_written_in_run") {
                $parquetOut = [int]$status.parquet_files_written_in_run
            }
            if ($status.PSObject.Properties.Name -contains "archives_per_hour") {
                $aph = [double]$status.archives_per_hour
            } elseif ($elapsedSec -gt 0) {
                $aph = $archivesDone * 3600.0 / $elapsedSec
            }
        } elseif ($elapsedSec -gt 0) {
            $aph = 0.0
        }

        $rec = [PSCustomObject]@{
            worker_count = $w
            success = $ok
            elapsed_sec = [math]::Round($elapsedSec, 2)
            archives_done = $archivesDone
            parquet_files = $parquetOut
            archives_per_hour = [math]::Round($aph, 2)
            output_dir = $outputDir
            status_json = $statusPath
            log_path = $logPath
        }
        $results.Add($rec) | Out-Null
        Write-Stamp ("Run {0} done: success={1} elapsed={2}s archives={3} aph={4}" -f $runTag, $ok, $rec.elapsed_sec, $archivesDone, $rec.archives_per_hour)
    }

    $resultsSorted = $results | Sort-Object -Property archives_per_hour -Descending
    Write-Stamp "Frame benchmark summary (best first):"
    $resultsSorted | Format-Table -AutoSize | Out-String | Write-Host

    $jsonOut = Join-Path $runtimeRoot "benchmark_summary.json"
    $csvOut = Join-Path $runtimeRoot "benchmark_summary.csv"
    $resultsSorted | ConvertTo-Json -Depth 4 | Set-Content -Path $jsonOut -Encoding UTF8
    $resultsSorted | Export-Csv -Path $csvOut -NoTypeInformation -Encoding UTF8
    Write-Stamp "Saved summary: $jsonOut"
    Write-Stamp "Saved summary: $csvOut"
}
finally {
    Pop-Location
}
