# AI Direct Guide

This folder is the runtime handoff surface for agent-to-agent continuation.

## 1. Read Order

1. `handover/ENTRYPOINT.md`
2. `handover/ai-direct/LATEST.md`
3. newest file in `handover/ai-direct/entries/`
4. `handover/ai-direct/live/00_Lesson_Recall.md`
5. `handover/ai-direct/live/01..05_*.md` (only for multi-agent gate flow)

## 2. File Roles

- `LATEST.md`: single current truth for all agents.
- `HANDOVER_TEMPLATE.md`: mandatory format for each new entry.
- `entries/*.md`: append-only session records.
- `live/01..05_*.md`: oracle/mechanic/auditor gate artifacts.

## 3. Update Rules

- At session start: read `LATEST.md` and latest `entries` note.
- At session end:
  - create one new `entries/*.md` file from template
  - update `LATEST.md`
- Keep `LATEST.md` short and current. Move detailed history to `entries/`.

## 4. Naming Rule for Entries

`YYYYMMDD_HHMMSS_short_topic.md`

Example:
`20260224_131500_stage2_windows_eta_update.md`

## 5. Mandatory Fields (Per Entry)

- `task_id`
- `timestamp_local`
- `timestamp_utc`
- `operator`
- `git_head`
- `hosts_touched`
- `summary`
- `next_actions`

## 6. 今日交接快速入口（审计链）

- `handover/ai-direct/entries/20260305_142336_v63_training_backtest_alignment_audit.md`（本轮总结，含原始字段证据与风险）
- `audit/v63.md`（v63 架构与约束映射）
- `/home/zepher/work/Omega_vNext/audit/v63_2025_q1q9_basematrix.meta.json`（训练输入与行数）
- `/home/zepher/work/Omega_vNext/artifacts/v63_q1q9_train_metrics.json`（训练 metrics）
- `/home/zepher/work/Omega_vNext/audit/v63_backtest_q4_status.json`（回测状态）
- `/home/zepher/work/Omega_vNext/audit/v63_backtest_q4_result.json`（回测结果）
- `handover/ai-direct/entries/20260305_094830_v63_vertex_train_success.md`（训练完成记录）
