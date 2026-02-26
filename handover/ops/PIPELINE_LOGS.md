# Pipeline Logs and Monitoring Index (v62)

This is the canonical log and artifact location index for Stage1/2/3 supervision.

## 1. Stage Sequence

1. Stage1 Base Lake ETL
2. Stage2 Physics Compute
3. Base Matrix Forge
4. Stage3 Train and Backtest

## 2. Stage1 (Base_L1)

| Host | Log | Output | Done Marker |
|---|---|---|---|
| Linux | `/home/zepher/work/Omega_vNext/audit/stage1_linux_v62.log` | `/omega_pool/parquet_data/v62_base_l1/host=linux1/*.parquet` | `*.parquet.done` |
| Linux (supervisor) | `/home/zepher/work/Omega_vNext/audit/linux_stage1_supervisor.log` | n/a | n/a |
| Windows | `C:\Omega_vNext\audit\stage1_windows_v62.log` | `D:\Omega_frames\v62_base_l1\host=windows1\*.parquet` | `*.parquet.done` |

## 3. Stage2 (Feature_L2)

### 3.1 Primary Stage2 Paths

| Host | Log | Output | Done Marker |
|---|---|---|---|
| Linux | `/home/zepher/work/Omega_vNext/audit/stage2_compute.log` | `/omega_pool/parquet_data/v62_feature_l2/host=linux1/*.parquet` | `*.parquet.done` |
| Windows | `D:\work\Omega_vNext\audit\stage2_compute.log` (or `C:\Omega_vNext\audit\stage2_compute.log`) | `D:\Omega_frames\v62_feature_l2\host=windows1\*.parquet` | `*.parquet.done` |

### 3.2 Targeted Resume / Recovery Paths

| Host | Purpose | Path |
|---|---|---|
| Linux | targeted runner log | `/home/zepher/work/Omega_vNext/audit/stage2_targeted_resume_linux.log` |
| Linux | launcher log | `/home/zepher/work/Omega_vNext/audit/stage2_targeted_resume_linux.launch.log` |
| Linux | fail ledger | `/home/zepher/work/Omega_vNext/audit/stage2_targeted_failed_linux.txt` |
| Linux | pending snapshot | `/home/zepher/work/Omega_vNext/audit/stage2_pending_linux.txt` |
| Linux | autopilot log | `/home/zepher/work/Omega_vNext/audit/stage2_autopilot.log` |
| Windows | targeted runner log (v2) | `D:\work\Omega_vNext\audit\stage2_targeted_resume_isolated_v2.log` |
| Windows | fail ledger (v2) | `D:\work\Omega_vNext\audit\stage2_targeted_failed_isolated_v2.txt` |
| Windows | pending snapshot (v2) | `D:\work\Omega_vNext\audit\stage2_pending_isolated_v2.txt` |

### 3.3 Stage2 Metric Semantics (Do Not Misread)

- `DONE_NOW`: current done-marker cardinality after runner loop.
- `FAILED_TOTAL`: cumulative unique failed-file ledger size (includes carry-in history).
- `RUN_FAILED`: this invocation's failures only.
- `DEFER not-started`: timeout occurred before file start marker; file is deferred, not marked failed.
- `FILES_PER_PROCESS`: orchestration batch size only; does not change Stage2 feature math.

Interpretation rule:
- Progress truth comes from `*.parquet.done` counts first, then runner counters. Do not infer completion solely from scheduler "Running" state.

## 4. Stage2.5 Base Matrix

Recommended log:
- `audit/forge_base_matrix.log`

Core outputs:
- `--output-parquet <path>`
- `--output-meta <path>`

## 5. Stage3 Train/Backtest

| Item | Location |
|---|---|
| Vertex job status | `gcloud ai custom-jobs describe <JOB_ID> --project=gen-lang-client-0250995579 --region=us-central1` |
| Vertex logs | Google Cloud Logs Explorer or `gcloud logging read 'resource.labels.job_id="<JOB_ID>"'` |
| Train artifact | `<output-uri>/omega_v6_xgb_final.pkl` |
| Train metrics | `<output-uri>/train_metrics.json` |
| Local backtest log | `audit/local_backtest.log` |
| Local backtest metrics | `audit/backtest_metrics.json` (or custom `--output`) |

## 6. Quick Checks

```bash
# Linux Stage1 state
ssh linux1-lx 'pgrep -af "stage1_linux_base_etl.py" || true; tail -n 5 /home/zepher/work/Omega_vNext/audit/stage1_linux_v62.log'

# Windows Stage2 done count
python3 .codex/skills/omega-run-ops/scripts/ssh_ps.py windows1-w1 --command '
$out="D:\\Omega_frames\\v62_feature_l2\\host=windows1";
"DONE=" + (Get-ChildItem $out -Filter "*.parquet.done" -File -ErrorAction SilentlyContinue).Count
'

# Linux Stage2 targeted runner tail + done ratio
ssh linux1-lx '
  tail -n 20 /home/zepher/work/Omega_vNext/audit/stage2_targeted_resume_linux.log;
  in=/omega_pool/parquet_data/v62_base_l1/host=linux1;
  out=/omega_pool/parquet_data/v62_feature_l2/host=linux1;
  echo "LNX_STAGE2=$(find "$out" -maxdepth 1 -name \"*.parquet.done\" | wc -l)/$(find "$in" -maxdepth 1 -name \"*.parquet\" | wc -l)"
'

# Windows Stage2 targeted runner tail + fail ledger size
python3 .codex/skills/omega-run-ops/scripts/ssh_ps.py windows1-w1 --command '
$log="D:\\work\\Omega_vNext\\audit\\stage2_targeted_resume_isolated_v2.log";
$fail="D:\\work\\Omega_vNext\\audit\\stage2_targeted_failed_isolated_v2.txt";
if (Test-Path $log) { Get-Content $log -Tail 20 }
if (Test-Path $fail) { "FAILED_LEDGER=" + (Get-Content $fail | ? { $_.Trim() -ne "" }).Count }
'

# Latest Vertex job
gcloud ai custom-jobs list --project=gen-lang-client-0250995579 --region=us-central1 --sort-by="~createTime" --limit=1
```

## 7. Full Multi-Stage Runbook

For complete supervision flow, use:
- `handover/ops/OMEGA_VM_V62_PIPELINE_MONITORING_NOTES.md`
