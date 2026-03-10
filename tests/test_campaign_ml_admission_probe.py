import sys
from pathlib import Path

import pytest
import numpy as np

pl = pytest.importorskip("polars")

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import run_campaign_ml_admission_probe as admission_probe


def _derived_frame() -> pl.DataFrame:
    rows = []
    dates = ["20240102", "20240103", "20240104", "20240105", "20240108", "20240109"]
    symbols = ["AAA", "BBB", "CCC", "DDD", "EEE"]
    base_values = {
        "AAA": [-1.0, -2.0, -5.0, -6.0, -7.0, -8.0],
        "BBB": [-0.5, -1.0, -2.0, -2.5, -3.0, -3.5],
        "CCC": [0.5, 1.0, 2.0, 2.5, 3.0, 3.5],
        "DDD": [-0.2, -0.4, -0.8, -1.0, -1.2, -1.4],
        "EEE": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
    }
    for di, pure_date in enumerate(dates):
        for symbol in symbols:
            psi = base_values[symbol][di]
            rows.append(
                {
                    "symbol": symbol,
                    "pure_date": pure_date,
                    "dPsiAmpE_10d": psi,
                    "FreshAmpStar_10d": psi / 2.0,
                    "PsiAmpE_10d": psi * 1.5,
                    "PsiAmpStar_10d": psi * 1.2,
                    "OmegaAmpE_10d": abs(psi) / 10.0,
                    "OmegaAmpStar_10d": abs(psi) / 12.0,
                    "vol20d": 0.02,
                    "pulse_count": 2 + di,
                    "pulse_concentration": 0.3 + (di / 20.0),
                    "barrier_10d": -1 if symbol == "AAA" else 0,
                    "excess_ret_t1_to_10d": -0.05 if symbol == "AAA" else (-0.01 if symbol == "BBB" else 0.02),
                }
            )
    return pl.DataFrame(rows)


def test_admission_mask_uses_negative_side_only() -> None:
    admitted, coverage = admission_probe.build_admission_frame_from_derived(_derived_frame(), threshold_pct=90.0)

    assert coverage["n_rows_admitted"] > 0
    assert admitted.select((pl.col("dPsiAmpE_10d") < 0).all()).item() is True
    assert admitted.select((pl.col("__admission_mask") == True).all()).item() is True


def test_no_rows_outside_admission_enter_training() -> None:
    admitted, _ = admission_probe.build_admission_frame_from_derived(_derived_frame(), threshold_pct=90.0)
    folds = admission_probe.build_forward_folds(admitted["pure_date"].unique().to_list())
    fold = folds[0]
    train_df = admitted.filter(pl.col("pure_date").is_in(fold["train_dates"]))

    assert train_df.height > 0
    assert train_df.select((pl.col("__admission_mask") == True).all()).item() is True
    assert train_df.select((pl.col("dPsiAmpE_10d") < 0).all()).item() is True


def test_forward_folds_do_not_leak_future_dates() -> None:
    folds = admission_probe.build_forward_folds(
        ["20240102", "20240103", "20240104", "20240105", "20240108", "20240109", "20240110", "20240111", "20240112", "20240115"]
    )

    for fold in folds:
        assert max(fold["train_dates"]) < min(fold["val_dates"])


def test_raw_same_count_baseline_is_inside_admitted_set_only() -> None:
    admitted, _ = admission_probe.build_admission_frame_from_derived(_derived_frame(), threshold_pct=90.0)
    val_df = admitted.with_columns(pl.Series("__pred_prob", np.linspace(0.1, 0.9, admitted.height), dtype=pl.Float64))

    summary = admission_probe.evaluate_selection_fraction(val_df, alpha=0.5)

    assert summary["model"]["n_rows_scored"] > 0
    assert summary["raw_same_count"]["n_rows_scored"] > 0
    assert summary["raw_same_count"]["n_rows_scored"] <= admitted.height
    assert admitted.select((pl.col("__admission_mask") == True).all()).item() is True
