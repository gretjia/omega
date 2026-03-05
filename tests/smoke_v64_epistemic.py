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
    df = pl.DataFrame({
        "symbol": ["MOCK_A"] * n_rows,
        "date": ["2026-03-05"] * n_rows,
        "time_end": [f"10:00:{i:02d}" for i in range(n_rows)],
        "bucket_id": np.arange(n_rows),
        "open": np.linspace(10.0, 11.0, n_rows), # 绝对线性上升 (方差塌缩的制造者)
        "close": np.linspace(10.0, 11.0, n_rows) + 0.001,
        "sigma": [0.01] * n_rows,
        "depth": [1000.0] * n_rows,
        "net_ofi": [50.0] * n_rows, # 稳定买盘
        "trade_vol": [100.0] * n_rows,
        "cancel_vol": [10.0] * n_rows,
    })
    
    cfg = load_l2_pipeline_config()
    
    # 1. 运行 V64 递归物理内核
    frames = apply_recursive_physics(df, cfg)
    
    # 2. 验证 Epiplexity 奇点释放 (999.0)
    max_epi = frames.select(pl.col("epiplexity").max()).item()
    print(f"Max Epiplexity Detected: {max_epi}")
    assert max_epi == 999.0, f"FAILED: Epiplexity singularity not triggered! Got {max_epi}"
    print("✅ PASS: Epiplexity singularity successfully unlocked (999.0).")
    
    # 3. 验证 Singularity Vector 熔铸
    assert "singularity_vector" in frames.columns, "FAILED: singularity_vector column missing!"
    
    # 对于完美线性上升且 OFI 稳定的数据，势能极其巨大
    max_singularity = frames.select(pl.col("singularity_vector").abs().max()).item()
    print(f"Max Singularity Vector Amplitude: {max_singularity}")
    assert max_singularity > 10.0, "FAILED: Singularity vector did not fuse the extreme signals properly."
    print("✅ PASS: The Epistemic Trinity successfully fused into singularity_vector.")
    
    print("=== ALL V64 SMOKE TESTS PASSED ===")

if __name__ == "__main__":
    smoke_test_v64_kernel()