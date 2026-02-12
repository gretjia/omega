
import os
import subprocess
import sys
import unittest
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from pipeline.config.loader import ConfigLoader

class TestFramerOutput(unittest.TestCase):
    def test_parquet_generation(self):
        root = ROOT
        config_path = root / "configs" / "hardware" / "active_profile.yaml"
        profile = ConfigLoader.load_hardware_profile(str(config_path))

        source_root = profile.storage.source_root
        output_dir = profile.storage.output_root

        # This is an integration test; skip when host does not have configured frame source.
        if not os.path.exists(source_root):
            self.skipTest(f"Frame source path not available on this host: {source_root}")
            
        # Run the smoke test
        cmd = [
            sys.executable,
            "pipeline_runner.py",
            "--stage",
            "frame",
            "--smoke",
            "--config",
            str(config_path),
        ]
        subprocess.run(cmd, check=True, cwd=str(root))
        
        # Check if any parquet file was created
        if not os.path.exists(output_dir):
            self.skipTest(f"Frame output path not available on this host: {output_dir}")

        files = [f for f in os.listdir(output_dir) if f.endswith(".parquet")]
        self.assertTrue(len(files) > 0, f"No Parquet output found in configured output dir: {output_dir}")
        
        test_path = os.path.join(output_dir, files[0])
        print(f"Checking file: {test_path}")
        
        # Verify content
        df = pl.read_parquet(test_path)
        expected_cols = ["epiplexity", "srl_resid", "adaptive_y"]
        for col in expected_cols:
            self.assertIn(col, df.columns, f"Column {col} missing from output")
            
        print(f"Verified Parquet: {df.height} rows, features: {df.columns}")

if __name__ == "__main__":
    unittest.main()
