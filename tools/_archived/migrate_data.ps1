# Data Migration Script (D: -> E:)
$ErrorActionPreference = "Stop"

function Migrate-Folder {
    param($Name)
    $src = "D:\Omega_vNext\data\$Name"
    $dst = "E:\data\$Name"
    
    Write-Host "`n>>> Processing: $Name" -ForegroundColor Cyan
    if (-not (Test-Path $src)) {
        Write-Host "Source not found, skipping."
        return
    }
    
    if (-not (Test-Path $dst)) {
        New-Item -Path $dst -ItemType Directory -Force | Out-Null
    }
    
    Write-Host "Robocopy Moving..."
    # /E (Recursive), /MOVE (Delete Source), /Z (Restartable), /MT:32 (Multi-threaded)
    $p = Start-Process robocopy -ArgumentList "`"$src`" `"$dst`" /E /MOVE /Z /MT:32 /R:10 /W:5 /NFL /NDL /NJH /NJS" -Wait -PassThru -NoNewWindow
    
    if ($p.ExitCode -ge 8) {
        Write-Host "Robocopy failed with code $($p.ExitCode)" -ForegroundColor Red
        return
    }
    
    if (-not (Test-Path $src)) {
        Write-Host "Migration complete. Creating Junction..."
        cmd /c mklink /J "$src" "$dst"
    } else {
        # Check if empty
        if ((Get-ChildItem $src -Recurse).Count -eq 0) {
            Write-Host "Source is empty. Deleting and Linking..."
            Remove-Item $src -Recurse -Force
            cmd /c mklink /J "$src" "$dst"
        } else {
            Write-Host "[!] Source NOT empty. Migration incomplete." -ForegroundColor Yellow
        }
    }
}

Migrate-Folder "level2"
Migrate-Folder "level2_frames_v40_win"

Write-Host "`nAll Migration Tasks Finished." -ForegroundColor Green
Read-Host "Press Enter to exit..."
