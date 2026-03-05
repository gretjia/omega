param(
    [string]$RuntimeRoot = "C:\Omega_vNext\audit\v51_runtime\windows\frame",
    [int]$MaxHours = 18
)

$ErrorActionPreference = "Continue"

$status2025 = Join-Path $RuntimeRoot "frame_status_2025.json"
$status202601 = Join-Path $RuntimeRoot "frame_status_202601.json"
$exitPath = Join-Path $RuntimeRoot "reframe_backtest_interval_exit_code.txt"
$monitorLog = Join-Path $RuntimeRoot "reframe_monitor.log"
$monitorJson = Join-Path $RuntimeRoot "reframe_monitor_latest.json"
$taskName = "\OmegaV51ReframeBacktest"

New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null

function Write-MonitorLog {
    param([string]$Text)
    $line = ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Text)
    Add-Content -LiteralPath $monitorLog -Value $line -Encoding UTF8
}

function Read-JsonSafe {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    try {
        return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json)
    }
    catch {
        return $null
    }
}

function Parse-StatusTs {
    param($Obj)
    if ($null -eq $Obj) { return [datetime]::MinValue }
    $raw = [string]$Obj.timestamp
    if ([string]::IsNullOrWhiteSpace($raw)) { return [datetime]::MinValue }
    $dt = $null
    if ([datetime]::TryParse($raw, [ref]$dt)) { return $dt }
    return [datetime]::MinValue
}

function Get-TaskMode {
    param([string]$Name)
    try {
        $q = schtasks /Query /TN $Name /FO LIST /V 2>$null
        $line = ($q | Where-Object { $_ -match "模式|Status|State" } | Select-Object -First 1)
        if ($line) { return ($line -replace "^[^:：]+[:：]\s*", "").Trim() }
    }
    catch {}
    return "UNKNOWN"
}

function Get-Snapshot {
    $s2025 = Read-JsonSafe -Path $status2025
    $s202601 = Read-JsonSafe -Path $status202601
    $t2025 = Parse-StatusTs -Obj $s2025
    $t202601 = Parse-StatusTs -Obj $s202601

    $active = $s2025
    $phase = "2025"
    if ($t202601 -gt $t2025) {
        $active = $s202601
        $phase = "202601"
    }

    $completed = $null
    $total = $null
    $remaining = $null
    $aph = $null
    $elapsed = $null
    if ($null -ne $active) {
        if ($active.PSObject.Properties.Name -contains "archives_completed_in_run") { $completed = [double]$active.archives_completed_in_run }
        if ($active.PSObject.Properties.Name -contains "archives_run_now") { $total = [double]$active.archives_run_now }
        if ($active.PSObject.Properties.Name -contains "archives_remaining_in_run") { $remaining = [double]$active.archives_remaining_in_run }
        if ($active.PSObject.Properties.Name -contains "archives_per_hour") { $aph = [double]$active.archives_per_hour }
        if ($active.PSObject.Properties.Name -contains "run_elapsed_sec") { $elapsed = [double]$active.run_elapsed_sec }
    }

    if (($null -eq $aph -or $aph -le 0.0) -and $null -ne $completed -and $completed -gt 0 -and $null -ne $elapsed -and $elapsed -gt 0) {
        $aph = ($completed * 3600.0) / $elapsed
    }
    if (($null -eq $remaining) -and $null -ne $total -and $null -ne $completed) {
        $remaining = [math]::Max(0.0, $total - $completed)
    }

    $etaMin = $null
    $etaAt = $null
    if ($null -ne $remaining -and $remaining -gt 0 -and $null -ne $aph -and $aph -gt 0.0) {
        $etaHours = $remaining / $aph
        $etaMin = [math]::Round($etaHours * 60.0, 1)
        $etaAt = (Get-Date).AddMinutes($etaMin).ToString("yyyy-MM-dd HH:mm:ss")
    }

    $taskMode = Get-TaskMode -Name $taskName
    $exitVal = $null
    if (Test-Path -LiteralPath $exitPath) {
        try { $exitVal = (Get-Content -LiteralPath $exitPath -Raw).Trim() } catch {}
    }

    return [ordered]@{
        now = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        phase = $phase
        task_mode = $taskMode
        run_status = if ($null -ne $active) { [string]$active.status } else { "unknown" }
        completed = $completed
        total = $total
        remaining = $remaining
        archives_per_hour = $aph
        run_elapsed_sec = $elapsed
        eta_minutes = $etaMin
        eta_at = $etaAt
        exit_code = $exitVal
    }
}

function Decide-IntervalMin {
    param($Snap, [datetime]$StartedAt)
    if ($null -ne $Snap.exit_code) { return 0 }

    $elapsedWallMin = [math]::Max(0.0, ((Get-Date) - $StartedAt).TotalMinutes)
    if ($elapsedWallMin -lt 60.0) {
        return 5  # first hour: dense checks
    }

    if ($null -ne $Snap.eta_minutes) {
        if ($Snap.eta_minutes -le 90.0) {
            return 10  # near ETA
        }
        return 30  # stable cruise
    }

    # No ETA yet after first hour => likely warm-up/stall, keep medium frequency
    return 15
}

$started = Get-Date
Write-MonitorLog "START monitor for OmegaV51ReframeBacktest"

while ($true) {
    $snap = Get-Snapshot
    $json = $snap | ConvertTo-Json -Depth 6
    Set-Content -LiteralPath $monitorJson -Value $json -Encoding UTF8

    Write-MonitorLog (
        "phase={0} task={1} status={2} completed={3}/{4} remaining={5} aph={6} eta_min={7} eta_at={8} exit={9}" -f
        $snap.phase, $snap.task_mode, $snap.run_status, $snap.completed, $snap.total, $snap.remaining,
        $snap.archives_per_hour, $snap.eta_minutes, $snap.eta_at, $snap.exit_code
    )

    if ($null -ne $snap.exit_code) {
        Write-MonitorLog "END monitor: frame task finished."
        break
    }

    if (((Get-Date) - $started).TotalHours -ge [double]$MaxHours) {
        Write-MonitorLog "END monitor: max wall time reached."
        break
    }

    $sleepMin = Decide-IntervalMin -Snap $snap -StartedAt $started
    if ($sleepMin -le 0) { break }
    Start-Sleep -Seconds ($sleepMin * 60)
}

