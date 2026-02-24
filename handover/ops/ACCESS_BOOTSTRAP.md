# Access Bootstrap (Credentials and SSH)

Goal: deterministic access for all agents without storing secrets in git.

## 1. Credential Policy

- Store credentials only in secure local surfaces.
- Keep only credential locations and validation commands in repo docs.
- Never commit private keys, passwords, OAuth refresh tokens, or raw ADC JSON.

## 2. Credential Locations (omega-vm)

- SSH config: `/home/zephryj/.ssh/config`
- Worker key (private): `/home/zephryj/.ssh/id_ed25519_omega_workers`
- Reverse-tunnel key (private): `/home/zephryj/.ssh/id_ed25519_mac_backssh`
- gcloud config: `/home/zephryj/.config/gcloud`
- ADC location: `/home/zephryj/.config/gcloud/application_default_credentials.json`

## 3. Required SSH Aliases

Expected aliases:
- `linux1-lx`
- `windows1-w1`
- `mac-back` (reverse tunnel to Mac)

Example config skeleton:

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

Host mac-back
    HostName localhost
    Port 2222
    User zephryj
    IdentityFile ~/.ssh/id_ed25519_mac_backssh
```

## 4. Bootstrap Steps

1. Run preflight:
   - `bash tools/agent_handover_preflight.sh`
2. If alias missing, update `~/.ssh/config`.
3. If auth fails, refresh remote `authorized_keys`.
4. Validate connectivity:
   - `ssh -o BatchMode=yes linux1-lx 'hostname; whoami'`
   - `ssh -o BatchMode=yes windows1-w1 'hostname && whoami'`

## 5. Worker Trust Anchors

- Linux authorized keys: `/home/zepher/.ssh/authorized_keys`
- Windows authorized keys: `C:\ProgramData\ssh\administrators_authorized_keys`

## 6. Tailscale Exit-Node Requirement

- `omega-vm` advertises exit node.
- Linux and Windows route egress through `omega-vm`.
- See detailed setup and verification:
  - `handover/ops/SSH_NETWORK_SETUP.md`

## 7. Escalation if Access Breaks

1. Confirm tailnet reachability (`tailscale ping` and TCP/22).
2. Confirm key presence and permissions on target host.
3. Confirm `sshd` service state on target host.
4. Record non-secret RCA in `handover/ai-direct/entries/*.md` and update `LATEST.md`.

