#!/usr/bin/env bash
set -u
cd /Users/zephryj/work/Omega_vNext || exit 1
while true; do
  ts="$(date '+%Y-%m-%d %H:%M:%S')"
  echo "[$ts] uplink cycle begin"
  PYTHONUNBUFFERED=1 python3 -u tools/mac_gateway_sync.py --bucket gs://omega_v52_central --host linux1 --hash aa8abb7
  rc1=$?
  ts="$(date '+%Y-%m-%d %H:%M:%S')"
  echo "[$ts] linux1 sync rc=$rc1"
  PYTHONUNBUFFERED=1 python3 -u tools/mac_gateway_sync.py --bucket gs://omega_v52_central --host windows1 --hash aa8abb7
  rc2=$?
  ts="$(date '+%Y-%m-%d %H:%M:%S')"
  echo "[$ts] windows1 sync rc=$rc2"
  echo "[$ts] uplink cycle sleep 300s"
  sleep 300
done
