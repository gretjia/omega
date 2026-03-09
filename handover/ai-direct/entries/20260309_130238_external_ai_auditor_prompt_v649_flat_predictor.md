---
entry_id: 20260309_130238_external_ai_auditor_prompt_v649_flat_predictor
task_id: TASK-EXTERNAL-AUDITOR-PROMPT-V649-FLAT-PREDICTOR
timestamp_local: 2026-03-09 13:02:38 +0000
timestamp_utc: 2026-03-09 13:02:38 +0000
operator: Codex
role: commander
branch: main
git_head: 5f4ba0a
status: completed
---

# External AI Auditor Prompt: V649 Path B Flat-Predictor Diagnosis

## 1. Copy-Paste Prompt

```text
You are auditing the OMEGA repository on current `main`, including the frozen V64-series math canon, the frozen V648 Path B blocked smoke, and the new V649 flat-predictor diagnosis.

Your task is to perform a recursive audit across three layers:

1. the frozen V64-series mathematical canon,
2. the V648 Path B continuous-label pivot and its blocked local smoke,
3. the V649 local-only diagnosis that explains why the first Path B regime collapsed.

The central questions are:

- after V649, can we honestly move forward with Path B as the leading branch,
- or does the evidence now suggest a deeper feature-label / target-shape problem that still blocks Path B?
- can we honestly claim, at this point, that V64 found `Epiplexity` and compressed out `intelligence`,
- or does the evidence still stop at “physics extraction exists, but downstream intelligence translation remains unproven”?

You must answer those directly.

Important operating constraints:

- Work from committed GitHub-visible evidence first.
- Treat repo-relative paths as the primary authority.
- When you cite evidence in your answer, always cite the exact repo-relative path that supports the claim.
- Some runtime artifacts are local-only and not committed; those are listed separately as optional controller-local evidence.
- Do not assume access to worker disks or cloud objects unless a path/URI is explicitly documented below.
- Do not reinterpret away any frozen V645 / V646 / V647 / V648 verdict.

First do the recursive V64 math audit by reading these committed repo-relative files in this order:

1. `OMEGA_CONSTITUTION.md`
2. `audit/v64_audit_evolution.md`
3. `audit/v64.md`
4. `audit/v642.md`
5. `audit/v643.md`
6. `audit/v643_auditor_pass.md`
7. `audit/v644_mediocristan_label_bottleneck.md`
8. `audit/v646_path_a_power_family_surface.md`
9. `audit/v647_anti_classifier_paradox.md`
10. `audit/v648_path_a_collapse_anti_classifier_paradox.md`
11. `audit/v649_path_b_flat_predictor_diagnosis.md`
12. `omega_core/kernel.py`
13. `omega_core/omega_math_core.py`
14. `omega_core/omega_etl.py`
15. `tools/stage2_physics_compute.py`
16. `tools/forge_base_matrix.py`

Then read the committed V648 -> V649 evidence in this order:

1. `handover/ai-direct/entries/20260309_122200_v648_path_b_continuous_label_pivot_spec_draft.md`
2. `handover/ai-direct/entries/20260309_122800_v648_spec_draft_gemini_pass.md`
3. `handover/ai-direct/entries/20260309_122827_v648_path_b_continuous_label_pivot_mission_open.md`
4. `handover/ai-direct/entries/20260309_124249_v648_local_contract_and_smoke_blocked.md`
5. `handover/ai-direct/entries/20260309_124940_v649_path_b_flat_predictor_diagnosis_spec_draft.md`
6. `handover/ai-direct/entries/20260309_125400_v649_spec_draft_gemini_pass.md`
7. `handover/ai-direct/entries/20260309_125420_v649_path_b_flat_predictor_diagnosis_mission_open.md`
8. `handover/ai-direct/entries/20260309_125538_v649_flat_predictor_diagnosis_complete.md`
9. `handover/ai-direct/LATEST.md`
10. `handover/ops/ACTIVE_PROJECTS.md`
11. `handover/ops/ACTIVE_MISSION_CHARTER.md`
12. `tools/run_optuna_sweep.py`
13. `tools/run_vertex_xgb_train.py`
14. `tools/evaluate_xgb_on_base_matrix.py`
15. `tests/test_vertex_optuna_split.py`
16. `tests/test_vertex_swarm_aggregate.py`
17. `tests/test_vertex_holdout_eval.py`
18. `tests/test_vertex_train_weight_mode.py`

Canonical constraints that remained frozen throughout V648 and V649:

- `omega_core/*` unchanged
- Stage3 gate contract unchanged:
  - `signal_epi_threshold=0.5`
  - `singularity_threshold=0.1`
  - `srl_resid_sigma_mult=2.0`
  - `topo_energy_min=2.0`
  - `stage3_param_contract=canonical_v64_1`
- temporal split unchanged:
  - train:
    - `2023`
  - validation:
    - `2024`
- holdout isolation unchanged:
  - optimization:
    - `2023,2024`
  - outer holdout:
    - `2025`
  - final canary:
    - `2026-01`
- Path B learner contract during V648/V649:
  - learner mode:
    - `reg_squarederror_excess_return`
  - label:
    - raw `t1_excess_return`
  - sample weights:
    - `none`

Frozen V648 blocked result:

- local smoke root:
  - `audit/runtime/v648_local_smoke_20260309_123500/workers/w00`
- summary:
  - `n_trials=10`
  - `n_completed=10`
  - `n_structural_guardrail_passed=0`
  - `n_spearman_floor_passed=0`
  - `best_value=-1000000000.0`
- strongest local values:
  - `max_val_spearman_ic=0.0`
  - `max_alpha_top_decile=1.244533029128729e-20`
  - `max_alpha_top_quintile=1.244533029128729e-20`

Frozen V649 diagnosis summary:

Train matrix authority:
- `gs://omega_v52_central/omega/staging/base_matrix/latest/stage3_train_2023_2024_20260309_005839/base_matrix_train_2023_2024.parquet`

After the frozen canonical mask and frozen `t1_excess_return` construction:

- train rows:
  - `379331`
- val rows:
  - `356832`
- train zero fraction:
  - `0.9126383026960623`
- val zero fraction:
  - `0.9085788270110304`
- train `abs_median`:
  - `0.0`
- val `abs_median`:
  - `0.0`

Probe A: replay the V648 trial-0 parameter shape
- result:
  - exact constant predictor
  - `train_pred_std=0.0`
  - `val_pred_std=0.0`
  - rounded unique predictions:
    - `1`
  - feature importance count:
    - `0`
  - `val_spearman_ic=0.0`
  - `val_auc_sign=0.5`

Probe B: low-regularization contrast
- result:
  - prediction variance recovered
  - all `16` features used
  - `val_pred_std=0.0026945871260126695`
  - `val_spearman_ic=0.008458359767276777`
  - `val_auc_sign=0.49061062250083853`
  - `val_alpha_top_decile=1.2134796680614228e-05`
  - `val_alpha_top_quintile=3.123546710946954e-05`
- meaning:
  - Path B is not mathematically forced to stay constant
  - but naive variance recovery still fails the structural-tail contract

Committed repo-relative evidence map:

- audit canon:
  - `audit/v64_audit_evolution.md`
  - `audit/v64.md`
  - `audit/v642.md`
  - `audit/v643.md`
  - `audit/v643_auditor_pass.md`
  - `audit/v644_mediocristan_label_bottleneck.md`
  - `audit/v646_path_a_power_family_surface.md`
  - `audit/v647_anti_classifier_paradox.md`
  - `audit/v648_path_a_collapse_anti_classifier_paradox.md`
  - `audit/v649_path_b_flat_predictor_diagnosis.md`
- mission / verdict chain:
  - `handover/ai-direct/entries/20260309_122200_v648_path_b_continuous_label_pivot_spec_draft.md`
  - `handover/ai-direct/entries/20260309_122800_v648_spec_draft_gemini_pass.md`
  - `handover/ai-direct/entries/20260309_122827_v648_path_b_continuous_label_pivot_mission_open.md`
  - `handover/ai-direct/entries/20260309_124249_v648_local_contract_and_smoke_blocked.md`
  - `handover/ai-direct/entries/20260309_124940_v649_path_b_flat_predictor_diagnosis_spec_draft.md`
  - `handover/ai-direct/entries/20260309_125400_v649_spec_draft_gemini_pass.md`
  - `handover/ai-direct/entries/20260309_125420_v649_path_b_flat_predictor_diagnosis_mission_open.md`
  - `handover/ai-direct/entries/20260309_125538_v649_flat_predictor_diagnosis_complete.md`
  - `handover/ai-direct/LATEST.md`
  - `handover/ops/ACTIVE_PROJECTS.md`
  - `handover/ops/ACTIVE_MISSION_CHARTER.md`
- code:
  - `tools/run_optuna_sweep.py`
  - `tools/run_vertex_xgb_train.py`
  - `tools/evaluate_xgb_on_base_matrix.py`
- tests:
  - `tests/test_vertex_optuna_split.py`
  - `tests/test_vertex_swarm_aggregate.py`
  - `tests/test_vertex_holdout_eval.py`
  - `tests/test_vertex_train_weight_mode.py`

Core V64 math / physics implementation files for recursive audit:

- `omega_core/kernel.py`
- `omega_core/omega_math_core.py`
- `omega_core/omega_etl.py`
- `tools/stage2_physics_compute.py`
- `tools/forge_base_matrix.py`

Optional local-only runtime evidence in the working tree:

- `audit/runtime/v648_local_smoke_20260309_123500/workers/w00/study_summary.json`
- `audit/runtime/v648_local_smoke_20260309_123500/workers/w00/trials.jsonl`
- `audit/runtime/v649_flat_diag_20260309_130000/path_b_probe_summary.json`
- `audit/runtime/v649_flat_diag_20260309_130000/path_b_probe_low_reg_summary.json`

My current questions, doubts, and requested guidance:

1. Is the dominant blocker now best described as:
   - target sparsity / zero-mass,
   - regression search-space degeneracy,
   - or a deeper feature-label mismatch that still makes raw `t1_excess_return` the wrong Path B target?

2. Does V649 justify continuing with Path B as the leading branch, or should Path B itself now be considered conceptually unstable?

3. If Path B remains justified, what is the minimum bounded next mission?
   Candidate axes:
   - explicit non-degeneracy gates inside local sweep,
   - variance-floor / no-split avoidance in the search space,
   - target transformation while keeping continuous labels,
   - robust regression loss while keeping the same raw label contract

4. Is it still honest to say:
   - V64 found `Epiplexity`,
   - but we still have not proven that we compressed out stable downstream `intelligence`?

I do not want only a verdict. I need your concrete thinking process and your narrowing logic:

- which hypothesis you eliminate first, and why,
- which evidence path is strongest and which is weak,
- what should remain frozen,
- what exact next mission axis is smallest but still decisive,
- what would count as a convergence signal vs another dead end.

Please answer in this exact structure:

1. Central claim:
   - `YES`
   - `PARTIAL ONLY`
   - `NO`
2. Short verdict
3. Ranked root causes
4. Concrete bugs or weak assumptions
5. Detailed reasoning path:
   - which evidence most strongly drove your conclusion
   - which alternative explanations you ruled out
6. Recommended next mission
7. Exact minimum decisive experiment
8. Convergence plan:
   - what to freeze
   - what single axis to change
   - what output metrics must improve together
   - what failure pattern would immediately kill that branch
9. Whether Path B should remain the leading branch
```

## 2. Notes

- This prompt is designed for a fresh recursive audit after V649 closed the first Path B diagnostic loop.
- The goal is not to re-open V648 or V649, but to extract a precise next-step mission from the frozen evidence.
