
## 2026-02-17 12:23:44 | watchdog_started
- hash: aa8abb7
- auto_resume: True
- autopilot_session: v60_autopilot_aa8abb7
- uplink_session: v60_uplink_aa8abb7
- autopilot_launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
- uplink_launch: bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
- live_state: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json
- events_log: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md

## 2026-02-17 15:13:22 | incident_captured
- reason: autopilot_not_running
- fingerprint: autopilot_not_running:monitor_frame
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_151322_autopilot_not_running.md

## 2026-02-17 15:13:22 | codex_exec_launched
- pid: 16219
- reason: autopilot_not_running
- incident_id: 20260217_151322_autopilot_not_running
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_151322_autopilot_not_running.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_151322_autopilot_not_running.codex_exec.log

## 2026-02-17 15:17:30 | codex_exec_finished
- pid: 16219
- incident_id: 20260217_151322_autopilot_not_running
- reason: autopilot_not_running
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_151322_autopilot_not_running.codex_report.txt
- [2026-02-17 15:49] Added strict recursive audit gates into `tools/v60_autopilot.py` at key nodes: bootstrap, frame_complete, pre_base_matrix, post_base_matrix, post_optimize, pre_train, pre_backtest, completed. Audit log path: `audit/runtime/v52/recursive_audit_aa8abb7.jsonl`.
- [2026-02-17 15:49] Resolved Linux 13-file 7z header corruption gap by Windows recovery run (12 files) plus no-BOM single-file rerun for `20241104`; final windows done count reached 263.
- [2026-02-17 15:49] Cleared duplicate autopilot process contamination risk by terminating stale PID chain (started 15:14) and keeping single active autopilot (started 15:43).

## 2026-02-17 16:07:03 | incident_captured
- reason: autopilot_status_stale
- fingerprint: autopilot_status_stale:build_base_matrix:4
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_160703_autopilot_status_stale.md

## 2026-02-17 16:07:03 | codex_exec_launched
- pid: 31512
- reason: autopilot_status_stale
- incident_id: 20260217_160703_autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_160703_autopilot_status_stale.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_160703_autopilot_status_stale.codex_exec.log

## 2026-02-17 16:15:18 | codex_exec_finished
- pid: 31512
- incident_id: 20260217_160703_autopilot_status_stale
- reason: autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_160703_autopilot_status_stale.codex_report.txt

## 2026-02-17 16:38:02 | incident_captured
- reason: autopilot_status_stale
- fingerprint: autopilot_status_stale:build_base_matrix:10
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_163802_autopilot_status_stale.md

## 2026-02-17 16:38:02 | codex_exec_launched
- pid: 37004
- reason: autopilot_status_stale
- incident_id: 20260217_163802_autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_163802_autopilot_status_stale.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_163802_autopilot_status_stale.codex_exec.log

## 2026-02-17 16:46:19 | codex_exec_finished
- pid: 37004
- incident_id: 20260217_163802_autopilot_status_stale
- reason: autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_163802_autopilot_status_stale.codex_report.txt

## 2026-02-17 17:09:02 | incident_captured
- reason: autopilot_status_stale
- fingerprint: autopilot_status_stale:build_base_matrix:16
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_170902_autopilot_status_stale.md

## 2026-02-17 17:09:02 | codex_exec_launched
- pid: 42902
- reason: autopilot_status_stale
- incident_id: 20260217_170902_autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_170902_autopilot_status_stale.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_170902_autopilot_status_stale.codex_exec.log

## 2026-02-17 17:17:18 | codex_exec_finished
- pid: 42902
- incident_id: 20260217_170902_autopilot_status_stale
- reason: autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_170902_autopilot_status_stale.codex_report.txt

## 2026-02-17 17:40:06 | incident_captured
- reason: autopilot_status_stale
- fingerprint: autopilot_status_stale:build_base_matrix:22
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_174006_autopilot_status_stale.md

## 2026-02-17 17:40:06 | codex_exec_launched
- pid: 49542
- reason: autopilot_status_stale
- incident_id: 20260217_174006_autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_174006_autopilot_status_stale.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_174006_autopilot_status_stale.codex_exec.log

## 2026-02-17 17:46:19 | codex_exec_finished
- pid: 49542
- incident_id: 20260217_174006_autopilot_status_stale
- reason: autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_174006_autopilot_status_stale.codex_report.txt

## 2026-02-17 18:11:10 | incident_captured
- reason: autopilot_status_stale
- fingerprint: autopilot_status_stale:build_base_matrix:28
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_181110_autopilot_status_stale.md

## 2026-02-17 18:11:10 | codex_exec_launched
- pid: 52490
- reason: autopilot_status_stale
- incident_id: 20260217_181110_autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_181110_autopilot_status_stale.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_181110_autopilot_status_stale.codex_exec.log

## 2026-02-17 18:17:26 | codex_exec_finished
- pid: 52490
- incident_id: 20260217_181110_autopilot_status_stale
- reason: autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_181110_autopilot_status_stale.codex_report.txt

## 2026-02-17 18:42:22 | incident_captured
- reason: autopilot_status_stale
- fingerprint: autopilot_status_stale:build_base_matrix:35
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_184222_autopilot_status_stale.md

## 2026-02-17 18:42:22 | codex_exec_launched
- pid: 57254
- reason: autopilot_status_stale
- incident_id: 20260217_184222_autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_184222_autopilot_status_stale.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_184222_autopilot_status_stale.codex_exec.log

## 2026-02-17 20:02:51 | watchdog_started
- hash: aa8abb7
- auto_resume: True
- autopilot_session: v60_autopilot_aa8abb7
- uplink_session: v60_uplink_aa8abb7
- autopilot_launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n2-highmem-16 --optimization-machine-type n2-highmem-16 --train-machine-type n2-standard-16 --backtest-machine-type n2-standard-8 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
- uplink_launch: bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
- live_state: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json
- events_log: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md

## 2026-02-17 20:02:55 | codex_exec_finished
- pid: 57254
- incident_id: 20260217_184222_autopilot_status_stale
- reason: autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_184222_autopilot_status_stale.codex_report.txt

## 2026-02-17 20:02:55 | incident_captured
- reason: upload_progress_stalled
- fingerprint: upload_progress_stalled:51
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_200255_upload_progress_stalled.md

## 2026-02-17 20:02:55 | codex_exec_launched
- pid: 87091
- reason: upload_progress_stalled
- incident_id: 20260217_200255_upload_progress_stalled
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_200255_upload_progress_stalled.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_200255_upload_progress_stalled.codex_exec.log

## 2026-02-17 20:04:03 | watchdog_started
- hash: aa8abb7
- auto_resume: True
- autopilot_session: v60_autopilot_aa8abb7
- uplink_session: v60_uplink_aa8abb7
- autopilot_launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n2-highmem-16 --optimization-machine-type n2-highmem-16 --train-machine-type n2-standard-16 --backtest-machine-type n2-standard-8 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
- uplink_launch: bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
- live_state: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json
- events_log: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md

## 2026-02-17 20:04:07 | codex_exec_finished
- pid: 87091
- incident_id: 20260217_200255_upload_progress_stalled
- reason: upload_progress_stalled
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_200255_upload_progress_stalled.codex_report.txt

## 2026-02-17 20:22:36 | autopilot_auto_resumed
- session: v60_autopilot_aa8abb7
- restart_count: 1
- launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n2-highmem-16 --optimization-machine-type n2-highmem-16 --train-machine-type n2-standard-16 --backtest-machine-type n2-standard-8 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1

## 2026-02-17 20:34:56 | autopilot_auto_resumed
- session: v60_autopilot_aa8abb7
- restart_count: 2
- launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n2-highmem-16 --optimization-machine-type n2-highmem-16 --train-machine-type n2-standard-16 --backtest-machine-type n2-standard-8 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1

## 2026-02-17 20:34:56 | incident_captured
- reason: autopilot_not_running
- fingerprint: autopilot_not_running:build_base_matrix
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_203456_autopilot_not_running.md

## 2026-02-17 20:34:56 | codex_exec_launched
- pid: 15764
- reason: autopilot_not_running
- incident_id: 20260217_203456_autopilot_not_running
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_203456_autopilot_not_running.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_203456_autopilot_not_running.codex_exec.log

## 2026-02-17 20:47:59 | watchdog_started
- hash: aa8abb7
- auto_resume: True
- autopilot_session: v60_autopilot_aa8abb7
- uplink_session: v60_uplink_aa8abb7
- autopilot_launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
- uplink_launch: bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
- live_state: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json
- events_log: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md

## 2026-02-17 20:48:58 | watchdog_started
- hash: aa8abb7
- auto_resume: True
- autopilot_session: v60_autopilot_aa8abb7
- uplink_session: v60_uplink_aa8abb7
- autopilot_launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
- uplink_launch: bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
- live_state: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json
- events_log: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md

## 2026-02-17 20:49:02 | codex_exec_finished
- pid: 15764
- incident_id: 20260217_203456_autopilot_not_running
- reason: autopilot_not_running
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_203456_autopilot_not_running.codex_report.txt

## 2026-02-17 21:07:47 | incident_captured
- reason: runner_error_JOB_STATE_FAILED
- fingerprint: runner_error:JOB_STATE_FAILED:7076634738787652583
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_210747_runner_error_JOB_STATE_FAILED.md

## 2026-02-17 21:07:47 | codex_exec_launched
- pid: 35935
- reason: runner_error_JOB_STATE_FAILED
- incident_id: 20260217_210747_runner_error_JOB_STATE_FAILED
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_210747_runner_error_JOB_STATE_FAILED.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_210747_runner_error_JOB_STATE_FAILED.codex_exec.log

## 2026-02-17 21:20:14 | codex_exec_finished
- pid: 35935
- incident_id: 20260217_210747_runner_error_JOB_STATE_FAILED
- reason: runner_error_JOB_STATE_FAILED
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_210747_runner_error_JOB_STATE_FAILED.codex_report.txt

## 2026-02-17 21:20:14 | autopilot_auto_resumed
- session: v60_autopilot_aa8abb7
- restart_count: 3
- launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1

## 2026-02-17 21:25:52 | watchdog_started
- hash: aa8abb7
- auto_resume: True
- autopilot_session: v60_autopilot_aa8abb7
- uplink_session: v60_uplink_aa8abb7
- autopilot_launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
- uplink_launch: bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
- live_state: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json
- events_log: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md

## 2026-02-17 21:27:58 | watchdog_started
- hash: aa8abb7
- auto_resume: True
- autopilot_session: v60_autopilot_aa8abb7
- uplink_session: v60_uplink_aa8abb7
- autopilot_launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
- uplink_launch: bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
- live_state: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json
- events_log: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md

## 2026-02-17 21:37:46 | train_backtest_guardrails_upgraded
- scope: post-base-matrix downstream hardening (no math changes)
- changes:
  - `tools/run_vertex_xgb_train.py`: strict day-key year filtering, optional `--max-files/--max-rows-per-file` (0=full), progress RSS logs, per-file GC, richer metrics.
  - `tools/run_cloud_backtest.py`: strict day-key + `--test-ym` filtering, defaults `--max-files=0` and `--max-rows-per-file=0`, progress RSS logs, per-file GC, richer metrics.
  - `tools/v60_autopilot.py`: explicit train/backtest cap args and submit pass-through + startup cap logging.
- docs:
  - added `handover/ai-direct/entries/20260217_v60_train_backtest_vertex_guardrails.md`
  - updated `handover/ai-direct/LATEST.md`
  - updated `.codex/skills/omega-run-ops/SKILL.md`
- rationale:
  - align v60 downstream with v52 cloud lessons while preserving v60 optimization-first design,
  - remove hidden sampling and reduce split-contamination risk.

## 2026-02-17 21:42:31 | incident_captured
- reason: runner_error_JOB_STATE_FAILED
- fingerprint: runner_error:JOB_STATE_FAILED:-8520511172024813007
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_214231_runner_error_JOB_STATE_FAILED.md

## 2026-02-17 21:42:32 | incident_captured
- reason: runner_error_JOB_STATE_FAILED
- fingerprint: runner_error:JOB_STATE_FAILED:1299260135675506610
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_214232_runner_error_JOB_STATE_FAILED.md

## 2026-02-17 21:42:32 | codex_exec_launched
- pid: 89489
- reason: runner_error_JOB_STATE_FAILED
- incident_id: 20260217_214232_runner_error_JOB_STATE_FAILED
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_214232_runner_error_JOB_STATE_FAILED.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_214232_runner_error_JOB_STATE_FAILED.codex_exec.log

## 2026-02-17 21:47:06 | watchdog_started
- hash: aa8abb7
- auto_resume: True
- autopilot_session: v60_autopilot_aa8abb7
- uplink_session: v60_uplink_aa8abb7
- autopilot_launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
- uplink_launch: bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
- live_state: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json
- events_log: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md

## 2026-02-17 21:47:10 | codex_exec_finished
- pid: 89489
- incident_id: 20260217_214232_runner_error_JOB_STATE_FAILED
- reason: runner_error_JOB_STATE_FAILED
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260217_214232_runner_error_JOB_STATE_FAILED.codex_report.txt

## 2026-02-17 22:01:35 | watchdog_started
- hash: aa8abb7
- auto_resume: True
- autopilot_session: v60_autopilot_aa8abb7
- uplink_session: v60_uplink_aa8abb7
- autopilot_launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
- uplink_launch: bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
- live_state: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json
- events_log: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md

## 2026-02-18 00:02:55 | incident_captured
- reason: autopilot_status_stale
- fingerprint: autopilot_status_stale:build_base_matrix:24
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_000255_autopilot_status_stale.md

## 2026-02-18 00:02:55 | codex_exec_launched
- pid: 21430
- reason: autopilot_status_stale
- incident_id: 20260218_000255_autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_000255_autopilot_status_stale.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_000255_autopilot_status_stale.codex_exec.log

## 2026-02-18 00:10:25 | watchdog_started
- hash: aa8abb7
- auto_resume: True
- autopilot_session: v60_autopilot_aa8abb7
- uplink_session: v60_uplink_aa8abb7
- autopilot_launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
- uplink_launch: bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
- live_state: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json
- events_log: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md

## 2026-02-18 00:10:25 | codex_exec_finished
- pid: 21430
- incident_id: 20260218_000255_autopilot_status_stale
- reason: autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_000255_autopilot_status_stale.codex_report.txt

## 2026-02-18 00:12:26 | autopilot_auto_resumed
- session: v60_autopilot_aa8abb7
- restart_count: 4
- launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1

## 2026-02-18 00:15:18 | codex_exec_finished
- pid: 21430
- incident_id: 20260218_000255_autopilot_status_stale
- reason: autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_000255_autopilot_status_stale.codex_report.txt

## 2026-02-18 00:33:48 | incident_captured
- reason: autopilot_status_stale
- fingerprint: autopilot_status_stale:build_base_matrix:30
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_003348_autopilot_status_stale.md

## 2026-02-18 00:33:48 | codex_exec_launched
- pid: 25543
- reason: autopilot_status_stale
- incident_id: 20260218_003348_autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_003348_autopilot_status_stale.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_003348_autopilot_status_stale.codex_exec.log

## 2026-02-18 00:46:08 | codex_exec_finished
- pid: 25543
- incident_id: 20260218_003348_autopilot_status_stale
- reason: autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_003348_autopilot_status_stale.codex_report.txt

## 2026-02-18 02:45:22 | incident_captured
- reason: autopilot_status_stale
- fingerprint: autopilot_status_stale:build_base_matrix:25
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_024522_autopilot_status_stale.md

## 2026-02-18 02:45:22 | codex_exec_launched
- pid: 41878
- reason: autopilot_status_stale
- incident_id: 20260218_024522_autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_024522_autopilot_status_stale.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_024522_autopilot_status_stale.codex_exec.log

## 2026-02-18 02:48:10 | watchdog_started
- hash: aa8abb7
- auto_resume: True
- autopilot_session: v60_autopilot_aa8abb7
- uplink_session: v60_uplink_aa8abb7
- autopilot_launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1
- uplink_launch: bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
- live_state: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json
- events_log: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md

## 2026-02-18 02:48:11 | codex_exec_finished
- pid: 41878
- incident_id: 20260218_024522_autopilot_status_stale
- reason: autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_024522_autopilot_status_stale.codex_report.txt

## 2026-02-18 02:55:39 | codex_exec_finished
- pid: 41878
- incident_id: 20260218_024522_autopilot_status_stale
- reason: autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_024522_autopilot_status_stale.codex_report.txt

## 2026-02-18 04:03:27 | incident_captured
- reason: runner_error_Traceback
- fingerprint: runner_error:Traceback:-2331095186589212064
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_040327_runner_error_Traceback.md

## 2026-02-18 04:03:27 | codex_exec_launched
- pid: 51501
- reason: runner_error_Traceback
- incident_id: 20260218_040327_runner_error_Traceback
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_040327_runner_error_Traceback.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_040327_runner_error_Traceback.codex_exec.log

## 2026-02-18 04:15:47 | codex_exec_finished
- pid: 51501
- incident_id: 20260218_040327_runner_error_Traceback
- reason: runner_error_Traceback
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_040327_runner_error_Traceback.codex_report.txt

## 2026-02-18 04:15:47 | autopilot_auto_resumed
- session: v60_autopilot_aa8abb7
- restart_count: 4
- launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1

## 2026-02-18 04:48:39 | incident_captured
- reason: runner_error_Traceback
- fingerprint: runner_error:Traceback:-4919616950667070212
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_044839_runner_error_Traceback.md

## 2026-02-18 04:48:39 | codex_exec_launched
- pid: 14594
- reason: runner_error_Traceback
- incident_id: 20260218_044839_runner_error_Traceback
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_044839_runner_error_Traceback.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_044839_runner_error_Traceback.codex_exec.log

## 2026-02-18 04:58:56 | codex_exec_finished
- pid: 14594
- incident_id: 20260218_044839_runner_error_Traceback
- reason: runner_error_Traceback
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_044839_runner_error_Traceback.codex_report.txt

## 2026-02-18 04:58:56 | autopilot_auto_resumed
- session: v60_autopilot_aa8abb7
- restart_count: 5
- launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type n1-highmem-32 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type n1-highmem-32 --train-machine-type n1-highmem-32 --backtest-machine-type n1-highmem-32 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601 >> audit/runtime/v52/autopilot_aa8abb7.runner.log 2>&1

## 2026-02-18 07:10:28 | incident_captured
- reason: autopilot_status_stale
- fingerprint: autopilot_status_stale:build_base_matrix:26
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_071028_autopilot_status_stale.md

## 2026-02-18 07:10:28 | codex_exec_launched
- pid: 31820
- reason: autopilot_status_stale
- incident_id: 20260218_071028_autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_071028_autopilot_status_stale.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_071028_autopilot_status_stale.codex_exec.log

## 2026-02-18 07:22:48 | codex_exec_finished
- pid: 31820
- incident_id: 20260218_071028_autopilot_status_stale
- reason: autopilot_status_stale
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_071028_autopilot_status_stale.codex_report.txt

## 2026-02-18 10:21:25 | watchdog_started
- hash: aa8abb7
- auto_resume: True
- autopilot_session: v60_autopilot_aa8abb7
- uplink_session: v60_uplink_aa8abb7
- autopilot_launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601
- uplink_launch: bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
- live_state: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json
- events_log: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md

## 2026-02-18 10:21:28 | incident_captured
- reason: runner_error_Traceback
- fingerprint: runner_error:Traceback:-9067547301494126147
- snapshot: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_102128_runner_error_Traceback.md

## 2026-02-18 10:21:28 | codex_exec_launched
- pid: 20991
- reason: runner_error_Traceback
- incident_id: 20260218_102128_runner_error_Traceback
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_102128_runner_error_Traceback.codex_report.txt
- log_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_102128_runner_error_Traceback.codex_exec.log

## 2026-02-18 10:31:45 | codex_exec_finished
- pid: 20991
- incident_id: 20260218_102128_runner_error_Traceback
- reason: runner_error_Traceback
- report_path: /Users/zephryj/work/Omega_vNext/audit/runtime/v52/incidents/20260218_102128_runner_error_Traceback.codex_report.txt

## 2026-02-18 10:31:45 | autopilot_auto_resumed
- session: v60_autopilot_aa8abb7
- restart_count: 6
- launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601

## 2026-02-18 10:44:06 | autopilot_auto_resumed
- session: v60_autopilot_aa8abb7
- restart_count: 7
- launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601

## 2026-02-18 10:54:23 | autopilot_auto_resumed
- session: v60_autopilot_aa8abb7
- restart_count: 8
- launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601

## 2026-02-18 11:06:44 | autopilot_auto_resumed
- session: v60_autopilot_aa8abb7
- restart_count: 9
- launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601

## 2026-02-18 11:19:05 | autopilot_auto_resumed
- session: v60_autopilot_aa8abb7
- restart_count: 10
- launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601

## 2026-02-18 11:33:29 | autopilot_auto_resumed
- session: v60_autopilot_aa8abb7
- restart_count: 11
- launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601

## 2026-02-18 11:43:46 | autopilot_auto_resumed
- session: v60_autopilot_aa8abb7
- restart_count: 12
- launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601

## 2026-02-18 11:56:07 | autopilot_auto_resumed
- session: v60_autopilot_aa8abb7
- restart_count: 13
- launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601

## 2026-02-18 12:08:28 | autopilot_auto_resumed
- session: v60_autopilot_aa8abb7
- restart_count: 14
- launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=5 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601

## 2026-02-18 12:10:07 | watchdog_started
- hash: aa8abb7
- auto_resume: True
- autopilot_session: v60_autopilot_aa8abb7
- uplink_session: v60_uplink_aa8abb7
- autopilot_launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=1 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601
- uplink_launch: bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
- live_state: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json
- events_log: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md

## 2026-02-18 12:29:57 | watchdog_started
- hash: aa8abb7
- auto_resume: True
- autopilot_session: v60_autopilot_aa8abb7
- uplink_session: v60_uplink_aa8abb7
- autopilot_launch: PYTHONUNBUFFERED=1 python3 -u tools/v60_autopilot.py --hash aa8abb7 --bucket gs://omega_v52_central/omega --linux-expected 484 --windows-expected 263 --upload-mode wait_existing --poll-sec 180 --stall-sec 1800 --base-matrix-exec-mode vertex --base-matrix-machine-type e2-highmem-16 --base-matrix-max-rows-per-file=0 --base-matrix-chunk-days=1 --optimization-machine-type c2-standard-30 --train-machine-type c2-standard-30 --backtest-machine-type c2-standard-30 --base-matrix-sync-timeout-sec 21600 --optimization-sync-timeout-sec 10800 --train-sync-timeout-sec 21600 --backtest-sync-timeout-sec 10800 --test-years 2025,2026 --test-year-months 2025,202601
- uplink_launch: bash /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_loop_aa8abb7.sh >> /Users/zephryj/work/Omega_vNext/audit/runtime/v52/uplink_aa8abb7.log 2>&1
- live_state: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_run_aa8abb7.json
- events_log: /Users/zephryj/work/Omega_vNext/handover/ai-direct/live/v60_events_aa8abb7.md
