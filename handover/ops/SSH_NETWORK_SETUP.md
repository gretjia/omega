# SSH Network Setup (Omega VM)

This document records the SSH configuration and credential locations used by `omega-vm` to connect to workers and monitor the v62 pipeline.

## 1. Summary of Connections

| Alias | Target | Connection Type | Identity File |
|-------|--------|-----------------|---------------|
| `mac-back` | Local Mac | Reverse Tunnel (localhost:2222) | `~/.ssh/id_ed25519_mac_backssh` |
| `linux1-lx` | Linux (100.64.97.113) | Tailscale Direct | `~/.ssh/id_ed25519_omega_workers` |
| `windows1-w1` | Windows (100.123.90.25) | Tailscale Direct | `~/.ssh/id_ed25519_omega_workers` |

## 2. Worker Connectivity (`linux1-lx`, `windows1-w1`)

A dedicated long-term key was generated on `omega-vm` for automated access to workers.

- **Private Key**: `/home/zephryj/.ssh/id_ed25519_omega_workers`
- **Public Key Fingerprint**: `SHA256:aNmM08iqAFQPrSDgTmdfy4spkJXXcXVVpgjYohTqnaY`

### Configuration (`/home/zephryj/.ssh/config`)
```sshconfig
Host linux1-lx
    HostName 100.64.97.113
    User zepher
    IdentityFile ~/.ssh/id_ed25519_omega_workers
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new
    ConnectTimeout 8

Host windows1-w1
    HostName 100.123.90.25
    User jiazi
    IdentityFile ~/.ssh/id_ed25519_omega_workers
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new
    ConnectTimeout 8
```

### Worker trust anchors

- Linux authorized key target: `/home/zepher/.ssh/authorized_keys`
- Windows authorized key target: `C:\ProgramData\ssh\administrators_authorized_keys`
- Windows firewall rule requirement: allow inbound TCP/22 from Tailscale subnet `100.64.0.0/10`

## 3. Reverse Tunnel to Mac (`mac-back`)

The Mac workstation maintains a reverse SSH tunnel to `omega-vm` to allow direct access back to the host machine.

- **Local Port on VM**: 2222
- **Key on VM**: `~/.ssh/id_ed25519_mac_backssh` (authorized on Mac)
- **Key on Mac**: `~/.ssh/id_ed25519_omega_backssh` (authorized on VM)
- **Persistence**: Managed via `LaunchAgent` on Mac (`com.zephryj.omega.backssh.plist`).

### Configuration (`~/.ssh/config`)
```sshconfig
Host mac-back
    HostName localhost
    Port 2222
    User zephryj
    IdentityFile ~/.ssh/id_ed25519_mac_backssh
```

## 4. GCP Credential Paths on omega-vm (Stage3 supervision)

For Vertex Train/Backtest monitoring on `omega-vm`:

- gcloud config directory: `/home/zephryj/.config/gcloud`
- ADC file: `/home/zephryj/.config/gcloud/application_default_credentials.json`
- Check active account:
  - `gcloud auth list`

## 5. Verification Commands

```bash
# Verify Linux
ssh linux1-lx "hostname; whoami"

# Verify Windows
ssh windows1-w1 "hostname && whoami"

# Verify Mac
ssh mac-back "uname -srm"

# Verify gcloud auth
gcloud auth list
```

## 6. Pipeline Supervision Entry

Use this as the canonical v62 monitor runbook:

- `handover/ops/OMEGA_VM_V62_PIPELINE_MONITORING_NOTES.md`

This includes Stage1 -> Stage2 -> Stage3 flow, logs, outputs, and 20-minute watch loop template.

## 7. Maintenance Notes
- If `mac-back` is down, check the `omega-backssh` service on the Mac.
- If worker access fails, ensure the public key is still in the target's `authorized_keys`.
