# OMEGA v5.0 Product Guidelines

## 1. 数学核心开发规范 (Math Core Development)
- **防御性纯函数 (Defensive Pure Functions)**：
    - 所有数学算子必须是无状态的（Stateless）。
    - 必须包含严格的输入校验（`NaN`/`Inf` 检查）和物理边界约束（如 `sigma_floor`, `depth_floor`）。
- **公式可读性 (Formula Readability)**：
    - 代码结构应优先镜像数学公式，使用清晰的变量命名（如 `srl_resid`, `epiplexity`）。
    - 复杂逻辑需附带简短的理论引用注释（如 `Sato 2025`）。

## 2. 并行与稳定性 (Parallelism & Stability)
- **可观测性 (Observability)**：
    - 并行 Worker 必须强制执行 `print(..., flush=True)` 以确保 Windows 环境下的日志实时性。
    - 使用统一的时间戳格式记录日志。
- **无死锁设计 (Deadlock Prevention)**：
    - 严禁 Worker 间使用复杂锁机制，优先使用磁盘 Checkpoint 或 IPC 状态同步。
- **确定性 (Determinism)**：
    - 严禁使用未播种的随机函数。所有随机过程必须由 `configs/` 中的 `seed` 驱动，确保结果 100% 可重现。
- **资源安全 (Resource Safety)**：
    - 必须集成内存门控机制，在资源紧张时主动降速或挂起。

## 3. 架构与数据合约 (Architecture & Data Contracts)
- **显式模式 (Explicit Schemas)**：
    - 严禁传递不透明的字典。使用 Pydantic 或 Dataclasses 定义组件间的通信合约。
- **零硬编码 (Zero Hardcoding)**：
    - 核心算法内部严禁定义默认参数。所有阈值和超参数必须从 `configs/` 加载。
- **阶段解耦 (Stage Decoupling)**：
    - `frame` -> `train` -> `backtest` 必须物理隔离。各阶段通过标准化的磁盘 Artifacts 交换数据。
- **鲁棒错误处理 (Robust Error Handling)**：
    - 必须捕获 Worker 异常的完整 `traceback` 并记录至专属 `.err` 文件。

## 4. 宪法与技能遵循 (Constitutional Compliance)
- 所有工程实现必须对齐 `OMEGA_CONSTITUTION.md` 的三位一体原则。
- 遵循 `parallel-backtest-debugger.skill` 中积累的 6 大避坑指南（如 Zombie 进程清理、`ret_k` 显式校验等）。
