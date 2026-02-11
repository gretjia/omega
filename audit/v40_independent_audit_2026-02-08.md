# v40 Independent Audit Report (Math + Engineering)

Date: 2026-02-08  
Auditor: Codex (independent pass)  
Scope:
- v40 design intent: `audit/v40_race_patch.md`, `audit/v40_race_patch_02.md`
- v40 implementation: `config.py`, `omega_v3_core/*`, `parallel_trainer/*`, `tools/run_l2_audit_driver.py`
- engineering constraints: `.agent/principles.yaml` + always-on skills (`math_core`, `engineering`, `v3_mainline_guard`, `hardcode_guard`, `ops`)

## 1) Executive Verdict

Status: **CONDITIONAL PASS**

- 数学主干总体与 v40 设计方向对齐（LZ76-only 主核、SRL 多幂次赛道、Topology 多流形、Sigma 能量门控、Anchor-Y 递归）。
- 工程主干总体对齐（代码落位在 `omega_v3_core/*`，并行 frame/train/backtest 支持状态快照与续作）。
- 但存在 **2 个 P1 问题**（会影响可审计性/可复现性/评估可信度），建议在正式全量训练前修复。

---

## 2) Findings (Ordered by Severity)

### [P1] 回测收益被固定阈值裁剪，影响赛马结论可信度
- Evidence: `parallel_trainer/run_parallel_backtest_v31.py:145`
- Current behavior:
  - `ret_k_clipped = np.clip(ret_k, -0.02, 0.02)`
- Why this is a problem:
  - 该阈值是业务结果相关阈值，不是纯数值稳定常数；会直接改变 PnL、交易评价与赛马对比。
  - 与“无硬编码交易阈值”原则不一致（`.agent/principles.yaml:21`, `.agent/principles.yaml:31`, `.agent/skills/hardcode_guard/SKILL.md:12`）。
- Recommendation:
  - 将回测裁剪阈值迁移到 `config.py`（例如 `L2TrainConfig` 或 `L2ValidationConfig`），默认关闭或由审计快照注入。
  - 在报告中打印“是否启用裁剪+阈值来源”，避免隐式影响结论。

### [P1] 先验学习流程非确定性，导致同数据重复运行不稳定
- Evidence:
  - `omega_v3_core/physics_auditor.py:138` (`random.sample`)
  - `omega_v3_core/physics_auditor.py:281` (`random.sample`)
  - `omega_v3_core/physics_auditor.py:287` (`random.shuffle`)
  - `omega_v3_core/physics_auditor.py:333`
- Why this is a problem:
  - `PLANCK_SIGMA_GATE` 与 `ANCHOR_Y` 是要进入运行期配置的关键先验；非确定性会削弱“版本可追溯、跨 AI 一致复现”。
  - 与可复现性要求有冲突（`.agent/principles.yaml:36`）。
- Recommendation:
  - 增加 `audit_seed` 配置并统一用于 sample/shuffle。
  - 将 seed 与 sample file list 一并写入 `production_config.json`。

### [P2] Renormalization 评分惩罚系数硬编码在审计器内
- Evidence: `omega_v3_core/physics_auditor.py:226`（`ortho > 0.3 -> penalty 0.5`）
- Why this is a problem:
  - 该规则会影响 best-scale 选择，属于影响主流程参数晋升的策略常数。
  - 目前未进入 config 或审计产物，不利于跨版本解释。
- Recommendation:
  - 抽到 config（例如 `L2ValidationConfig`/新建审计配置项），并记录到导出的审计配置中。

### [P2] `ops` 技能文档与当前 v40 并行流程存在漂移
- Evidence:
  - `.agent/skills/ops/SKILL.md:13-24` 仍以 `tools/run_v3_training.py`、`run_l2_audit.py` 为主入口
  - 当前 v40 主执行链已是 `parallel_trainer/run_parallel_v31.py`、`parallel_trainer/run_parallel_backtest_v31.py`、`jobs/windows_v40/start_v40_pipeline_win.ps1`
- Why this is a problem:
  - 新 AI 可能按旧入口执行，影响日志统一与续作机制。
- Recommendation:
  - 更新 `ops` skill：将 v40 并行入口和 `audit/v40_runtime/windows/*` 状态路径列为优先流程。

---

## 3) Alignment Matrix (v40 Design vs Implementation)

### 3.1 Epiplexity (LZ76 winner, pure math + no manual patch)
- Design reference: `audit/v40_race_patch.md`（LZ76 胜出）+ `audit/v40_race_patch_02.md:224-243`（去除 `r<0.15` 手工惩罚，改由能量门控）
- Implementation:
  - `omega_v3_core/omega_math_core.py:34-38` (`calc_epiplexity -> calc_epiplexity_lz76`)
  - `omega_v3_core/omega_math_core.py:98-117` 线性 LZ76 输出
  - `omega_v3_core/kernel.py:89-93` 低能量帧走 `fallback_value`
- Verdict: **Aligned**

### 3.2 SRL race (0.33/0.5/0.66) + anti-spoof effective depth
- Design reference: `audit/v40_race_patch.md` SRL 多幂次赛道
- Implementation:
  - `config.py:574-576` race exponents + lane names
  - `omega_v3_core/omega_math_core.py:206-264` lane residuals + implied Y
  - `omega_v3_core/omega_math_core.py:228-235` spoof ratio -> effective depth penalty
- Verdict: **Aligned**

### 3.3 Topology race (Micro/Classic/Trend) + denominator guards
- Design reference: `audit/v40_race_patch.md` Topology 三流形；`audit/v40_race_patch_02.md` 分母陷阱防护
- Implementation:
  - ETL traces: `omega_v3_core/omega_etl.py:328-330`
  - Topology race config: `config.py:619-635`
  - Runtime compute: `omega_v3_core/kernel.py:104-125`
  - Denominator floors: `omega_v3_core/omega_math_core.py:326-332`
- Verdict: **Aligned**

### 3.4 Energy gate + anchor prior (zero hard-coding direction)
- Design reference: `audit/v40_race_patch_02.md:144-158`, `:246-269`
- Implementation:
  - energy gate switch/threshold: `config.py:608-610`, `omega_v3_core/kernel.py:89-93`
  - anchor recursion: `config.py:589-592`, `omega_v3_core/kernel.py:163-165`
  - priors derivation: `omega_v3_core/physics_auditor.py:124-205`
  - runtime load: `config.py:774-809`
- Verdict: **Aligned (with reproducibility caveat from P1)**

### 3.5 Mainline placement & compatibility discipline
- Skill requirement: `.agent/skills/v3_mainline_guard/SKILL.md:12-23`
- Implementation:
  - 本次核心逻辑集中在 `omega_v3_core/*` 与执行适配层 `parallel_trainer/*`、`tools/*`
  - 未见将业务逻辑回灌到根 shim 的证据
- Verdict: **Aligned**

### 3.6 Ops resilience (logging/resume/monitoring)
- Requirement: `.agent/skills/ops/SKILL.md:30-33`（日志可审计）
- Implementation:
  - train status/checkpoint: `parallel_trainer/run_parallel_v31.py:177-194`, `:239-261`
  - backtest status/state: `parallel_trainer/run_parallel_backtest_v31.py:214-235`, `:256-273`
  - frame status: `tools/run_l2_audit_driver.py:298-311`, `:356-372`
- Verdict: **Aligned**

---

## 4) Independent Verification Executed

1. Recursive audit script:
- Command: `./.venv/bin/python tools/v40_recursive_audit.py`
- Result: **PASS** (cfg invariants, runtime smoke, energy-gate smoke)

2. Syntax sanity:
- Command: `./.venv/bin/python -m py_compile ...`
- Result: **PASS**（核心相关文件编译通过）

3. README sync gate:
- Command: `python3 tools/check_readme_sync.py`
- Result: **PASS**

---

## 5) Release Gate Recommendation (Before Full v40 Training)

必须修复后再全量训练（Gate-Blockers）：
1. P1: `ret_k` 裁剪阈值配置化并可审计（移除硬编码 `±0.02`）。
2. P1: 先验学习流程加确定性 seed 与样本记录。

可并行修复（非阻塞但建议）：
1. P2: renorm penalty 常数配置化。
2. P2: 更新 `ops` skill 到 v40 并行主流程。

---

## 6) Final Audit Conclusion

v40 升级在数学框架上已经形成可运行闭环，且与设计文档主方向基本一致。  
当前主要风险不在“数学是否实现”，而在“审计可复现性与评估阈值透明性”。  
完成上述两个 P1 后，建议进入下一轮正式训练与回测。
