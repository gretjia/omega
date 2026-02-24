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

| Host | Log | Output | Done Marker |
|---|---|---|---|
| Linux | `/home/zepher/work/Omega_vNext/audit/stage2_compute.log` | `/omega_pool/parquet_data/v62_feature_l2/host=linux1/*.parquet` | `*.parquet.done` |
| Windows | `D:\work\Omega_vNext\audit\stage2_compute.log` (or `C:\Omega_vNext\audit\stage2_compute.log`) | `D:\Omega_frames\v62_feature_l2\host=windows1\*.parquet` | `*.parquet.done` |

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

# Latest Vertex job
gcloud ai custom-jobs list --project=gen-lang-client-0250995579 --region=us-central1 --sort-by="~createTime" --limit=1
```

## 7. Full Multi-Stage Runbook

For complete supervision flow, use:
- `handover/ops/OMEGA_VM_V62_PIPELINE_MONITORING_NOTES.md`

