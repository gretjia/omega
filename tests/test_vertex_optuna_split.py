import sys
from argparse import Namespace
from pathlib import Path

import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config import FEATURE_COLS
from tools.launch_vertex_swarm_optuna import _assert_empty_output_uri, _submit_one_worker
from tools.run_optuna_sweep import _canonical_fingerprint, _prepare_temporal_split, _trial_payload


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


def test_prepare_temporal_split_builds_train_val_once(tmp_path: Path) -> None:
    matrix_path = tmp_path / "base_matrix_train_2023_2024.parquet"
    df = pl.DataFrame(
        [
            _row("20230105", 1, 0.02, 0.0),
            _row("20230105", 1, -0.01, 0.5),
            _row("20240108", 1, 0.03, 1.0),
            _row("20240108", 1, -0.02, 1.5),
        ]
    )
    df.write_parquet(matrix_path)

    args = Namespace(
        base_matrix_uri=str(matrix_path),
        train_year="2023",
        val_year="2024",
        singularity_threshold=0.10,
        signal_epi_threshold=0.5,
        srl_resid_sigma_mult=2.0,
        topo_energy_min=2.0,
        weight_mode="physics_abs_singularity",
        learner_mode="binary_logistic_sign",
    )
    datasets = _prepare_temporal_split(args)

    assert datasets["dtrain"].num_row() == 2
    assert datasets["dval"].num_row() == 2
    assert datasets["summary"]["train_rows"] == 2
    assert datasets["summary"]["val_rows"] == 2
    assert datasets["summary"]["dtrain_build_count"] == 1
    assert datasets["summary"]["dval_build_count"] == 1
    assert datasets["summary"]["temporal_assertion_passed"] is True
    assert datasets["summary"]["train_max_date"] == "20230105"
    assert datasets["summary"]["val_min_date"] == "20240108"
    assert datasets["summary"]["learner_mode"] == "binary_logistic_sign"
    assert datasets["summary"]["weight_mode"] == "physics_abs_singularity"
    assert datasets["canonical_fingerprint"] == _canonical_fingerprint(args)


def test_prepare_temporal_split_supports_abs_excess_return_weights(tmp_path: Path) -> None:
    matrix_path = tmp_path / "base_matrix_train_2023_2024.parquet"
    df = pl.DataFrame(
        [
            _row("20230105", 1, 0.06, 0.0),
            _row("20230105", 1, -0.01, 0.5),
            _row("20240108", 1, 0.09, 1.0),
            _row("20240108", 1, -0.02, 1.5),
        ]
    )
    df.write_parquet(matrix_path)

    args = Namespace(
        base_matrix_uri=str(matrix_path),
        train_year="2023",
        val_year="2024",
        singularity_threshold=0.10,
        signal_epi_threshold=0.5,
        srl_resid_sigma_mult=2.0,
        topo_energy_min=2.0,
        weight_mode="abs_excess_return",
        learner_mode="binary_logistic_sign",
    )
    datasets = _prepare_temporal_split(args)

    assert datasets["summary"]["weight_mode"] == "abs_excess_return"
    assert datasets["summary"]["train_weight_sum"] > 0.0
    assert datasets["summary"]["val_weight_sum"] > 0.0


def test_prepare_temporal_split_supports_sqrt_abs_excess_return_weights(tmp_path: Path) -> None:
    matrix_path = tmp_path / "base_matrix_train_2023_2024.parquet"
    df = pl.DataFrame(
        [
            _row("20230105", 1, 0.09, 0.0),
            _row("20230105", 1, -0.01, 0.5),
            _row("20240108", 1, 0.16, 1.0),
            _row("20240108", 1, -0.04, 1.5),
        ]
    )
    df.write_parquet(matrix_path)

    args = Namespace(
        base_matrix_uri=str(matrix_path),
        train_year="2023",
        val_year="2024",
        singularity_threshold=0.10,
        signal_epi_threshold=0.5,
        srl_resid_sigma_mult=2.0,
        topo_energy_min=2.0,
        weight_mode="sqrt_abs_excess_return",
        learner_mode="binary_logistic_sign",
    )
    datasets = _prepare_temporal_split(args)

    assert datasets["summary"]["weight_mode"] == "sqrt_abs_excess_return"
    assert datasets["summary"]["train_weight_sum"] > 0.0
    assert datasets["summary"]["val_weight_sum"] > 0.0


def test_prepare_temporal_split_supports_pow_0p75_abs_excess_return_weights(tmp_path: Path) -> None:
    matrix_path = tmp_path / "base_matrix_train_2023_2024.parquet"
    df = pl.DataFrame(
        [
            _row("20230105", 1, 0.09, 0.0),
            _row("20230105", 1, -0.01, 0.5),
            _row("20240108", 1, 0.16, 1.0),
            _row("20240108", 1, -0.04, 1.5),
        ]
    )
    df.write_parquet(matrix_path)

    args = Namespace(
        base_matrix_uri=str(matrix_path),
        train_year="2023",
        val_year="2024",
        singularity_threshold=0.10,
        signal_epi_threshold=0.5,
        srl_resid_sigma_mult=2.0,
        topo_energy_min=2.0,
        weight_mode="pow_0p75_abs_excess_return",
        learner_mode="binary_logistic_sign",
    )
    datasets = _prepare_temporal_split(args)

    assert datasets["summary"]["weight_mode"] == "pow_0p75_abs_excess_return"
    assert datasets["summary"]["train_weight_sum"] > 0.0
    assert datasets["summary"]["val_weight_sum"] > 0.0


def test_prepare_temporal_split_supports_path_b_regression_labels(tmp_path: Path) -> None:
    matrix_path = tmp_path / "base_matrix_train_2023_2024.parquet"
    df = pl.DataFrame(
        [
            _row("20230105", 1, 0.06, 0.0),
            _row("20230105", 1, -0.01, 0.5),
            _row("20240108", 1, 0.09, 1.0),
            _row("20240108", 1, -0.02, 1.5),
        ]
    )
    df.write_parquet(matrix_path)

    args = Namespace(
        base_matrix_uri=str(matrix_path),
        train_year="2023",
        val_year="2024",
        singularity_threshold=0.10,
        signal_epi_threshold=0.5,
        srl_resid_sigma_mult=2.0,
        topo_energy_min=2.0,
        weight_mode="physics_abs_singularity",
        learner_mode="reg_squarederror_excess_return",
    )
    datasets = _prepare_temporal_split(args)

    assert datasets["summary"]["learner_mode"] == "reg_squarederror_excess_return"
    assert datasets["dtrain"].num_row() == 2
    assert datasets["dval"].num_row() == 2


def test_trial_payload_does_not_require_runtime_trial_state() -> None:
    class DummyTrial:
        number = 7

    payload = _trial_payload(
        DummyTrial(),
        params={
            "max_depth": 4,
            "learning_rate": 0.03,
            "subsample": 0.9,
            "colsample_bytree": 0.8,
            "min_child_weight": 1.0,
            "gamma": 0.0,
            "reg_lambda": 1.0,
            "reg_alpha": 0.0,
            "num_boost_round": 120,
        },
        auc=0.71,
        alpha_top_decile=0.02,
        alpha_top_quintile=0.01,
        learner_mode="binary_logistic_sign",
    )
    assert payload["trial_number"] == 7
    assert payload["state"] == "COMPLETE"
    assert payload["learner_mode"] == "binary_logistic_sign"
    assert payload["objective_metric"] == "val_auc"
    assert payload["auc_guardrail_passed"] is True


def test_trial_payload_alpha_objective_respects_auc_guardrail() -> None:
    class DummyTrial:
        number = 8

    payload = _trial_payload(
        DummyTrial(),
        params={
            "max_depth": 4,
            "learning_rate": 0.03,
            "subsample": 0.9,
            "colsample_bytree": 0.8,
            "min_child_weight": 1.0,
            "gamma": 0.0,
            "reg_lambda": 1.0,
            "reg_alpha": 0.0,
            "num_boost_round": 120,
        },
        auc=0.71,
        alpha_top_decile=0.02,
        alpha_top_quintile=0.01,
        objective_metric="alpha_top_quintile",
        min_val_auc=0.75,
        learner_mode="binary_logistic_sign",
    )
    assert payload["objective_metric"] == "alpha_top_quintile"
    assert payload["raw_objective_value"] == 0.01
    assert payload["auc_guardrail_enabled"] is True
    assert payload["auc_guardrail_passed"] is False
    assert payload["objective_value"] < 0.0


def test_trial_payload_alpha_objective_can_disable_auc_guardrail() -> None:
    class DummyTrial:
        number = 9

    payload = _trial_payload(
        DummyTrial(),
        params={
            "max_depth": 4,
            "learning_rate": 0.03,
            "subsample": 0.9,
            "colsample_bytree": 0.8,
            "min_child_weight": 1.0,
            "gamma": 0.0,
            "reg_lambda": 1.0,
            "reg_alpha": 0.0,
            "num_boost_round": 120,
        },
        auc=0.44,
        alpha_top_decile=0.02,
        alpha_top_quintile=0.01,
        objective_metric="alpha_top_quintile",
        min_val_auc=0.0,
        learner_mode="reg_squarederror_excess_return",
    )
    assert payload["learner_mode"] == "reg_squarederror_excess_return"
    assert payload["auc_guardrail_enabled"] is False
    assert payload["auc_guardrail_passed"] is True
    assert payload["objective_value"] == 0.01


def test_launch_worker_seed_offsets_by_worker_index() -> None:
    captured = {}

    def fake_submit_job(**kwargs):
        captured["script_args"] = list(kwargs["script_args"])
        return {"resource_name": "dummy"}

    args = Namespace(
        base_matrix_uri="gs://bucket/train.parquet",
        machine_type="n2-standard-16",
        n_trials_per_worker=10,
        train_year="2023",
        val_year="2024",
        objective_metric="alpha_top_quintile",
        min_val_auc=0.75,
        weight_mode="abs_excess_return",
        code_bundle_uri="gs://bucket/code.zip",
        sync=False,
        spot=True,
        force_gcloud_fallback=True,
        sync_timeout_sec=0,
        base_seed=42,
    )
    attempt = _submit_one_worker(
        submit_job=fake_submit_job,
        args=args,
        script_path="tools/run_optuna_sweep.py",
        worker_id="w03",
        output_uri="gs://bucket/results/w03",
        spot=True,
    )
    script_args = captured["script_args"]
    seed_idx = script_args.index("--seed")
    assert script_args[seed_idx + 1] == "45"
    objective_idx = script_args.index("--objective-metric")
    auc_idx = script_args.index("--min-val-auc")
    weight_idx = script_args.index("--weight-mode")
    assert script_args[objective_idx + 1] == "alpha_top_quintile"
    assert script_args[auc_idx + 1] == "0.75"
    assert script_args[weight_idx + 1] == "abs_excess_return"
    assert attempt["seed"] == 45


def test_assert_empty_output_uri_rejects_nonempty_local_prefix(tmp_path: Path) -> None:
    output_root = tmp_path / "existing"
    output_root.mkdir()
    (output_root / "marker.json").write_text("{}", encoding="utf-8")
    try:
        _assert_empty_output_uri(str(output_root), label="results_prefix_uri")
    except RuntimeError as exc:
        assert "results_prefix_uri_not_empty" in str(exc)
    else:
        raise AssertionError("expected non-empty prefix rejection")
