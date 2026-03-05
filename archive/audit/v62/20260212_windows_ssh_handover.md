# 2026-02-12 Windows_1 SSH 连通 Smoke 交接单

目标：
- 仅打通 `Mac -> Windows_1` 的 SSH 连接。
- 不启动 OMEGA framing/train/backtest。
- 所有命令默认在 **Windows PowerShell** 执行。

---

## 0. 在 Windows 上准备（管理员 PowerShell）

先打开管理员 PowerShell，执行：

```powershell
$ErrorActionPreference = "Stop"

# 1) 安装 OpenSSH Server（若已安装会显示 Installed）
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# 2) 启动并设为开机自启
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic

# 3) 开放防火墙 22 端口（优先启用系统默认规则）
if (Get-NetFirewallRule -Name OpenSSH-Server-In-TCP -ErrorAction SilentlyContinue) {
  Enable-NetFirewallRule -Name OpenSSH-Server-In-TCP
} else {
  New-NetFirewallRule -Name OpenSSH-Server-In-TCP -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
}

# 可选：限制仅家庭局域网访问
# Set-NetFirewallRule -Name OpenSSH-Server-In-TCP -RemoteAddress LocalSubnet

# 4) 确认 22 端口在监听
netstat -ano | findstr ":22"
```

---

## 1. 配置公钥登录（管理员 PowerShell）

说明：把下面 `$MacPublicKey` 替换成你 Mac 上 `~/.ssh/id_ed25519.pub` 的整行内容（`ssh-ed25519 ...`）。

```powershell
$ErrorActionPreference = "Stop"

# 把这行替换为你 Mac 的公钥（整行）
$MacPublicKey = "ssh-ed25519 REPLACE_WITH_YOUR_MAC_PUBLIC_KEY"

# 1) 写入当前 Windows 用户 authorized_keys
$UserSshDir = Join-Path $env:USERPROFILE ".ssh"
$UserAuthKeys = Join-Path $UserSshDir "authorized_keys"
New-Item -ItemType Directory -Force -Path $UserSshDir | Out-Null
if (!(Test-Path $UserAuthKeys)) { New-Item -ItemType File -Path $UserAuthKeys | Out-Null }
if (-not (Select-String -Path $UserAuthKeys -Pattern [regex]::Escape($MacPublicKey) -Quiet)) {
  Add-Content -Path $UserAuthKeys -Value $MacPublicKey
}

# 2) 同时写入 administrators_authorized_keys（Windows 管理员账号常用路径）
$AdminAuthKeys = "C:\ProgramData\ssh\administrators_authorized_keys"
if (!(Test-Path $AdminAuthKeys)) { New-Item -ItemType File -Path $AdminAuthKeys -Force | Out-Null }
if (-not (Select-String -Path $AdminAuthKeys -Pattern [regex]::Escape($MacPublicKey) -Quiet)) {
  Add-Content -Path $AdminAuthKeys -Value $MacPublicKey
}

# 3) 修复权限（OpenSSH 对权限很敏感）
icacls $UserSshDir /inheritance:r | Out-Null
icacls $UserSshDir /grant "$env:USERNAME:(OI)(CI)F" | Out-Null

icacls $UserAuthKeys /inheritance:r | Out-Null
icacls $UserAuthKeys /grant "$env:USERNAME:F" | Out-Null

icacls $AdminAuthKeys /inheritance:r | Out-Null
icacls $AdminAuthKeys /grant "Administrators:F" "SYSTEM:F" | Out-Null

# 4) 重启 sshd 使配置与权限即时生效
Restart-Service sshd
```

---

## 8. Mac 复测命令（授权完成后）

授权完成并重启 `sshd` 后，请通知 Mac 侧执行：

```bash
ssh -b 192.168.3.49 -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new jiazi@192.168.3.112 "hostname && whoami"
```

说明：
- 该 Mac 当前有双网卡同网段（`en0`/`en1`），默认路由偶发 `No route to host`。
- 显式绑定源 IP `192.168.3.49` 可稳定到达 Windows_1。

---

## 2. Windows 本机自检（不经过 Mac）

```powershell
# 本机 loopback 测试：确认 sshd 可以登录
ssh -o StrictHostKeyChecking=no $env:USERNAME@localhost "hostname && whoami"
```

若出现主机名和用户名，说明 Windows 端 SSH 服务正常。

---

## 3. 提供给 Mac 的连接信息（在 Windows 执行）

```powershell
whoami
hostname
ipconfig
```

把以下信息发给我：
- Windows 登录用户名（如 `DESKTOP-XXX\\your_user` 的 `your_user`）
- Windows 主机名
- 同一局域网 IPv4（例如 `192.168.50.23`）

---

## 4. Mac 侧 smoke（仅连通，不跑计算）

我这边会执行类似命令（不会启动 OMEGA 任务）：

```bash
ssh -o StrictHostKeyChecking=accept-new <windows_user>@<windows_ip> "hostname && whoami"
```

---

## 5. 失败排查（Windows）

### 5.1 连接被拒绝 / 超时

```powershell
Get-Service sshd
netstat -ano | findstr ":22"
Get-NetFirewallRule -Name OpenSSH-Server-In-TCP
```

### 5.2 公钥认证失败（Permission denied (publickey)）

```powershell
# 查看 sshd 日志（若系统存在该日志文件）
Get-Content "C:\ProgramData\ssh\logs\sshd.log" -Tail 200

# 重新应用权限并重启服务
Restart-Service sshd
```

---

## 6. 本次操作边界

本交接单仅做 SSH 连接烟雾测试，不包含：
- `python pipeline_runner.py --stage frame`
- `parallel_trainer/run_parallel_v31.py`
- `parallel_trainer/run_parallel_backtest_v31.py`

等当前 pipeline 跑完后，再进入远程执行与自动化编排。

---

## 7. 异步握手：Mac 公钥（已提供）

请使用以下公钥进行授权：

`ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAID/DbbiUlffA+HW5K0xYsxq41A5BO4XdYw5JN3ebCNkQ zephryj@ZephrydeMac-Studio.local`

Windows 端可直接执行（管理员 PowerShell）：

```powershell
$ErrorActionPreference = "Stop"
$MacPublicKey = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAID/DbbiUlffA+HW5K0xYsxq41A5BO4XdYw5JN3ebCNkQ zephryj@ZephrydeMac-Studio.local"

$UserSshDir = Join-Path $env:USERPROFILE ".ssh"
$UserAuthKeys = Join-Path $UserSshDir "authorized_keys"
New-Item -ItemType Directory -Force -Path $UserSshDir | Out-Null
if (!(Test-Path $UserAuthKeys)) { New-Item -ItemType File -Path $UserAuthKeys | Out-Null }
if (-not (Select-String -Path $UserAuthKeys -Pattern [regex]::Escape($MacPublicKey) -Quiet)) { Add-Content -Path $UserAuthKeys -Value $MacPublicKey }

$AdminAuthKeys = "C:\ProgramData\ssh\administrators_authorized_keys"
if (!(Test-Path $AdminAuthKeys)) { New-Item -ItemType File -Path $AdminAuthKeys -Force | Out-Null }
if (-not (Select-String -Path $AdminAuthKeys -Pattern [regex]::Escape($MacPublicKey) -Quiet)) { Add-Content -Path $AdminAuthKeys -Value $MacPublicKey }

Restart-Service sshd
```

---

## 8. Mac 复测命令（授权完成后）

授权完成并重启 `sshd` 后，请通知 Mac 侧执行：

```bash
ssh -b 192.168.3.49 -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new jiazi@192.168.3.112 "hostname && whoami"
```

说明：
- 该 Mac 当前有双网卡同网段（`en0`/`en1`），默认路由偶发 `No route to host`。
- 显式绑定源 IP `192.168.3.49` 可稳定到达 Windows_1。
