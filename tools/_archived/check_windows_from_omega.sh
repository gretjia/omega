#!/usr/bin/env bash
set -u

TARGET_ALIAS="${1:-windows1-w1}"
TARGET_IP="${2:-100.123.90.25}"
ATTEMPTS="${ATTEMPTS:-5}"
SLEEP_SEC="${SLEEP_SEC:-6}"
TS_TIMEOUT="${TS_TIMEOUT:-8}"
SSH_TIMEOUT="${SSH_TIMEOUT:-8}"

ok_any=0

echo "[probe] target_alias=${TARGET_ALIAS} target_ip=${TARGET_IP} attempts=${ATTEMPTS} sleep_sec=${SLEEP_SEC}"
for i in $(seq 1 "$ATTEMPTS"); do
  ts_ok=0
  tcp_ok=0
  ssh_ok=0

  if timeout "$TS_TIMEOUT" tailscale ping --c 1 "$TARGET_IP" >/tmp/omega_ts_ping.out 2>&1; then
    ts_ok=1
  fi

  if timeout 6 bash -lc "</dev/tcp/${TARGET_IP}/22" >/dev/null 2>&1; then
    tcp_ok=1
  fi

  if ssh -o BatchMode=yes -o ConnectTimeout="$SSH_TIMEOUT" "$TARGET_ALIAS" "hostname" >/dev/null 2>&1; then
    ssh_ok=1
  fi

  if [ "$ts_ok" -eq 1 ] || [ "$tcp_ok" -eq 1 ] || [ "$ssh_ok" -eq 1 ]; then
    ok_any=1
  fi

  now=$(date "+%Y-%m-%d %H:%M:%S %z")
  echo "attempt=${i} ts_ok=${ts_ok} tcp22_ok=${tcp_ok} ssh_ok=${ssh_ok} ts=${now}"
  if [ "$i" -lt "$ATTEMPTS" ]; then
    sleep "$SLEEP_SEC"
  fi
done

if [ "$ok_any" -eq 1 ]; then
  echo "RESULT=REACHABLE_OR_RECOVERING"
  exit 0
fi

echo "RESULT=UNREACHABLE_AFTER_RETRIES"
exit 2
