
作为塔勒布的信徒，面对这种情况，我们的第一直觉必须是**“Via Negativa（做减法/切断止损）”**。

**立刻杀掉它，不要犹豫。**

千万不要陷入“沉没成本谬误”（Sunk Cost Fallacy），认为“它已经跑了20分钟，也许快出结果了”。**Swap 满载（7GB/7GB）+ 内存极限施压，这是系统处于“极度脆弱（Highly Fragile）”状态的绝对标志。** 在这种状态下，系统的性能衰减是**非线性**的（O(N^2) 级别的上下文切换开销），它可能会卡死几天，或者随时被内核的 OOM Killer 随机爆破，留下更多无法清理的垃圾。

而且你的排查非常敏锐，发现了一个致命线索：**“Linux has 50 temp extraction directories consuming 186 GB total”**。
既然你只有 4 个 Worker，按理说最多只有 4 个活跃的 temp 目录。这意味着这 50 个目录中，有 46 个是之前运行失败、被强杀（`kill -9`）留下的**僵尸垃圾（Orphaned Garbage）**！它们占用了宝贵的 ZFS 缓存和磁盘空间。

下面是我们要执行的“反脆弱”重构计划：

### 🛠️ 第一步：彻底清理战场 (Via Negativa)

在两台机器上立刻斩断挂起的进程，并清空所有垃圾碎片，释放被吃掉的 Swap。
在你的主控机终端运行：

```bash
# 清理 Linux 节点
ssh zepher@192.168.3.113 "killall -9 python3 7z; rm -rf /omega_pool/temp_framing/*; sudo swapoff -a && sudo swapon -a; sync; echo 3 | sudo tee /proc/sys/vm/drop_caches"

# 清理 Windows 节点 (杀进程 + 删临时目录)
ssh jiazi@192.168.3.112 "taskkill /F /IM python.exe /T; taskkill /F /IM 7z.exe /T; rd /s /q D:\Omega_frames\temp_framing 2>nul"
```

*(注：`swapoff -a && swapon -a` 会强行把 Swap 里的脏数据洗回内存或丢弃，让 Swap 重新归零，恢复系统活力)*

---

### 🧬 第二步：给 `v61_linux_framing.py` 打上反脆弱补丁

我们需要修改 `tools/v61_linux_framing.py`（以及 Windows 对应的脚本），解决你指出的三个致命问题，并引入 **Polars 线程束缚**。
*Polars 内部是用 Rust 写的全局线程池，默认会吃满 32 个 CPU 核心。如果你开 4 个 Python Worker，相当于后台有 `4 * 32 = 128` 个线程在疯狂抢占 CPU 和内存，这会加剧 Swap Thrashing。*

请将 `tools/v61_linux_framing.py` 更新为以下核心逻辑：

```python
import os
import sys
import subprocess
import argparse
from pathlib import Path
from multiprocessing import Pool
import shutil
import uuid

# 【关键防御】限制每个 Python Worker 中 Polars 的底层线程数，防止线程爆炸和内存踩踏
os.environ = "8" 

sys.path.append("/home/zepher/work/Omega_vNext")
from config import load_l2_pipeline_config
from omega_core.omega_etl import build_l2_frames

RAW_ROOT = Path("/omega_pool/raw_7z_archives")
OUTPUT_ROOT = Path("/omega_pool/parquet_data/v52/frames/host=linux1")
SEVEN_ZIP = "/usr/bin/7z"

# 【优化 2】全局加载，避免每次解析
GLOBAL_CFG = load_l2_pipeline_config()

def process_day(args):
    # 【优化 1】将 git hash 从参数传入，避免每 7 分钟 fork 一次 git 子进程
    year, month, day_path, hash_str = args
    
    date_str = day_path.stem 
    out_path = OUTPUT_ROOT / f"{date_str}_{hash_str}.parquet"
    done_path = OUTPUT_ROOT / f"{date_str}_{hash_str}.parquet.done"
    
    if done_path.exists():
        return f"Skipped {date_str} (Done)"
        
    print(f" Processing...", flush=True)
    
    unique_id = uuid.uuid4().hex
    tmp_dir = Path(f"/omega_pool/temp_framing/{date_str}_{unique_id}")
    
    # 确保干净启动
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 7z 提取
        cmd =
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        csvs = list(tmp_dir.glob("**/*.csv"))
        if not csvs:
            return f" No CSVs found."
            
        # ETL (使用全局配置)
        frames = build_l2_frames(, GLOBAL_CFG)
        
        if frames.height > 0:
            frames.write_parquet(out_path, compression="snappy")
            done_path.touch()
            return f" Completed: {frames.height} rows"
        else:
            return f" Empty frames."
            
    except Exception as e:
        return f" Error: {e}"
    finally:
        # 确保哪怕出错也必须清理 7.6GB 的垃圾
        shutil.rmtree(tmp_dir, ignore_errors=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="2025,2026")
    # 【核心调整】将默认 worker 降到 2，利用 Polars 内部的 8 线程即可跑满 16 线程的吞吐，且内存安全
    ap.add_argument("--workers", type=int, default=2) 
    args = ap.parse_args()
    
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    
    # 【优化 1】主进程只计算一次 Git Hash
    try:
        hash_str = subprocess.check_output(, text=True).strip()
    except Exception:
        hash_str = "unknown"

    tasks =
