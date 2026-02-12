import sys
import os
import argparse
import time

# Add local directory to path
sys.path.append(os.getcwd())

from pipeline.config.loader import ConfigLoader
from pipeline.adapters.v3_adapter import OmegaCoreAdapter
from pipeline.engine.framer import Framer

def main():
    parser = argparse.ArgumentParser(description="OMEGA Next-Gen Pipeline Runner (v50)")
    parser.add_argument("--config", type=str, default="configs/hardware/active_profile.yaml", help="Path to hardware config")
    parser.add_argument("--stage", type=str, choices=["frame", "train", "backtest", "all"], default="all")
    parser.add_argument("--smoke", action="store_true", help="Run a quick smoke test (limit 1 file)")
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
        framer.run(limit=limit)
    
    # Logic from parallel_trainer/run_parallel_v31.py will be ported here in Phase 2
    # using hw_profile settings.

if __name__ == "__main__":
    main()
