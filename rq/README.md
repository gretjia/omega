# OMEGA RQ Adapter (`rq`)

> Last updated: 2026-02-11 (v5.0 Alignment Pending)

本 README 只描述 Ricequant 适配层职责。  
全局规范、技能索引、跨模块流程请查看 [`../README.md`](../README.md)。

## 模块职责

`rq/` 是外部平台适配层，负责把 OMEGA 数学内核连接到 Ricequant 生态：
1. 数据接入（本地数据与 rqdatac）
2. 因子算子封装
3. 策略执行桥接

## 目录结构

1. `rq/interface.py`: 统一入口
2. `rq/data/`: 数据访问与本地/远端切换
3. `rq/factor/`: 因子与物理算子
4. `rq/alpha/`: 策略执行接口
5. `rq/optimizer/`: 组合优化占位层

## 最小用法

```python
import rq.interface as OmegaRQ

OmegaRQ.init()
tensor = OmegaRQ.data.get_maxwell_tensor("000032.XSHE")
op = OmegaRQ.factor
```

## 配置与约束

1. 不使用硬编码绝对路径（如 `d:/...`）
2. 统一通过根目录 `config.py` 和适配器配置读取路径与开关
3. 平台接入变更优先更新 skill：`qmtsdk` / `rqsdk`
