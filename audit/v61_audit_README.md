# OMEGA v6.1 "Anti-Fragile" — Audit Package Guide

> **For Google AI Studio Comprehensive Audit**
> Upload this `.zip` and paste this guide as your prompt context.

## 🎯 Audit Request

Please perform a comprehensive code review of OMEGA v6.1, a high-frequency quantitative trading system for China A-Shares.
Focus on: mathematical correctness of the physics engine, data integrity (cross-symbol contamination), ML pipeline soundness, and distributed framing architecture.

## 📁 File Topology

```
v61_audit/
├── README_AUDIT.md          ← YOU ARE HERE (Start reading this)
│
├── config.py                ← Master configuration (L2PipelineConfig, physics params)
├── config_v6.py             ← v6-specific config extensions
├── orchestrator.py          ← Top-level pipeline orchestrator
├── pipeline_runner.py       ← Pipeline execution entry point
│
├── omega_core/              ← ★ PHYSICS ENGINE (MOST CRITICAL)
│   ├── kernel.py            ← Core physics: SRL, Epiplexity, TDA, recursive state machine
│   ├── omega_etl.py         ← Level-2 tick data ETL (Polars pipeline, volume clock)
│   ├── omega_etl_ashare.py  ← A-share specific ETL extensions
│   ├── omega_math_core.py   ← Mathematical primitives (topology, entropy)
│   ├── omega_math_vectorized.py ← Vectorized math operations
│   ├── trainer.py           ← XGBoost model training (target alignment, feature engineering)
│   ├── trainer_v60_xgb.py   ← v60 XGBoost training wrapper
│   └── physics_auditor.py   ← Self-auditing physics validation
│
├── pipeline/                ← Pipeline framework
│   ├── engine/framer.py     ← Frame construction engine
│   ├── adapters/v3_adapter.py
│   ├── interfaces/math_core.py
│   └── config/              ← Hardware config, loader
│
├── tools/                   ← ★ OPERATIONAL SCRIPTS (v61 focus)
│   ├── v61_linux_framing.py       ← Sharded framing agent (Linux, Anti-Fragile Edition)
│   ├── v61_windows_framing.py     ← Sharded framing agent (Windows)
│   ├── v61_run_local_backtest.py  ← v61 local backtester
│   ├── v60_swarm_xgb.py          ← Optuna hyperparameter sweep
│   ├── v60_forge_base_matrix_local.py ← Base matrix builder (local)
│   ├── v60_autopilot.py          ← Distributed autopilot orchestrator
│   ├── run_vertex_xgb_train.py   ← Vertex AI training submission
│   ├── build_7z_shards.py        ← 7z archive sharding utility
│   └── run_v61_framing_detached.bat ← Windows launcher
│
├── tests/                   ← Test suite
│   ├── test_sharding_v61.py      ← Sharding determinism tests
│   ├── verify_v61_pipeline.py    ← v61 pipeline verification
│   ├── test_kernel_srl_numba.py  ← Kernel SRL physics tests
│   ├── test_math_core.py         ← Math primitives tests
│   └── ...
│
└── audit/                   ← ★ ARCHITECTURE DECISIONS & BUG ANALYSIS
    ├── v61.md               ← Chief Architect audit: 4 fatal ML bugs identified
    ├── v61_fix.md           ← Surgical patch directives (Data Bleeding fixes)
    ├── v61_vertex_guide.md  ← Vertex AI deployment guide
    └── 20260221_linux_crash_root_cause.md ← ZFS+cgroup memory deadlock analysis
```

## 🔬 Key Areas for Audit

### 1. Physics Engine (`omega_core/kernel.py`)

- **SRL (Square Root Law)** residual computation — is the sign correct for A-share momentum?
- **Epiplexity** computation — topological dimension reduction
- **Cross-symbol isolation**: `syms[i] != syms[i-1]` boundary detection (line ~203)
- **Zero-copy extraction**: `.cast().to_numpy()` vs `.to_list()` for nested lists

### 2. ETL Pipeline (`omega_core/omega_etl.py`)

- All `.cum_sum()`, `.rolling_mean()` must have `.over("symbol")` for multi-symbol batches
- Anti-aliasing low-pass filter: `rolling_mean(window_size=3)` on `v_ofi`/`depth`
- Volume clock bucketing with dynamic bucket sizes

### 3. ML Training (`omega_core/trainer.py`, `tools/v60_swarm_xgb.py`)

- Target variable: should use **excess return** (subtract cross-sectional mean), not absolute return
- Optuna sweep: `min_samples` guard to prevent dataset collapse (2067 rows from 5.7M)
- Feature engineering: XGBoost should see broad manifold, not memorized outliers

### 4. Distributed Framing (`tools/v61_*_framing.py`)

- `POLARS_MAX_THREADS=8` to prevent thread explosion
- Deterministic sharding: `md5(filename) % total_shards`
- Atomic parquet writes (`.tmp` → rename)

## 🧬 Version History Context

- **v5.2**: Single-symbol physics, manual hyperparameters
- **v6.0**: Multi-symbol batching, Vertex AI cloud training, Optuna sweep
- **v6.1**: Anti-fragile patches — fixed data bleeding, momentum sign, excess return target, anti-aliasing
