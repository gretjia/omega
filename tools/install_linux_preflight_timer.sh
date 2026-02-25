#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Install/refresh Omega Linux preflight systemd timer.

Usage:
  bash tools/install_linux_preflight_timer.sh [options]

Options:
  --repo-root <path>   Repo root on Linux host. Default: /home/zepher/work/Omega_vNext
  --user <name>        Service user. Default: current user
  --interval-min <n>   Timer interval in minutes. Default: 10
  --min-cache-gb <n>   Minimum cache free-space threshold (GB). Default: 50
  --disable            Disable and remove installed timer/service
  -h, --help           Show help

Notes:
  - Must run on Linux with systemd.
  - Requires sudo to write /etc/systemd/system unit files.
EOF
}

repo_root="/home/zepher/work/Omega_vNext"
svc_user="$(id -un)"
interval_min="10"
min_cache_gb="50"
disable_mode=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      repo_root="${2:-}"
      shift 2
      ;;
    --user)
      svc_user="${2:-}"
      shift 2
      ;;
    --interval-min)
      interval_min="${2:-}"
      shift 2
      ;;
    --min-cache-gb)
      min_cache_gb="${2:-}"
      shift 2
      ;;
    --disable)
      disable_mode=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This installer must run on Linux host (systemd)." >&2
  exit 2
fi

if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemctl not found. This host is not systemd-capable." >&2
  exit 2
fi

if [[ ! -d "${repo_root}" ]]; then
  echo "Repo root does not exist: ${repo_root}" >&2
  exit 2
fi

svc_name="omega_linux_preflight"
svc_file="/etc/systemd/system/${svc_name}.service"
timer_file="/etc/systemd/system/${svc_name}.timer"
log_file="${repo_root}/audit/linux_preflight_timer.log"
json_out="${repo_root}/audit/runtime/linux_preflight/latest.json"

if [[ ${disable_mode} -eq 1 ]]; then
  echo "Disabling ${svc_name}.timer ..."
  sudo systemctl disable --now "${svc_name}.timer" || true
  sudo rm -f "${svc_file}" "${timer_file}"
  sudo systemctl daemon-reload
  echo "Removed ${svc_file} and ${timer_file}"
  exit 0
fi

if ! [[ "${interval_min}" =~ ^[0-9]+$ ]] || [[ "${interval_min}" -lt 1 ]]; then
  echo "--interval-min must be a positive integer." >&2
  exit 2
fi

mkdir -p "$(dirname "${log_file}")"
mkdir -p "$(dirname "${json_out}")"

tmp_svc="$(mktemp)"
tmp_timer="$(mktemp)"
trap 'rm -f "${tmp_svc}" "${tmp_timer}"' EXIT

cat > "${tmp_svc}" <<EOF
[Unit]
Description=Omega Linux Runtime Preflight
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=${svc_user}
Group=${svc_user}
WorkingDirectory=${repo_root}
ExecStart=/usr/bin/env python3 ${repo_root}/tools/linux_runtime_preflight.py --repo-root ${repo_root} --auto-fix --min-cache-free-gb ${min_cache_gb} --json-out ${json_out}
StandardOutput=append:${log_file}
StandardError=append:${log_file}
Nice=10

[Install]
WantedBy=multi-user.target
EOF

cat > "${tmp_timer}" <<EOF
[Unit]
Description=Run Omega Linux Runtime Preflight every ${interval_min} minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=${interval_min}min
Persistent=true
Unit=${svc_name}.service

[Install]
WantedBy=timers.target
EOF

echo "Installing ${svc_file}"
sudo install -m 0644 "${tmp_svc}" "${svc_file}"
echo "Installing ${timer_file}"
sudo install -m 0644 "${tmp_timer}" "${timer_file}"

sudo systemctl daemon-reload
sudo systemctl enable --now "${svc_name}.timer"

echo
echo "Timer status:"
sudo systemctl status "${svc_name}.timer" --no-pager || true
echo
echo "Next runs:"
systemctl list-timers "${svc_name}.timer" --no-pager || true
echo
echo "Manual run:"
echo "  sudo systemctl start ${svc_name}.service"
echo "Log:"
echo "  tail -n 120 ${log_file}"
echo "JSON report:"
echo "  cat ${json_out}"
