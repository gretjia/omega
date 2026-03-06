# V64 审计演化总览

## 目的

这份文档把 V64 从最初的架构师直觉，到审计师逐轮压缩问题空间，再到最终放行的全过程串成一条清晰脉络。重点不是罗列版本号，而是回答 5 个问题：

1. 第一版架构师到底想做什么
2. 第一轮审计抓住了什么根本问题
3. 我们如何把“哲学直觉”改造成“可证明、可运行、可测试”的主链
4. 后续审计又把哪些残留问题继续压缩出来
5. 最终为什么能签字放行

---

## 一页结论

V64 的真实演化逻辑，不是“连续加 patch”，而是一次逐步收敛的范式迁移：

- `V64.0`：架构师提出“压缩即智能”，想把 `Topology + Epiplexity + SRL` 熔铸成单一主力探测引擎。
- `第一次严格审计`：指出工程实现背叛了这个哲学，尤其是伪奇点、几何破缺、门控混用、量纲错误。
- `V64.1 / V64.2`：系统从“残差对时间的线性探针”切换到“SRL 残差相对原始价格波动的压缩率”，并把修复从内核一路打通到 `config / docs / tests`。
- `V64.2 二次审计`：继续指出 repo 级仍未完全单义化，尤其是 `Δk`、`bits_srl`、`has_singularity -> srl_resid = 0` 这类残留问题。
- `V64.3`：完成最后三根毒刺的切除，收敛成单一 canonical runtime math core。
- `最终放行`：审计师撤回最后 3 个 blocker，确认当前主运行数学链已经闭合；剩余只是一点非阻断的 legacy 命名债务。

工程验证上，V64.3 还额外经历了一次 `backtest` 停滞修复。最终 isolated smoke 通过了：

- `Stage 2`
- `forge / base matrix`
- `training`
- `backtest`

所以最终通过，不是只靠“数学解释变漂亮”，而是：

- 数学主链闭合
- 配置/文档/测试口径一致
- 工程链路真实跑通

---

## 版本脉络总表

| 阶段 | 核心主张 / 发现 | 关键问题 | 采取动作 | 结果 |
| --- | --- | --- | --- | --- |
| `V64.0` 初始架构 | 压缩即智能；Topology + Epiplexity + SRL 三位一体 | 实现里用工程 hack 扭曲了原理 | 架构师提出彻底重构方向 | 给出大方向，但还没闭合 |
| `v64.md` Bourbaki Synthesis / Closure | 接受外部审计的四个硬伤 | 伪奇点、几何破缺、门控混用、量纲错误 | 改 rolling gain、改 kernel 门控、改 config、加回归测试 | 主运行路径接近正确 |
| `v642.md` 审计 | “比上一版强很多，但不签 absolute closure” | 同名不同义、`Δk` 未证明、`bits_srl` 双重压缩、`srl_resid` 被覆写 | 从 repo 级统一定义、补内核级测试、继续收口 docs/config | 从“修硬伤”进入“定义统一” |
| `v643.md` 最终 override | 最后 3 个 blocker 直接点名 | `Δk`、`has_singularity` 覆写、`bits_srl` | 删 ghost parameter、删 residual rewrite、删第二套压缩学 | canonical runtime math core 收敛 |
| `v643_auditor_pass.md` | 审计师复核 | 对账当前 GitHub main | 撤回上一轮 3 个 blocker | 正式放行 canonical runtime math core |
| `handover` smoke 验证 | 工程主链验证 | local backtest 停滞 | 改默认执行路径，弃用 multiprocessing-first | 全链路 smoke 通过 |

---

## 第一阶段：最初的架构师主张，到底是什么

最早的 V64 不是从“调参数”开始，而是从一个强哲学命题开始：

> 压缩即智能。

也就是：

- 散户主导时，市场近似高熵布朗运动，轨迹难压缩
- 主力进场时，价格轨迹被强行拉进结构化流形，可压缩性急剧提升
- 只要能抓到“被压缩”的片段，再结合 SRL 方向信息，就能抓住主力作案痕迹

对应的原始架构口号，是把：

- `Topology`：空间折叠
- `Epiplexity`：信息压缩
- `SRL`：方向/冲击

熔铸成统一的 `Singularity Vector`。

### 架构师第一次点名的“工程背叛”

早期 `v64.md` 直接把当时实现里的三个问题点出来：

1. 残差塌缩时被强行写回 `0.0`
2. `R²` 被上限钳住，奇点被盖住
3. `bits_linear / bits_srl / bits_topology` 被当成竞争项，而不是同一头巨兽的三个投影

来源：

- `audit/v64.md` 开头的 `[ SYSTEM ARCHITECT FINAL OVERRIDE: THE EPISTEMIC AWAKENING ]`

这一阶段的重要意义不是“提出了正确代码”，而是第一次明确了 V64 的哲学方向：

- 不接受平庸的平滑化
- 不接受为了防报错而抹掉极端事件
- 不接受把多维物理投影强行做成 winner-take-all

---

## 第二阶段：第一次严格审计，四个硬伤把系统从“直觉正确”打到“工程不合格”

在后续的 Bourbaki 审计里，系统被要求从“强哲学直觉”升级成“数学-工程闭环”。

### 审计师抓到的四个硬伤

这四个硬伤构成了 V64 中段最关键的转折点：

1. **伪奇点**
- 不能靠 `999.0` 这种手工注入值代表信息爆发
- 必须让公式自己在正确极限下自然爆发

2. **几何破缺**
- `topo_area` 和 `topo_energy` 必须来自同一个闭合流形
- 不能用一个开集面积去配另一个闭合周长

3. **门控语义混用**
- 不能用同一个阈值同时表示：
  - Brownian baseline 下的 `Y` 更新环境
  - 最终信号触发门

4. **量纲错误**
- 无量纲的几何量，不能拿去和带价格单位的量直接比较

对应文档来源：

- `audit/v64.md` 中的 `[ SYSTEM ARCHITECT OVERRIDE: THE BOURBAKI SYNTHESIS & ABSOLUTE CLOSURE ]`
- `audit/v64.md` 中的 `[ SYSTEM ARCHITECT ABSOLUTE OVERRIDE: THE BOURBAKI CLOSURE ]`

### 我们的第一次系统性应对

这一轮之后，系统做的不是局部修补，而是方向上的硬切换：

1. **压缩率定义换轨**
- 从“残差对时间的线性拟合”切换到
- `Var(ΔP) / Var(R)` 这条 SRL-relative compression 路线

2. **门控语义解耦**
- `brownian_q_threshold`
- `signal_epi_threshold`
- `topo_energy_min`

3. **几何同源性恢复**
- `topo_area` 不再允许被 manifold overwrite

4. **测试和配置进入主战场**
- 不是只改 runtime
- 而是同时改 `config / docs / tests`

这一轮结束后，系统已经不是最早那种“靠奇点情绪驱动的版本”了，而是开始进入可证明的闭环路线。

---

## 第三阶段：`v642.md` 审计，问题从“硬伤”升级成“定义统一”

`v642.md` 的判断很关键：

> 比上一版强很多，但我还不会签 “absolute closure”。

这句话说明四个最初硬伤的方向已经基本修对，但 repo 级语义还没完全单义化。

### `v642.md` 明确指出的 4 个 repo 级问题

1. **同名不同义**
- `epiplexity` 在 runtime 和 legacy helper 中可能指向两个不同数学对象

2. **`Δk = 2` 没有重新证明**
- 旧的 `2` 属于线性探针
- 新的 SRL 生成式模型不能自动继承这个惩罚项

3. **`bits_srl` 仍保留第二套压缩学**
- 即使主 `epiplexity` 改了
- 只要 `bits_srl` 还在，repo 就不是单一压缩语义

4. **`has_singularity -> out_srl_resid = 0` 必须删除**
- 否则 residual 就不再是纯物理推导，而是被标签篡改过的观测量

来源：

- [v642.md](/home/zephryj/projects/omega/audit/v642.md)

### 这一轮应对的本质

这轮修复的重点，从“修 bug”转成了“统一定义”：

- 不能只让主链数学大致成立
- 必须保证同一个名词，在 `math core / kernel / config / docs / tests` 里是同一个对象

这也是为什么 `README`、`omega_core/README.md`、`config.py`、`tests/test_v64_absolute_closure.py` 进入了核心 scope。

---

## 第四阶段：`v643.md` 最终 override，最后 3 个 blocker 被直接点名

到了 `v643.md`，问题空间已经被审计师压缩到只剩 3 个阻断项：

1. `Δk = 2` 这个 ghost parameter 还没绝对删除
2. `has_singularity` 仍在篡改 `srl_resid`
3. `bits_srl` 仍让系统保留第二套压缩语义

这时架构师给出的不是抽象方向，而是接近手术刀级别的 patch 指令：

- `omega_core/omega_math_rolling.py`
- `omega_core/kernel.py`
- `config.py`
- `tests/test_v64_absolute_closure.py`
- `README.md`
- `omega_core/README.md`

来源：

- [v643.md](/home/zephryj/projects/omega/audit/v643.md)

---

## 第五阶段：最终代码证据，说明这 3 个 blocker 为什么已经关闭

这一部分是整个 V64 演化里最重要的证据层。

### 证据 1：`Δk` 已经从 canonical rolling compression path 消失

当前实现证据：

- `omega_core/omega_math_rolling.py:104-153`

```python
@njit(parallel=True, cache=True)
def calc_srl_compression_gain_rolling(
    price_change: np.ndarray,
    srl_residuals: np.ndarray,
    window: int,
    dist_to_boundary: np.ndarray
) -> np.ndarray:
    ...
    if var_dp < PLANCK_CONSTANT:
        out[i] = 0.0
        continue

    safe_var_r = max(var_r, PLANCK_CONSTANT)
    ratio = var_dp / safe_var_r

    if ratio > 1.0:
        out[i] = (window / 2.0) * math.log(ratio)
```

这段代码证明：

- 函数签名里已经没有 `delta_k`
- 公式只保留 `Var(ΔP) / Var(R)` 的对数增益
- `Zero-variance -> zero signal`

对应测试锁：

- `tests/test_v64_absolute_closure.py:113-130`

```python
sig = inspect.signature(calc_srl_compression_gain_rolling)
assert "delta_k" not in sig.parameters
...
assert "delta_k = 2.0" not in content
```

### 证据 2：`has_singularity` 不再改写 `srl_resid`

当前实现证据：

- `omega_core/kernel.py:121-125`
- `omega_core/kernel.py:202-212`

```python
if "has_singularity" in frames.columns:
    has_singularity = _safe_bool_col("has_singularity")
    out_is_active = out_is_active & (~has_singularity)

# singularity labels may gate activity, but must never rewrite
# the residual that feeds the compression score.

out_epi_raw = calc_srl_compression_gain_rolling(
    price_change=price_change,
    srl_residuals=out_srl_resid,
    window=window_len,
    dist_to_boundary=dist_to_boundary,
)
```

这里可以看出：

- singularity 只参与 activity mask
- `out_srl_resid` 没有被人为写成 `0`
- 压缩增益直接消费物理 residual

对应测试锁：

- `tests/test_v64_absolute_closure.py:133-163`

```python
assert "out_srl_resid[has_singularity_mask] = 0.0" not in content
...
assert resid != 0.0
```

### 证据 3：`bits_srl` 已经删除，系统只保留单一压缩语义

当前实现证据：

- `omega_core/kernel.py:292-319`

```python
canonical_epi = pl.col("epiplexity").forward_fill().over(group_expr)
compactness = (4.0 * math.pi * pl.col("topo_area").abs()) / (pl.col("topo_energy")**2 + 1e-12)
bits_topo = (compactness * math.log(window_len)).forward_fill().over(group_expr).clip(lower_bound=0.0)
srl_phase = pl.col("srl_resid").sign() * pl.col("srl_resid").abs().sqrt()

main_force_singularity = (
    canonical_epi.fill_null(0.0) +
    bits_topo.fill_null(0.0)
) * srl_phase

res_df = res_df.with_columns([
    canonical_epi.alias("bits_linear"),
    bits_topo.alias("bits_topology"),
    srl_phase.alias("srl_phase"),
    main_force_singularity.alias("singularity_vector"),
    pl.lit(1).alias("dominant_probe"),
])
```

这说明：

- 只剩 `canonical_epi`
- `bits_topology` 保留为空间闭合量
- `srl_phase` 只承担方向/相位
- `dominant_probe` 被降级为兼容占位符 `1`
- 不再有 `bits_srl` 第二压缩分支

对应测试锁：

- `tests/test_v64_absolute_closure.py:191-210`

```python
assert "bits_srl" not in result.columns
assert set(result.get_column("dominant_probe").drop_nulls().unique().to_list()) <= {1}
expected = (bits_linear + bits_topology) * srl_phase
np.testing.assert_allclose(result.get_column("singularity_vector").to_numpy(), expected)
```

### 证据 4：配置已经收口到新语义

当前实现证据：

- `config.py:616-680`

```python
class L2EpiplexityConfig:
    min_trace_len: int = 60
    fallback_value: float = 0.0
    sigma_gate_enabled: bool = False
    sigma_gate: float = 0.0

class L2SignalConfig:
    signal_epi_threshold: float = 0.5
    srl_resid_sigma_mult: float = 2.0
    topo_area_min_abs: float = 1e-9
    topo_energy_min: float = 2.0
    spoofing_ratio_max: float = 2.5
    min_ofi_for_y_update: float = 100.0
```

这说明：

- `peace_threshold` 已退出主战场
- `topo_energy_sigma_mult` 也不再承担有效语义
- 信号门和 Brownian baseline 门已解耦

---

## 第六阶段：为什么最终审计可以放行

最终的放行不是“因为架构师说数学绝对闭合”，而是因为审计师在重新核对当前 `GitHub main` 后，撤回了之前最后 3 个 blocker。

来源：

- [v643_auditor_pass.md](/home/zephryj/projects/omega/audit/v643_auditor_pass.md)

审计师最终确认：

1. `Δk = 2` 不能复现
2. `has_singularity -> out_srl_resid = 0.0` 不能复现
3. `bits_srl` 第二套压缩学不能复现

并给出最终签字：

> 放行 canonical runtime math core。  
> 撤回此前那 3 个 blocker。

这一句的分量非常重，因为它意味着：

- 当前主运行数学链已经收敛成单一对象
- 量纲一致
- 推导闭合
- 测试锁存在
- 不再有他此前点名的三处核心阻断

---

## 第七阶段：工程闭环不是自动获得的，`backtest` 还额外暴露了一个真实问题

数学主链放行之后，工程上还发生了一次非常真实的 smoke 问题：

- `tools/run_local_backtest.py` 在本地 smoke 中进入无进展停滞

症状是：

- 发现 `5409` 个 symbol
- 切出 `109` 个 batch
- 启动 worker 后不再前进

最终修复不是继续堆 multiprocessing，而是反过来把默认路径改成：

- 顺序批处理
- `multiprocessing` 只保留显式 opt-in
- 增加 batch 进度日志
- 输出目录写入前先创建

来源：

- `handover/ai-direct/entries/20260306_134038_v643_backtest_stall_triage.md`
- `handover/ai-direct/entries/20260306_135658_v643_backtest_remediation_smoke_pass.md`

这个阶段很重要，因为它证明：

- V64 的最后通过，不只是“数学通过”
- 还包括真实运行链在现代工程约束下可以稳定落地

---

## 最终状态

截至当前主链，V64 的结论可以用一句话概括：

> V64 从“压缩即智能”的哲学直觉，经过多轮审计逼近，最终收敛为一个单一、可推导、可测试、可运行的 canonical runtime math core。

### 已经完成的部分

- `epiplexity` 的 canonical runtime 定义已单义化
- `Δk = 0` 已落实到 rolling compression path
- `has_singularity` 不再篡改 `srl_resid`
- `bits_srl` 不再作为第二套压缩学存活
- `config / docs / tests` 已与主链语义对齐
- isolated smoke 已跑通 `Stage 2 -> forge -> training -> backtest`

### 还剩的非阻断项

审计师最后保留了一个非阻断备注：

- repo 中仍有少量历史 `SRL race` 命名残影

这不再污染 canonical compression path，但如果目标是“仓库级零历史语义债务”，后续仍值得继续清理。

---

## 推荐阅读顺序

如果只想在最短时间内看懂 V64 的整个发展逻辑，建议按这个顺序读：

1. [v64.md](/home/zephryj/projects/omega/audit/v64.md)
2. [v642.md](/home/zephryj/projects/omega/audit/v642.md)
3. [v643.md](/home/zephryj/projects/omega/audit/v643.md)
4. [v643_auditor_pass.md](/home/zephryj/projects/omega/audit/v643_auditor_pass.md)
5. [omega_math_rolling.py](/home/zephryj/projects/omega/omega_core/omega_math_rolling.py)
6. [kernel.py](/home/zephryj/projects/omega/omega_core/kernel.py)
7. [test_v64_absolute_closure.py](/home/zephryj/projects/omega/tests/test_v64_absolute_closure.py)
8. [LATEST.md](/home/zephryj/projects/omega/handover/ai-direct/LATEST.md)

