# Access Bootstrap (SSH and Credentials)

Goal: make host access deterministic for every agent takeover without storing secrets in git.

## 1) Non-Secret Registry

Host metadata is tracked in:
- `handover/ops/HOSTS_REGISTRY.yaml`

It contains:
- alias
- host/ip
- user
- repo root path
- probe command examples

It must not contain:
- passwords
- private keys
- tokens

## 2) Credential Source of Truth

Credentials should come from local secure surfaces:

- `~/.ssh/config` (host alias + identity file reference)
- `~/.ssh/*` key files
- OS keychain / secret manager (if used)

Do not write secrets to:
- `handover/`
- `audit/`
- `README.md`

## 3) Required Aliases (Recommended)

Add these aliases in `~/.ssh/config`:

```sshconfig
Host windows1-w1
    HostName 192.168.3.112
    User jiazi
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new
    ConnectTimeout 8

Host linux1-lx
    HostName 192.168.3.113
    User zepher
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new
    ConnectTimeout 8
```

If your Mac has multi-NIC routing issues, add:
- `BindAddress <your_mac_lan_ip>`

## 4) Connectivity Smoke

Linux:

```bash
ssh linux1-lx 'hostname; whoami; uptime'
```

Windows:

```bash
ssh windows1-w1 "hostname && whoami"
python3 .codex/skills/omega-run-ops/scripts/ssh_ps.py windows1-w1 --command '$PSVersionTable.PSVersion; whoami'
```

## 5) Bootstrap References (Historical but Useful)

- `audit/20260212_mac_ssh_handover.md`
- `audit/20260212_windows_ssh_handover.md`
- `tools/setup_linux_ssh.ps1`

## 6) If Credentials Are Missing

1. Run:
   - `bash tools/agent_handover_preflight.sh`
2. If alias missing, update `~/.ssh/config`.
3. If key auth fails, re-authorize public key on target host.
4. Record only non-secret recovery notes in `handover/ai-direct/entries/`.

