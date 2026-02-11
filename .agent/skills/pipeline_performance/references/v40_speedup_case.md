# v40 Speedup Case (Reusable Engineering Highlights)

## 背景

本次提速任务不是“单点调参”，而是分两轮推进：
1. I/O 优化前的整体工程优化（CPU/调度/对象生命周期/列裁剪/线程治理）
2. I/O 拓扑优化（staging、copy/extract 节流、chunk 策略、日志与续作）

核心原则：先 CPU/工程、再 I/O、最后才考虑 GPU。

## 核心软件工程要素

### 1) 约束先行（Guardrails-First）
1. 数学核心不变：优化只触及执行层，不改公式语义。
2. 质量不降：用固定 split 与一致性指标做前后对照。
3. fail-closed：train/backtest 数据分离和 overlap 检测默认强制。

### 2) 证据驱动（Evidence-First）
1. 先冻结 baseline，再做修改，避免“感觉优化”。
2. 指标统一：frame 看 archives/hour，train 看 rows/s，backtest 看 files/s + 审计状态。
3. 决策由真实运行报告驱动，不由主观偏好驱动。

### 3) 性能与可靠性一体化（Perf = Throughput + Recoverability）
1. 高吞吐不等于可生产：必须配套状态写盘、断点续作、可监控日志。
2. 假死常见根因是“无心跳 + 长 I/O 阶段”；需通过 status/log 频率治理降低误判。
3. 原子写 + 重试是 Windows 共享盘环境的必要条件。

### 4) 分层优化顺序（Less Is More）
1. 先做低风险高收益项（worker 复用、chunksize、列裁剪、线程治理）。
2. 再做 I/O 拓扑（staging + chunk + cleanup），避免共享盘抖动。
3. GPU 不应提前介入主链路，避免把“工程问题”误当“算力问题”。

## 亮点沉淀（可复用）

1. **Phase 化治理**：每阶段收口一次，避免长上下文导致失控。
2. **双闭环验证**：
   - 工程闭环：吞吐、稳定性、续作
   - 业务闭环：PnL + 物理审计指标
3. **统一入口脚本**：把参数、路径、清理策略、split 策略写死到可复用 wrapper，减少人因错误。
4. **默认安全策略**：默认 staging、默认 cleanup、默认 fail-closed、默认 resume。
5. **跨机器可观测性**：日志/状态固定路径，Mac 可实时观察 Windows 运行状态。

## 常见反模式（后续避免）

1. 先大规模并发再查 I/O 拥塞（顺序颠倒）。
2. 只看速度不看质量（导致“快但错”）。
3. 只看日志不看状态文件（误判运行阶段）。
4. 在共享盘环境下忽略原子写和写冲突重试。
5. 将 GPU 当作第一响应，而不是最后增量。

## 推荐复用模板

每次提速任务都按以下顺序复用：
1. Baseline snapshot
2. Phase 1（CPU/工程）
3. Phase 2（I/O）
4. Smoke + fullrun
5. Recursive audit
6. Handover + README sync
