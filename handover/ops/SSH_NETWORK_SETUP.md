# SSH and Network Setup (omega-vm)

This document records the stable network and SSH topology used by omega-vm to supervise Linux/Windows workers.

## 1. Connection Topology

| Alias | Target | Route | Identity File |
|---|---|---|---|
| `linux1-lx` | `100.64.97.113` | Tailscale | `~/.ssh/id_ed25519_omega_workers` |
| `windows1-w1` | `100.123.90.25` | Tailscale | `~/.ssh/id_ed25519_omega_workers` |
| `mac-back` | `localhost:2222` | Reverse tunnel from Mac | `~/.ssh/id_ed25519_mac_backssh` |

## 2. Key Locations (omega-vm)

- Worker private key: `/home/zephryj/.ssh/id_ed25519_omega_workers`
- Worker public key: `/home/zephryj/.ssh/id_ed25519_omega_workers.pub`
- Reverse tunnel key: `/home/zephryj/.ssh/id_ed25519_mac_backssh`
- SSH config: `/home/zephryj/.ssh/config`

## 3. Worker Trust Anchors

- Linux: `/home/zepher/.ssh/authorized_keys`
- Windows: `C:\ProgramData\ssh\administrators_authorized_keys`

## 4. Tailscale Exit-Node Policy

Required policy:
- `omega-vm` advertises exit node.
- `linux1-lx` and `windows1-w1` use `omega-vm` as exit node.

Verification examples:

```bash
# omega-vm
sudo tailscale set --advertise-exit-node=true

# Linux
ssh linux1-lx 'tailscale status --json | rg ExitNodeStatus -n || true'

# Windows
python3 .codex/skills/omega-run-ops/scripts/ssh_ps.py windows1-w1 --command '
$j = & "C:\\Program Files\\Tailscale\\tailscale.exe" status --json | ConvertFrom-Json;
$j.ExitNodeStatus | ConvertTo-Json -Compress
'
```

## 5. Connectivity Smoke

```bash
ssh -o BatchMode=yes linux1-lx 'hostname; whoami'
ssh -o BatchMode=yes windows1-w1 'hostname && whoami'
ssh -o BatchMode=yes mac-back 'uname -srm'
```

## 6. Related Docs

- Access policy: `handover/ops/ACCESS_BOOTSTRAP.md`
- Host metadata: `handover/ops/HOSTS_REGISTRY.yaml`
- Pipeline supervision runbook: `handover/ops/OMEGA_VM_V62_PIPELINE_MONITORING_NOTES.md`

