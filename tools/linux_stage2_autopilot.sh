#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Linux Stage2 autopilot: keep Stage2 running until all inputs have .done markers.

Usage:
  bash tools/linux_stage2_autopilot.sh [options]

Options:
  --repo-root <path>         Repo root. Default: /home/zepher/work/Omega_vNext
  --input-dir <path>         Stage2 input dir. Default: /omega_pool/parquet_data/v62_base_l1/host=linux1
  --output-dir <path>        Stage2 output dir. Default: /omega_pool/parquet_data/v62_feature_l2/host=linux1
  --timeout-sec <n>          Per-file timeout for targeted runner. Default: 2400
  --poll-sec <n>             Poll interval. Default: 90
  --batch-size <n>           OMEGA_STAGE2_SYMBOL_BATCH_SIZE. Default: 24
  --polars-threads <n>       OMEGA_STAGE2_POLARS_THREADS. Default: 6
  --log-file <path>          Autopilot log path. Default: audit/stage2_autopilot.log
  --once                     One iteration only.
  -h, --help                 Show help.
EOF
}

repo_root="/home/zepher/work/Omega_vNext"
input_dir="/omega_pool/parquet_data/v62_base_l1/host=linux1"
output_dir="/omega_pool/parquet_data/v62_feature_l2/host=linux1"
timeout_sec="2400"
poll_sec="60"
batch_size="8"
polars_threads="4"
log_file="audit/stage2_autopilot.log"
once=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) repo_root="${2:-}"; shift 2 ;;
    --input-dir) input_dir="${2:-}"; shift 2 ;;
    --output-dir) output_dir="${2:-}"; shift 2 ;;
    --timeout-sec) timeout_sec="${2:-}"; shift 2 ;;
    --poll-sec) poll_sec="${2:-}"; shift 2 ;;
    --batch-size) batch_size="${2:-}"; shift 2 ;;
    --polars-threads) polars_threads="${2:-}"; shift 2 ;;
    --log-file) log_file="${2:-}"; shift 2 ;;
    --once) once=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ "${log_file}" != /* ]]; then
  log_file="${repo_root}/${log_file}"
fi
mkdir -p "$(dirname "${log_file}")"

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "linux_stage2_autopilot.sh must run on Linux." >&2
  exit 2
fi

cd "${repo_root}"

log() {
  printf '%s %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$*" | tee -a "${log_file}" >/dev/null
}

iteration=0
while true; do
  iteration=$((iteration + 1))
  input_total="$(find "${input_dir}" -maxdepth 1 -type f -name '*.parquet' | wc -l || true)"
  done_total="$(find "${output_dir}" -maxdepth 1 -type f -name '*.parquet.done' | wc -l || true)"
  pending=$((input_total - done_total))
  if [[ "${pending}" -lt 0 ]]; then
    pending=0
  fi
  active_units="$(systemctl list-units 'omega_stage2_linux_*' --state=running --no-legend --no-pager | awk '{print $1}' | xargs echo || true)"

  log "[iter=${iteration}] input=${input_total} done=${done_total} pending=${pending} active_units='${active_units:-<none>}'"

  if [[ "${input_total}" -gt 0 && "${done_total}" -ge "${input_total}" ]]; then
    log "[complete] stage2 done markers reached input cardinality; autopilot exiting."
    exit 0
  fi

  if [[ -z "${active_units// }" ]]; then
    log "[action] no active stage2 unit; launching targeted resume in heavy-workload.slice (timeout=${timeout_sec}s, batch_size=${batch_size}, polars_threads=${polars_threads})."
    OMEGA_STAGE2_SYMBOL_BATCH_SIZE="${batch_size}" \
    OMEGA_STAGE2_POLARS_THREADS="${polars_threads}" \
      bash tools/launch_linux_stage2_heavy_slice.sh \
        --repo-root "${repo_root}" \
        --input-dir "${input_dir}" \
        --output-dir "${output_dir}" \
        --timeout-sec "${timeout_sec}" >> "${log_file}" 2>&1 || true
  fi

  if [[ "${once}" -eq 1 ]]; then
    exit 0
  fi
  sleep "${poll_sec}"
done
