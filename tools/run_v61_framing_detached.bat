@echo off
cd /d C:\Omega_vNext
C:\Windows\System32\cmd.exe /c python tools/v61_windows_framing.py --years 2025,2026 --workers 4 > framing_v61.log 2>&1
