
import os
import subprocess
import unittest
import polars as pl

class TestFramerOutput(unittest.TestCase):
    def test_parquet_generation(self):
        # Ensure output directory is clean for the test file
        output_dir = "D:/Omega_frames/v50/output"
        test_file = "20240201.parquet"
        test_path = os.path.join(output_dir, test_file)
        if os.path.exists(test_path):
            os.remove(test_path)
            
        # Run the smoke test
        cmd = ["python", "pipeline_runner.py", "--stage", "frame", "--smoke"]
        subprocess.run(cmd, check=True)
        
        # Check if any parquet file was created
        files = [f for f in os.listdir(output_dir) if f.endswith(".parquet")]
        self.assertTrue(len(files) > 0, f"No Parquet output found in {output_dir}")
        
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
