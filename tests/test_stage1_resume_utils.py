import tempfile
import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.stage1_resume_utils import (
    clear_stale_done_marker,
    ensure_done_for_existing_parquet,
    find_existing_done_for_date,
)


class TestStage1ResumeUtils(unittest.TestCase):
    def test_find_existing_done_for_date_ignores_stale_done(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            stale_done = root / "20230103_deadbee.parquet.done"
            valid_parquet = root / "20230103_fbd5c8b.parquet"
            valid_done = root / "20230103_fbd5c8b.parquet.done"

            stale_done.touch()
            valid_parquet.touch()
            valid_done.touch()

            found = find_existing_done_for_date(root, "20230103")
            self.assertEqual(found, valid_done)

    def test_clear_stale_done_marker(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out_path = root / "20230104_fbd5c8b.parquet"
            done_path = root / "20230104_fbd5c8b.parquet.done"
            done_path.touch()

            changed = clear_stale_done_marker(out_path, done_path)
            self.assertTrue(changed)
            self.assertFalse(done_path.exists())

    def test_ensure_done_for_existing_parquet(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out_path = root / "20230105_fbd5c8b.parquet"
            done_path = root / "20230105_fbd5c8b.parquet.done"
            out_path.touch()

            changed = ensure_done_for_existing_parquet(out_path, done_path)
            self.assertTrue(changed)
            self.assertTrue(done_path.exists())


if __name__ == "__main__":
    unittest.main()
