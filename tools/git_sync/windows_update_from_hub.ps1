param(
    [string]$RepoPath = "C:\Omega_vNext",
    [string]$RemoteName = "hub",
    [string]$Branch = "main",
    [switch]$AllowDirty,
    [bool]$FetchTags = $true
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Invoke-Git {
    param(
        [string[]]$Args
    )
    & git -C $RepoPath @Args
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Args -join ' ') failed with exit code $LASTEXITCODE"
    }
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git command not found. Install Git for Windows first."
}

if (-not (Test-Path $RepoPath)) {
    throw "Repository path does not exist: $RepoPath"
}

if (-not (Test-Path (Join-Path $RepoPath ".git"))) {
    throw "Not a Git repository: $RepoPath"
}

& git -C $RepoPath remote get-url $RemoteName 1>$null 2>$null
if ($LASTEXITCODE -ne 0) {
    throw "Remote '$RemoteName' does not exist in $RepoPath"
}

if (-not $AllowDirty) {
    & git -C $RepoPath diff --quiet --exit-code
    if ($LASTEXITCODE -ne 0) {
        throw "Working tree has unstaged changes. Commit/stash first or use -AllowDirty."
    }

    & git -C $RepoPath diff --cached --quiet --exit-code
    if ($LASTEXITCODE -ne 0) {
        throw "Index has staged changes. Commit/stash first or use -AllowDirty."
    }
}

$fetchArgs = @("fetch", $RemoteName, "--prune")
if ($FetchTags) {
    $fetchArgs += "--tags"
}
Write-Host "[Sync] Fetching from $RemoteName..."
Invoke-Git -Args $fetchArgs

& git -C $RepoPath show-ref --verify --quiet "refs/heads/$Branch"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[Sync] Local branch '$Branch' not found. Creating tracking branch."
    Invoke-Git -Args @("switch", "-c", $Branch, "--track", "$RemoteName/$Branch")
} else {
    Invoke-Git -Args @("switch", $Branch)
}

Write-Host "[Sync] Pulling latest '$Branch' with ff-only..."
Invoke-Git -Args @("pull", "--ff-only", $RemoteName, $Branch)

$head = (& git -C $RepoPath rev-parse --short HEAD).Trim()
Write-Host "[Done] $RepoPath is now at $head on $Branch"
