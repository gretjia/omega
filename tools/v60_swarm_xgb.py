#!/usr/bin/env python3
"""
v60 in-memory manifold slicing swarm (Optuna + XGBoost).

Key constraints from v60 optimization audit:
- Never rerun ETL per trial.
- Search physics gates + XGBoost hyperparameters jointly.
- Use in-memory boolean slicing for O(1)-style trial filtering.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    clean = uri.replace("gs://", "", 1)
    bucket, blob = clean.split("/", 1)
    return bucket, blob


def _download_file(gcs_uri: str, local_path: Path) -> None:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.check_call(["gsutil", "cp", gcs_uri, str(local_path)])
        return
    except Exception:
        pass

    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    storage.Client().bucket(bucket_name).blob(blob_name).download_to_filename(str(local_path))


def _upload_json(payload: dict, gcs_uri: str) -> None:
    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(gcs_uri)
    tmp = Path("v60_swarm_result.json")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(str(tmp))


def _install_dependencies() -> None:
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "optuna",
            "xgboost",
            "numpy",
            "polars",
            "google-cloud-storage",
            "gcsfs",
            "fsspec",
            "psutil",
            "python-json-logger",
        ]
    )


def _bootstrap_codebase(code_bundle_uri: str) -> None:
    _download_file(code_bundle_uri, Path("omega_core.zip"))
    shutil.unpack_archive("omega_core.zip", extract_dir=".")
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())


class EpistemicSwarmV6:
    def __init__(self, base_matrix_path: str, feature_cols: list[str]):
        import polars as pl

        print(f"Loading Base Matrix into RAM: {base_matrix_path}", flush=True)
        self.df = pl.read_parquet(base_matrix_path)

        required = [
            "epiplexity",
            "srl_resid_050",
            "sigma_eff",
            "topo_area",
            "topo_energy",
            "t1_fwd_return",
        ]
        missing = [c for c in required if c not in self.df.columns]
        if missing:
            raise ValueError(f"Base matrix missing required columns: {missing}")

        feat_missing = [c for c in feature_cols if c not in self.df.columns]
        if feat_missing:
            raise ValueError(f"Base matrix missing feature columns: {feat_missing}")

        # v6.1: Orthogonalize Target (Excess Return)
        # Check for 'date' column for group-wise mean
        if "date" not in self.df.columns:
            # Fallback: if no date, maybe we can't do exact excess return.
            # But base_matrix SHOULD have date.
            # Let's try to load it if it was excluded, but we loaded everything with read_parquet
            raise ValueError("Base matrix must contain 'date' column for Excess Return calculation.")

        print("Calculating Excess Return (Alpha) target without Look-Ahead Bias...", flush=True)
        self.df = self.df.with_columns([
            (pl.col("t1_fwd_return") - pl.col("t1_fwd_return").mean().over(["date", "time"])).alias("t1_excess_return")
        ])
        
        self.feature_cols = list(feature_cols)
        self.epi = self.df.get_column("epiplexity").to_numpy()
        self.srl = self.df.get_column("srl_resid_050").to_numpy()
        self.sigma = self.df.get_column("sigma_eff").to_numpy()
        self.topo_area = self.df.get_column("topo_area").to_numpy()
        self.topo_energy = self.df.get_column("topo_energy").to_numpy()

        self.X = self.df.select(self.feature_cols).to_numpy()
        # Original absolute target (kept for reference/logging if needed, but we use excess for training)
        self.y = (self.df.get_column("t1_fwd_return").to_numpy() > 0).astype(int)
        # v6.1 Alpha Target
        self.y_excess = (self.df.get_column("t1_excess_return").to_numpy() > 0).astype(int)

    def objective(
        self,
        trial,
        min_samples: int,
        nfold: int,
        early_stopping_rounds: int,
        num_boost_round: int,
        seed: int,
    ) -> float:
        import optuna
        import xgboost as xgb
        import polars as pl

        # V62 Fix: Strict hard-caps on ranges to strictly prevent dataset collapse
        peace_threshold = trial.suggest_float("peace_threshold", 0.05, 0.20)
        srl_mult = trial.suggest_float("srl_resid_sigma_mult", 0.5, 2.0)
        topo_energy_mult = trial.suggest_float("topo_energy_sigma_mult", 1.0, 3.0)

        xgb_params = {
            "max_depth": trial.suggest_int("max_depth", 2, 5),
            "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.1, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "tree_method": "hist",
            "objective": "binary:logistic",
            "eval_metric": "auc",
            "n_jobs": -1,
            "seed": int(seed),
        }

        physics_mask = (
            (self.epi > peace_threshold)
            & (np.abs(self.srl) > srl_mult * self.sigma)
            & (self.topo_energy > topo_energy_mult * self.sigma)
        )

        n_mask = int(np.sum(physics_mask))
        if n_mask < int(min_samples):
            raise optuna.TrialPruned(f"Physics collapse too severe: {n_mask} < {min_samples}")

        X_clean = self.X[physics_mask]
        
        # v6.1: Excess Return Target (Alpha)
        # Re-calculate y dynamically to ensure we aren't using pre-computed contaminated labels
        # Note: We need t1_fwd_return from base_matrix but we need to demean it by DATE.
        # But 'date' isn't currently in self.df for simple slicing.
        # FIX: We must have pre-calculated 't1_excess_return' or do it globally in __init__.
        # For efficiency, let's assume __init__ handles it.
        # Check if 't1_excess_return' exists, else raise error.
        
        if not hasattr(self, "y_excess"):
             raise RuntimeError("y_excess not computed in __init__")
             
        y_clean = self.y_excess[physics_mask]
        weights_clean = (self.epi * np.log1p(np.abs(self.topo_area)))[physics_mask]

        finite = np.isfinite(weights_clean) & (weights_clean > 1e-8)
        if int(np.sum(finite)) < int(min_samples):
            raise optuna.TrialPruned("Insufficient finite weighted samples.")

        X_clean = X_clean[finite]
        y_clean = y_clean[finite]
        weights_clean = weights_clean[finite]

        dtrain = xgb.DMatrix(X_clean, label=y_clean, weight=weights_clean, feature_names=self.feature_cols)

        cv_results = xgb.cv(
            params=xgb_params,
            dtrain=dtrain,
            num_boost_round=int(num_boost_round),
            nfold=int(nfold),
            early_stopping_rounds=int(early_stopping_rounds),
            seed=int(seed),
        )
        if cv_results.empty:
            raise optuna.TrialPruned("Empty CV result.")
        return float(cv_results["test-auc-mean"].max())


def _resolve_base_matrix_path(path_or_uri: str) -> str:
    if path_or_uri.startswith("gs://"):
        local = Path("base_matrix.parquet").resolve()
        _download_file(path_or_uri, local)
        return str(local)
    p = Path(path_or_uri)
    if not p.exists():
        raise FileNotFoundError(f"Base matrix not found: {path_or_uri}")
    return str(p)


def main() -> int:
    ap = argparse.ArgumentParser(description="v60 swarm optimizer (in-memory manifold slicing)")
    ap.add_argument("--base-matrix", default="")
    ap.add_argument("--base-matrix-uri", default="")
    ap.add_argument("--n-trials", type=int, default=50)
    # V62 Fix: Strict min-samples penalty threshold
    ap.add_argument("--min-samples", type=int, default=50000)
    ap.add_argument("--nfold", type=int, default=5)
    ap.add_argument("--early-stopping-rounds", type=int, default=15)
    ap.add_argument("--num-boost-round", type=int, default=150)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--output-local", default="")
    ap.add_argument("--output-uri", default="")
    ap.add_argument("--install-deps", action="store_true")
    ap.add_argument("--bootstrap-code", action="store_true")
    ap.add_argument("--code-bundle-uri", default="gs://omega_v52/staging/code/omega_core.zip")
    args = ap.parse_args()

    if args.install_deps:
        _install_dependencies()

    if args.bootstrap_code:
        _bootstrap_codebase(args.code_bundle_uri)

    from config_v6 import FEATURE_COLS
    import optuna
    from optuna.trial import TrialState

    base_matrix_ref = args.base_matrix_uri.strip() or args.base_matrix.strip()
    if not base_matrix_ref:
        raise SystemExit("Either --base-matrix or --base-matrix-uri is required.")

    base_matrix_path = _resolve_base_matrix_path(base_matrix_ref)
    swarm = EpistemicSwarmV6(base_matrix_path=base_matrix_path, feature_cols=list(FEATURE_COLS))

    t0 = time.time()
    study = optuna.create_study(direction="maximize")
    study.optimize(
        lambda trial: swarm.objective(
            trial,
            min_samples=int(args.min_samples),
            nfold=int(args.nfold),
            early_stopping_rounds=int(args.early_stopping_rounds),
            num_boost_round=int(args.num_boost_round),
            seed=int(args.seed),
        ),
        n_trials=int(args.n_trials),
    )

    completed_trials = [t for t in study.trials if t.state == TrialState.COMPLETE]
    if completed_trials:
        result = {
            "status": "completed",
            "best_params": dict(study.best_params),
            "best_value": float(study.best_value),
            "n_trials": int(len(study.trials)),
            "n_completed": int(len(completed_trials)),
            "base_matrix": str(base_matrix_ref),
            "feature_cols": list(FEATURE_COLS),
            "seconds": round(time.time() - t0, 2),
            "job_id": os.environ.get("CLOUD_ML_JOB_ID", "unknown"),
        }
    else:
        result = {
            "status": "no_complete_trials",
            "best_params": {},
            "best_value": None,
            "n_trials": int(len(study.trials)),
            "n_completed": 0,
            "base_matrix": str(base_matrix_ref),
            "feature_cols": list(FEATURE_COLS),
            "seconds": round(time.time() - t0, 2),
            "job_id": os.environ.get("CLOUD_ML_JOB_ID", "unknown"),
            "message": "All trials pruned; relax min-samples or use a larger base matrix.",
        }

    if args.output_local:
        out = Path(args.output_local)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.output_uri:
        _upload_json(result, args.output_uri)

    print("--- V60 SWARM RESULT JSON START ---")
    print(json.dumps(result, ensure_ascii=False))
    print("--- V60 SWARM RESULT JSON END ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
