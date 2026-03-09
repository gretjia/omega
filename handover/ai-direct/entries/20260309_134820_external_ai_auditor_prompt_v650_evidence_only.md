---
entry_id: 20260309_134820_external_ai_auditor_prompt_v650_evidence_only
task_id: TASK-EXTERNAL-AUDITOR-PROMPT-V650-EVIDENCE-ONLY
timestamp_local: 2026-03-09 13:48:20 +0000
timestamp_utc: 2026-03-09 13:48:20 +0000
operator: Codex
role: commander
branch: main
git_head: 5395018
status: completed
---

# External AI Auditor Prompt: V650 Evidence-Only Packet

## 1. Copy-Paste Prompt

```text
You are auditing the OMEGA repository on current `main`.

This packet is intentionally evidence-only.

- It does not include my questions.
- It does not include my hypotheses.
- It does not include my preferred answer.

Your task is to perform a recursive audit using the evidence and repo-relative paths below, then produce your own:

1. central claim,
2. short verdict,
3. ranked root causes,
4. evidence-backed reasoning path,
5. convergence plan,
6. concrete next-mission narrowing.

When citing evidence, always cite the exact repo-relative path that supports the claim.

Use the material in this order.

## A. Current Round First: V650 Zero-Mass Gravity Well

### A1. Current-round audit authority / spec / mission / result

- `audit/v650_zero_mass_gravity_well.md`
- `handover/ai-direct/entries/20260309_131310_v650_zero_mass_gravity_well_spec_draft.md`
- `handover/ai-direct/entries/20260309_131707_v650_spec_draft_gemini_pass.md`
- `handover/ai-direct/entries/20260309_132836_v650_zero_mass_gravity_well_mission_open.md`
- `handover/ai-direct/entries/20260309_133613_v650_local_robust_loss_kill_condition_triggered.md`

### A2. Current-round code and test surfaces

- `tools/run_optuna_sweep.py`
- `tests/test_vertex_optuna_split.py`

### A3. Current-round local runtime evidence

- `audit/runtime/v650_local_sweep_20260309_133400/worker_local/study_summary.json`
- `audit/runtime/v650_local_sweep_20260309_133400/worker_local/trials.jsonl`

### A4. Current-round factual summary

Use these as factual checkpoints and verify them against the files above:

- scope:
  - local-only
  - sweep-only
  - no GCP
  - no retrain
  - no holdout
- learner mode:
  - `reg_pseudohuber_excess_return`
- weight mode:
  - `none`
- objective metric:
  - `structural_tail_monotonicity_gate`
- trials:
  - `n_trials=10`
  - `n_completed=10`
- gates:
  - `n_structural_guardrail_passed=0`
  - `n_spearman_floor_passed=0`
  - `n_non_degeneracy_passed=0`
  - `n_local_continuation_passed=0`
- best objective:
  - `best_value=-1000000000.0`
- observed degeneration:
  - `val_pred_std=0.0` or `5.684341886080802e-14`
  - rounded unique predictions:
    - `1`
  - non-zero feature-importance count:
    - `0`
  - `val_spearman_ic=0.0`
  - `val_auc=0.5`

## B. Full Evidence Chain From Path A Exploration Onward

Read the following by directory and relative path.

### B1. `audit/`

- `audit/v644_mediocristan_label_bottleneck.md`
- `audit/v646_path_a_power_family_surface.md`
- `audit/v647_anti_classifier_paradox.md`
- `audit/v648_path_a_collapse_anti_classifier_paradox.md`
- `audit/v649_path_b_flat_predictor_diagnosis.md`
- `audit/v650_zero_mass_gravity_well.md`

### B2. `handover/ai-direct/entries/`

Use this chain in chronological order.

- `handover/ai-direct/entries/20260309_050702_gc_swarm_optuna_pilot_and_champion_retrain_complete.md`
- `handover/ai-direct/entries/20260309_054700_holdout_base_matrix_evaluation_complete.md`
- `handover/ai-direct/entries/20260309_070752_v644_agentos_final_execution_spec.md`
- `handover/ai-direct/entries/20260309_071432_v644_alpha_first_local_implementation_pass.md`
- `handover/ai-direct/entries/20260309_072256_v644_alpha_first_pilot_stop_gate.md`
- `handover/ai-direct/entries/20260309_074955_asymmetric_label_pivot_mission_open.md`
- `handover/ai-direct/entries/20260309_080141_v645_path_a_local_micro_sweep_positive.md`
- `handover/ai-direct/entries/20260309_084315_v645_path_a_retrain_and_fresh_holdout_partial_pass.md`
- `handover/ai-direct/entries/20260309_090713_v645_path_b_local_compare_weaker_than_path_a.md`
- `handover/ai-direct/entries/20260309_091728_v646_path_a_refinement_mission_open.md`
- `handover/ai-direct/entries/20260309_094727_v646_path_a_sqrt_refinement_mixed_holdout_verdict.md`
- `handover/ai-direct/entries/20260309_100300_v646_path_a_pow075_second_slice_local_only.md`
- `handover/ai-direct/entries/20260309_100830_v646_path_a_pow0875_third_slice_local_only.md`
- `handover/ai-direct/entries/20260309_100901_v646_path_a_pow0625_fourth_slice_local_only.md`
- `handover/ai-direct/entries/20260309_101348_external_ai_auditor_prompt_v646_power_family.md`
- `handover/ai-direct/entries/20260309_105249_v647_structural_tail_monotonicity_gate_spec_draft.md`
- `handover/ai-direct/entries/20260309_105540_v647_spec_draft_gemini_pass.md`
- `handover/ai-direct/entries/20260309_110100_v647_structural_tail_monotonicity_gate_mission_open.md`
- `handover/ai-direct/entries/20260309_111100_v647_local_contract_and_smoke_pass.md`
- `handover/ai-direct/entries/20260309_112400_v647_gcp_swarm_and_holdout_gate_failed.md`
- `handover/ai-direct/entries/20260309_113200_external_ai_auditor_prompt_v647_structural_gate.md`
- `handover/ai-direct/entries/20260309_122200_v648_path_b_continuous_label_pivot_spec_draft.md`
- `handover/ai-direct/entries/20260309_122800_v648_spec_draft_gemini_pass.md`
- `handover/ai-direct/entries/20260309_122827_v648_path_b_continuous_label_pivot_mission_open.md`
- `handover/ai-direct/entries/20260309_124249_v648_local_contract_and_smoke_blocked.md`
- `handover/ai-direct/entries/20260309_124940_v649_path_b_flat_predictor_diagnosis_spec_draft.md`
- `handover/ai-direct/entries/20260309_125400_v649_spec_draft_gemini_pass.md`
- `handover/ai-direct/entries/20260309_125420_v649_path_b_flat_predictor_diagnosis_mission_open.md`
- `handover/ai-direct/entries/20260309_125538_v649_flat_predictor_diagnosis_complete.md`
- `handover/ai-direct/entries/20260309_130238_external_ai_auditor_prompt_v649_flat_predictor.md`
- `handover/ai-direct/entries/20260309_131310_v650_zero_mass_gravity_well_spec_draft.md`
- `handover/ai-direct/entries/20260309_131707_v650_spec_draft_gemini_pass.md`
- `handover/ai-direct/entries/20260309_132836_v650_zero_mass_gravity_well_mission_open.md`
- `handover/ai-direct/entries/20260309_133613_v650_local_robust_loss_kill_condition_triggered.md`

### B3. `audit/runtime/`

These are controller-local runtime artifacts. Use them as local evidence where needed.

#### V644

- `audit/runtime/swarm_optuna_v644_pilot_20260309_071719/vertex_swarm_launch_manifest.json`

#### V645

- `audit/runtime/v645_path_a_local_20260309_080040/worker_local/study_summary.json`
- `audit/runtime/v645_path_a_local_20260309_080040/worker_local/trials.jsonl`
- `audit/runtime/v645_path_a_retrain_20260309_081034/model/train_metrics.json`
- `audit/runtime/v645_path_a_retrain_20260309_081034/model/omega_xgb_final.pkl`
- `audit/runtime/v645_path_b_local_20260309_090552/worker_local/study_summary.json`
- `audit/runtime/v645_path_b_local_20260309_090552/worker_local/trials.jsonl`

#### V646

- `audit/runtime/v646_path_a_refine_local_20260309_093827/worker_local/study_summary.json`
- `audit/runtime/v646_path_a_refine_local_20260309_093827/worker_local/trials.jsonl`
- `audit/runtime/v646_path_a_retrain_20260309_094045/model/train_metrics.json`
- `audit/runtime/v646_path_a_retrain_20260309_094045/model/omega_xgb_final.pkl`
- `audit/runtime/v646_path_a_refine2_local_20260309_095500/worker_local/study_summary.json`
- `audit/runtime/v646_path_a_refine2_local_20260309_095500/worker_local/trials.jsonl`
- `audit/runtime/v646_path_a_refine3_local_20260309_100600/worker_local/study_summary.json`
- `audit/runtime/v646_path_a_refine3_local_20260309_100600/worker_local/trials.jsonl`
- `audit/runtime/v646_path_a_refine4_local_20260309_100700/worker_local/study_summary.json`
- `audit/runtime/v646_path_a_refine4_local_20260309_100700/worker_local/trials.jsonl`

#### V647

- `audit/runtime/v647_local_smoke_20260309_110859/worker_local/study_summary.json`
- `audit/runtime/v647_local_smoke_20260309_110859/worker_local/trials.jsonl`
- `audit/runtime/v647_local_smoke_20260309_110859/aggregate/swarm_leaderboard.json`
- `audit/runtime/v647_local_smoke_20260309_110859/aggregate/champion_params.json`
- `audit/runtime/v647_gcp_swarm_20260309_111500/vertex_swarm_launch_manifest.json`
- `audit/runtime/v647_champion_retrain_20260309_111700/model/train_metrics.json`
- `audit/runtime/v647_champion_retrain_20260309_111700/model/omega_xgb_final.pkl`

#### V648

- `audit/runtime/v648_local_smoke_20260309_123500/workers/w00/study_summary.json`
- `audit/runtime/v648_local_smoke_20260309_123500/workers/w00/trials.jsonl`

#### V649

- `audit/runtime/v649_flat_diag_20260309_130000/path_b_probe_summary.json`
- `audit/runtime/v649_flat_diag_20260309_130000/path_b_probe_low_reg_summary.json`

#### V650

- `audit/runtime/v650_local_sweep_20260309_133400/worker_local/study_summary.json`
- `audit/runtime/v650_local_sweep_20260309_133400/worker_local/trials.jsonl`

### B4. Current operational truth

- `handover/ai-direct/LATEST.md`
- `handover/ops/ACTIVE_PROJECTS.md`
- `handover/ops/ACTIVE_MISSION_CHARTER.md`
- `handover/BOARD.md`

### B5. Active code surfaces used by this chain

- `tools/run_optuna_sweep.py`
- `tools/run_vertex_xgb_train.py`
- `tools/evaluate_xgb_on_base_matrix.py`
- `tools/aggregate_vertex_swarm_results.py`
- `tools/launch_vertex_swarm_optuna.py`

### B6. Active tests used by this chain

- `tests/test_vertex_optuna_split.py`
- `tests/test_vertex_train_weight_mode.py`
- `tests/test_vertex_holdout_eval.py`
- `tests/test_vertex_swarm_aggregate.py`

### B7. Canonical math / physics context for recursive audit

- `OMEGA_CONSTITUTION.md`
- `audit/v64_audit_evolution.md`
- `audit/v64.md`
- `audit/v642.md`
- `audit/v643.md`
- `audit/v643_auditor_pass.md`
- `omega_core/kernel.py`
- `omega_core/omega_math_core.py`
- `omega_core/omega_etl.py`
- `tools/stage2_physics_compute.py`
- `tools/forge_base_matrix.py`

## C. Output Requirement

Use the evidence above and write a recursive audit that includes:

1. central claim,
2. short verdict,
3. ranked root causes,
4. evidence-backed reasoning path,
5. convergence plan,
6. next-mission narrowing.

Do not cite unstated assumptions when an exact repo-relative path is available.
```

