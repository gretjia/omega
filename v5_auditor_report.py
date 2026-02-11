import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from omega_core.physics_auditor import OmegaPhysicsAuditor
from config import load_l2_pipeline_config

def main():
    print("--- OMEGA v5.0 Physics Audit Driver ---")
    
    # Paths
    data_dir = "D:/Omega_frames/v50/output"
    audit_out = "audit/v5_smoke_audit"
    
    if not os.path.exists(data_dir):
        print(f"[Error] Data directory not found: {data_dir}")
        return

    # 1. Initialize Auditor
    cfg = load_l2_pipeline_config()
    auditor = OmegaPhysicsAuditor(data_dir=data_dir, output_dir=audit_out, cfg=cfg)
    
    print(f"[Audit] Scanning {len(auditor.files)} files in {data_dir}...")
    
    # 2. Run Audit
    try:
        metrics = auditor.run_continuous_calibration()
        
        print("\n--- Audit Results ---")
        print(json.dumps(metrics, indent=4))
        
        # 3. Final Verification
        snr = metrics.get("Topo_SNR", 0)
        ortho = metrics.get("Orthogonality", 0)
        
        print(f"\n[Verify] Topo_SNR: {snr if snr is not None else 0:.4f}")
        print(f"[Verify] Orthogonality: {ortho if ortho is not None else 0:.4f}")
        
        if snr and snr > 0:
            print("[Pass] Structural signal detected (SNR > 0).")
        else:
            print("[Warn] Low structural signal.")
            
        print(f"[Done] Audit report saved to {audit_out}/production_config.json")
        
    except Exception as e:
        print(f"[Error] Audit failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()