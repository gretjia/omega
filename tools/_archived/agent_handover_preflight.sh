#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MISSING=0

print_ok() {
  printf '[OK] %s\n' "$1"
}

print_warn() {
  printf '[WARN] %s\n' "$1"
}

print_err() {
  printf '[ERR] %s\n' "$1"
}

echo "== OMEGA Multi-Agent Handover Preflight =="
echo "Repo: $ROOT_DIR"
echo

REQUIRED_FILES=(
  "audit/constitution_v2.md"
  "handover/ENTRYPOINT.md"
  "handover/README.md"
  "handover/ai-direct/LATEST.md"
  "handover/ops/FILE_TOPOLOGY.md"
  "handover/ops/SKILLS_TOOLS_INDEX.md"
  "handover/ops/ACCESS_BOOTSTRAP.md"
  "handover/ops/HOSTS_REGISTRY.yaml"
)

echo "== Required files =="
for rel in "${REQUIRED_FILES[@]}"; do
  if [[ -f "$ROOT_DIR/$rel" ]]; then
    print_ok "$rel"
  else
    print_err "Missing: $rel"
    MISSING=1
  fi
done
echo

REQUIRED_SKILL_SCRIPTS=(
  ".codex/skills/multi-agent-ops/scripts/deploy_and_check.py"
  ".codex/skills/multi-agent-ops/scripts/switch_profile.py"
  ".codex/skills/multi-agent-ops/scripts/log_debug_experience.py"
  ".codex/skills/omega-run-ops/scripts/ssh_ps.py"
)

echo "== Executable skill scripts =="
for rel in "${REQUIRED_SKILL_SCRIPTS[@]}"; do
  if [[ -f "$ROOT_DIR/$rel" ]]; then
    print_ok "$rel"
  else
    print_err "Missing skill script: $rel"
    MISSING=1
  fi
done
echo

SSH_CONFIG="$HOME/.ssh/config"
REQUIRED_ALIASES=("windows1-w1" "linux1-lx")

echo "== SSH alias readiness =="
if [[ -f "$SSH_CONFIG" ]]; then
  HOST_LINES="$(awk '/^[[:space:]]*Host[[:space:]]+/ {for (i=2; i<=NF; i++) print $i}' "$SSH_CONFIG" | sed '/^\*/d' || true)"
  if [[ -z "${HOST_LINES:-}" ]]; then
    print_warn "No concrete host aliases found in $SSH_CONFIG"
  fi
  for alias in "${REQUIRED_ALIASES[@]}"; do
    if printf '%s\n' "$HOST_LINES" | grep -Fxq "$alias"; then
      print_ok "Alias present: $alias"
    else
      print_warn "Alias missing: $alias (see handover/ops/ACCESS_BOOTSTRAP.md)"
      MISSING=1
    fi
  done
else
  print_warn "~/.ssh/config not found"
  MISSING=1
fi
echo

echo "== Fallback direct targets (non-secret) =="
echo "windows1: jiazi@192.168.3.112"
echo "linux1:   zepher@192.168.3.113"
echo

if [[ "$MISSING" -ne 0 ]]; then
  print_warn "Preflight finished with gaps. Resolve warnings before unattended multi-agent operations."
  exit 2
fi

print_ok "Preflight passed."

