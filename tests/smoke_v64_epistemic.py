import sys
import os
from pathlib import Path
import numpy as np
import polars as pl

# 设定项目根目录
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from omega_core.kernel import apply_recursive_physics
from config import load_l2_pipeline_config

def smoke_test_v64_kernel():
    print("=== V64 EXTREMISTAN SMOKE TEST ===")
    
    # 直接造 DataFrame 送入内核，跳过 ETL 读取阶段的校验（专门测试 Kernel 纯物理逻辑）
    n_rows = 100
    price_change = np.linspace(0.01, 0.20, n_rows)
    open_px = np.linspace(10.0, 11.0, n_rows)
    df = pl.DataFrame({
        "symbol": ["MOCK_A"] * n_rows,
        "date": ["2026-03-05"] * n_rows,
        "time_end": [f"10:00:{i:02d}" for i in range(n_rows)],
        "bucket_id": np.arange(n_rows),
        "open": open_px,
        "close": open_px + price_change,
        "sigma": [0.01] * n_rows,
        "depth": [1000.0] * n_rows,
        "net_ofi": np.linspace(25.0, 250.0, n_rows),
        "trade_vol": [100.0] * n_rows,
        "cancel_vol": [10.0] * n_rows,
    })
    
    cfg = load_l2_pipeline_config()
    
    # 1. 运行 V64 递归物理内核
    frames = apply_recursive_physics(df, cfg)
    
    # 2. 验证新的相对压缩增益定义：必须为正且不能再依赖 999.0 伪奇点
    max_epi = frames.select(pl.col("epiplexity").max()).item()
    print(f"Max Epiplexity Detected: {max_epi}")
    assert np.isfinite(max_epi) and max_epi > 0.0, f"FAILED: canonical compression gain did not emerge. Got {max_epi}"
    assert max_epi != 999.0, f"FAILED: fake 999.0 pseudo-singularity resurfaced. Got {max_epi}"
    print("✅ PASS: Canonical compression gain emerged without pseudo-singularity hacks.")
    
    # 3. 验证 Singularity Vector 熔铸
    assert "singularity_vector" in frames.columns, "FAILED: singularity_vector column missing!"
    
    # 新定义下，向量只需要保持有限且可观测，不再依赖旧三重 bits 叠加的爆炸幅度
    max_singularity = frames.select(pl.col("singularity_vector").abs().max()).item()
    print(f"Max Singularity Vector Amplitude: {max_singularity}")
    assert np.isfinite(max_singularity) and max_singularity > 0.0, (
        "FAILED: singularity_vector should remain finite and non-zero under structured input."
    )
    print("✅ PASS: The canonical compression + topology path successfully fused into singularity_vector.")
    
    print("=== ALL V64 SMOKE TESTS PASSED ===")

if __name__ == "__main__":
    smoke_test_v64_kernel()
