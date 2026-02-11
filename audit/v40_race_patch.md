这是一个基于 **LZ76 胜出** 这一里程碑式结果的 **v4.0 终局升级方案**。

**LZ76 的胜出是第一性原理的胜利。**
它证明了 A 股微观结构的本质——**“算法生成的序列” (Algorithmic Generation)**。

* Zlib 失败，说明主力操盘不是简单的“文本复制粘贴”。
* Permutation 失败，说明仅看“排序”丢弃了太多的幅度信息。
* **LZ76 胜出，说明主力在不断地以特定的速率生成“受控的新模式” (Controlled Novelty)。**

基于这个结果，我们可以确立 **v4.0 的物理架构**。以下是针对你问题的深度审计与执行方案。

---

### 第一部分：Epiplexity 的终局优化 (Epiplexity v4.0)

**1. 如何优化公式？**
你问：*是最优的吗？*
**回答：实验结果说“不”。**
LZ76 在你的赛马中是以 **线性 ()** 的形式参赛并胜出的。这说明 Trainer 明确告诉你：**“我不需要你做非线性映射，越有序信号越强，直接给我线性的  就好。”**

* **决策**：废除抛物线，废除 Zlib，废除 Permutation，确立 LZ76 为唯一核心。
* **新公式**：
$$ Epiplexity = 1.0 - \frac{C_{LZ}(n)}{n / \log_2 n} $$
*(其中  为 LZ76 复杂度计数，分母为理论归一化因子)*
* ：极度有序（死板的主力算法）。
* ：极度随机（散户噪音）。

---

### 第二部分：将“赛马”扩展至 SRL 和 Topology

**是的，这是下一步的核心战略。**
既然你已经掌握了“并行赛马”这个大杀器，就不要再猜 SRL 的幂次是 0.5 还是 0.6 了，**让它们一起上场，优胜劣汰。**

#### 1. SRL (根号法则) —— 赛“物理定律”

**测试点：冲击敏感度 (Exponent)**
标准理论是 。但在 A 股，由于涨跌停限制（流动性截断）和散户羊群效应，这个指数是漂移的。

* **赛道设计**：
* **Lane A**:  (Soft) —— 假设市场很脆弱，少量资金引起大波动（立方根）。
* **Lane B**:  (Standard) —— 标准物理状态（平方根）。
* **Lane C**:  (Hard) —— 假设市场很硬，冲击呈线性增长（接近线性）。

#### 2. Topology (拓扑) —— 赛“相空间”

**测试点：观察坐标系 (Manifold)**
目前的拓扑是基于 `Price-OFI` 的。但这一定是最佳视角吗？我们来测试三种不同的几何流形。

* **赛道设计**：
* **Lane A (Micro)**: **Price vs OFI**。捕捉微观供需错配（当前基准）。
* **Lane B (Classic)**: **Price vs Volume**。捕捉传统“量价背离”（经典技术分析）。
* **Lane C (Trend)**: **Price vs Time**。捕捉单纯的“加速/减速”（作为对照组，如果它胜出，说明复杂的 TDA 是多余的）。

---

### 第三部分：v4.0 核心代码实现 (The Race Edition)

请更新以下文件。这将是一次**去肥增肌**的升级：移除 Zlib/Perm 的冗余代码，引入 SRL/Topo 的多维探测。

#### 1. `omega_config.py` (新增赛马配置)

```python
class OmegaConfig:
    # ... (保留原有常数 PLANCK_STD 等) ...
    
    # [A] Epiplexity Winner Config
    # LZ76 胜出，固化为核心算法
    EPI_BLOCK_MIN_LEN = 10
    EPI_SYMBOL_THRESH = 0.5
    
    # [B] SRL Race Config (New!)
    # 并行计算三个幂次，由 Trainer 决定权重
    SRL_RACE_EXPONENTS = [0.33, 0.5, 0.66]
    SRL_MIN_DEPTH = 1.0
    
    # [C] Topology Race Config (New!)
    # 定义不同的相空间组合 (X_Col, Y_Col, X_Scale, Y_Scale)
    TOPO_MANIFOLDS = {
        "Micro":   ("Price_Trace", "OFI_Trace", "PLANCK_PRICE", "PLANCK_VOL"),
        "Classic": ("Price_Trace", "Vol_Trace", "PLANCK_PRICE", "PLANCK_VOL"),
        "Trend":   ("Price_Trace", "Time_Trace", "PLANCK_PRICE", "PLANCK_STD")
    }
    TOPO_GREEN_COEFF = 0.5

```

#### 2. `omega_math_core.py` (纯 LZ76 + 物理赛马)

```python
import numpy as np
import math

class OmegaMath:
    
    # =========================================================
    # 1. Epiplexity Kernel (Winner: LZ76 Linear)
    # =========================================================
    @staticmethod
    def calc_epiplexity_final(trace, min_len, symbol_thresh, planck_std):
        """
        [Epiplexity v4.0] 
        Only LZ76. Linear Output. No Parabola.
        """
        n = len(trace)
        if n < min_len: return 0.0
        
        # 1. 预处理 (差分 + 动态阈值)
        diff = np.diff(trace)
        scale = max(np.std(diff), planck_std)
        threshold = symbol_thresh * scale
        
        # 2. 转化为三态序列 "012"
        # 0: Down, 1: Flat, 2: Up
        s_lz = "".join(['2' if d > threshold else '0' if d < -threshold else '1' for d in diff])
        
        # 3. LZ76 复杂度计数 (内联优化版)
        n_s = len(s_lz)
        if n_s == 0: return 0.0
        
        i, c, u, v, vmax = 0, 1, 1, 1, 1
        while u + v <= n_s:
            if s_lz[i + v] == s_lz[u + v]:
                v += 1
            else:
                vmax = max(v, vmax)
                i += 1
                if i == u:
                    c += 1; u += vmax; v = 1; i = 0; vmax = v
                else:
                    v = 1
        
        # 4. 归一化 (Lempel-Ziv Normalization)
        # r = Complexity / Limit
        if n_s <= 1: return 0.0
        norm_factor = n_s / math.log2(n_s)
        r = c / norm_factor
        
        # 5. 输出结构度 (Linear Inversion)
        # 限制在 [0, 1] 区间
        return max(1.0 - r, 0.0)

    # =========================================================
    # 2. SRL Race Kernel (Parallel Exponents)
    # =========================================================
    @staticmethod
    def calc_srl_race(price_change, sigma, net_ofi, depth, current_Y, planck_std, min_depth, exponents):
        """
        [Physics Race] 计算不同幂次下的物理残差
        Returns: list of residuals
        """
        eff_depth = max(depth, min_depth)
        safe_vol = max(sigma, planck_std)
        
        base_factor = abs(net_ofi) / eff_depth
        residuals = []
        
        for k in exponents:
            # I = Y * Sigma * (Q/D)^k
            # 注意: Y 在此处作为缩放基准，Trainer 会通过权重调整实际系数
            raw_impact = safe_vol * (base_factor ** k)
            theory_impact = np.sign(net_ofi) * current_Y * raw_impact
            residuals.append(price_change - theory_impact)
            
        return residuals

    # =========================================================
    # 3. Topology Race Kernel (Manifold Geometry)
    # =========================================================
    @staticmethod
    def calc_topology_area(x_trace, y_trace, x_scale, y_scale, green_coeff):
        """
        [Geometry Race] 通用拓扑面积计算
        """
        x = np.array(x_trace)
        y = np.array(y_trace)
        if len(x) != len(y) or len(x) < 2: return 0.0
        
        # 鲁棒归一化
        x_norm = (x - np.mean(x)) / max(np.std(x), x_scale)
        y_norm = (y - np.mean(y)) / max(np.std(y), y_scale)
        
        # 辛几何面积 (Green's Theorem)
        cross = x_norm[:-1] * y_norm[1:] - x_norm[1:] * y_norm[:-1]
        area = green_coeff * np.sum(cross)
        
        return area

```

#### 3. `omega_kernel.py` (数据流适配)

**关键修改**：Map 阶段必须聚合 `Vol_Trace` 和 `Time_Trace`，以支持新的拓扑赛道。

```python
# [Phase 1: Map] 聚合部分增加 Trace
            # ... Inside aggregation ...
            pl.col("P_micro").alias("Price_Trace"),
            pl.col("v_OFI").cum_sum().alias("OFI_Trace"),
            pl.col(self.cols["Vol"]).cum_sum().alias("Vol_Trace"), # 新增: 量轨迹
            # 构造 Time_Trace (简单的 0,1,2...索引序列即可)
            pl.int_range(0, pl.count()).alias("Time_Trace"), 
            # ...

# [Phase 2: Reduce]
            # ... Inside Reduce Loop ...
            
            # 1. Epiplexity (Winner: LZ76 Linear)
            epi = OmegaMath.calc_epiplexity_final(
                trace=row["Price_Trace"],
                min_len=cfg.EPI_BLOCK_MIN_LEN,
                symbol_thresh=cfg.EPI_SYMBOL_THRESH,
                planck_std=cfg.PLANCK_STD
            )
            
            # 2. SRL Race (3 Lanes)
            srl_resids = OmegaMath.calc_srl_race(
                price_change=row["Close"] - row["Open"],
                sigma=row["Sigma"],
                net_ofi=row["Net_OFI"],
                depth=row["Depth"],
                current_Y=current_Y,
                planck_std=cfg.PLANCK_STD,
                min_depth=cfg.SRL_MIN_DEPTH,
                exponents=cfg.SRL_RACE_EXPONENTS
            )
            
            # 3. Topology Race (3 Lanes)
            topo_results = {}
            for name, (xn, yn, xs, ys) in cfg.TOPO_MANIFOLDS.items():
                x_scale = getattr(cfg, xs)
                y_scale = getattr(cfg, ys)
                area = OmegaMath.calc_topology_area(
                    row[xn], row[yn], x_scale, y_scale, cfg.TOPO_GREEN_COEFF
                )
                topo_results[f"Topo_{name}"] = area

            # 4. Y Update (使用中间值 0.5 维护状态，保持稳定性)
            resid_std = srl_resids[1] 
            # ... (Adaptive Y Update Logic using resid_std) ...
            
            # 结果打包
            results.append({
                "Time": row["Time"],
                "Epiplexity": epi,
                
                # SRL Race Features
                "SRL_Resid_033": srl_resids[0],
                "SRL_Resid_050": srl_resids[1],
                "SRL_Resid_066": srl_resids[2],
                
                # Topo Race Features (Unpack Dict)
                **topo_results,
                
                "Adaptive_Y": current_Y,
                "Sigma": row["Sigma"]
            })

```

### 第四部分：下一步行动

1. **执行 Round 2 训练**：这其实是一次 **“A 股全物理参数测定实验”**。
2. **观测重点**：

* **SRL**：如果 `0.33` 胜出，说明 A 股是个“易碎品”（少量资金就能砸盘）。
* **Topology**：如果 `Topo_Classic` (量价) 胜出 `Topo_Micro` (价流)，说明 Level-2 的高频 OFI 并没有提供比分钟级成交量更多的几何信息。这是一个极其重要的**去伪存真**测试。

你正在让数据自己说话，寻找最适合它的物理定律。这比任何人工调参都高级。
