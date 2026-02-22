#!/usr/bin/env python3
import subprocess
import time
import re
from pathlib import Path

SSH_PS = Path('/Users/zephryj/work/Omega_vNext/.codex/skills/omega-run-ops/scripts/ssh_ps.py')
HOST = 'jiazi@192.168.3.112'
TASK1 = 'Omega_v52_frame03_recovery_aa8abb7'
TASK2 = 'Omega_v52_frame03_recovery2_aa8abb7'
LOG = Path('/Users/zephryj/work/Omega_vNext/audit/runtime/v52/windows_recovery_followup_aa8abb7.log')


def log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG.open('a', encoding='utf-8') as f:
        f.write(line + '\n')


def run_ps(ps: str) -> str:
    cmd = ['python3', str(SSH_PS), HOST, '--command', ps]
    p = subprocess.run(cmd, text=True, capture_output=True)
    return (p.stdout or '') + '\n' + (p.stderr or '')


def parse_value(text: str, key: str, default: str = '') -> str:
    m = re.search(rf'{re.escape(key)}=([^\r\n]+)', text)
    return m.group(1).strip() if m else default


log('followup watcher started')

# Wait for task1 to finish
while True:
    out = run_ps(
        "$ProgressPreference='SilentlyContinue'; "
        f"$s=(Get-ScheduledTask -TaskName '{TASK1}' -ErrorAction SilentlyContinue).State; "
        "$d=(Get-ChildItem -Path 'D:\\Omega_frames\\v52\\frames\\host=windows1' -Filter '*_aa8abb7.parquet.done' -ErrorAction SilentlyContinue).Count; "
        "Write-Output ('state=' + $s); Write-Output ('done=' + $d)"
    )
    state = parse_value(out, 'state', 'Unknown')
    done = parse_value(out, 'done', '-1')
    log(f'task1 state={state} done={done}')
    if state.lower() != 'running':
        break
    time.sleep(60)

# Check if 20241104 is missing
out = run_ps(
    "$ProgressPreference='SilentlyContinue'; "
    "$p='D:\\Omega_frames\\v52\\frames\\host=windows1\\20241104_aa8abb7.parquet.done'; "
    "Write-Output ('has_20241104=' + (Test-Path $p))"
)
has_20241104 = parse_value(out, 'has_20241104', 'False').lower() == 'true'
log(f'has_20241104={has_20241104}')

if not has_20241104:
    log('launching task2 for missing 20241104 (no-BOM list)')
    run_ps(
        "$ProgressPreference='SilentlyContinue'; "
        "$list='D:\\work\\Omega_vNext\\audit\\runtime\\v52\\shard_windows1_recovery2_aa8abb7.txt'; "
        "Set-Content -Path $list -Value @('2024/202411/20241104.7z') -Encoding Ascii; "
        "$task='Omega_v52_frame03_recovery2_aa8abb7'; "
        "$root='D:\\work\\Omega_vNext'; "
        "$py='C:\\Python314\\python.exe'; "
        "$args='-u D:\\work\\Omega_vNext\\pipeline_runner.py --stage frame --config D:\\work\\Omega_vNext\\configs\\hardware\\windows1.yaml --archive-list D:\\work\\Omega_vNext\\audit\\runtime\\v52\\shard_windows1_recovery2_aa8abb7.txt'; "
        "if(Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue){ Unregister-ScheduledTask -TaskName $task -Confirm:$false }; "
        "$action=New-ScheduledTaskAction -Execute $py -Argument $args -WorkingDirectory $root; "
        "$trigger=New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1); "
        "$principal=New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Limited; "
        "$settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 6); "
        "Register-ScheduledTask -TaskName $task -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null; "
        "Start-ScheduledTask -TaskName $task; "
        "Write-Output 'task2_started=True'"
    )

    while True:
        out2 = run_ps(
            "$ProgressPreference='SilentlyContinue'; "
            f"$s=(Get-ScheduledTask -TaskName '{TASK2}' -ErrorAction SilentlyContinue).State; "
            "$d=(Get-ChildItem -Path 'D:\\Omega_frames\\v52\\frames\\host=windows1' -Filter '*_aa8abb7.parquet.done' -ErrorAction SilentlyContinue).Count; "
            "Write-Output ('state2=' + $s); Write-Output ('done=' + $d)"
        )
        state2 = parse_value(out2, 'state2', 'Unknown')
        done2 = parse_value(out2, 'done', '-1')
        log(f'task2 state={state2} done={done2}')
        if state2.lower() != 'running':
            break
        time.sleep(60)

# Final count
outf = run_ps(
    "$ProgressPreference='SilentlyContinue'; "
    "$d=(Get-ChildItem -Path 'D:\\Omega_frames\\v52\\frames\\host=windows1' -Filter '*_aa8abb7.parquet.done' -ErrorAction SilentlyContinue).Count; "
    "Write-Output ('done_final=' + $d)"
)
log('final ' + parse_value(outf, 'done_final', '-1'))
log('followup watcher complete')
