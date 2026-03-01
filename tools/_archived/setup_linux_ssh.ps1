$ErrorActionPreference = "Stop"

$KeyPath = "$env:USERPROFILE\.ssh\id_ed25519_omega"
$RemoteHost = "192.168.3.113"  # UPDATED IP
$RemoteUser = "root"

Write-Host "--- OMEGA Linux SSH Setup ---"

# 1. Generate Key if missing
if (-not (Test-Path "$KeyPath.pub")) {
    Write-Host "Generating new Ed25519 key pair: $KeyPath"
    Write-Host ">>> PLEASE PRESS ENTER TWICE when prompted for passphrase <<<"
    # Interactive generation
    ssh-keygen -t ed25519 -f "$KeyPath"
} else {
    Write-Host "Using existing key: $KeyPath"
}

# 2. Read Public Key
$PubKey = Get-Content "$KeyPath.pub"
if (-not $PubKey) {
    Write-Error "Could not read public key from $KeyPath.pub"
}

Write-Host "`nReady to copy public key to $RemoteUser@$RemoteHost"
Write-Host "You will be prompted for the password ('Gret5784') next."
Write-Host "-----------------------------------------------------"

# 3. Copy ID
# We pipe the key into ssh which appends to authorized_keys
# Added -o StrictHostKeyChecking=no to avoid yes/no prompt for new host
$Command = "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$PubKey' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

ssh -o StrictHostKeyChecking=no $RemoteUser@$RemoteHost $Command

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] Key uploaded!"
    Write-Host "You can now connect without a password using:"
    Write-Host "ssh -i $KeyPath $RemoteUser@$RemoteHost"
    
    # Generate a convenient config entry
    $ConfigPath = "$env:USERPROFILE\.ssh\config"
    $ConfigEntry = "
Host omega-linux
    HostName $RemoteHost
    User $RemoteUser
    IdentityFile $KeyPath
"
    Add-Content -Path $ConfigPath -Value $ConfigEntry -ErrorAction SilentlyContinue
    Write-Host "Added 'omega-linux' alias to your SSH config."
} else {
    Write-Host "`n[FAIL] SSH command failed. Please check password and connectivity."
}
