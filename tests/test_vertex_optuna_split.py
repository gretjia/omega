import sys
from argparse import Namespace
from pathlib import Path

import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config import FEATURE_COLS
from tools.launch_vertex_swarm_optuna import _assert_empty_output_uri, _submit_one_worker, _validate_launch_contract
from tools.run_optuna_sweep import (
    _canonical_fingerprint,
    _prepare_temporal_split,
    _trial_payload,
    _validate_objective_runtime_contract,
)


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


def test_prepare_temporal_split_supports_pow_0p875_abs_excess_return_weights(tmp_path: Path) -> None:
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
        weight_mode="pow_0p875_abs_excess_return",
        learner_mode="binary_logistic_sign",
    )
    datasets = _prepare_temporal_split(args)

    assert datasets["summary"]["weight_mode"] == "pow_0p875_abs_excess_return"
    assert datasets["summary"]["train_weight_sum"] > 0.0
    assert datasets["summary"]["val_weight_sum"] > 0.0


def test_prepare_temporal_split_supports_pow_0p625_abs_excess_return_weights(tmp_path: Path) -> None:
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
        weight_mode="pow_0p625_abs_excess_return",
        learner_mode="binary_logistic_sign",
    )
    datasets = _prepare_temporal_split(args)

    assert datasets["summary"]["weight_mode"] == "pow_0p625_abs_excess_return"
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
        weight_mode="none",
        learner_mode="reg_squarederror_excess_return",
    )
    datasets = _prepare_temporal_split(args)

    assert datasets["summary"]["learner_mode"] == "reg_squarederror_excess_return"
    assert datasets["summary"]["weight_mode"] == "none"
    assert datasets["summary"]["weighting_enabled"] is False
    assert datasets["summary"]["train_weight_sum"] is None
    assert datasets["summary"]["val_weight_sum"] is None
    assert datasets["dtrain"].num_row() == 2
    assert datasets["dval"].num_row() == 2


def test_prepare_temporal_split_supports_path_b_pseudohuber_labels(tmp_path: Path) -> None:
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
        weight_mode="none",
        learner_mode="reg_pseudohuber_excess_return",
    )
    datasets = _prepare_temporal_split(args)

    assert datasets["summary"]["learner_mode"] == "reg_pseudohuber_excess_return"
    assert datasets["summary"]["weight_mode"] == "none"
    assert datasets["summary"]["weighting_enabled"] is False
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
        val_spearman_ic=0.0,
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
        val_spearman_ic=0.0,
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
        val_spearman_ic=0.01,
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


def test_trial_payload_structural_tail_metric_returns_mean_when_guards_pass() -> None:
    class DummyTrial:
        number = 10

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
        auc=0.52,
        val_spearman_ic=0.0,
        alpha_top_decile=0.03,
        alpha_top_quintile=0.01,
        objective_metric="structural_tail_monotonicity_gate",
        min_val_auc=0.505,
        min_val_spearman_ic=0.0,
        learner_mode="binary_logistic_sign",
    )
    assert payload["objective_metric"] == "structural_tail_monotonicity_gate"
    assert payload["raw_objective_value"] == 0.02
    assert payload["auc_guardrail_passed"] is True
    assert payload["tail_monotonicity_passed"] is True
    assert payload["structural_guardrail_passed"] is True
    assert payload["objective_value"] == 0.02


def test_trial_payload_structural_tail_metric_penalizes_auc_floor_failure() -> None:
    class DummyTrial:
        number = 11

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
        auc=0.49,
        val_spearman_ic=0.0,
        alpha_top_decile=0.03,
        alpha_top_quintile=0.01,
        objective_metric="structural_tail_monotonicity_gate",
        min_val_auc=0.505,
        min_val_spearman_ic=0.0,
        learner_mode="binary_logistic_sign",
    )
    assert payload["auc_guardrail_passed"] is False
    assert payload["tail_monotonicity_passed"] is True
    assert payload["structural_guardrail_passed"] is False
    assert payload["objective_value"] < 0.0


def test_trial_payload_structural_tail_metric_penalizes_inverted_tail() -> None:
    class DummyTrial:
        number = 12

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
        auc=0.53,
        val_spearman_ic=0.0,
        alpha_top_decile=0.01,
        alpha_top_quintile=0.02,
        objective_metric="structural_tail_monotonicity_gate",
        min_val_auc=0.505,
        min_val_spearman_ic=0.0,
        learner_mode="binary_logistic_sign",
    )
    assert payload["auc_guardrail_passed"] is True
    assert payload["tail_monotonicity_passed"] is False
    assert payload["structural_guardrail_passed"] is False
    assert payload["objective_value"] < 0.0


def test_trial_payload_structural_tail_metric_uses_spearman_for_path_b() -> None:
    class DummyTrial:
        number = 13

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
        auc=0.48,
        val_spearman_ic=0.02,
        alpha_top_decile=0.03,
        alpha_top_quintile=0.01,
        objective_metric="structural_tail_monotonicity_gate",
        min_val_auc=0.0,
        min_val_spearman_ic=0.0,
        learner_mode="reg_squarederror_excess_return",
    )
    assert payload["structural_metric_name"] == "val_spearman_ic"
    assert payload["auc_guardrail_enabled"] is False
    assert payload["spearman_guardrail_enabled"] is True
    assert payload["spearman_guardrail_passed"] is True
    assert payload["tail_monotonicity_passed"] is True
    assert payload["structural_guardrail_passed"] is True
    assert payload["objective_value"] == 0.02


def test_trial_payload_regression_non_degeneracy_gate_penalizes_flat_predictions() -> None:
    class DummyTrial:
        number = 14

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
        auc=0.52,
        val_spearman_ic=0.03,
        alpha_top_decile=0.03,
        alpha_top_quintile=0.01,
        objective_metric="structural_tail_monotonicity_gate",
        min_val_auc=0.0,
        min_val_spearman_ic=0.02,
        learner_mode="reg_pseudohuber_excess_return",
        val_pred_std=0.0,
        rounded_unique_predictions=1,
        non_zero_feature_importance_count=0,
        enforce_non_degeneracy_gate=True,
    )
    assert payload["non_degeneracy_gate_enabled"] is True
    assert payload["non_degeneracy_passed"] is False
    assert payload["structural_guardrail_passed"] is False
    assert payload["objective_value"] < 0.0


def test_trial_payload_regression_non_degeneracy_gate_allows_live_predictions() -> None:
    class DummyTrial:
        number = 15

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
        auc=0.52,
        val_spearman_ic=0.03,
        alpha_top_decile=0.03,
        alpha_top_quintile=0.01,
        objective_metric="structural_tail_monotonicity_gate",
        min_val_auc=0.0,
        min_val_spearman_ic=0.02,
        learner_mode="reg_pseudohuber_excess_return",
        val_pred_std=0.01,
        rounded_unique_predictions=7,
        non_zero_feature_importance_count=5,
        enforce_non_degeneracy_gate=True,
    )
    assert payload["non_degeneracy_gate_enabled"] is True
    assert payload["non_degeneracy_passed"] is True
    assert payload["structural_guardrail_passed"] is True
    assert payload["objective_value"] == 0.02


def test_validate_objective_runtime_contract_supports_v647_binary_and_v648_path_b() -> None:
    args = Namespace(
        objective_metric="structural_tail_monotonicity_gate",
        min_val_auc=0.505,
        min_val_spearman_ic=0.0,
        weight_mode="sqrt_abs_excess_return",
        learner_mode="binary_logistic_sign",
    )
    _validate_objective_runtime_contract(args)

    path_b = Namespace(
        objective_metric="structural_tail_monotonicity_gate",
        min_val_auc=0.0,
        min_val_spearman_ic=0.0,
        weight_mode="none",
        learner_mode="reg_squarederror_excess_return",
    )
    _validate_objective_runtime_contract(path_b)

    path_b_huber = Namespace(
        objective_metric="structural_tail_monotonicity_gate",
        min_val_auc=0.0,
        min_val_spearman_ic=0.0,
        weight_mode="none",
        learner_mode="reg_pseudohuber_excess_return",
    )
    _validate_objective_runtime_contract(path_b_huber)

    bad_weight = Namespace(
        objective_metric="structural_tail_monotonicity_gate",
        min_val_auc=0.0,
        min_val_spearman_ic=0.0,
        weight_mode="sqrt_abs_excess_return",
        learner_mode="reg_squarederror_excess_return",
    )
    try:
        _validate_objective_runtime_contract(bad_weight)
    except RuntimeError as exc:
        assert "structural_tail_objective_requires_weight_mode" in str(exc)
    else:
        raise AssertionError("expected weight-mode lock failure")

    bad_floor = Namespace(
        objective_metric="structural_tail_monotonicity_gate",
        min_val_auc=0.1,
        min_val_spearman_ic=0.0,
        weight_mode="none",
        learner_mode="reg_squarederror_excess_return",
    )
    try:
        _validate_objective_runtime_contract(bad_floor)
    except RuntimeError as exc:
        assert "path_b_structural_tail_does_not_use_auc_floor" in str(exc)
    else:
        raise AssertionError("expected regression floor failure")


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
        min_val_spearman_ic=0.0,
        weight_mode="abs_excess_return",
        learner_mode="binary_logistic_sign",
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
    spearman_idx = script_args.index("--min-val-spearman-ic")
    weight_idx = script_args.index("--weight-mode")
    learner_idx = script_args.index("--learner-mode")
    assert script_args[objective_idx + 1] == "alpha_top_quintile"
    assert script_args[auc_idx + 1] == "0.75"
    assert script_args[spearman_idx + 1] == "0.0"
    assert script_args[weight_idx + 1] == "abs_excess_return"
    assert script_args[learner_idx + 1] == "binary_logistic_sign"
    assert attempt["seed"] == 45


def test_validate_launch_contract_supports_v647_binary_and_v648_path_b() -> None:
    good = Namespace(
        objective_metric="structural_tail_monotonicity_gate",
        min_val_auc=0.505,
        min_val_spearman_ic=0.0,
        weight_mode="sqrt_abs_excess_return",
        learner_mode="binary_logistic_sign",
    )
    _validate_launch_contract(good)

    path_b = Namespace(
        objective_metric="structural_tail_monotonicity_gate",
        min_val_auc=0.0,
        min_val_spearman_ic=0.0,
        weight_mode="none",
        learner_mode="reg_squarederror_excess_return",
    )
    _validate_launch_contract(path_b)

    bad = Namespace(
        objective_metric="structural_tail_monotonicity_gate",
        min_val_auc=0.0,
        min_val_spearman_ic=0.0,
        weight_mode="sqrt_abs_excess_return",
        learner_mode="reg_squarederror_excess_return",
    )
    try:
        _validate_launch_contract(bad)
    except RuntimeError as exc:
        assert "structural_tail_objective_requires_weight_mode" in str(exc)
    else:
        raise AssertionError("expected launch-contract learner-mode failure")


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
