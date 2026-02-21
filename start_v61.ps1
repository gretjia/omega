Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Set-Content -Path C:\Omega_vNext\framing_v61.log -Value "Starting v61 framing via powershell..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/c python C:\Omega_vNext\tools\v61_windows_framing.py --years 2023,2024,2025,2026 --workers 1 --shard 1 --total-shards 2 > C:\Omega_vNext\framing_v61.log 2>&1" -WindowStyle Hidden
