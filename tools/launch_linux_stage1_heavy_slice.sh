#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Launch Linux Stage1 ETL in heavy-workload.slice (not user.slice).

Usage:
  bash tools/launch_linux_stage1_heavy_slice.sh [options] [-- <stage1 args>]

Options:
  --repo-root <path>   Repo root on Linux host. Default: /home/zepher/work/Omega_vNext
  --unit <name>        Systemd unit name. Default: omega_stage1_linux_<timestamp>
  --log <path>         Log path (absolute or repo-relative). Default: audit/stage1_linux_v62.log
  --python <path>      Python interpreter. Default: <repo-root>/.venv/bin/python (fallback: /usr/bin/python3)
  --dry-run            Print command only, do not execute.
  -h, --help           Show help.

If no stage1 args are provided after "--", safe defaults are used:
  --years 2023,2024,2025,2026 --total-shards 4 --shard 0,1,2 --workers 1

Examples:
  bash tools/launch_linux_stage1_heavy_slice.sh
  bash tools/launch_linux_stage1_heavy_slice.sh -- --years 2026 --total-shards 8 --shard 0,1 --workers 1
  bash tools/launch_linux_stage1_heavy_slice.sh --dry-run -- --years 2025,2026 --workers 1
EOF
}

repo_root="/home/zepher/work/Omega_vNext"
unit="omega_stage1_linux_$(date +%Y%m%d_%H%M%S)"
log_path="audit/stage1_linux_v62.log"
python_bin=""
dry_run=0
stage_args=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root)
      repo_root="${2:-}"
      shift 2
      ;;
    --unit)
      unit="${2:-}"
      shift 2
      ;;
    --log)
      log_path="${2:-}"
      shift 2
      ;;
    --python)
      python_bin="${2:-}"
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      if [[ $# -gt 0 ]]; then
        stage_args=("$@")
      fi
      break
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "${repo_root}" || -z "${unit}" || -z "${log_path}" ]]; then
  echo "repo_root/unit/log_path cannot be empty." >&2
  exit 2
fi

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This launcher must run on Linux host (systemd)." >&2
  exit 2
fi

if ! command -v systemd-run >/dev/null 2>&1 || ! command -v systemctl >/dev/null 2>&1; then
  echo "systemd-run/systemctl not found. This host is not systemd-capable." >&2
  exit 2
fi

if [[ ${#stage_args[@]} -eq 0 ]]; then
  stage_args=(
    --years 2023,2024,2025,2026
    --total-shards 4
    --shard 0,1,2
    --workers 1
  )
fi

if [[ "${log_path}" != /* ]]; then
  log_path="${repo_root}/${log_path}"
fi

if [[ -z "${python_bin}" ]]; then
  if [[ -x "${repo_root}/.venv/bin/python" ]]; then
    python_bin="${repo_root}/.venv/bin/python"
  else
    python_bin="/usr/bin/python3"
  fi
fi

if [[ "${python_bin}" != /* ]]; then
  python_bin="$(command -v "${python_bin}" || true)"
fi
if [[ -z "${python_bin}" || ! -x "${python_bin}" ]]; then
  echo "Python interpreter not executable: ${python_bin:-<empty>}" >&2
  exit 2
fi

if ! "${python_bin}" -c 'import polars' >/dev/null 2>&1; then
  echo "Python '${python_bin}' cannot import polars. Aborting." >&2
  exit 2
fi

echo "== Slice Guardrail Check =="
systemctl show user-1000.slice -p MemoryHigh -p MemoryMax --no-pager || true
systemctl show heavy-workload.slice -p MemoryHigh -p MemoryMax --no-pager || true
echo
echo "Python: ${python_bin}"
echo "RunAs UID:GID = $(id -u):$(id -g)"
echo

cmd=(
  sudo systemd-run
  --unit "${unit}"
  --slice=heavy-workload.slice
  --uid "$(id -u)"
  --gid "$(id -g)"
  --working-directory "${repo_root}"
  --property=OOMPolicy=kill
  --property=OOMScoreAdjust=300
  --property=MemoryAccounting=yes
  --property=CPUAccounting=yes
  --property=IOAccounting=yes
  --property=TimeoutStopSec=30s
  --property="StandardOutput=append:${log_path}"
  --property="StandardError=append:${log_path}"
  --collect
  --no-block
  "${python_bin}" -u tools/stage1_linux_base_etl.py
  "${stage_args[@]}"
)

echo "== Launch Command =="
printf '%q ' "${cmd[@]}"
echo
echo

if [[ ${dry_run} -eq 1 ]]; then
  echo "[DRY-RUN] Not executed."
  exit 0
fi

"${cmd[@]}"
sleep 1

echo "== Unit Status =="
sudo systemctl show "${unit}" -p Id -p ActiveState -p SubState -p Slice --no-pager || true
active_state="$(sudo systemctl show "${unit}" -p ActiveState --value --no-pager 2>/dev/null || true)"
actual_slice="$(sudo systemctl show "${unit}" -p Slice --value --no-pager 2>/dev/null || true)"
if [[ "${active_state}" == "active" || "${active_state}" == "activating" ]]; then
  if [[ "${actual_slice}" != "heavy-workload.slice" ]]; then
    echo "[FATAL] ${unit} is in unexpected slice: ${actual_slice:-<none>}" >&2
    echo "Stopping unit to avoid user.slice OOM risk..." >&2
    sudo systemctl stop "${unit}" || true
    exit 3
  fi
else
  if sudo journalctl -u "${unit}" -n 60 --no-pager 2>/dev/null \
    | rg -F "[FATAL] stage1 is not running in heavy-workload.slice." >/dev/null; then
    echo "[FATAL] stage1 self-guard rejected non-heavy-workload startup." >&2
    exit 4
  fi
fi
echo
echo "Log tail:"
echo "  tail -n 80 ${log_path}"
echo "Journal:"
echo "  sudo journalctl -u ${unit} -n 120 --no-pager"
