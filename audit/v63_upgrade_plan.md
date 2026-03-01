# V63 "The Epistemic Release" 升级计划 (Plan Mode)

## 1. 升级目标
严格贯彻首席量化架构师对于 V63（Kolmogorov-Sato Separation）的数学内核演进要求。将物理学的严谨性转化为图灵安全的机器代码。

## 2. 核心数学修正 (The Mathematical Patches)
本次升级包含三个核心的理论闭环修复：
1.  **等周定理的拓扑闭环 (Isoperimetric Perimeter Closure)**：在计算 `Q_topo` 时，不仅需要面积闭合，周长也必须严格闭合（补充 `dx_close`, `dy_close`），以修复趋势行情下拓扑商被系统性高估的物理破缺。
2.  **拓扑预热掩码 (Topology Warm-Up Mask)**：引入 `srl_is_active` 掩码。解决微观状态机中“数据不足（NULL）”与“布朗运动（0）”的混淆问题，保护物理基线的因果时间箭头，防止开盘集合竞价的未校准高波动污染 Sato 参数 $Y$。
3.  **废除 `fastmath` (Turing Fundamentalism)**：剥离 Numba 中的 `fastmath=True` 编译优化，强制恢复严格的 IEEE-754 浮点运算结合律。彻底消除底层多线程浮点漂移导致的状态机分叉，保证 bit-for-bit 的绝对确定性。
4.  **维持并行并发 (Retain Parallelism)**：明确 `parallel=True` 在无跨线程约化变量（Cross-thread reduction）时是绝对图灵安全的，继续保留以榨干 AMD AI Max 的多核算力。

## 3. 实施步骤与动作列表 (Execution Steps)

### 阶段 1：数学核心重写 (The Numba Kernels)
*   **目标文件**：`omega_core/omega_math_rolling.py`
*   **动作**：
    *   覆写 `calc_isoperimetric_topology_rolling`。移除 `fastmath`，补齐周长的闭环项 (`dx_close` / `dy_close`)。
    *   覆写 `calc_residual_epiplexity_rolling`。移除 `fastmath`。

### 阶段 2：状态机逻辑反转 (The Inverted Turing Machine)
*   **目标文件**：`omega_core/omega_math_vectorized.py`
*   **动作**：
    *   引入新的核心算子 `calc_srl_recursion_loop_v63`（替换原有的 `calc_srl_recursion_loop`）。
    *   注入拓扑门控逻辑：仅在 `out_q_topo < chaos_threshold` 且 `srl_is_active` 有效时更新 Sato 参数 $Y$。

### 阶段 3：因果路由图装配 (Causal Routing Injection)
*   **目标文件**：`omega_core/kernel.py`
*   **动作**：
    *   在 `_apply_recursive_physics` 函数内，重构数学算子的调用链。
    *   顺序必须是：Topology -> Warm-up Masking -> SRL Recursion -> Residual MDL。

### 阶段 4：全局去版本化清理 (Version Agnosticism)
*   **目标文件**：项目内所有的 Markdown 报告、文档、配置文件和脚本名。
*   **动作**：
    *   执行全局正则扫描，将散落在文档和变量名中的特定硬编码版本号（如 v52, v60, v61, v62）统一清除或替换为泛用的动态名称（如 `current_version`, `latest`）。防止后续 V63、V64 迭代时持续遭遇版本号污染与命名空间地雷。
    *   仅在必要的文件内（如 `config.py`）保留一个单一的 Source of Truth。

### 阶段 5：独立特工审计 (Recursive AI Audit)
*   **动作**：计划落成后，启动一个独立的 Gemini CLI 子进程（Auditor Agent）。将架构师的指令与实施后的代码进行 Diff 比对，确保 100% 字节级对齐，没有遗漏任何一个负号或缩进。