# 2026-03-05 09:48 +0000 (V63 Vertex q1q9 Train Completed)

## 状态确认
- 作业：`projects/269018079180/locations/us-central1/customJobs/306719677785047040`
- 显示名：`omega-v63-train-q1q9-20260305-0944`
- 状态：`JOB_STATE_SUCCEEDED`
- 关键时间：
  - createTime: `2026-03-05T09:44:09.593330Z`
  - startTime: `2026-03-05T09:44:23Z`
  - endTime: `2026-03-05T09:44:54Z`
  - 实际耗时约：`31s`

## 产物
- `gs://omega_v52_central/omega/staging/base_matrix/v63/q1q9_2025/model/omega_xgb_final.pkl`
- `gs://omega_v52_central/omega/staging/base_matrix/v63/q1q9_2025/model/train_metrics.json`

## 训练指标（metrics）
- `base_rows=561281`
- `mask_rows=603`
- `total_training_rows=586`
- `seconds=0.24`
- 覆盖参数：
  - `peace_threshold=0.5253567667772991`
  - `srl_resid_sigma_mult=1.9773888188507172`
  - `topo_energy_sigma_mult=5.427559578121958`
  - `xgb_max_depth=5`
  - `xgb_learning_rate=0.03`
  - `xgb_subsample=0.9`
  - `xgb_colsample_bytree=0.8`
  - `num_boost_round=150`

## 备注
- 相比上一次失败提交（`7099555290743308288`），本次修复版作业已成功提交并完成。
- 当前建议动作：立即开始 Stage3 训练产物对齐与回测评估（确认模型有效性），并在通过指标门禁后进入后续版本化归档。
