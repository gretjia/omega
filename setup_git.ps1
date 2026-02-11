$ErrorActionPreference = "Stop"

$toolsDir = Join-Path $PSScriptRoot "tools"
if (!(Test-Path $toolsDir)) {
    New-Item -ItemType Directory -Path $toolsDir | Out-Null
    Write-Host "Created tools directory."
}

$zipPath = Join-Path $toolsDir "MinGit.zip"
$gitDir = Join-Path $toolsDir "MinGit"

if (!(Test-Path $gitDir)) {
    Write-Host "Downloading MinGit..."
    # Using a specific version of MinGit
    $url = "https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.1/MinGit-2.47.1-64-bit.zip"
    Invoke-WebRequest -Uri $url -OutFile $zipPath
    
    Write-Host "Extracting MinGit..."
    Expand-Archive -Path $zipPath -DestinationPath $gitDir -Force
    
    Remove-Item $zipPath -Force
    Write-Host "MinGit installed to $gitDir"
} else {
    Write-Host "MinGit already exists at $gitDir"
}

$gitCmdPath = Join-Path $gitDir "cmd"
Write-Host "Git cmd path: $gitCmdPath"
