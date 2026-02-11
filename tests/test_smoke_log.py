
import os
import subprocess
import unittest

class TestSmokeLog(unittest.TestCase):
    def test_log_creation(self):
        # Run the smoke test
        cmd = ["python", "pipeline_runner.py", "--stage", "frame", "--smoke"]
        subprocess.run(cmd, check=True)
        
        # Check if a log file was created in audit/
        # We expect something like audit/_pipeline_smoke_test.log
        log_found = False
        for f in os.listdir("audit"):
            if "smoke" in f.lower() and f.endswith(".log"):
                log_found = True
                break
        
        self.assertTrue(log_found, "Smoke test log file not found in audit/")

if __name__ == "__main__":
    unittest.main()
