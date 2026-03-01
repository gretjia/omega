param(
    [ValidateRange(1, 3600)]
    [int]$PollSec = 1,
    [ValidateRange(1, 3600)]
    [int]$CalmPollSec = 5,
    [ValidateRange(1, 86400)]
    [int]$ReportIntervalSec = 60,
    [ValidateRange(1, 86400)]
    [int]$ActionCooldownSec = 2,
    [ValidateRange(1, 600)]
    [int]$TermGraceSec = 3,
    [ValidateRange(50, 5000)]
    [int]$RecoveryProbeDelayMs = 250,

    [Alias("SoftPct")]
    [ValidateRange(0.1, 100.0)]
    [double]$MemPct = 10.0,
    [Alias("HardPct")]
    [ValidateRange(0.1, 100.0)]
    [double]$MemKillPct = 5.0,

    [Alias("SoftFreeGB")]
    [ValidateRange(0.1, 4096.0)]
    [double]$MemMinGB = 12.0,
    [Alias("HardFreeGB")]
    [ValidateRange(0.1, 4096.0)]
    [double]$MemKillGB = 6.0,

    [ValidateRange(0.1, 100.0)]
    [double]$SwapPct = 10.0,
    [ValidateRange(0.1, 100.0)]
    [double]$SwapKillPct = 5.0,
    [ValidateRange(0.0, 4096.0)]
    [double]$SwapMinGB = 0.0,
    [ValidateRange(0.0, 4096.0)]
    [double]$SwapKillGB = 0.0,
    [switch]$SwapProbeFailOpen,

    [ValidateRange(0.0, 16384.0)]
    [double]$MinVictimMB = 1024.0,
    [ValidateRange(1, 32)]
    [int]$MaxVictimsPerCycle = 3,

    [string]$TargetCmdRegex = ".+",
    [switch]$AllowWildcardTarget,
    [string]$PreferRegex = "",
    [string]$ProtectRegex = "",
    [switch]$AvoidAsPenalty,
    [string]$AvoidRegex = "^(explorer\\.exe|powershell\\.exe|pwsh\\.exe|cmd\\.exe|conhost\\.exe|windowsterminal\\.exe|ssh\\.exe|sshd\\.exe|code\\.exe|codex\\.exe|gemini\\.exe)$",
    [string]$IgnoreRegex = "^(system|registry|memory compression|idle|csrss\\.exe|wininit\\.exe|winlogon\\.exe|smss\\.exe|lsass\\.exe|services\\.exe|svchost\\.exe|fontdrvhost\\.exe|dwm\\.exe|taskhostw\\.exe|sihost\\.exe)$",

    [string]$LogPath = "D:\\work\\Omega_vNext\\audit\\runtime\\ops\\windows_memory_guard.log",
    [switch]$DryRun,
    [switch]$Once
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Ensure-LogDir {
    param([string]$Path)
    $dir = Split-Path -Parent $Path
    if ([string]::IsNullOrWhiteSpace($dir)) { return }
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

function Format-DataPairs {
    param([hashtable]$Data)
    if ($null -eq $Data -or $Data.Count -eq 0) { return "" }
    $pairs = @()
    foreach ($k in ($Data.Keys | Sort-Object)) {
        $pairs += ("{0}={1}" -f $k, $Data[$k])
    }
    return ($pairs -join " ")
}

function Write-GuardLog {
    param(
        [string]$Level,
        [string]$Message,
        [hashtable]$Data = @{}
    )
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $kv = Format-DataPairs -Data $Data
    $line = if ([string]::IsNullOrWhiteSpace($kv)) {
        "[{0}][{1}] {2}" -f $ts, $Level, $Message
    } else {
        "[{0}][{1}] {2} | {3}" -f $ts, $Level, $Message, $kv
    }

    try {
        Add-Content -Path $LogPath -Value $line -ErrorAction Stop
    } catch {
        Write-Output $line
        Write-Output ("[{0}][ERROR] log_write_failed | err={1}" -f $ts, $_.Exception.Message)
    }
}

function Get-MemoryStats {
    $os = $null
    try {
        $os = Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
    } catch {
        Write-GuardLog "ERROR" "os_probe_failed" @{ err = $_.Exception.Message }
        return $null
    }
    if ($null -eq $os) { return $null }

    $totalMemMB = [double]$os.TotalVisibleMemorySize / 1024.0
    $availMemMB = 0.0
    try {
        $availCounter = Get-Counter '\\Memory\\Available MBytes' -ErrorAction Stop
        $availMemMB = [double]$availCounter.CounterSamples[0].CookedValue
    } catch {
        $availMemMB = [double]$os.FreePhysicalMemory / 1024.0
    }

    if ($totalMemMB -le 0) { return $null }

    $swapTotalMB = 0.0
    $swapUsedMB = 0.0
    $swapProbeOk = $true
    try {
        $pageRows = @(Get-CimInstance Win32_PageFileUsage -ErrorAction Stop)
        if ($pageRows.Count -gt 0) {
            $swapTotalMB = [double](($pageRows | Measure-Object -Property AllocatedBaseSize -Sum).Sum)
            $swapUsedMB = [double](($pageRows | Measure-Object -Property CurrentUsage -Sum).Sum)
        }
    } catch {
        $swapProbeOk = $false
        Write-GuardLog "WARN" "pagefile_probe_failed" @{ err = $_.Exception.Message }
    }

    $swapFreeMB = [Math]::Max(0.0, $swapTotalMB - $swapUsedMB)
    $memAvailPct = [Math]::Round(($availMemMB / $totalMemMB) * 100.0, 2)
    $swapFreePct = if ($swapTotalMB -gt 0.0) {
        [Math]::Round(($swapFreeMB / $swapTotalMB) * 100.0, 2)
    } else {
        100.0
    }

    return @{
        MemTotalMB = [Math]::Round($totalMemMB, 2)
        MemAvailMB = [Math]::Round($availMemMB, 2)
        MemAvailPct = $memAvailPct
        SwapTotalMB = [Math]::Round($swapTotalMB, 2)
        SwapFreeMB = [Math]::Round($swapFreeMB, 2)
        SwapFreePct = $swapFreePct
        SwapProbeOk = [bool]$swapProbeOk
    }
}

function Get-PressureState {
    param([hashtable]$Mem)

    $memTermByPctMB = $Mem.MemTotalMB * ($MemPct / 100.0)
    $memKillByPctMB = $Mem.MemTotalMB * ($MemKillPct / 100.0)
    $memTermMB = [Math]::Min($memTermByPctMB, $MemMinGB * 1024.0)
    $memKillMB = [Math]::Min($memKillByPctMB, $MemKillGB * 1024.0)

    $memKillHit = ($Mem.MemAvailMB -le $memKillMB)
    $memTermHit = ($Mem.MemAvailMB -le $memTermMB)

    $swapTermHit = $false
    $swapKillHit = $false
    $swapTermMB = 0.0
    $swapKillMB = 0.0
    if (-not [bool]$Mem.SwapProbeOk) {
        if ($SwapProbeFailOpen) {
            $swapTermHit = $true
            $swapKillHit = $true
        }
    } elseif ($Mem.SwapTotalMB -le 0.0) {
        $swapTermHit = $true
        $swapKillHit = $true
    } else {
        $swapTermByPctMB = $Mem.SwapTotalMB * ($SwapPct / 100.0)
        $swapKillByPctMB = $Mem.SwapTotalMB * ($SwapKillPct / 100.0)
        if ($SwapMinGB -gt 0.0) {
            $swapTermMB = [Math]::Min($swapTermByPctMB, $SwapMinGB * 1024.0)
        } else {
            $swapTermMB = $swapTermByPctMB
        }
        if ($SwapKillGB -gt 0.0) {
            $swapKillMB = [Math]::Min($swapKillByPctMB, $SwapKillGB * 1024.0)
        } else {
            $swapKillMB = $swapKillByPctMB
        }
        $swapTermHit = ($Mem.SwapFreeMB -le $swapTermMB)
        $swapKillHit = ($Mem.SwapFreeMB -le $swapKillMB)
    }

    $mode = "NORMAL"
    if ($memKillHit -and $swapKillHit) {
        $mode = "KILL"
    } elseif ($memTermHit -and $swapTermHit) {
        $mode = "TERM"
    }

    return @{
        Mode = $mode
        MemTermMB = [Math]::Round($memTermMB, 2)
        MemKillMB = [Math]::Round($memKillMB, 2)
        SwapTermMB = [Math]::Round($swapTermMB, 2)
        SwapKillMB = [Math]::Round($swapKillMB, 2)
        SwapTermHit = [bool]$swapTermHit
        SwapKillHit = [bool]$swapKillHit
    }
}

function Get-CandidateProcesses {
    param(
        [double]$MinWsMB,
        [string]$TargetCmdPattern,
        [string]$PreferRegexPattern,
        [string]$ProtectRegexPattern,
        [bool]$AvoidAsPenaltyMode,
        [string]$AvoidRegexPattern,
        [string]$IgnoreRegexPattern
    )

    $rows = @()
    $procMap = @{}
    Get-Process -ErrorAction SilentlyContinue | ForEach-Object {
        $procMap[$_.Id] = $_
    }

    $cims = @()
    try {
        $cims = @(Get-CimInstance Win32_Process -ErrorAction Stop)
    } catch {
        Write-GuardLog "ERROR" "process_probe_failed" @{ err = $_.Exception.Message }
        return $rows
    }

    $targetPattern = if ([string]::IsNullOrWhiteSpace($TargetCmdPattern)) { ".+" } else { $TargetCmdPattern }

    foreach ($p in $cims) {
        $pid = [int]$p.ProcessId
        if ($pid -le 4 -or $pid -eq $PID) { continue }

        $name = [string]$p.Name
        if ([string]::IsNullOrWhiteSpace($name)) { continue }
        $nameLower = $name.ToLowerInvariant()
        $cmdLine = [string]$p.CommandLine
        if ([string]::IsNullOrWhiteSpace($cmdLine)) {
            $cmdLine = $name
        }
        $cmdLower = $cmdLine.ToLowerInvariant()

        if ($cmdLower -inotmatch $targetPattern -and $nameLower -inotmatch $targetPattern) {
            continue
        }

        if (
            -not [string]::IsNullOrWhiteSpace($IgnoreRegexPattern) -and
            (($nameLower -imatch $IgnoreRegexPattern) -or ($cmdLower -imatch $IgnoreRegexPattern))
        ) {
            continue
        }
        if (
            -not [string]::IsNullOrWhiteSpace($ProtectRegexPattern) -and
            (($nameLower -imatch $ProtectRegexPattern) -or ($cmdLower -imatch $ProtectRegexPattern))
        ) {
            continue
        }

        $wsMB = 0.0
        if ($procMap.ContainsKey($pid)) {
            $wsMB = [Math]::Round(([double]$procMap[$pid].WorkingSet64 / 1MB), 2)
        } elseif ($p.WorkingSetSize) {
            $wsMB = [Math]::Round(([double]$p.WorkingSetSize / 1MB), 2)
        }
        if ($wsMB -lt $MinWsMB) { continue }

        $score = $wsMB
        if (
            -not [string]::IsNullOrWhiteSpace($PreferRegexPattern) -and
            (($nameLower -imatch $PreferRegexPattern) -or ($cmdLower -imatch $PreferRegexPattern))
        ) {
            $score += 300.0
        }
        if (
            -not [string]::IsNullOrWhiteSpace($AvoidRegexPattern) -and
            (($nameLower -imatch $AvoidRegexPattern) -or ($cmdLower -imatch $AvoidRegexPattern))
        ) {
            if ($AvoidAsPenaltyMode) {
                $score -= 300.0
            } else {
                continue
            }
        }

        $rows += [PSCustomObject]@{
            Pid = $pid
            Name = $name
            WS_MB = $wsMB
            Score = [Math]::Round($score, 2)
            Cmd = $cmdLine
        }
    }

    return ($rows | Sort-Object `
        @{ Expression = "Score"; Descending = $true }, `
        @{ Expression = "WS_MB"; Descending = $true })
}

function Get-CmdSignature {
    param([string]$Cmd)
    $raw = if ([string]::IsNullOrWhiteSpace($Cmd)) { "<none>" } else { $Cmd.Trim() }
    $sha1 = [System.Security.Cryptography.SHA1]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($raw)
        $hash = [BitConverter]::ToString($sha1.ComputeHash($bytes)).Replace("-", "").ToLowerInvariant()
    } finally {
        $sha1.Dispose()
    }
    $short = if ($raw.Length -gt 120) { $raw.Substring(0, 120) } else { $raw }
    return ("{0}:{1}" -f $hash.Substring(0, 12), $short)
}

function Act-OnVictims {
    param(
        [PSObject[]]$Candidates,
        [string]$Mode,
        [int]$Limit,
        [int]$GraceSeconds,
        [switch]$DryRunMode
    )

    $acted = @()
    foreach ($c in ($Candidates | Select-Object -First $Limit)) {
        $cmdSig = Get-CmdSignature -Cmd $c.Cmd
        $tag = "{0}:{1}(ws={2}MB,score={3},cmd={4})" -f $c.Pid, $c.Name, $c.WS_MB, $c.Score, $cmdSig
        if ($DryRunMode) {
            Write-GuardLog "ACTION" "dryrun_${Mode}" @{ victim = $tag; cmd_sig = $cmdSig }
            $acted += ("DRYRUN:{0}" -f $tag)
            continue
        }

        try {
            if ($Mode -eq "KILL") {
                Stop-Process -Id $c.Pid -Force -ErrorAction Stop
            } else {
                Stop-Process -Id $c.Pid -ErrorAction Stop
                Start-Sleep -Seconds $GraceSeconds
            }
            $acted += $tag
            Write-GuardLog "ACTION" "${Mode}_ok" @{ victim = $tag; cmd_sig = $cmdSig }
        } catch {
            Write-GuardLog "WARN" "${Mode}_failed" @{ victim = $tag; cmd_sig = $cmdSig; err = $_.Exception.Message }
        }
    }
    return $acted
}

if (-not ($MemKillPct -le $MemPct)) {
    throw "Invariant failed: require MemKillPct <= MemPct"
}
if (-not ($SwapKillPct -le $SwapPct)) {
    throw "Invariant failed: require SwapKillPct <= SwapPct"
}
if (-not ($MemKillGB -le $MemMinGB)) {
    throw "Invariant failed: require MemKillGB <= MemMinGB"
}
if ($SwapMinGB -gt 0.0 -and -not ($SwapKillGB -le $SwapMinGB)) {
    throw "Invariant failed: require SwapKillGB <= SwapMinGB when SwapMinGB > 0"
}
if ([string]::IsNullOrWhiteSpace($TargetCmdRegex)) {
    $TargetCmdRegex = ".+"
}
$targetPatternNorm = $TargetCmdRegex.Trim()
if (-not $AllowWildcardTarget -and ($targetPatternNorm -eq ".*" -or $targetPatternNorm -eq "^.*$")) {
    throw "Invariant failed: wildcard TargetCmdRegex requires -AllowWildcardTarget."
}

Ensure-LogDir -Path $LogPath
Write-GuardLog "INFO" "start" @{
    poll_sec = $PollSec
    calm_poll_sec = $CalmPollSec
    report_interval_sec = $ReportIntervalSec
    action_cooldown_sec = $ActionCooldownSec
    term_grace_sec = $TermGraceSec
    recovery_probe_delay_ms = $RecoveryProbeDelayMs
    mem_pct = $MemPct
    mem_kill_pct = $MemKillPct
    mem_min_gb = $MemMinGB
    mem_kill_gb = $MemKillGB
    swap_pct = $SwapPct
    swap_kill_pct = $SwapKillPct
    swap_min_gb = $SwapMinGB
    swap_kill_gb = $SwapKillGB
    swap_probe_fail_open = [bool]$SwapProbeFailOpen
    target_cmd_regex = $TargetCmdRegex
    protect_regex = $ProtectRegex
    avoid_as_penalty = [bool]$AvoidAsPenalty
    allow_wildcard_target = [bool]$AllowWildcardTarget
    min_victim_mb = $MinVictimMB
    max_victims_per_cycle = $MaxVictimsPerCycle
    dry_run = [bool]$DryRun
}

$lastMode = ""
$lastActionAt = [DateTime]::MinValue
$nextReportAt = Get-Date
$sleepSecNext = $PollSec

while ($true) {
    try {
        $m = Get-MemoryStats
        if ($null -eq $m) {
            Write-GuardLog "WARN" "memory_stats_null"
            if ($Once) { break }
            Start-Sleep -Seconds $PollSec
            continue
        }

        $pressure = Get-PressureState -Mem $m
        $mode = [string]$pressure.Mode

        if ($mode -ne $lastMode) {
            Write-GuardLog "STATE" "mode_transition" @{
                mode = $mode
                mem_avail_mb = $m.MemAvailMB
                mem_avail_pct = $m.MemAvailPct
                mem_term_mb = $pressure.MemTermMB
                mem_kill_mb = $pressure.MemKillMB
                swap_free_pct = $m.SwapFreePct
                swap_term_mb = $pressure.SwapTermMB
                swap_kill_mb = $pressure.SwapKillMB
                swap_total_mb = $m.SwapTotalMB
                swap_probe_ok = [bool]$m.SwapProbeOk
            }
            $lastMode = $mode
        }

        $now = Get-Date
        if ($mode -ne "NORMAL" -and ($now - $lastActionAt).TotalSeconds -ge $ActionCooldownSec) {
            $cycleVictims = @()
            $cycleMode = $mode
            $cycleStats = $m
            $cyclePressure = $pressure
            $budget = $MaxVictimsPerCycle
            $cycleCandidateCount = 0
            while ($cycleMode -ne "NORMAL" -and $budget -gt 0) {
                $candidates = Get-CandidateProcesses `
                    -MinWsMB $MinVictimMB `
                    -TargetCmdPattern $TargetCmdRegex `
                    -PreferRegexPattern $PreferRegex `
                    -ProtectRegexPattern $ProtectRegex `
                    -AvoidAsPenaltyMode ([bool]$AvoidAsPenalty) `
                    -AvoidRegexPattern $AvoidRegex `
                    -IgnoreRegexPattern $IgnoreRegex

                if ($null -eq $candidates -or $candidates.Count -eq 0) {
                    Write-GuardLog "WARN" "no_candidates" @{ mode = $cycleMode; min_victim_mb = $MinVictimMB }
                    break
                }
                $cycleCandidateCount = [Math]::Max($cycleCandidateCount, [int]$candidates.Count)

                $actedNow = Act-OnVictims `
                    -Candidates $candidates `
                    -Mode $cycleMode `
                    -Limit 1 `
                    -GraceSeconds $TermGraceSec `
                    -DryRunMode:$DryRun

                if ($null -eq $actedNow -or $actedNow.Count -eq 0) {
                    Start-Sleep -Seconds 1
                    break
                }

                $cycleVictims += $actedNow
                $budget -= $actedNow.Count

                if ($DryRun) {
                    break
                }

                Start-Sleep -Milliseconds $RecoveryProbeDelayMs
                $cycleStats = Get-MemoryStats
                if ($null -eq $cycleStats) {
                    break
                }
                $cyclePressure = Get-PressureState -Mem $cycleStats
                $cycleMode = [string]$cyclePressure.Mode
            }

            if ($cycleVictims.Count -gt 0) {
                Write-GuardLog "ACTION" "memory_pressure_action" @{
                    mode = $mode
                    final_mode = $cycleMode
                    victims = ($cycleVictims -join ",")
                    candidate_count = $cycleCandidateCount
                    mem_avail_mb = $cycleStats.MemAvailMB
                    mem_avail_pct = $cycleStats.MemAvailPct
                    swap_free_pct = $cycleStats.SwapFreePct
                    dry_run = [bool]$DryRun
                }
            }
            $lastActionAt = $now
        }

        if ($now -ge $nextReportAt) {
            Write-GuardLog "HEARTBEAT" "status" @{
                mode = $mode
                mem_avail_mb = $m.MemAvailMB
                mem_total_mb = $m.MemTotalMB
                mem_avail_pct = $m.MemAvailPct
                swap_free_mb = $m.SwapFreeMB
                swap_total_mb = $m.SwapTotalMB
                swap_free_pct = $m.SwapFreePct
            }
            $nextReportAt = $now.AddSeconds($ReportIntervalSec)
        }

        $sleepSecNext = $PollSec
        if ($mode -eq "NORMAL") {
            $memComfortPct = [Math]::Max($MemPct * 3.0, 35.0)
            $swapComfortPct = [Math]::Max($SwapPct * 3.0, 35.0)
            $swapComfort = ($m.SwapTotalMB -le 0.0) -or ($m.SwapFreePct -ge $swapComfortPct)
            if ($m.MemAvailPct -ge $memComfortPct -and $swapComfort) {
                $sleepSecNext = [Math]::Max($PollSec, $CalmPollSec)
            }
        }
    } catch {
        Write-GuardLog "ERROR" "guard_loop_error" @{ err = $_.Exception.Message }
        $sleepSecNext = $PollSec
    }

    if ($Once) { break }
    Start-Sleep -Seconds $sleepSecNext
}

Write-GuardLog "INFO" "exit"
