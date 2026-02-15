import sys
import os
import argparse
import time
import re

# Add local directory to path
sys.path.append(os.getcwd())

from pipeline.config.loader import ConfigLoader
from pipeline.adapters.v3_adapter import OmegaCoreAdapter
from pipeline.engine.framer import Framer

_WIN_ABS_RE = re.compile(r"^[A-Za-z]:[\\\\/]")


def _is_windows_abs_path(p: str) -> bool:
    return bool(_WIN_ABS_RE.match(p)) or p.startswith("\\\\")


def _load_archive_list(list_path: str) -> list[str]:
    archives: list[str] = []
    with open(list_path, "r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            archives.append(line)
    return archives


def _resolve_archive_paths(entries: list[str], source_root: str) -> list[str]:
    out: list[str] = []
    for p in entries:
        p = p.strip().strip('"').strip("'")
        # Allow forward slashes in list files for cross-OS portability.
        p_norm = p.replace("\\", "/")
        if os.path.isabs(p_norm) or _is_windows_abs_path(p):
            out.append(os.path.normpath(p))
        else:
            out.append(os.path.normpath(os.path.join(source_root, p_norm)))
    return out


def main():
    parser = argparse.ArgumentParser(description="OMEGA Next-Gen Pipeline Runner (v50)")
    parser.add_argument("--config", type=str, default="configs/hardware/active_profile.yaml", help="Path to hardware config")
    parser.add_argument("--stage", type=str, choices=["frame", "train", "backtest", "all"], default="all")
    parser.add_argument("--smoke", action="store_true", help="Run a quick smoke test (limit 1 file)")
    parser.add_argument(
        "--archive-list",
        type=str,
        default=None,
        help="Optional: path to a text file listing .7z archives (relative to storage.source_root unless absolute).",
    )
    args = parser.parse_args()

    print(f"--- OMEGA PIPELINE ENGINE v50.0.1 ---")
    
    # 0. Setup Logging
    log_dir = "audit"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"_pipeline_{args.stage}.log")
    if args.smoke:
        log_file = os.path.join(log_dir, f"_pipeline_{args.stage}_smoke.log")
    
    def log(msg):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_msg = f"[{timestamp}] {msg}"
        print(formatted_msg)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(formatted_msg + "\n")
    
    log(f"Starting session: {args.stage.upper()} (Smoke: {args.smoke})")
    
    # 1. Load Hardware Configuration
    if not os.path.exists(args.config):
        print(f"[Warn] Config not found: {args.config}")
        print(f"[Init] Generating default 32-Core Workstation profile...")
        ConfigLoader.create_default_yaml(args.config)
        
    try:
        hw_profile = ConfigLoader.load_hardware_profile(args.config)
        print(f"[Config] Loaded Profile: {hw_profile.profile_name}")
        print(f"         Storage Source: {hw_profile.storage.source_root}")
        print(f"         Storage Stage : {hw_profile.storage.stage_root} (Target IOPS Zone)")
        print(f"         Compute       : {hw_profile.compute.framing_workers} Workers")
    except Exception as e:
        print(f"[Error] Failed to load config: {e}")
        return

    # 2. Initialize Math Core
    try:
        from config import load_l2_pipeline_config
        l2_cfg = load_l2_pipeline_config()
        
        core = OmegaCoreAdapter()
        core.initialize({"pipeline_cfg": l2_cfg})
        print(f"[Core]   Initialized: {core.version}")
    except Exception as e:
        print(f"[Error] Core init failed: {e}")
        return

    # 3. Execution
    print(f"\n[Engine] Starting Stage: {args.stage.upper()}")
    
    # Use physical SSD for all stages (Stability First)
    hw_profile.compute.max_workers = {
        "frame": hw_profile.compute.framing_workers,
        "train": hw_profile.compute.training_workers,
        "backtest": hw_profile.compute.backtest_workers,
        "all": hw_profile.compute.framing_workers
    }.get(args.stage, hw_profile.compute.framing_workers)
    
    log(f"Resource Config: Physical SSD Staging (Workers: {hw_profile.compute.max_workers})")

    if args.stage in ["frame", "all"]:
        framer = Framer(hw_profile, core, logger=log)
        limit = 1 if args.smoke else 0

        if args.archive_list:
            rel = _load_archive_list(args.archive_list)
            archives = _resolve_archive_paths(rel, hw_profile.storage.source_root)
            log(f"Explicit archive list enabled: {args.archive_list} ({len(archives)} entries)")
            framer.run_archives(archives, limit=limit)
        else:
            framer.run(limit=limit)
    
    # Logic from parallel_trainer/run_parallel_v31.py will be ported here in Phase 2
    # using hw_profile settings.

if __name__ == "__main__":
    main()
