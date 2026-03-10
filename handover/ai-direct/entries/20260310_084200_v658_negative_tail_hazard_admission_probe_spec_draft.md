# V658 Spec Draft: Negative-Tail Hazard Admission Probe

Status: Draft for Gemini math audit
Date: 2026-03-10 08:42 UTC
Mission candidate: V658 Negative-Tail Hazard Admission Probe

## 1. Why This Mission Exists

V657 passed, but only under a narrow evaluator semantics:

- one-sided
- sign-aware
- threshold / hazard

It did not reopen broad ML.

So the next truthful step is not:

- another forge rewrite
- another signal-family rewrite
- cloud training
- holdout use

It is to test whether a learner can sharpen a single already-proven trigger.

## 2. Frozen Boundaries

The following stay frozen:

- `tools/forge_campaign_state.py`
- daily spine
- `entry_open_t1`
- `excess_ret_t1_to_Hd`
- triple-barrier semantics
- same-sign pulse compression
- V655A soft-mass candidate stream
- V655B amplitude-aware daily fold
- V656 transition derivation formulas
- the frozen V655B H1 campaign matrix
- ML / Vertex / holdout closure outside this admission probe
- `omega_core/*`
- Stage2 artifacts

## 3. Single Allowed Change Axis

Change only:

- the admission protocol

from:

- raw threshold trigger only

to:

- trigger-conditioned hazard learner

## 4. Frozen Primary Contract

Primary signal:

- `dPsiAmpE_10d`

Primary side:

- `negative`

Primary horizon:

- `10d`

Primary admission threshold:

- negative-side `90th` percentile of absolute magnitude

Shadow control only:

- `FreshAmpStar_10d`
- `negative`

No search is allowed over:

- signal family
- side
- horizon
- admission threshold

## 5. Canonical Mathematics

Let:

- `x_{i,d} = dPsiAmpE_10d`

Define the negative-side universe on date `d`:

- `N_d = { i : x_{i,d} < -eps }`

Define the admission quantile:

- `q^-_{d,90} = Q_0.90({ |x_{i,d}| : i in N_d })`

Define the admission mask:

- `G_{i,d} = 1{ i in N_d and |x_{i,d}| >= q^-_{d,90} }`

Primary binary label:

- `Y_{i,d} = 1{ barrier_10d(i,d) = -1 }`

Primary signed return:

- `R_{i,d} = -excess_ret_t1_to_10d(i,d)`

Frozen feature set:

- `dPsiAmpE_10d`
- `FreshAmpStar_10d`
- `PsiAmpE_10d`
- `PsiAmpStar_10d`
- `OmegaAmpE_10d`
- `OmegaAmpStar_10d`
- `vol20d`
- `pulse_count`
- `pulse_concentration`

Learner target:

- estimate `p_hat_{i,d} ~= P(Y_{i,d}=1 | Z_{i,d}, G_{i,d}=1)`

Fixed loss:

- binary logistic loss only

## 6. Model-vs-Baseline Evaluation

The learner is evaluated inside the admitted set only.

For each validation date `d` and selection fraction `alpha in {0.50, 0.25}`:

- `S_model(d, alpha) = { i : G_{i,d}=1 and p_hat_{i,d} >= Q_{1-alpha,d}(p_hat) }`
- `S_raw(d, alpha) = { i : G_{i,d}=1 and |x_{i,d}| >= Q_{1-alpha,d}(|x|) }`

Date-neutral signed return:

- `Rbar_model(alpha) = mean_d mean_{i in S_model(d, alpha)} R_{i,d}`
- `Rbar_raw(alpha) = mean_d mean_{i in S_raw(d, alpha)} R_{i,d}`

Date-neutral hazard success:

- `Hbar_model(alpha) = mean_d mean_{i in S_model(d, alpha)} Y_{i,d}`
- `Hbar_raw(alpha) = mean_d mean_{i in S_raw(d, alpha)} Y_{i,d}`

Logloss guard:

- `logloss_model < logloss_constant`

## 7. Engineering Translation

### 7.1 Writable files

- `tools/run_campaign_ml_admission_probe.py`
- `tests/test_campaign_ml_admission_probe.py`
- handover / audit files for V658

### 7.2 Implementation requirements

Create a lightweight local-only tool:

- `tools/run_campaign_ml_admission_probe.py`

This tool must:

1. read the frozen V655B campaign matrix
2. derive the frozen V656 transition columns in-memory
3. build the fixed negative-tail admission mask from `dPsiAmpE_10d`
4. train one fixed low-capacity `binary:logistic` learner inside admitted rows only
5. evaluate two chronological forward folds
6. compare model-selected subsets against raw same-count baseline subsets

No forge rewrite is allowed.

No new signal family is allowed.

No hyperparameter sweep is allowed.

## 8. AgentOS Team

Commander:

- owns scope, integration, git, and handover

Formula Integrity Auditor:

- engine:
  - `gemini -p`
- model rule:
  - default `gemini 3.1 pro preview` only
- responsibility:
  - audit every formula-bearing diff against:
    - `audit/v658_negative_tail_hazard_admission_probe.md`
    - `audit/v657_h1_sign_aware_threshold_pass_evidence.md`

Admission Probe Engineer:

- responsibility:
  - implement the fixed admitted-set learner without changing forge or signal derivations

Leakage Auditor:

- responsibility:
  - verify admitted-set-only training
  - verify chronological folds
  - verify raw same-count baseline is computed inside the admitted set only

Runtime Orchestrator:

- responsibility:
  - keep outputs isolated
  - enforce local-only / no-cloud / no-holdout sequencing
  - use polling agents instead of watchdog / supervisor programs

ML Admission Gatekeeper:

- responsibility:
  - refuse any broader ML reopening unless V658 beats both constant-baseline logloss and raw same-count baseline economics

## 9. Runtime Shape

Wave 1 remains:

- local-only
- no GCP / Vertex
- no holdout
- no Optuna
- no forge rerun

Preferred runtime basis:

- existing V655B H1 campaign matrix on `linux1-lx`

Two forward folds:

- Fold A:
  - first `60%` dates train
  - next `20%` dates validate
- Fold B:
  - first `80%` dates train
  - final `20%` dates validate

## 10. Success Criteria

V658 earns continuation only if:

1. on each fold:
   - `logloss_model < logloss_constant`
2. and for at least one `alpha in {0.50, 0.25}` on each fold:
   - `Rbar_model(alpha) > Rbar_raw(alpha)`
   - `Hbar_model(alpha) > Hbar_raw(alpha)`

## 11. Kill Condition

Kill V658 and keep broader ML closed if:

- the fixed admitted-set learner is implemented cleanly
- forge and transition derivations remain frozen
- but the learner cannot beat:
  - constant-baseline logloss
  - and raw same-count baseline economics

## 12. Definition of Done For This Draft Stage

This draft is ready for execution only when:

- the new audit authority is landed under `audit/`
- the single admission-protocol change axis is explicit
- the frozen boundaries are explicit
- `gemini -p` has audited the draft and any required fixes are folded in
