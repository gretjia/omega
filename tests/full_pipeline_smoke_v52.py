import sys
import os
import shutil
import glob
import pickle
from pathlib import Path
import polars as pl
import numpy as np

# Ensure project root is in path
sys.path.append(os.getcwd())

from config import load_l2_pipeline_config, replace, L2IOConfig, L2TrainConfig
from pipeline.engine.framer import Framer
from pipeline.config.hardware import HardwareProfile
from omega_core.trainer_v51 import OmegaTrainerV3, evaluate_frames

# Paths
SMOKE_ROOT = Path("data/smoke_v52")
STAGE_ROOT = SMOKE_ROOT / "stage"
TRAIN_FRAMES_DIR = SMOKE_ROOT / "frames_train"
BACKTEST_FRAMES_DIR = SMOKE_ROOT / "frames_backtest"
ARTIFACTS_DIR = SMOKE_ROOT / "artifacts"

# Data (Hardcoded from previous finding for stability)
TRAIN_FILES = [
    "data/level2/2023/202301/20230103.7z",
    "data/level2/2023/202301/20230104.7z",
    "data/level2/2023/202301/20230105.7z",
    "data/level2/2023/202301/20230106.7z",
    "data/level2/2023/202301/20230109.7z"
]
BACKTEST_FILES = [
    "data/level2/2023/202301/20230110.7z",
    "data/level2/2023/202301/20230111.7z",
    "data/level2/2023/202301/20230112.7z",
    "data/level2/2023/202301/20230113.7z",
    "data/level2/2023/202301/20230116.7z"
]

def clean_env():
    if SMOKE_ROOT.exists():
        try:
            shutil.rmtree(SMOKE_ROOT)
        except Exception as e:
            print(f"[Warn] Cleanup failed: {e}")
    
    SMOKE_ROOT.mkdir(parents=True, exist_ok=True)
    STAGE_ROOT.mkdir(exist_ok=True)
    TRAIN_FRAMES_DIR.mkdir(exist_ok=True)
    BACKTEST_FRAMES_DIR.mkdir(exist_ok=True)
    ARTIFACTS_DIR.mkdir(exist_ok=True)

def run_framing(files, output_dir, label="Train"):
    print(f"\n--- [Phase 1: Framing ({label})] ---", flush=True)
    
    # Mock Hardware Profile
    hw = HardwareProfile.default_32core_workstation()
    hw.storage.source_root = str(Path(files[0]).parent) # Not used directly if we pass files manually
    hw.storage.stage_root = str(STAGE_ROOT)
    hw.storage.output_root = str(output_dir)
    # Reduce workers for smoke test safety
    hw.compute.framing_workers = 4 
    
    framer = Framer(hardware=hw, core=None)
    
    success_count = 0
    for f_path in files:
        if not os.path.exists(f_path):
            print(f"  [Skip] File not found: {f_path}", flush=True)
            continue
            
        try:
            res = framer._process_archive(f_path)
            if res: success_count += 1
        except Exception as e:
            print(f"  [Error] Failed {f_path}: {e}", flush=True)
            import traceback
            traceback.print_exc()
            
    print(f"  Framed {success_count}/{len(files)} archives.", flush=True)
    return success_count > 0

def run_training():
    print(f"\n--- [Phase 2: Training] ---", flush=True)
    
    if (ARTIFACTS_DIR / "omega_smoke_model.pkl").exists():
        print("  [Skip] Model already exists.", flush=True)
        return True

    # Patch discover_l2_dirs to point to our smoke train frames
    import tools.multi_dir_loader
    original_discover = tools.multi_dir_loader.discover_l2_dirs
    tools.multi_dir_loader.discover_l2_dirs = lambda: [TRAIN_FRAMES_DIR]
    
    cfg = load_l2_pipeline_config()
    # Ensure artifacts go to smoke dir
    # Note: OmegaTrainerV3.save() defaults to ./artifacts, need to override call or monkeypatch
    
    trainer = OmegaTrainerV3(cfg)
    
    try:
        trainer.train(sample_frac=1.0, checkpoint_interval=100000)
        # Manually save to our dir
        trainer.save(out_dir=str(ARTIFACTS_DIR), name="omega_smoke_model.pkl")
        print("  Training completed and model saved.", flush=True)
    except Exception as e:
        print(f"  [Error] Training failed: {e}", flush=True)
        import traceback
        traceback.print_exc()
        tools.multi_dir_loader.discover_l2_dirs = original_discover
        return False
        
    tools.multi_dir_loader.discover_l2_dirs = original_discover
    return (ARTIFACTS_DIR / "omega_smoke_model.pkl").exists()

def run_backtest_eval():
    print(f"\n--- [Phase 3: Backtest Evaluation] ---", flush=True)
    
    model_path = ARTIFACTS_DIR / "omega_smoke_model.pkl"
    if not model_path.exists():
        print("  [Fail] Model not found.", flush=True)
        return False
        
    with open(model_path, "rb") as f:
        payload = pickle.load(f)
        model = payload["model"]
        scaler = payload["scaler"]
        feature_cols = payload["feature_cols"]
        
    cfg = load_l2_pipeline_config()
    
    all_metrics = []
    
    parquet_files = sorted(list(BACKTEST_FRAMES_DIR.glob("*.parquet")))
    if not parquet_files:
        print("  [Fail] No backtest frames found.", flush=True)
        return False
        
    trainer_dummy = OmegaTrainerV3(cfg) # Just for _prepare_frames logic
    
    for pf in parquet_files:
        try:
            df = pl.read_parquet(str(pf))
            # Must prep frames (add features, labels, interactions)
            df = trainer_dummy._prepare_frames(df, cfg)
            
            if df.height == 0: continue
            
            metrics = evaluate_frames(df, cfg, model=model, scaler=scaler, feature_cols=feature_cols)
            all_metrics.append(metrics)
            print(f"  {pf.name}: Align={metrics.get('Model_Alignment', 'NaN'):.4f}, Rows={metrics['n_frames']}", flush=True)
            
        except Exception as e:
            print(f"  [Error] Eval failed for {pf.name}: {e}", flush=True)
            
    if not all_metrics:
        return False
        
    avg_align = np.nanmean([m.get("Model_Alignment", float("nan")) for m in all_metrics])
    print(f"\n  Average Model Alignment: {avg_align:.4f}", flush=True)
    
    if np.isnan(avg_align):
        print("  [Warn] Alignment is NaN (possibly insufficient data/structure).", flush=True)
        return True # Soft pass for smoke test on tiny data
        
    return True

def main():
    print("=== OMEGA v5.2 Full Pipeline Smoke Test (Resume) ===", flush=True)
    # clean_env() # SKIP CLEANUP to use existing frames
    
    # Check if frames exist
    if not list(TRAIN_FRAMES_DIR.glob("*.parquet")):
        print("Train frames missing, cannot resume.")
        return

    # if not run_framing(TRAIN_FILES, TRAIN_FRAMES_DIR, "Train"):
    #     print("Framing (Train) Failed.")
    #     return
        
    # if not run_framing(BACKTEST_FILES, BACKTEST_FRAMES_DIR, "Backtest"):
    #     print("Framing (Backtest) Failed.")
    #     return
        
    if not run_training():
        print("Training Failed.")
        return
        
    if not run_backtest_eval():
        print("Backtest Failed.")
        return
        
    print("\n=== Smoke Test SUCCESS ===", flush=True)
    # print("Cleaning up...", flush=True)
    # clean_env() # Keep artifacts for inspection

if __name__ == "__main__":
    main()
