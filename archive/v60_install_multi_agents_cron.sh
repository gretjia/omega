#!/usr/bin/env bash
set -euo pipefail

HASH="${1:-aa8abb7}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY_BIN="${PY_BIN:-$(command -v python3)}"
CRON_PATH="$(dirname "${PY_BIN}"):/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${HOME}/.local/bin:${HOME}/.npm-global/bin"
ENABLE_LINUX="${ENABLE_LINUX:-1}"

if [[ -z "${PY_BIN}" ]]; then
  echo "python3 not found"
  exit 1
fi

mkdir -p "${ROOT}/audit/runtime/v60/agents"

STATE_PATH="${ROOT}/audit/runtime/v60/multi_agents_${HASH}.state.json"
EVENT_LOG="${ROOT}/audit/runtime/v60/multi_agents_${HASH}.events.log"
DEBUG_DIR="${ROOT}/audit/runtime/v60/incidents"

MARK_BEGIN="# OMEGA_V60_MULTI_AGENTS_BEGIN_${HASH}"
MARK_END="# OMEGA_V60_MULTI_AGENTS_END_${HASH}"
MARK_BEGIN_ANY='^# OMEGA_V60_MULTI_AGENTS_BEGIN_'
MARK_END_ANY='^# OMEGA_V60_MULTI_AGENTS_END_'

TMP="$(mktemp)"
crontab -l 2>/dev/null > "${TMP}" || true

# Keep a single active Omega v60 block by removing all previous hash blocks.
awk -v b="${MARK_BEGIN_ANY}" -v e="${MARK_END_ANY}" '
  $0 ~ b {skip=1; next}
  $0 ~ e {skip=0; next}
  skip!=1 {print}
' "${TMP}" > "${TMP}.clean"
mv "${TMP}.clean" "${TMP}"

{
  echo "${MARK_BEGIN}"
  echo "PATH=${CRON_PATH}"
  echo "*/2 * * * * cd ${ROOT} && ${PY_BIN} ${ROOT}/tools/v60_multi_agent_tick.py --hash ${HASH} --role windows-monitor --state-path ${STATE_PATH} --event-log ${EVENT_LOG} --debug-dir ${DEBUG_DIR} --symbols-per-batch 25 --max-workers 6 --trigger-debug-agent >> ${ROOT}/audit/runtime/v60/agents/windows-monitor.log 2>&1"
  if [[ "${ENABLE_LINUX}" == "1" ]]; then
    echo "*/3 * * * * cd ${ROOT} && ${PY_BIN} ${ROOT}/tools/v60_multi_agent_tick.py --hash ${HASH} --role linux-bootstrap --state-path ${STATE_PATH} --event-log ${EVENT_LOG} --debug-dir ${DEBUG_DIR} --linux-frame-dir /omega_pool/parquet_data/v52/frames/host=linux1 --symbols-per-batch 25 --max-workers 6 --sync-per-tick 0 >> ${ROOT}/audit/runtime/v60/agents/linux-bootstrap.log 2>&1"
    echo "*/2 * * * * cd ${ROOT} && ${PY_BIN} ${ROOT}/tools/v60_multi_agent_tick.py --hash ${HASH} --role linux-monitor --state-path ${STATE_PATH} --event-log ${EVENT_LOG} --debug-dir ${DEBUG_DIR} --linux-frame-dir /omega_pool/parquet_data/v52/frames/host=linux1 --symbols-per-batch 25 --max-workers 6 --trigger-debug-agent >> ${ROOT}/audit/runtime/v60/agents/linux-monitor.log 2>&1"
  fi
  echo "*/5 * * * * cd ${ROOT} && ${PY_BIN} ${ROOT}/tools/v60_multi_agent_tick.py --hash ${HASH} --role autopilot-gate --state-path ${STATE_PATH} --event-log ${EVENT_LOG} --debug-dir ${DEBUG_DIR} >> ${ROOT}/audit/runtime/v60/agents/autopilot-gate.log 2>&1"
  echo "${MARK_END}"
} >> "${TMP}"

crontab "${TMP}"
rm -f "${TMP}"

echo "Installed multi-agent cron block for hash=${HASH}"
echo "State: ${STATE_PATH}"
echo "Events: ${EVENT_LOG}"
