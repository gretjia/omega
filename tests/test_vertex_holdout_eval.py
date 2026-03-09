import json
import pickle
import sys
from argparse import Namespace
from pathlib import Path

import polars as pl
import pytest
import xgboost as xgb

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config import FEATURE_COLS
from tools import evaluate_xgb_on_base_matrix as holdout_eval


def _row(date: str, time_value: int, t1_fwd_return: float, offset: float) -> dict:
    row = {
        "date": date,
        "time": time_value,
        "epiplexity": 1.0,
        "is_energy_active": True,
        "sigma_eff": 1.0,
        "singularity_vector": 0.25,
        "spoof_ratio": 1.0,
        "srl_resid": 3.0,
        "t1_fwd_return": t1_fwd_return,
        "topo_area": 1.0,
        "topo_energy": 3.0,
    }
    for idx, col in enumerate(FEATURE_COLS):
        row[col] = float(idx) + offset
    return row


def _write_eval_payload(path: Path, matrix_path: Path) -> None:
    args = Namespace(
        base_matrix_uri=str(matrix_path),
        expected_date_prefix="2025",
        singularity_threshold=0.10,
        signal_epi_threshold=0.5,
        srl_resid_sigma_mult=2.0,
        topo_energy_min=2.0,
        dataset_role="outer_holdout",
    )
    datasets = holdout_eval._prepare_holdout_dataset(args, feature_cols=list(FEATURE_COLS))
    dtrain = datasets["dholdout"]
    booster = xgb.train(
        params={
            "objective": "binary:logistic",
            "eval_metric": "auc",
            "tree_method": "hist",
            "max_depth": 3,
            "eta": 0.2,
            "seed": 42,
        },
        dtrain=dtrain,
        num_boost_round=6,
    )
    with path.open("wb") as f:
        pickle.dump({"model": booster, "scaler": None, "feature_cols": list(FEATURE_COLS)}, f)


def test_prepare_holdout_dataset_asserts_date_prefix(tmp_path: Path) -> None:
    matrix_path = tmp_path / "base_matrix_holdout_2025.parquet"
    df = pl.DataFrame(
        [
            _row("20250102", 1, 0.02, 0.0),
            _row("20250102", 1, -0.01, 0.5),
            _row("20250103", 1, 0.03, 1.0),
            _row("20250103", 1, -0.02, 1.5),
        ]
    )
    df.write_parquet(matrix_path)

    args = Namespace(
        base_matrix_uri=str(matrix_path),
        expected_date_prefix="2025",
        singularity_threshold=0.10,
        signal_epi_threshold=0.5,
        srl_resid_sigma_mult=2.0,
        topo_energy_min=2.0,
        dataset_role="outer_holdout",
    )
    datasets = holdout_eval._prepare_holdout_dataset(args, feature_cols=list(FEATURE_COLS))

    assert datasets["summary"]["base_rows"] == 4
    assert datasets["summary"]["eval_rows"] == 4
    assert datasets["summary"]["scope_diag"]["date_prefix_assertion_passed"] is True
    assert datasets["summary"]["scope_diag"]["date_min"] == "20250102"
    assert datasets["summary"]["scope_diag"]["date_max"] == "20250103"


def test_prepare_holdout_dataset_rejects_scope_mismatch(tmp_path: Path) -> None:
    matrix_path = tmp_path / "base_matrix_holdout_bad.parquet"
    df = pl.DataFrame(
        [
            _row("20250102", 1, 0.02, 0.0),
            _row("20250102", 1, -0.01, 0.5),
            _row("20240201", 1, 0.03, 1.0),
            _row("20240201", 1, -0.02, 1.5),
        ]
    )
    df.write_parquet(matrix_path)

    args = Namespace(
        base_matrix_uri=str(matrix_path),
        expected_date_prefix="2025",
        singularity_threshold=0.10,
        signal_epi_threshold=0.5,
        srl_resid_sigma_mult=2.0,
        topo_energy_min=2.0,
        dataset_role="outer_holdout",
    )
    with pytest.raises(RuntimeError, match="holdout_scope_prefix_mismatch"):
        holdout_eval._prepare_holdout_dataset(args, feature_cols=list(FEATURE_COLS))


def test_evaluate_holdout_writes_metrics(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    matrix_path = tmp_path / "base_matrix_holdout_2025.parquet"
    model_path = tmp_path / "omega_xgb_final.pkl"
    output_root = tmp_path / "output"
    df = pl.DataFrame(
        [
            _row("20250102", 1, 0.02, 0.0),
            _row("20250102", 1, -0.01, 0.5),
            _row("20250103", 1, 0.03, 1.0),
            _row("20250103", 1, -0.02, 1.5),
            _row("20250106", 1, 0.04, 2.0),
            _row("20250106", 1, -0.03, 2.5),
        ]
    )
    df.write_parquet(matrix_path)
    _write_eval_payload(model_path, matrix_path)

    monkeypatch.setattr(
        "sys.argv",
        [
            "evaluate_xgb_on_base_matrix.py",
            "--base-matrix-uri",
            str(matrix_path),
            "--model-uri",
            str(model_path),
            "--output-uri",
            str(output_root),
            "--dataset-role",
            "outer_holdout",
            "--expected-date-prefix",
            "2025",
        ],
    )
    holdout_eval.main()

    metrics = json.loads((output_root / "holdout_metrics.json").read_text(encoding="utf-8"))
    assert metrics["status"] == "completed"
    assert metrics["dataset_role"] == "outer_holdout"
    assert metrics["dataset_summary"]["eval_rows"] == 6
    assert metrics["dataset_summary"]["scope_diag"]["date_prefix_assertion_passed"] is True
    assert 0.0 <= metrics["auc"] <= 1.0
