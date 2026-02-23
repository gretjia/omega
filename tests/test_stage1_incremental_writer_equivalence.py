import csv
import tempfile
import unittest
from pathlib import Path
import sys

import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import load_l2_pipeline_config
from omega_core.omega_etl import build_l1_base_ticks
from tools.stage1_incremental_writer import write_l1_incremental_parquet


def _write_csv(path: Path, headers: list[str], rows: list[list[object]], encoding: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=encoding, newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


class TestStage1IncrementalWriterEquivalence(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = load_l2_pipeline_config()
        self.encoding = self.cfg.io.csv_encoding or "utf-8"

    def _assert_frame_equal(self, expected: pl.DataFrame, actual: pl.DataFrame) -> None:
        self.assertEqual(expected.columns, actual.columns)
        self.assertEqual(expected.height, actual.height)
        self.assertEqual(expected.to_dict(as_series=False), actual.to_dict(as_series=False))

    def test_unified_csv_equivalence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            headers = [
                "万得代码",
                "交易所代码",
                "自然日",
                "时间",
                "成交价",
                "成交量",
                "成交额",
                "申买价1",
                "申买量1",
                "申卖价1",
                "申卖量1",
            ]
            rows_a = [
                ["000001.SZ", "SZ", "20230103", 93000000, 10.0, 100, 1000, 9.9, 1000, 10.1, 1000],
                ["000001.SZ", "SZ", "20230103", 93003000, 10.2, 130, 1326, 10.1, 1100, 10.3, 1100],
                ["000001.SZ", "SZ", "20230103", 93006000, 10.3, 160, 1648, 10.2, 1200, 10.4, 1200],
            ]
            rows_b = [
                ["000002.SZ", "SZ", "20230103", 93000000, 20.0, 200, 4000, 19.9, 900, 20.1, 900],
                ["000002.SZ", "SZ", "20230103", 93003000, 20.2, 260, 5252, 20.1, 950, 20.3, 950],
                ["000002.SZ", "SZ", "20230103", 93006000, 20.1, 300, 6030, 20.0, 980, 20.2, 980],
            ]

            f_a = root / "20230103" / "000001.SZ" / "000001.SZ.csv"
            f_b = root / "20230103" / "000002.SZ" / "000002.SZ.csv"
            _write_csv(f_a, headers, rows_a, self.encoding)
            _write_csv(f_b, headers, rows_b, self.encoding)

            csvs = [str(f_a), str(f_b)]
            expected = build_l1_base_ticks(csvs, self.cfg)

            out = root / "out_unified.parquet"
            written_rows = write_l1_incremental_parquet(
                csv_paths=csvs,
                cfg=self.cfg,
                tmp_parquet_path=out,
                symbol_batch_size=1,
                build_fn=build_l1_base_ticks,
            )
            actual = pl.read_parquet(out)

            self.assertEqual(written_rows, expected.height)
            self._assert_frame_equal(expected, actual)

    def test_split_csv_equivalence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            quote_headers = ["时间", "申买价1", "申买量1", "申卖价1", "申卖量1"]
            trade_headers = ["时间", "成交价格", "成交数量", "成交金额", "万得代码", "交易所代码", "自然日"]

            q_a = [
                [93000000, 9.9, 1000, 10.1, 1000],
                [93003000, 10.1, 1100, 10.3, 1100],
                [93006000, 10.2, 1200, 10.4, 1200],
            ]
            t_a = [
                [93000500, 10.0, 100, 1000, "000001.SZ", "SZ", "20230103"],
                [93003500, 10.2, 130, 1326, "000001.SZ", "SZ", "20230103"],
                [93006500, 10.3, 160, 1648, "000001.SZ", "SZ", "20230103"],
            ]
            q_b = [
                [93000000, 19.9, 900, 20.1, 900],
                [93003000, 20.1, 950, 20.3, 950],
                [93006000, 20.0, 980, 20.2, 980],
            ]
            t_b = [
                [93000500, 20.0, 200, 4000, "000002.SZ", "SZ", "20230103"],
                [93003500, 20.2, 260, 5252, "000002.SZ", "SZ", "20230103"],
                [93006500, 20.1, 300, 6030, "000002.SZ", "SZ", "20230103"],
            ]
            q_c = [
                [93000000, 29.9, 800, 30.1, 800],
                [93003000, 30.1, 820, 30.3, 820],
                [93006000, 30.0, 840, 30.2, 840],
            ]
            t_c = [
                [93000500, 30.0, 300, 9000, "000003.SZ", "SZ", "20230103"],
                [93003500, 30.2, 340, 10268, "000003.SZ", "SZ", "20230103"],
                [93006500, 30.1, 380, 11438, "000003.SZ", "SZ", "20230103"],
            ]

            qa_path = root / "20230103" / "000001.SZ" / "行情.csv"
            ta_path = root / "20230103" / "000001.SZ" / "逐笔成交.csv"
            qb_path = root / "20230103" / "000002.SZ" / "行情.csv"
            tb_path = root / "20230103" / "000002.SZ" / "逐笔成交.csv"
            qc_path = root / "20230103" / "000003.SZ" / "行情.csv"
            tc_path = root / "20230103" / "000003.SZ" / "逐笔成交.csv"

            _write_csv(qa_path, quote_headers, q_a, self.encoding)
            _write_csv(ta_path, trade_headers, t_a, self.encoding)
            _write_csv(qb_path, quote_headers, q_b, self.encoding)
            _write_csv(tb_path, trade_headers, t_b, self.encoding)
            _write_csv(qc_path, quote_headers, q_c, self.encoding)
            _write_csv(tc_path, trade_headers, t_c, self.encoding)

            csvs = [str(qa_path), str(ta_path), str(qb_path), str(tb_path), str(qc_path), str(tc_path)]
            expected = build_l1_base_ticks(csvs, self.cfg)

            out = root / "out_split.parquet"
            written_rows = write_l1_incremental_parquet(
                csv_paths=csvs,
                cfg=self.cfg,
                tmp_parquet_path=out,
                symbol_batch_size=2,
                build_fn=build_l1_base_ticks,
            )
            actual = pl.read_parquet(out)

            self.assertEqual(written_rows, expected.height)
            self._assert_frame_equal(expected, actual)

    def test_schema_alignment_across_batches(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p_a = root / "20230103" / "000001.SZ" / "a.csv"
            p_b = root / "20230103" / "000002.SZ" / "b.csv"
            p_a.parent.mkdir(parents=True, exist_ok=True)
            p_b.parent.mkdir(parents=True, exist_ok=True)
            p_a.write_text("x", encoding="utf-8")
            p_b.write_text("x", encoding="utf-8")

            def fake_build(csv_path_or_paths, _cfg):
                path_str = (
                    str(csv_path_or_paths[0])
                    if isinstance(csv_path_or_paths, list)
                    else str(csv_path_or_paths)
                )
                if "000001.SZ" in path_str:
                    return pl.DataFrame(
                        {
                            "symbol": ["000001.SZ"],
                            "time": [93000000],
                            "price": [10.1],
                            "ask_v2": [1200.0],
                        }
                    )
                return pl.DataFrame(
                    {
                        "symbol": ["000002.SZ"],
                        "time": pl.Series("time", [93000000], dtype=pl.Int32),
                        "price": [20],  # int on purpose
                        # ask_v2 intentionally missing
                    }
                )

            out = root / "out_schema_align.parquet"
            written_rows = write_l1_incremental_parquet(
                csv_paths=[str(p_a), str(p_b)],
                cfg=self.cfg,
                tmp_parquet_path=out,
                symbol_batch_size=1,
                build_fn=fake_build,
            )
            actual = pl.read_parquet(out)

            self.assertEqual(written_rows, 2)
            self.assertEqual(actual.columns, ["symbol", "time", "price", "ask_v2"])
            self.assertEqual(actual.height, 2)
            self.assertIsNone(actual.to_dict(as_series=False)["ask_v2"][1])

    def test_schema_alignment_within_same_batch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p_a = root / "20230103" / "000001.SZ" / "a.csv"
            p_b = root / "20230103" / "000002.SZ" / "b.csv"
            p_a.parent.mkdir(parents=True, exist_ok=True)
            p_b.parent.mkdir(parents=True, exist_ok=True)
            p_a.write_text("x", encoding="utf-8")
            p_b.write_text("x", encoding="utf-8")

            def fake_build(csv_path_or_paths, _cfg):
                path_str = (
                    str(csv_path_or_paths[0])
                    if isinstance(csv_path_or_paths, list)
                    else str(csv_path_or_paths)
                )
                if "000001.SZ" in path_str:
                    return pl.DataFrame(
                        {
                            "symbol": ["000001.SZ"],
                            "time": [93000000],
                            "price": [10.1],
                            "ask_v2": [1200.0],
                        }
                    )
                return pl.DataFrame(
                    {
                        "symbol": ["000002.SZ"],
                        "time": [93000000],
                        "price": [20.2],
                        "bid_v2": [900.0],
                    }
                )

            out = root / "out_schema_align_same_batch.parquet"
            written_rows = write_l1_incremental_parquet(
                csv_paths=[str(p_a), str(p_b)],
                cfg=self.cfg,
                tmp_parquet_path=out,
                symbol_batch_size=2,  # force mixed schemas into one concat batch
                build_fn=fake_build,
            )
            actual = pl.read_parquet(out)

            self.assertEqual(written_rows, 2)
            self.assertEqual(actual.columns, ["symbol", "time", "price", "ask_v2", "bid_v2"])
            self.assertEqual(actual.height, 2)
            rows = actual.to_dict(as_series=False)
            self.assertIsNone(rows["bid_v2"][0])
            self.assertIsNone(rows["ask_v2"][1])


if __name__ == "__main__":
    unittest.main()
