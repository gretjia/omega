---
name: ai_handover
description: AI Agent Handover Protocol - Fast context acquisition for new AI sessions. Read this FIRST.
---

# AI Handover Protocol

## Section 0: Reading Instructions

PRIORITY: Read sections in order 0→1→2→3→4. Stop at Section 4 to check handover state.

GOAL: Minimize context re-acquisition time between AI sessions.

FORMAT: This document uses machine-parseable structures. Human rhetoric is intentionally omitted.

### 0.1 Handover Protocol

**NEW AI SESSION START**:
1. Read THIS file (SKILL.md) for project structure
2. Read `handover_log.md` (same directory) for latest session state
3. Continue from "Next AI Should" section in the log

**CURRENT AI SESSION END** (when user says "handover" / "交接" / "换班"):
1. Execute workflow: `.agent/workflows/handover.md`
2. Run validation gate: `python3 tools/check_readme_sync.py` (must pass before handover log write)
3. Prepend new entry to `handover_log.md` with:
   - Completed tasks
   - Current state
   - Next steps for successor AI
   - Modified files
   - Validation gate result (`README sync: PASS/FAIL`)
   - Warnings
4. Notify user that handover is recorded

---

## Section 1: Project Identity

```yaml
project_name: OMEGA vNext
type: Quantitative Trading System
domain: A-Share Market (China)
base_path: .
python_env: conda activate OMEGA
```

### 1.1 Core Mathematical Framework

The system is built on THREE orthogonal mathematical pillars. All three MUST be present in any trading decision:

| Pillar | Purpose | Key Equation | Output |
|:-------|:--------|:-------------|:-------|
| TDA | Detect market "shape" | Persistent Homology on Takens-embedded point cloud | β₀ (clusters), β₁ (loops) |
| SRL | Measure price impact physics | I = Y·σ·√(Q/V) | SRL_Residual = I_actual - I_predicted |
| Epiplexity | Separate learnable structure from noise | MDL decomposition = Structure_bits + Residual_bits | ρ = E/(E+H) tradability ratio |

### 1.2 Key Constraint: Volume Clock

CRITICAL: All math operations MUST use Volume Time (equal-volume bars), NOT physical time.
REASON: SRL is linear in volume time; non-linear in physical time.
A-SHARE SPECIFIC: 9:30-10:00 has 10x information density vs 14:00.

---

## Section 2: Protected Artifacts

### 2.1 Parameter Principles (Constitution Article II)

**CORE RULE**: "There are NO static parameters." - OMEGA Constitution

```python
# ❌ PROHIBITED: Hardcoded trading thresholds (limits model intelligence)
STOP_LOSS = -0.03       # PROHIBITED - must be Entropy-gated
TAKE_PROFIT = 0.15      # PROHIBITED - must be model-learned
trigger_floor = 1.2     # PROHIBITED - must be dynamic quantile
gamma_scale = 0.15      # PROHIBITED - must be adaptive

# ✅ ALLOWED: Architecture parameters (define network structure, not trading logic)
OBS_INPUT_DIM = 120     # Network input dimension
OBS_HIDDEN_DIM = 32     # Network hidden dimension

# ✅ REQUIRED: Dynamic/Recursive thresholds
threshold = quantile(rolling_history, 0.95)  # Distribution-based
exit_signal = entropy_gated_control_law(H_T, S_T)  # Information-theoretic
```

**WHY**: Hardcoded STOP_LOSS/TAKE_PROFIT prevents model from learning optimal exit strategies.

### 2.2 Protected Files (Require confirmation before edit)

```
omega_v3_core/kernel.py      # Decision brain (active core)
omega_v3_core/omega_math_core.py # Math engine (active core)
feature_factory.py           # Training feature extraction
data_pipeline.py             # Data preprocessing
config.py                    # Global configuration
legacy_model/v1/kernel.py    # Legacy v1 core (when explicitly requested)
legacy_model/v1/omega_math_core.py # Legacy v1 math core
*.pkl                        # Trained models
```

### 2.3 Modification Protocol

IF modifying protected file:
  1. CREATE `audit/vXXXX_parameter_change_proposal.md`
  2. INCLUDE: reason, expected_effect, backtest_comparison
  3. RUN: Industrial Scanner verification
  4. NOTIFY user with diff table before execution

---

## Section 3: Directory Structure

```
./
├── OMEGA_CONSTITUTION.md        # [READ] First principles
├── README.md                    # [READ] Architecture overview
├── config.py                    # Global config center
├── omega_v3_core/               # [ACTIVE] v3 mainline core
│   ├── kernel.py                # Decision brain (v3)
│   ├── omega_math_core.py       # Math algorithms (v3)
│   └── trainer.py               # Strategy trainer (v3)
├── legacy_model/v1/             # [LEGACY] v1 implementation
│   ├── kernel.py
│   ├── omega_math_core.py
│   └── trainer.py
├── kernel.py                    # Compatibility shim -> legacy_model/v1/kernel.py
├── omega_math_core.py           # Compatibility shim -> legacy_model/v1/omega_math_core.py
├── trainer.py                   # Compatibility shim -> legacy_model/v1/trainer.py
│
├── .agent/skills/               # [READ] AI behavior rules
│   ├── omega_development/       # Core dev rules + param protection
│   ├── math_consistency/        # Train/infer sync protocol
│   ├── data_integrity_guard/    # Data schema validation
│   ├── evidence_based_reasoning/# Evidence-first decisions
│   ├── evolution_knowledge/     # Version history forensics
│   └── ai_handover/             # THIS FILE
│
├── audit/                       # Historical audits & proposals
│   ├── Bible.md                 # [READ] Full math derivation
│   └── Bible_AUDIT.md           # First-principles code audit
│
├── data/                        # Data warehouse
│   ├── history_ticks/           # [DO NOT DELETE] Raw tick CSV
│   ├── binary_ticks/            # [REBUILDABLE] Cached NPY
│   ├── level2/                  # [DO NOT DELETE] L2 archives
│   ├── level2_frames_win2023/   # [REBUILDABLE] 2023 Parquet
│   └── level2_frames_mac2024/   # [REBUILDABLE] 2024 Parquet
│
├── jobs/                        # Distributed training
│   ├── windows_2023/            # Ryzen 128G worker
│   └── mac_2024/                # M4 Max worker
│
└── tools/                       # Utility scripts
    └── run_l2_audit_driver.py   # Parallel L2 processor
```

---

## Section 4: Handover State

### Dynamic State Source

Do not store live project state in this file.

Single source of truth for current state:
- `.agent/skills/ai_handover/handover_log.md`

Session start protocol:
1. Read the most recent handover entry.
2. Extract:
   - completed tasks
   - active issues
   - blocked decisions
   - next actions
3. Treat this SKILL as protocol; treat `handover_log.md` as runtime state.

Session end protocol:
1. Run `python3 tools/check_readme_sync.py` and confirm PASS.
2. Append/prepend a new entry to `handover_log.md`.
3. Include:
   - date/time
   - what changed
   - evidence paths
   - validation gate status (`README sync`)
   - next recommended step

---

## Section 5: Verification Checklists

### 5.1 Before Modifying omega_v3_core/kernel.py

```
[ ] Did I read the existing formula's physical meaning?
[ ] Do I have mathematical justification for the change?
[ ] Did I sync feature_factory.py?
[ ] Did I add boundary guards (np.maximum, np.clip)?
[ ] Did I notify user with before/after comparison?
```

### 5.2 Before Processing New Data Source

```
[ ] Did I print sample: type(), columns, first row?
[ ] Did I verify field names match expected schema?
[ ] Did I check for string-encoded arrays (e.g., "[21.5, 21.6]")?
[ ] Did I add schema validation guard function?
```

### 5.3 Before Making Claims

```
[ ] Did I check audit/ for historical evidence?
[ ] Did I grep the codebase for prior occurrences?
[ ] Am I citing a file path and line number?
[ ] If guessing, did I explicitly state "INFERENCE: ..."?
```

---

## Section 6: Common Failure Modes

### 6.1 Zero Trades

SYMPTOM: Backtest completes, Trades = 0
CHECK:
  - trigger_floor value (should be 1.2, not 0.5)
  - Surprise locked at high value
  - Kappa computed on raw values instead of Z-score

### 6.2 Infinite ROI

SYMPTOM: ROI > 1000%
CHECK:
  - Cash deduction after buy
  - Limit-up stock purchase prevention
  - Position overflow

### 6.3 Train/Infer Mismatch

SYMPTOM: Model works in training, fails in backtest
CHECK:
  - feature_factory.py vs omega_v3_core/kernel.py sync
  - Z-score vs raw value normalization
  - Tensor shape (N, 120, 5) vs (N, 11, 5)

---

## Section 7: Quick Reference Commands

```powershell
# Single stock quick test
python omega_standaloner.py --stock 000032 --debug

# Check L2 training progress
type data\level2_frames_win2023\_audit_state.jsonl | find /c /v ""

# Activate environment
conda activate OMEGA

# Project root
cd /path/to/Omega_vNext
```

---

## Section 8: Skill File Index

Governance note: keep always-on skills minimal and treat process/governance skills as on-demand.  
Reference: `.agent/skills/meta/skill_library_governance.md`

| Skill | Path | When to Read |
|:------|:-----|:-------------|
| ai_handover | `.agent/skills/ai_handover/SKILL.md` | FIRST, every session |
| omega_development | `.agent/skills/omega_development/SKILL.md` | Before any code edit |
| v3_mainline_guard | `.agent/skills/v3_mainline_guard/SKILL.md` | Before changing core paths / deciding v3 vs legacy |
| hardcode_guard | `.agent/skills/hardcode_guard/SKILL.md` | Before introducing any threshold/gate constant |
| config_promotion_protocol | `.agent/skills/config_promotion_protocol/SKILL.md` | When promoting discovered params into config.py |
| innovation_sandbox | `.agent/skills/innovation_sandbox/SKILL.md` | When running high-freedom experiments before productionization |
| multi_agent_rule_sync | `.agent/skills/multi_agent_rule_sync/SKILL.md` | When updating cross-agent rules |
| math_consistency | `.agent/skills/math_consistency/SKILL.md` | Before core-kernel/feature changes |
| data_integrity_guard | `.agent/skills/data_integrity_guard/SKILL.md` | Before processing new data |
| evidence_based_reasoning | `.agent/skills/evidence_based_reasoning/SKILL.md` | Before making claims |
| evolution_knowledge | `.agent/skills/evolution_knowledge/SKILL.md` | Before parameter changes |
| omega_data | `.agent/skills/omega_data/SKILL.md` | When locating data files |

---

## Section 9: Glossary

| Term | Definition |
|:-----|:-----------|
| TDA | Topological Data Analysis - extracts shape features from point clouds |
| SRL | Square-Root Law - I ∝ σ√(Q/V), price impact scales with √volume |
| Epiplexity | Learnable complexity component of time-bounded MDL |
| H_T | Time-Bounded Entropy - irreducible noise component |
| Volume Clock | Time axis redefined as "per N shares traded" instead of seconds |
| SRL Residual | I_actual - I_predicted; negative = hidden liquidity |
| Takens Embedding | Delay embedding τ, dimension d to reconstruct phase space |
| β₁ | Betti-1: count of 1-dimensional holes (loops) in persistent homology |

---

END OF HANDOVER DOCUMENT
