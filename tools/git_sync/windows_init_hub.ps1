param(
    [string]$SourceRepoPath = "C:\Omega_vNext",
    [string]$BareHubPath = "C:\Git\Omega_vNext.git",
    [string]$RemoteName = "hub",
    [bool]$PushTags = $true
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Invoke-Git {
    param(
        [string[]]$Args,
        [string]$RepoPath = ""
    )

    if ([string]::IsNullOrWhiteSpace($RepoPath)) {
        & git @Args
    } else {
        & git -C $RepoPath @Args
    }

    if ($LASTEXITCODE -ne 0) {
        throw "git $($Args -join ' ') failed with exit code $LASTEXITCODE"
    }
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git command not found. Install Git for Windows first."
}

if (-not (Test-Path $SourceRepoPath)) {
    throw "Source repository path does not exist: $SourceRepoPath"
}

if (-not (Test-Path (Join-Path $SourceRepoPath ".git"))) {
    throw "Not a Git repository: $SourceRepoPath"
}

$hubParent = Split-Path -Parent $BareHubPath
if (-not (Test-Path $hubParent)) {
    New-Item -ItemType Directory -Path $hubParent -Force | Out-Null
}

if (-not (Test-Path $BareHubPath)) {
    Write-Host "[Init] Creating bare hub: $BareHubPath"
    Invoke-Git -Args @("init", "--bare", $BareHubPath)
} else {
    $isBare = (& git --git-dir $BareHubPath rev-parse --is-bare-repository 2>$null).Trim()
    if ($LASTEXITCODE -ne 0 -or $isBare -ne "true") {
        throw "Target exists but is not a valid bare repository: $BareHubPath"
    }
    Write-Host "[Init] Bare hub already exists: $BareHubPath"
}

$remoteExists = $false
& git -C $SourceRepoPath remote get-url $RemoteName 1>$null 2>$null
if ($LASTEXITCODE -eq 0) {
    $remoteExists = $true
}

if ($remoteExists) {
    $currentUrl = (& git -C $SourceRepoPath remote get-url $RemoteName).Trim()
    if ($currentUrl -ne $BareHubPath) {
        Write-Host "[Config] Updating remote '$RemoteName' URL:"
        Write-Host "         $currentUrl -> $BareHubPath"
        Invoke-Git -RepoPath $SourceRepoPath -Args @("remote", "set-url", $RemoteName, $BareHubPath)
    } else {
        Write-Host "[Config] Remote '$RemoteName' already points to bare hub."
    }
} else {
    Write-Host "[Config] Adding remote '$RemoteName' -> $BareHubPath"
    Invoke-Git -RepoPath $SourceRepoPath -Args @("remote", "add", $RemoteName, $BareHubPath)
}

Write-Host "[Push] Pushing all branches to '$RemoteName'..."
Invoke-Git -RepoPath $SourceRepoPath -Args @("push", $RemoteName, "--all")

if ($PushTags) {
    Write-Host "[Push] Pushing all tags to '$RemoteName'..."
    Invoke-Git -RepoPath $SourceRepoPath -Args @("push", $RemoteName, "--tags")
}

$computer = $env:COMPUTERNAME
Write-Host ""
Write-Host "[Done] Hub is ready."
Write-Host "Use this SSH remote URL from other machines (replace <user>):"
Write-Host "  ssh://<user>@$computer/C:/Git/Omega_vNext.git"
Write-Host ""
Write-Host "Example on Mac/Windows2:"
Write-Host "  git remote add hub ssh://<user>@$computer/C:/Git/Omega_vNext.git"
