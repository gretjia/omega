import tempfile
import time
import unittest
from pathlib import Path
import sys
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.stage2_physics_compute import _dedupe_l1_files_by_date


class TestStage2InputDedupe(unittest.TestCase):
    def test_keeps_newest_file_per_date(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a_old = root / "20230103_aaaaaaa.parquet"
            a_new = root / "20230103_bbbbbbb.parquet"
            b = root / "20230104_ccccccc.parquet"
            misc = root / "custom_name.parquet"

            for p in (a_old, a_new, b, misc):
                p.touch()

            now = time.time()
            old_ts = now - 10
            new_ts = now
            b_ts = now - 5
            misc_ts = now - 3

            os.utime(a_old, (old_ts, old_ts))
            os.utime(a_new, (new_ts, new_ts))
            os.utime(b, (b_ts, b_ts))
            os.utime(misc, (misc_ts, misc_ts))

            selected, dropped = _dedupe_l1_files_by_date(
                [str(a_old), str(a_new), str(b), str(misc)]
            )

            self.assertIn(str(a_new), selected)
            self.assertIn(str(b), selected)
            self.assertIn(str(misc), selected)
            self.assertNotIn(str(a_old), selected)
            self.assertEqual(dropped, [str(a_old)])


if __name__ == "__main__":
    unittest.main()
