# 2026-03-05 09:44 +0000 (V63 Stage3 Vertex Retrain Retry)

## 情况确认
- V63 的 BaseMatrix 训练用数据（`2025-01~2025-09`）已在 `linux1-lx` 完成，且元数据核验通过：
  - `audit/v63_2025_q1q9_basematrix.parquet`
  - `audit/v63_2025_q1q9_basematrix.meta.json`
  - `batch_count=39, base_rows=561281, input_file_count=141, status=ok`
- 之前提交的 Vertex 任务存在命令行注入问题：`run_vertex` heredoc 里 `gs://` 取值语句被 Shell 误解析，导致 `custom_job` 直接失败。
- 该失败作业：`projects/269018079180/locations/us-central1/customJobs/7099555290743308288`
  - `displayName=omega-v63-train-q1q9-20260305-0938`
  - `state=JOB_STATE_FAILED`

## 已执行修复
- 在 `omega-vm` 侧重建并上传训练包：
  - `gs://omega_v52_central/staging/code/omega_core_stage3.zip`
  - `gs://omega_v52_central/staging/code/payloads/v63_q1q9/run_vertex_xgb_train.py`
- 使用同构脚本参数重建作业配置，修正命令注入与参数引用后，重新提交训练任务：
  - 任务: `omega-v63-train-q1q9-20260305-0944`
  - 资源名: `projects/269018079180/locations/us-central1/customJobs/306719677785047040`
  - 当前状态: `JOB_STATE_PENDING`
  - 输出前缀: `gs://omega_v52_central/omega/staging/base_matrix/v63/q1q9_2025/model`
  - 训练参数沿用 q1q9 的 gate：
    - `peace_threshold=0.5253567667772991`
    - `srl_resid_sigma_mult=1.9773888188507172`
    - `topo_energy_sigma_mult=5.427559578121958`

## 下一步
- 继续轮询 `jobs state` 与 `stream-logs`，确认作业进入 RUNNING 并在 1~2 周期内产出 `train_metrics.json`。
