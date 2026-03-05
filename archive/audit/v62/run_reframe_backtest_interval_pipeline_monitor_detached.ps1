param(
    [string]$RuntimeRoot = "C:\Omega_vNext\audit\v51_runtime\windows\frame_pipeline",
    [int]$MaxHours = 20
)

$ErrorActionPreference = "Continue"

$logPath = Join-Path $RuntimeRoot "reframe_backtest_interval_pipeline.log"
$exitPath = Join-Path $RuntimeRoot "reframe_backtest_interval_pipeline_exit_code.txt"
$monLog = Join-Path $RuntimeRoot "reframe_backtest_interval_pipeline_monitor.log"
$monJson = Join-Path $RuntimeRoot "reframe_backtest_interval_pipeline_monitor_latest.json"
$taskName = "\OmegaV51ReframeBacktestPipeline"

New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null

function Write-Mon {
    param([string]$Text)
    $line = ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Text)
    Add-Content -LiteralPath $monLog -Value $line -Encoding UTF8
}

function Get-TaskMode {
    try {
        $q = schtasks /Query /TN $taskName /FO LIST /V 2>$null
        $line = ($q | Where-Object { $_ -match "模式|Status|State" } | Select-Object -First 1)
        if ($line) { return ($line -replace "^[^:：]+[:：]\s*", "").Trim() }
    } catch {}
    return "UNKNOWN"
}

function Get-Snapshot {
    $exists = Test-Path -LiteralPath $logPath
    if (-not $exists) {
        return [ordered]@{
            now = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            task_mode = Get-TaskMode
            log_ready = $false
            total_archives = $null
            done_count = 0
            skip_count = 0
            processed_count = 0
            entries_per_hour = $null
            eta_minutes = $null
            eta_at = $null
            exit_code = $null
        }
    }

    $raw = Get-Content -LiteralPath $logPath
    $total = $null
    foreach ($line in $raw) {
        if ($line -match "Found\s+(\d+)\s+archives\.)") {
            $total = [double]$matches[1]
            break
        }
    }
    $done = ($raw | Where-Object { $_ -match "^\[Done\]" } | Measure-Object).Count
    $skip = ($raw | Where-Object { $_ -match "^\[Skip\]" } | Measure-Object).Count
    $processed = $done + $skip

    # Start timestamp from wrapper header line.
    $startedAt = $null
    foreach ($line in $raw) {
        if ($line -match "^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\s+START") {
            $tmp = $null
            if ([datetime]::TryParse($matches[1], [ref]$tmp)) {
                $startedAt = $tmp
                break
            }
        }
    }
    if ($null -eq $startedAt) { $startedAt = Get-Date }
    $elapsedHours = [math]::Max(0.001, ((Get-Date) - $startedAt).TotalHours)
    $eph = [math]::Round($processed / $elapsedHours, 3)

    $etaMin = $null
    $etaAt = $null
    if ($null -ne $total -and $total -gt 0 -and $eph -gt 0) {
        $remaining = [math]::Max(0.0, $total - $processed)
        $etaMin = [math]::Round(($remaining / $eph) * 60.0, 1)
        $etaAt = (Get-Date).AddMinutes($etaMin).ToString("yyyy-MM-dd HH:mm:ss")
    }

    $exitVal = $null
    if (Test-Path -LiteralPath $exitPath) {
        try { $exitVal = (Get-Content -LiteralPath $exitPath -Raw).Trim() } catch {}
    }

    return [ordered]@{
        now = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        task_mode = Get-TaskMode
        log_ready = $true
        total_archives = $total
        done_count = $done
        skip_count = $skip
        processed_count = $processed
        entries_per_hour = $eph
        eta_minutes = $etaMin
        eta_at = $etaAt
        exit_code = $exitVal
    }
}

function Interval-Min {
    param($Snap, [datetime]$StartedAt)
    if ($null -ne $Snap.exit_code) { return 0 }

    $elapsedMin = [math]::Max(0.0, ((Get-Date) - $StartedAt).TotalMinutes)
    if ($elapsedMin -lt 60.0) { return 10 } # first hour dense
    if ($null -ne $Snap.eta_minutes -and $Snap.eta_minutes -le 120.0) { return 10 } # near completion
    return 30
}

$started = Get-Date
Write-Mon "START pipeline monitor"

while ($true) {
    $snap = Get-Snapshot
    $snap | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $monJson -Encoding UTF8
    Write-Mon ("task={0} done={1} skip={2} total={3} eph={4} eta_min={5} eta_at={6} exit={7}" -f $snap.task_mode, $snap.done_count, $snap.skip_count, $snap.total_archives, $snap.entries_per_hour, $snap.eta_minutes, $snap.eta_at, $snap.exit_code)

    if ($null -ne $snap.exit_code) {
        Write-Mon "END pipeline monitor: exit file detected."
        break
    }
    if (((Get-Date) - $started).TotalHours -ge [double]$MaxHours) {
        Write-Mon "END pipeline monitor: max wall time reached."
        break
    }
    $sleepMin = Interval-Min -Snap $snap -StartedAt $started
    if ($sleepMin -le 0) { break }
    Start-Sleep -Seconds ($sleepMin * 60)
}

