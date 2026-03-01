# OMEGA VM Runbook: v62 Pipeline (Stage1 -> Stage2 -> Stage3)

## 1. Scope

This runbook is for agents running on `omega-vm` that supervise and operate the full v62 flow across:

- Linux worker `linux1-lx`
- Windows worker `windows1-w1`
- GCP Vertex AI (training/backtest stage)

It includes:

- what to run after Stage1/Stage2
- where logs and artifacts are
- where credentials are
- how to supervise with low overhead

## 2. v62 Flow (What comes after Stage1 and Stage2)

v62 operational sequence:

1. Stage1 Base Lake ETL (`tools/stage1_*_base_etl.py`)
2. Stage2 Physics Compute (`tools/stage2_physics_compute.py`)
3. Base Matrix Forge (`tools/forge_base_matrix.py`) from Feature_L2
4. Stage3 Train/Backtest
5. Optional cloud/local artifact validation

Important:

- Stage3 training payload `tools/run_vertex_xgb_train.py` does not consume raw Feature_L2 directly.
- It expects a prebuilt base matrix (`--base-matrix-uri`) and output prefix (`--output-uri`).

## 3. Credentials (Where they are)

### 3.1 SSH credentials on omega-vm

- SSH config: `/home/zephryj/.ssh/config`
- Worker private key: `/home/zephryj/.ssh/id_ed25519_omega_workers`
- Host aliases in config:
  - `linux1-lx` -> `100.64.97.113` user `zepher`
  - `windows1-w1` -> `100.123.90.25` user `jiazi`

Connectivity smoke:

```bash
ssh -o BatchMode=yes linux1-lx "hostname; whoami"
ssh -o BatchMode=yes windows1-w1 "hostname && whoami"
```

### 3.2 Worker-side SSH trust anchors

- Linux authorized keys: `/home/zepher/.ssh/authorized_keys`
- Windows authorized keys (admin context): `C:\ProgramData\ssh\administrators_authorized_keys`

### 3.3 GCP credentials on omega-vm

- gcloud config dir: `/home/zephryj/.config/gcloud`
- ADC file: `/home/zephryj/.config/gcloud/application_default_credentials.json`
- Active gcloud account is managed via `gcloud auth login` / `gcloud auth application-default login`

Quick check:

```bash
gcloud auth list
ls -la ~/.config/gcloud/application_default_credentials.json
```

### 3.4 Tailscale exit-node policy (required)

Requirement:

- `omega-vm` uses WireGuard connection via HK.
- Linux and Windows use `omega-vm` (`10.88.0.1`) directly via WireGuard subnet route over Tailscale.

Set/verify:

```bash
# omega-vm
sudo wg show

# linux1-lx
# SSH directly via 10.88.0.1

# windows1-w1 (PowerShell)
# SSH directly via 10.88.0.1
```

Verification:

```bash
ssh linux1-lx 'tailscale status --json | sed -n "1,140p"'
ssh windows1-w1 'powershell -NoProfile -Command "$j=(& \"C:\Program Files\Tailscale\tailscale.exe\" status --json | ConvertFrom-Json); $j.ExitNodeStatus | ConvertTo-Json -Compress"'
```

## 4. Logs and Artifacts (Where they are)

### 4.1 Stage1

- Linux Stage1 log:
  - `/home/zepher/work/Omega_vNext/audit/stage1_linux_v62.log`
- Linux supervisor log:
  - `/home/zepher/work/Omega_vNext/audit/linux_stage1_supervisor.log`
- Linux Stage1 output:
  - `/omega_pool/parquet_data/v62_base_l1/host=linux1/*.parquet`
  - done markers: `*.parquet.done`

- Windows Stage1 log:
  - `C:\Omega_vNext\audit\stage1_windows_v62.log`
- Windows Stage1 output:
  - `D:\Omega_frames\v62_base_l1\host=windows1\*.parquet`
  - done markers: `*.parquet.done`

### 4.2 Stage2

- Stage2 may print only to stdout unless redirected.
- Recommended log file:
  - Linux: `/home/zepher/work/Omega_vNext/audit/stage2_compute.log`
  - Windows: `D:\work\Omega_vNext\audit\stage2_compute.log` or `C:\Omega_vNext\audit\stage2_compute.log`

- Stage2 outputs:
  - Linux target (typical): `/omega_pool/parquet_data/v62_feature_l2/host=linux1`
  - Windows target (typical): `D:\Omega_frames\v62_feature_l2\host=windows1`
  - done markers: `*.parquet.done`

### 4.3 Base Matrix Forge (between Stage2 and Stage3)

- Local output files (you decide path at run-time):
  - `--output-parquet` (required)
  - `--output-meta` (optional)
- Optional cloud upload:
  - `--output-uri` and `--output-meta-uri` (GCS)

### 4.4 Stage3 Train/Backtest

- Vertex training logs:
  - Google Cloud Logs Explorer
  - `gcloud logging read` by `resource.labels.job_id`
- Vertex training state:
  - `gcloud ai custom-jobs describe <JOB_ID> --region=us-central1 --project=gen-lang-client-0250995579`
- Training artifacts (from `run_vertex_xgb_train.py`):
  - `<output-uri>/omega_v6_xgb_final.pkl`
  - `<output-uri>/train_metrics.json`

- Local backtest log (recommended):
  - run with `2>&1 | tee audit/local_backtest.log`
- Local backtest output JSON:
  - default `backtest_metrics.json` or `--output <path>`

## 5. Supervision Commands

## 5.1 Stage1 Linux

```bash
ssh linux1-lx '
  date "+%Y-%m-%d %H:%M:%S %Z"
  pgrep -af "tools/stage1_linux_base_etl.py" || true
  stat -c "%y %s" /home/zepher/work/Omega_vNext/audit/stage1_linux_v62.log
  tail -n 20 /home/zepher/work/Omega_vNext/audit/stage1_linux_v62.log
'
```

Run-level counters from latest run block:

```bash
ssh linux1-lx 'bash -s' <<'BASH'
cd /home/zepher/work/Omega_vNext
LOG=audit/stage1_linux_v62.log
START=$(rg -n "^Active Shards:" "$LOG" | tail -n1 | cut -d: -f1)
tail -n +"$START" "$LOG" > /tmp/stage1_tail.$$
echo "TOTAL_ASSIGNED=$(rg -n '^Files assigned to this shard' /tmp/stage1_tail.$$ | tail -n1 | sed -E 's/.*: ([0-9]+).*/\1/')"
echo "COMPLETED=$(rg -n '^\[[0-9]{8}\] Completed:' /tmp/stage1_tail.$$ | wc -l)"
echo "SKIPPED=$(rg -n '^\[[0-9]{8}\] Skipped' /tmp/stage1_tail.$$ | wc -l)"
echo "ERR=$(rg -n '^\[[0-9]{8}\] (Error|CRITICAL)' /tmp/stage1_tail.$$ | wc -l)"
echo "FINISHED=$(rg -n '^=== FRAMING COMPLETE ===' /tmp/stage1_tail.$$ | wc -l)"
rm -f /tmp/stage1_tail.$$
BASH
```

## 5.2 Stage1 Windows

```bash
ssh windows1-w1 'powershell -NoProfile -Command "
$ErrorActionPreference=''SilentlyContinue''
Get-ScheduledTask -TaskName ''Omega_v62_stage1_win'' | Select-Object TaskName,State | Format-Table -HideTableHeaders
if (Test-Path ''C:\Omega_vNext\audit\stage1_windows_v62.log'') {
  Get-Content ''C:\Omega_vNext\audit\stage1_windows_v62.log'' -Tail 20
}
$out=''D:\Omega_frames\v62_base_l1\host=windows1''
if (Test-Path $out) {
  Write-Output (''DONE_COUNT='' + (Get-ChildItem -Path $out -Filter ''*.parquet.done'' -File -ErrorAction SilentlyContinue).Count)
}
"'
```

## 5.3 Stage2 Windows (current main path)

```bash
ssh windows1-w1 'powershell -NoProfile -Command "
$ErrorActionPreference=''SilentlyContinue''
Get-CimInstance Win32_Process | ? { $_.CommandLine -like ''*stage2_physics_compute.py*'' } |
  Select-Object ProcessId,CreationDate,CommandLine | Format-List
$in=''D:\Omega_frames\v62_base_l1\host=windows1''
$out=''D:\Omega_frames\v62_feature_l2\host=windows1''
if (Test-Path $in)  { Write-Output (''INPUT='' + (Get-ChildItem $in -Filter ''*.parquet'' -File -ErrorAction SilentlyContinue).Count) }
if (Test-Path $out) { Write-Output (''DONE=''  + (Get-ChildItem $out -Filter ''*.parquet.done'' -File -ErrorAction SilentlyContinue).Count) }
"'
```

## 5.4 Base Matrix Forge supervision

Recommended start command with log:

```bash
python3 tools/forge_base_matrix.py \
  --input-pattern "/omega_pool/parquet_data/v62_feature_l2/host=linux1/*.parquet" \
  --output-parquet "/omega_pool/parquet_data/v62_base_matrix/base_matrix.parquet" \
  --output-meta "/omega_pool/parquet_data/v62_base_matrix/base_matrix.meta.json" \
  2>&1 | tee audit/forge_base_matrix.log
```

Monitor:

```bash
tail -n 50 audit/forge_base_matrix.log
```

## 5.5 Stage3 Vertex training supervision

List recent jobs:

```bash
gcloud ai custom-jobs list \
  --project=gen-lang-client-0250995579 \
  --region=us-central1 \
  --sort-by="~createTime" \
  --limit=10
```

Describe one job:

```bash
gcloud ai custom-jobs describe <JOB_ID> \
  --project=gen-lang-client-0250995579 \
  --region=us-central1
```

Read logs for one job:

```bash
gcloud logging read 'resource.labels.job_id="<JOB_ID>"' \
  --project=gen-lang-client-0250995579 \
  --limit=50 \
  --order=desc
```

Verify output artifacts:

```bash
gcloud storage ls <OUTPUT_URI>/
gcloud storage cat <OUTPUT_URI>/train_metrics.json
```

## 5.6 Stage3 local backtest supervision

Recommended run:

```bash
python3 tools/run_local_backtest.py \
  --model-path /path/to/omega_v6_xgb_final.pkl \
  --frames-dir /path/to/feature_or_frame_dir \
  --output audit/backtest_metrics.json \
  --workers 8 \
  2>&1 | tee audit/local_backtest.log
```

Monitor:

```bash
tail -n 50 audit/local_backtest.log
cat audit/backtest_metrics.json
```

## 5.7 Compatibility preflight before Train/Backtest

Run a schema/sample gate before expensive Train/Backtest:

```bash
python3 tools/_archived/check_frame_train_backtest_compat.py \
  --input-pattern "/omega_pool/parquet_data/v62_feature_l2/host=linux1/*.parquet"
```

## 6. 20-Minute Watch Loop Template (on omega-vm)

```bash
while true; do
  echo "===== $(date '+%Y-%m-%d %H:%M:%S %Z') ====="
  echo "[Linux Stage1]"
  ssh linux1-lx 'pgrep -af "stage1_linux_base_etl.py" || true; tail -n 3 /home/zepher/work/Omega_vNext/audit/stage1_linux_v62.log'
  echo "[Windows Stage2]"
  ssh windows1-w1 'powershell -NoProfile -Command "$out=''D:\Omega_frames\v62_feature_l2\host=windows1''; if(Test-Path $out){''DONE='' + (Get-ChildItem $out -Filter ''*.parquet.done'' -File -ErrorAction SilentlyContinue).Count}"'
  echo "[Vertex latest job]"
  gcloud ai custom-jobs list --project=gen-lang-client-0250995579 --region=us-central1 --sort-by="~createTime" --limit=1
  sleep 1200
done
```

## 7. Stage Gate Rules (Do not jump stages too early)

Stage1 -> Stage2:

- Stage1 process/task is terminal
- done markers stop increasing and reach expected shard scope
- no unresolved burst of CRITICAL errors

Stage2 -> Base Matrix:

- Stage2 process is terminal
- Feature_L2 done markers match expected unique-date scope
- output path has stable parquet set

Base Matrix -> Stage3 Train:

- base matrix parquet exists and readable
- base matrix meta exists (recommended)
- train input URI and output URI are fixed before submit

## 8. Notes on command drift

README quick start is conceptual. Current scripts are source of truth:

- `tools/stage1_linux_base_etl.py`
- `tools/stage1_windows_base_etl.py`
- `tools/stage2_physics_compute.py`
- `tools/forge_base_matrix.py`
- `tools/run_vertex_xgb_train.py` (payload; requires `--base-matrix-uri`, `--output-uri`, `--code-bundle-uri`)
- `tools/run_local_backtest.py`

If README one-line command conflicts with `--help`, use script `--help`.

## 9. Credential safety

- Never paste private key or ADC JSON contents into handover.
- Store only file paths and validation commands.
- If rotating `/home/zephryj/.ssh/id_ed25519_omega_workers`, update both worker `authorized_keys` first.
