# OMEGA v5.0: The Holographic Damper

> **"Physics is invariant. Structure is emergent. The observer is bounded."**

OMEGA v5.0 represents the convergence of **Universal Market Physics** (Sato 2025) and **Computational Information Theory** (Finzi 2026). It abandons empirical parameter tuning in favor of deriving trading signals from first principles: the universality of the Square-Root Law and the compressibility of market data.

---

## 核心哲学 (The Theoretical Pillars)

1.  **The Universal Law (Sato 2025)**
    *   **Principle:** The price impact exponent $\delta$ is **strictly 0.5**.
    *   **Action:** Removed "SRL Race". Hardcoded $\delta = 0.5$.
    *   **Implied Y:** We invert the law ($Y = \frac{\Delta P}{\sigma \sqrt{Q/D}}$) to measure the instantaneous "rigidity" of the market structure.

2.  **Epiplexity as Compression Gain (Finzi 2026)**
    *   **Principle:** Complexity is not randomness. Structure is defined by the ability of a bounded observer (Linear Model) to outperform a naive observer (Mean).
    *   **Metric:** $Gain = 1 - \frac{Var(Residuals)}{Var(Total)}$.
    *   **Action:** Replaced LZ76 with Compression Gain. High Gain = High Structure = Actionable Signal.

3.  **The Holographic Damper**
    *   **Problem:** Updating internal state ($Y$) during noise (Low Epiplexity) causes model drift.
    *   **Solution:** A gating mechanism. The model only learns/updates when Epiplexity > Threshold.
    *   **Metaphor:** A damper that stiffens when it hits a solid object (Structure) but remains loose in air (Noise).

4.  **Causal Volume Projection (Paradox 3 Fix)**
    *   **Fix:** Volume buckets are now sized by linearly extrapolating current cumulative volume based on elapsed time. This eliminates look-ahead bias found in v40.
    *   **Implementation:** `omega_etl.py` now strictly enforces time-sorting of slices to ensure `cum_vol` is monotonic and causal.

---

## 系统架构 (v5.0 Architecture)

OMEGA v5.0 adopts a **Modular Pipeline Architecture**, separating Configuration, Logic, and Execution.

```mermaid
graph TD
    Config[configs/*.yaml] --> Runner[pipeline_runner.py]
    Runner --> Pipeline[pipeline/]
    
    subgraph "The Engine (pipeline/)"
        Adapter[adapters/OmegaCoreAdapter] --> Interface[interfaces/IMathCore]
        Framer[engine/framer.py] --> Adapter
    end
    
    subgraph "The Core (omega_core/)"
        Kernel[kernel.py] --> Math[omega_math_core.py]
        ETL[omega_etl.py] --> Math
    end
    
    Framer -- Calls --> Kernel
```

### 目录结构 (Directory Structure)

*   **`pipeline/`**: **The Execution Engine.**
    *   `config/`: Pydantic/Dataclass schemas for Hardware & Model.
    *   `interfaces/`: Abstract Base Classes (IMathCore) for future-proofing.
    *   `adapters/`: Glue code that binds `omega_core` to the pipeline.
    *   `engine/`: The logic for Framing, Training, and Backtesting.
*   **`omega_core/`**: **The Math Core (v5.0).**
    *   `omega_math_core.py`: Pure physics formulas (SRL 0.5, Compression Gain).
    *   `kernel.py`: The Holographic Damper logic.
    *   `trainer.py`: SGD Online Learning implementation (Multi-Symbol Aware).
*   **`configs/`**: **Configuration as Code.**
    *   `hardware/`: Hardware profiles (e.g., `active_profile.yaml`).
*   **`parallel_trainer/`**: **High-Performance Driver.**
    *   Legacy-compatible multiprocessing drivers for Training/Backtesting.
*   **`archive/`**: Legacy v1/v3/v40 code that is no longer active.

---

## 快速开始 (Quick Start)

多机代码发布入口（Mac 一键推送并触发 Windows1/Windows2 更新）：
- `tools/git_sync/mac_publish_and_rollout.sh`
- 细则见下方 `9. Mac 一键代码发布到 Windows1/Windows2`

### 1. 配置硬件
OMEGA v5.0 自动检测硬件配置。首次运行会自动生成默认配置：
```bash
python pipeline_runner.py
```
编辑 generated `configs/hardware/active_profile.yaml` to match your paths (e.g., Source on E:, Stage on D:).

### 2. 执行 Framing (Smoke Test)
验证管道是否连通：
```bash
python pipeline_runner.py --stage frame --smoke
```

### 3. 全量 Framing (Phase 1)
```bash
python pipeline_runner.py --stage frame
```
*Note: This process runs massively parallel (48+ workers) and groups data by symbol to ensure Volume Clock integrity.*

### 4. 训练 (Phase 2)
```bash
python parallel_trainer/run_parallel_v31.py --stage-dir D:/Omega_train_stage
```
*Note: Ensure `D:/Omega_train_stage` exists for high-speed IO.*

### 5. 回测 (Phase 3)
```bash
python parallel_trainer/run_parallel_backtest_v31.py
```

### 6. Mac 主控 SSH（Windows_1）
已验证可从 Mac 无交互连接 Windows_1（仅连通 smoke，不触发 framing/train/backtest）。

Windows_1:
- Hostname: `DESKTOP-41JIDL2`
- User: `jiazi`
- IP: `192.168.3.112`

Mac `~/.ssh/config` 固化条目：
```sshconfig
Host windows1-w1
    HostName 192.168.3.112
    User jiazi
    BindAddress 192.168.3.49
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    PreferredAuthentications publickey
    StrictHostKeyChecking accept-new
    ConnectTimeout 8
```

连通 smoke:
```bash
ssh windows1-w1 "hostname && whoami"
```

说明：当前 Mac 存在双网卡同网段场景，需绑定源地址（`BindAddress 192.168.3.49`）以避免偶发 `No route to host`。

### 7. Windows_1 后台训练与实时监控（v5）
当前已固化 detached 训练脚本：`audit/v5_runtime/windows/train/run_train_detached.ps1`。

1) 在 Mac 侧同步脚本到 Windows_1：
```bash
scp audit/v5_runtime/windows/train/run_train_detached.ps1 windows1-w1:/C:/Omega_vNext/audit/v5_runtime/windows/train/run_train_detached.ps1
```

2) 首次创建计划任务（只需一次）：
```bash
ssh windows1-w1 "cmd /c schtasks /Create /TN OmegaTrainDetached /SC ONCE /ST 00:00 /TR \"powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\\Omega_vNext\\audit\\v5_runtime\\windows\\train\\run_train_detached.ps1\" /RL HIGHEST /F"
```

3) 每次启动训练（脱离 SSH 会话）：
```bash
ssh windows1-w1 "cmd /c schtasks /Run /TN OmegaTrainDetached"
```

4) 监控进度（Mac 侧随时执行）：
```bash
ssh windows1-w1 "powershell -NoProfile -Command \"Get-Content 'C:\\Omega_vNext\\audit\\v5_runtime\\windows\\train\\train_status.json'\""
ssh windows1-w1 "powershell -NoProfile -Command \"Get-Content 'C:\\Omega_vNext\\audit\\v5_runtime\\windows\\train\\train.log' -Tail 40\""
ssh windows1-w1 "powershell -NoProfile -Command \"Get-Process -Name python -ErrorAction SilentlyContinue | Select-Object Id,StartTime,CPU,WorkingSet64 | Format-Table -AutoSize\""
```

5) 快速判定是否异常退出：
```bash
ssh windows1-w1 "powershell -NoProfile -Command \"if (Test-Path 'C:\\Omega_vNext\\audit\\v5_runtime\\windows\\train\\train_exit_code.txt') { Get-Content 'C:\\Omega_vNext\\audit\\v5_runtime\\windows\\train\\train_exit_code.txt' } else { 'RUNNING' }\""
```

6) 已验证的稳定参数（CPU 训练）：
- `workers=8`
- `batch_rows=750000`
- `checkpoint_rows=1500000`
- `stage_dir=D:/Omega_train_stage`
- `stage_chunk_files=16`
- `stage_copy_workers=4`
- 断点续跑开启（不使用 `--no-resume`）

### 8. Windows_1 后台回测与实时监控（v5）
当前已固化 detached 回测脚本：`audit/v5_runtime/windows/backtest/run_backtest_detached.ps1`。

1) 在 Mac 侧同步脚本到 Windows_1：
```bash
scp audit/v5_runtime/windows/backtest/run_backtest_detached.ps1 windows1-w1:/C:/Omega_vNext/audit/v5_runtime/windows/backtest/run_backtest_detached.ps1
```

2) 首次创建计划任务（只需一次）：
```bash
ssh windows1-w1 "cmd /c schtasks /Create /TN OmegaBacktestDetached /SC ONCE /ST 00:00 /TR \"powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\\Omega_vNext\\audit\\v5_runtime\\windows\\backtest\\run_backtest_detached.ps1\" /RL HIGHEST /F"
```

3) 每次启动回测（脱离 SSH 会话）：
```bash
ssh windows1-w1 "cmd /c schtasks /Run /TN OmegaBacktestDetached"
```

4) 监控回测进度：
```bash
ssh windows1-w1 "powershell -NoProfile -Command \"Get-Content 'C:\\Omega_vNext\\audit\\v5_runtime\\windows\\backtest\\backtest_status.json'\""
ssh windows1-w1 "powershell -NoProfile -Command \"Get-Content 'C:\\Omega_vNext\\audit\\v5_runtime\\windows\\backtest\\backtest.log' -Tail 60\""
ssh windows1-w1 "powershell -NoProfile -Command \"if (Test-Path 'C:\\Omega_vNext\\audit\\v5_runtime\\windows\\backtest\\backtest_exit_code.txt') { Get-Content 'C:\\Omega_vNext\\audit\\v5_runtime\\windows\\backtest\\backtest_exit_code.txt' } else { 'RUNNING' }\""
```

5) 审计门控说明：
- 默认 `fail_on_audit_failed=true`。
- 若最终 `FINAL AUDIT STATUS: FAILED`，进程会以 `exit code 1` 退出（属于策略审计失败，不是进程崩溃）。
- 若希望回测始终产出报告但不因审计失败返回非零，可在脚本参数中加入 `--allow-audit-failed`。

### 9. Mac 一键代码发布到 Windows1/Windows2（推荐）

目标：避免手工复制粘贴，仅同步代码，不同步 `data/`、`artifacts/` 等大目录。

#### 9.1 一次性初始化（Windows1 执行）

1) 在 `Windows1` 建立 bare hub：
```powershell
powershell -ExecutionPolicy Bypass -File tools\git_sync\windows_init_hub.ps1 `
  -SourceRepoPath C:\Omega_vNext `
  -BareHubPath C:\Git\Omega_vNext.git `
  -RemoteName hub
```

2) `Mac` 配置 hub 远端（已存在则 `set-url`）：
```bash
git remote add hub "ssh://<user>@windows1/C:/Git/Omega_vNext.git"
```

3) `Windows2` 首次克隆：
```powershell
git clone "ssh://<user>@windows1/C:/Git/Omega_vNext.git" C:\Omega_vNext
cd C:\Omega_vNext
git remote rename origin hub
```

#### 9.2 SSH 主机别名（Mac `~/.ssh/config`）

至少配置两个目标主机（示例）：
```sshconfig
Host windows1-w1
    HostName 192.168.3.112
    User jiazi
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new

Host windows2-w2
    HostName <windows2_ip>
    User <windows2_user>
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new
```

#### 9.3 日常一键发布（Mac 执行）

默认发布当前分支到 `hub`，并依次远程执行 `windows_update_from_hub.ps1`：
```bash
./tools/git_sync/mac_publish_and_rollout.sh --remote hub --branch main
```

带版本标签发布：
```bash
./tools/git_sync/mac_publish_and_rollout.sh --remote hub --branch main --tag v2026.02.12-r2
```

指定目标主机列表：
```bash
./tools/git_sync/mac_publish_and_rollout.sh --remote hub --branch main --hosts windows1-w1,windows2-w2
```

#### 9.4 仅在 Windows 单机更新（手工兜底）

```powershell
powershell -ExecutionPolicy Bypass -File tools\git_sync\windows_update_from_hub.ps1 `
  -RepoPath C:\Omega_vNext `
  -RemoteName hub `
  -Branch main
```

#### 9.5 使用约束（必须遵守）

- Git 仅管理代码、配置、脚本、文档。
- `data/`、`artifacts/`、运行日志保持本地，不进入版本库。
- 发布以 `main`/tag 为准，Windows 侧不要直接在生产目录做临时提交后长期不推送。

---

## 关键文档 (Documentation)

*   **[audit/v5_explain.md](audit/v5_explain.md)**: v5.0 的详细解释文档（理论背景与代码实现）。
*   **[audit/OMEGA_NextGen_Architecture_Plan.md](audit/OMEGA_NextGen_Architecture_Plan.md)**: 未来架构演进路线图。
*   **[audit/v40_storage_estimation_2020_2026.md](audit/v40_storage_estimation_2020_2026.md)**: 存储规划指南。
*   **[docs/git_multi_machine_hub.md](docs/git_multi_machine_hub.md)**: Mac + Windows1 + Windows2 代码同步/发布规范（避免手工复制粘贴）。
*   **[omega_core/README.md](omega_core/README.md)**: Core 数学内核说明。
*   **[parallel_trainer/README.md](parallel_trainer/README.md)**: 并行训练/回测执行说明。
*   **[rq/README.md](rq/README.md)**: RQ 相关模块说明。

## Agent Skills Index

*   [.agent/skills/ai_handover/SKILL.md](.agent/skills/ai_handover/SKILL.md)
*   [.agent/skills/config_promotion_protocol/SKILL.md](.agent/skills/config_promotion_protocol/SKILL.md)
*   [.agent/skills/data_download/SKILL.md](.agent/skills/data_download/SKILL.md)
*   [.agent/skills/data_integrity_guard/SKILL.md](.agent/skills/data_integrity_guard/SKILL.md)
*   [.agent/skills/engineering/SKILL.md](.agent/skills/engineering/SKILL.md)
*   [.agent/skills/evidence_based_reasoning/SKILL.md](.agent/skills/evidence_based_reasoning/SKILL.md)
*   [.agent/skills/evolution_knowledge/SKILL.md](.agent/skills/evolution_knowledge/SKILL.md)
*   [.agent/skills/hardcode_guard/SKILL.md](.agent/skills/hardcode_guard/SKILL.md)
*   [.agent/skills/innovation_sandbox/SKILL.md](.agent/skills/innovation_sandbox/SKILL.md)
*   [.agent/skills/math_consistency/SKILL.md](.agent/skills/math_consistency/SKILL.md)
*   [.agent/skills/math_core/SKILL.md](.agent/skills/math_core/SKILL.md)
*   [.agent/skills/multi_agent_rule_sync/SKILL.md](.agent/skills/multi_agent_rule_sync/SKILL.md)
*   [.agent/skills/omega_data/SKILL.md](.agent/skills/omega_data/SKILL.md)
*   [.agent/skills/omega_development/SKILL.md](.agent/skills/omega_development/SKILL.md)
*   [.agent/skills/omega_engineering/SKILL.md](.agent/skills/omega_engineering/SKILL.md)
*   [.agent/skills/ops/SKILL.md](.agent/skills/ops/SKILL.md)
*   [.agent/skills/parallel-backtest-debugger/SKILL.md](.agent/skills/parallel-backtest-debugger/SKILL.md)
*   [.agent/skills/physics/SKILL.md](.agent/skills/physics/SKILL.md)
*   [.agent/skills/pipeline_performance/SKILL.md](.agent/skills/pipeline_performance/SKILL.md)
*   [.agent/skills/qmtsdk/SKILL.md](.agent/skills/qmtsdk/SKILL.md)
*   [.agent/skills/rqsdk/SKILL.md](.agent/skills/rqsdk/SKILL.md)
*   [.agent/skills/v3_mainline_guard/SKILL.md](.agent/skills/v3_mainline_guard/SKILL.md)

---

> **Note:** v40 Frames are **NOT COMPATIBLE** with v5.0 due to the Paradox 3 fix. Please re-run framing.
