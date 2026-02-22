param(
    [string]$TaskName = "Omega_Windows_MemoryGuard",
    [string]$RepoRoot = "D:\work\Omega_vNext",
    [string]$LogPath = "D:\work\Omega_vNext\audit\runtime\ops\windows_memory_guard.log",

    [Alias("SoftPct")]
    [double]$MemPct = 10.0,
    [Alias("HardPct")]
    [double]$MemKillPct = 5.0,

    [Alias("SoftFreeGB")]
    [double]$MemMinGB = 12.0,
    [Alias("HardFreeGB")]
    [double]$MemKillGB = 6.0,

    [double]$SwapPct = 10.0,
    [double]$SwapKillPct = 5.0,
    [double]$SwapMinGB = 0.0,
    [double]$SwapKillGB = 0.0,
    [switch]$SwapProbeFailOpen,

    [int]$PollSec = 1,
    [int]$CalmPollSec = 5,
    [int]$ReportIntervalSec = 60,
    [int]$ActionCooldownSec = 2,
    [int]$TermGraceSec = 3,
    [int]$RecoveryProbeDelayMs = 250,

    [double]$MinVictimMB = 1024.0,
    [int]$MaxVictimsPerCycle = 3,

    [string]$TargetCmdRegex = ".+",
    [switch]$AllowWildcardTarget,
    [string]$PreferRegex = "",
    [string]$ProtectRegex = "",
    [switch]$AvoidAsPenalty,
    [string]$AvoidRegex = "^(explorer\\.exe|powershell\\.exe|pwsh\\.exe|cmd\\.exe|conhost\\.exe|windowsterminal\\.exe|ssh\\.exe|sshd\\.exe|code\\.exe|codex\\.exe|gemini\\.exe)$",
    [string]$IgnoreRegex = "^(system|registry|memory compression|idle|csrss\\.exe|wininit\\.exe|winlogon\\.exe|smss\\.exe|lsass\\.exe|services\\.exe|svchost\\.exe|fontdrvhost\\.exe|dwm\\.exe|taskhostw\\.exe|sihost\\.exe)$",

    [switch]$GuardDryRun,
    [switch]$StartNow
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$guardScript = Join-Path $RepoRoot "tools\windows_memory_guard.ps1"
if (-not (Test-Path $guardScript)) {
    throw "Guard script not found: $guardScript"
}
if ([string]::IsNullOrWhiteSpace($TargetCmdRegex)) {
    $TargetCmdRegex = ".+"
}
$targetPatternNorm = $TargetCmdRegex.Trim()
if (-not $AllowWildcardTarget -and ($targetPatternNorm -eq ".*" -or $targetPatternNorm -eq "^.*$")) {
    throw "Wildcard TargetCmdRegex requires -AllowWildcardTarget."
}
if ($SwapMinGB -gt 0.0 -and -not ($SwapKillGB -le $SwapMinGB)) {
    throw "Invariant failed: require SwapKillGB <= SwapMinGB when SwapMinGB > 0"
}

$psArgs = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", "`"$guardScript`"",
    "-LogPath", "`"$LogPath`"",
    "-PollSec", "$PollSec",
    "-CalmPollSec", "$CalmPollSec",
    "-ReportIntervalSec", "$ReportIntervalSec",
    "-ActionCooldownSec", "$ActionCooldownSec",
    "-TermGraceSec", "$TermGraceSec",
    "-RecoveryProbeDelayMs", "$RecoveryProbeDelayMs",
    "-MemPct", "$MemPct",
    "-MemKillPct", "$MemKillPct",
    "-MemMinGB", "$MemMinGB",
    "-MemKillGB", "$MemKillGB",
    "-SwapPct", "$SwapPct",
    "-SwapKillPct", "$SwapKillPct",
    "-SwapMinGB", "$SwapMinGB",
    "-SwapKillGB", "$SwapKillGB",
    "-MinVictimMB", "$MinVictimMB",
    "-MaxVictimsPerCycle", "$MaxVictimsPerCycle",
    "-TargetCmdRegex", "`"$TargetCmdRegex`"",
    "-PreferRegex", "`"$PreferRegex`"",
    "-ProtectRegex", "`"$ProtectRegex`"",
    "-AvoidRegex", "`"$AvoidRegex`"",
    "-IgnoreRegex", "`"$IgnoreRegex`""
)
if ($GuardDryRun) {
    $psArgs += "-DryRun"
}
if ($SwapProbeFailOpen) {
    $psArgs += "-SwapProbeFailOpen"
}
if ($AllowWildcardTarget) {
    $psArgs += "-AllowWildcardTarget"
}
if ($AvoidAsPenalty) {
    $psArgs += "-AvoidAsPenalty"
}
$argString = $psArgs -join " "

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argString -WorkingDirectory $RepoRoot
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Days 3650)

try {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
} catch {
    throw ("register_task_failed: {0}" -f $_.Exception.Message)
}

if ($StartNow) {
    Start-ScheduledTask -TaskName $TaskName
}

$t = Get-ScheduledTask -TaskName $TaskName
$ti = Get-ScheduledTaskInfo -TaskName $TaskName

[PSCustomObject]@{
    task_name             = $TaskName
    task_state            = $t.State
    last_run_time         = $ti.LastRunTime
    last_task_result      = $ti.LastTaskResult
    guard_script          = $guardScript
    log_path              = $LogPath
    run_level             = "Highest"
    mem_pct               = $MemPct
    mem_kill_pct          = $MemKillPct
    mem_min_gb            = $MemMinGB
    mem_kill_gb           = $MemKillGB
    swap_pct              = $SwapPct
    swap_kill_pct         = $SwapKillPct
    swap_min_gb           = $SwapMinGB
    swap_kill_gb          = $SwapKillGB
    swap_probe_fail_open  = [bool]$SwapProbeFailOpen
    min_victim_mb         = $MinVictimMB
    max_victims_per_cycle = $MaxVictimsPerCycle
    target_cmd_regex      = $TargetCmdRegex
    protect_regex         = $ProtectRegex
    avoid_as_penalty      = [bool]$AvoidAsPenalty
    allow_wildcard_target = [bool]$AllowWildcardTarget
    guard_dry_run         = [bool]$GuardDryRun
} | Format-List
