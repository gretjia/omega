#!/usr/bin/env bash
set -euo pipefail

RUN_ID="${1:-$(date -u +%Y%m%dT%H%M%SZ)}"
PROJECT_ROOT="/home/zephryj/projects/omega"
AUDIT_DIR="${PROJECT_ROOT}/audit/stage3_full"
LINUX_HOST="linux1-lx"
WINDOWS_HOST="windows1-w1"
LINUX_ROOT="/home/zepher/work/Omega_vNext"

LINUX_META="${LINUX_ROOT}/audit/stage3_full/linux1_base_matrix_full_fast.meta.json"
LINUX_PARQ="${LINUX_ROOT}/audit/stage3_full/linux1_base_matrix_full_fast.parquet"
LINUX_WIN_PARQ="${LINUX_ROOT}/audit/stage3_full/windows1_base_matrix_full.parquet"
LINUX_WIN_META="${LINUX_ROOT}/audit/stage3_full/windows1_base_matrix_full.meta.json"
LINUX_MERGED_PARQ="${LINUX_ROOT}/audit/stage3_full/v62_dualhost_base_matrix_full.parquet"
LINUX_MERGED_META="${LINUX_ROOT}/audit/stage3_full/v62_dualhost_base_matrix_full.meta.json"

WIN_PARQ='D:\work\Omega_vNext\audit\stage3_full\windows1_base_matrix_full.parquet'
WIN_META='D:\work\Omega_vNext\audit\stage3_full\windows1_base_matrix_full.meta.json'

GCS_PREFIX="gs://omega_v52_central/stage3/v62_${RUN_ID}"
GCS_BASE_URI="${GCS_PREFIX}/v62_dualhost_base_matrix_full.parquet"
GCS_META_URI="${GCS_PREFIX}/v62_dualhost_base_matrix_full.meta.json"
GCS_TRAIN_OUT="${GCS_PREFIX}/train"
GCS_CODE_BUNDLE="gs://omega_v52_central/staging/code/omega_core_${RUN_ID}.zip"

LOG_FILE="${AUDIT_DIR}/stage3_orchestrator_${RUN_ID}.log"
mkdir -p "${AUDIT_DIR}"
exec >>"${LOG_FILE}" 2>&1

log() {
  printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"
}

log "RUN_ID=${RUN_ID}"
log "Waiting for Linux full base matrix: ${LINUX_META}"
until ssh "${LINUX_HOST}" "test -f '${LINUX_META}'"; do
  sleep 30
done
log "Linux full base matrix detected."

log "Checking Windows full base matrix artifacts."
ssh "${WINDOWS_HOST}" "python -c \"import os,sys; p=r'${WIN_PARQ}'; m=r'${WIN_META}'; sys.exit(0 if os.path.exists(p) and os.path.exists(m) else 1)\""
log "Windows artifacts present."

log "Streaming Windows full base matrix parquet -> Linux."
ssh "${WINDOWS_HOST}" "python -c \"import sys; sys.stdout.buffer.write(open(r'${WIN_PARQ}','rb').read())\"" \
  | ssh "${LINUX_HOST}" "cat > '${LINUX_WIN_PARQ}'"

log "Streaming Windows full base matrix meta -> Linux."
ssh "${WINDOWS_HOST}" "python -c \"import sys; sys.stdout.buffer.write(open(r'${WIN_META}','rb').read())\"" \
  | ssh "${LINUX_HOST}" "cat > '${LINUX_WIN_META}'"

log "Merging Linux+Windows base matrices on Linux host."
ssh "${LINUX_HOST}" "cd '${LINUX_ROOT}' && ./.venv/bin/python - <<'PY'
import json
from pathlib import Path
import polars as pl

base = Path('audit/stage3_full')
l = base / 'linux1_base_matrix_full_fast.parquet'
w = base / 'windows1_base_matrix_full.parquet'
out = base / 'v62_dualhost_base_matrix_full.parquet'
meta = base / 'v62_dualhost_base_matrix_full.meta.json'

lf = pl.concat([pl.scan_parquet(str(l)), pl.scan_parquet(str(w))], how='diagonal_relaxed')
df = lf.collect()
df.write_parquet(str(out), compression='zstd')

payload = {
    'linux_rows': int(pl.scan_parquet(str(l)).select(pl.len()).collect().item()),
    'windows_rows': int(pl.scan_parquet(str(w)).select(pl.len()).collect().item()),
    'combined_rows': int(df.height),
    'combined_cols': int(df.width),
    'linux_source': str(l),
    'windows_source': str(w),
    'combined_output': str(out),
}
meta.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(payload, ensure_ascii=False))
PY"

log "Uploading merged artifacts to GCS (streaming, no local disk staging)."
ssh "${LINUX_HOST}" "cat '${LINUX_MERGED_PARQ}'" | gcloud storage cp - "${GCS_BASE_URI}"
ssh "${LINUX_HOST}" "cat '${LINUX_MERGED_META}'" | gcloud storage cp - "${GCS_META_URI}"
log "Uploaded: ${GCS_BASE_URI}"
log "Uploaded: ${GCS_META_URI}"

log "Submitting Vertex training job."
cd "${PROJECT_ROOT}"
python3 tools/submit_vertex_sweep.py \
  --script tools/run_vertex_xgb_train.py \
  --machine-type e2-highmem-16 \
  --code-bundle-uri "${GCS_CODE_BUNDLE}" \
  --force-gcloud-fallback \
  --script-arg=--base-matrix-uri \
  --script-arg="${GCS_BASE_URI}" \
  --script-arg=--output-uri \
  --script-arg="${GCS_TRAIN_OUT}" \
  --script-arg=--code-bundle-uri \
  --script-arg="${GCS_CODE_BUNDLE}"

STATE_JSON="${AUDIT_DIR}/stage3_orchestrator_${RUN_ID}.state.json"
cat > "${STATE_JSON}" <<JSON
{
  "run_id": "${RUN_ID}",
  "gcs_base_uri": "${GCS_BASE_URI}",
  "gcs_meta_uri": "${GCS_META_URI}",
  "gcs_train_output_uri": "${GCS_TRAIN_OUT}",
  "gcs_code_bundle_uri": "${GCS_CODE_BUNDLE}",
  "log_file": "${LOG_FILE}"
}
JSON

log "Orchestration completed."
log "State: ${STATE_JSON}"
