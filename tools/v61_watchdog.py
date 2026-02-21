#!/usr/bin/env python3
"""
v61 OMEGA Watchdog
Run this locally on the Mac to monitor the remote framing nodes (Linux & Windows).
Will trigger visual notifications and Voice alerts (Ting-Ting) if anomalies are detected.
"""

import time
import os
import subprocess
import datetime
import sys

# Mac Text-to-Speech alert
def say_alert(msg):
    print(f"\n\033[91m🚨 WATCHDOG ALERT: {msg}\033[0m\n")
    # MacOS notification
    os.system(f"""osascript -e 'display notification "{msg}" with title "OMEGA WATCHDOG"'""")
    # MacOS Chinese voice
    os.system(f"say -v Ting-Ting '{msg}'")

def ssh_cmd(host, cmd, timeout=10):
    try:
        r = subprocess.run(["ssh", "-o", "ConnectTimeout=5", host, cmd], 
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip()
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"
    except Exception as e:
        return -1, str(e)

def run_watchdog():
    print(f"[{datetime.datetime.now()}] Gearing up OMEGA Watchdog (v61)...")
    print("Monitoring nodes: Linux(192.168.3.113), Windows(192.168.3.112)\n")
    
    linux = "zepher@192.168.3.113"
    windows = "jiazi@192.168.3.112"
    
    l_last_files = 0
    w_last_files = 0
    stalled_minutes = 0

    while True:
        now_str = datetime.datetime.now().strftime('%H:%M:%S')
        try:
            # --- LINUX CHECKS ---
            _, l_ps = ssh_cmd(linux, "ps aux | grep python3 | grep -v grep | grep v61_linux")
            l_alive = "v61_linux" in l_ps
            
            _, l_fs = ssh_cmd(linux, "df -h / | tail -1 | awk '{print $5}'")
            l_mem = ssh_cmd(linux, "free -g | grep Mem | awk '{print $7}'")[1]
            l_tail = ssh_cmd(linux, "tail -n 1 ~/work/Omega_vNext/framing_v61.log")[1][-80:]
            
            l_cnt_out = ssh_cmd(linux, "find /omega_pool/parquet_data/v61 -name '*.done' 2>/dev/null | wc -l")[1]
            l_cnt = int(l_cnt_out) if l_cnt_out.isdigit() else l_last_files

            # --- WINDOWS CHECKS ---
            _, w_ps = ssh_cmd(windows, 'powershell -Command "Get-Process -Name python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id"')
            w_alive = len(w_ps) > 0

            w_fs = ssh_cmd(windows, 'powershell -Command "$d=Get-Volume -DriveLetter C; [math]::Round(($d.Size - $d.SizeRemaining)/$d.Size * 100)"')[1]
            w_tail_cmd = 'powershell -Command "Get-Content C:\\Omega_vNext\\framing_v61.log -Tail 1 -ErrorAction SilentlyContinue"'
            w_tail = ssh_cmd(windows, w_tail_cmd)[1][-80:]
            
            w_cnt_cmd = 'powershell -Command "(Get-ChildItem -Path D:\\Omega_frames\\v61 -Recurse -Filter *.done -ErrorAction SilentlyContinue | Measure-Object).Count"'
            w_cnt_out = ssh_cmd(windows, w_cnt_cmd)[1]
            w_cnt = int(w_cnt_out) if w_cnt_out.isdigit() else w_last_files

            # --- DASHBOARD PRINT ---
            sys.stdout.write(f"\r\033[K[{now_str}] ")
            sys.stdout.write(f"🐧 Linux [Files: {l_cnt} | 💽 {l_fs}] <{l_tail}>  |  ")
            sys.stdout.write(f"🪟 Windows [Files: {w_cnt} | 💽 {w_fs}%] <{w_tail}>")
            sys.stdout.flush()

            # --- ALARM LOGIC ---
            if not l_alive: say_alert("Linux framing 进程已掉线！")
            if not w_alive: say_alert("Windows framing 进程已掉线！")
            
            if l_fs == "100%" or l_fs == "99%": say_alert("Linux Root 根节点磁盘爆满！")
            if l_mem.isdigit() and int(l_mem) < 2: say_alert("Linux 可用内存不足低于2G！")
            
            error_keywords = ["CRITICAL", "Error", "killed", "OOM"]
            if any(k in l_tail for k in error_keywords) and "Empty frames" not in l_tail:
                say_alert(f"Linux 日志出现错误词: {l_tail}")
            if any(k in w_tail for k in error_keywords) and "Empty frames" not in w_tail:
                say_alert(f"Windows 日志出现错误词: {w_tail}")

            # Check Stall
            if l_cnt == l_last_files and w_cnt == w_last_files:
                stalled_minutes += 1
                if stalled_minutes >= 30:
                    say_alert("进度已停滞长达 30 分钟没有新产出！")
            else:
                stalled_minutes = 0

            l_last_files = l_cnt
            w_last_files = w_cnt

            time.sleep(60)

        except KeyboardInterrupt:
            print("\nWatchdog safely terminated.")
            break
        except Exception as e:
            print(f"\n[Warning] Poll cycle error: {e}")
            time.sleep(10)

if __name__ == '__main__':
    run_watchdog()
