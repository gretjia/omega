import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import aggregate_vertex_swarm_results as aggregate


def _write_worker(root: Path, worker_id: str, fingerprint: dict, trials: list[dict]) -> None:
    worker_dir = root / "workers" / worker_id
    worker_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "status": "completed",
        "worker_id": worker_id,
        "job_id": f"job-{worker_id}",
        "n_trials": len(trials),
        "n_completed": len(trials),
        "seconds": 12.5,
        "split_summary": {
            "train_rows": 100,
            "val_rows": 80,
        },
        "canonical_fingerprint": fingerprint,
    }
    (worker_dir / "study_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with (worker_dir / "trials.jsonl").open("w", encoding="utf-8") as f:
        for row in trials:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def test_aggregate_prefers_simpler_model_within_epsilon(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    results_root = tmp_path / "results"
    output_root = tmp_path / "output"
    fingerprint = {"stage3_param_contract": "canonical_v64_1", "sha256": "abc123"}
    _write_worker(
        results_root,
        "w00",
        fingerprint,
        [
            {
                "trial_number": 0,
                "val_auc": 0.7010,
                "alpha_top_decile": 0.02,
                "alpha_top_quintile": 0.01,
                "max_depth": 6,
                "num_boost_round": 320,
                "params": {
                    "max_depth": 6,
                    "learning_rate": 0.04,
                    "subsample": 0.9,
                    "colsample_bytree": 0.8,
                    "min_child_weight": 2.0,
                    "gamma": 0.1,
                    "reg_lambda": 1.2,
                    "reg_alpha": 0.01,
                    "num_boost_round": 320,
                },
            }
        ],
    )
    _write_worker(
        results_root,
        "w01",
        fingerprint,
        [
            {
                "trial_number": 0,
                "val_auc": 0.7004,
                "alpha_top_decile": 0.03,
                "alpha_top_quintile": 0.02,
                "max_depth": 4,
                "num_boost_round": 140,
                "params": {
                    "max_depth": 4,
                    "learning_rate": 0.03,
                    "subsample": 0.85,
                    "colsample_bytree": 0.75,
                    "min_child_weight": 1.5,
                    "gamma": 0.0,
                    "reg_lambda": 1.0,
                    "reg_alpha": 0.001,
                    "num_boost_round": 140,
                },
            }
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "aggregate_vertex_swarm_results.py",
            "--results-prefix-uri",
            str(results_root),
            "--output-uri",
            str(output_root),
            "--simplicity-epsilon",
            "0.001",
            "--min-workers",
            "2",
            "--min-completed-trials",
            "2",
        ],
    )
    aggregate.main()

    champion = json.loads((output_root / "champion_params.json").read_text(encoding="utf-8"))
    leaderboard = json.loads((output_root / "swarm_leaderboard.json").read_text(encoding="utf-8"))
    assert champion["champion_params"]["max_depth"] == 4
    assert champion["champion_params"]["num_boost_round"] == 140
    assert champion["trainer_overrides"]["xgb_gamma"] == 0.0
    assert leaderboard["completed_trials"] == 2
    assert leaderboard["champion_pool_size"] == 2
    assert leaderboard["worker_summaries"][0]["train_rows"] == 100


def test_aggregate_rejects_fingerprint_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    results_root = tmp_path / "results"
    output_root = tmp_path / "output"
    _write_worker(
        results_root,
        "w00",
        {"stage3_param_contract": "canonical_v64_1", "sha256": "aaa"},
        [
            {
                "trial_number": 0,
                "val_auc": 0.61,
                "alpha_top_decile": 0.0,
                "alpha_top_quintile": 0.0,
                "max_depth": 4,
                "num_boost_round": 100,
                "params": {
                    "max_depth": 4,
                    "learning_rate": 0.03,
                    "subsample": 0.9,
                    "colsample_bytree": 0.8,
                    "min_child_weight": 1.0,
                    "gamma": 0.0,
                    "reg_lambda": 1.0,
                    "reg_alpha": 0.0,
                    "num_boost_round": 100,
                },
            }
        ],
    )
    _write_worker(
        results_root,
        "w01",
        {"stage3_param_contract": "canonical_v64_1", "sha256": "bbb"},
        [
            {
                "trial_number": 0,
                "val_auc": 0.60,
                "alpha_top_decile": 0.0,
                "alpha_top_quintile": 0.0,
                "max_depth": 5,
                "num_boost_round": 120,
                "params": {
                    "max_depth": 5,
                    "learning_rate": 0.02,
                    "subsample": 0.85,
                    "colsample_bytree": 0.75,
                    "min_child_weight": 1.5,
                    "gamma": 0.1,
                    "reg_lambda": 1.2,
                    "reg_alpha": 0.01,
                    "num_boost_round": 120,
                },
            }
        ],
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "aggregate_vertex_swarm_results.py",
            "--results-prefix-uri",
            str(results_root),
            "--output-uri",
            str(output_root),
            "--min-workers",
            "2",
        ],
    )
    with pytest.raises(RuntimeError, match="canonical_fingerprint_mismatch"):
        aggregate.main()
