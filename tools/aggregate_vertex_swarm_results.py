#!/usr/bin/env python3
"""
Aggregate distributed Optuna worker outputs into one leaderboard and one champion artifact.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def _parse_gcs_uri(uri: str) -> tuple[str, str]:
    clean = uri.replace("gs://", "", 1)
    bucket, blob = clean.split("/", 1)
    return bucket, blob


def _list_trial_uris(prefix_uri: str) -> list[str]:
    if not prefix_uri.startswith("gs://"):
        base = Path(prefix_uri)
        return [str(p) for p in sorted(base.rglob("trials.jsonl"))]
    try:
        listing = subprocess.run(
            ["gsutil", "ls", f"{prefix_uri.rstrip('/')}/**"],
            capture_output=True,
            text=True,
            check=True,
        )
        return sorted([line.strip() for line in listing.stdout.splitlines() if line.strip().endswith("trials.jsonl")])
    except Exception:
        pass
    from google.cloud import storage

    bucket_name, prefix = _parse_gcs_uri(prefix_uri.rstrip("/") + "/dummy")
    prefix = prefix.rsplit("/", 1)[0] + "/"
    blobs = storage.Client().bucket(bucket_name).list_blobs(prefix=prefix)
    return sorted([f"gs://{bucket_name}/{b.name}" for b in blobs if b.name.endswith("trials.jsonl")])


def _download(uri: str, local_path: Path) -> None:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    if not uri.startswith("gs://"):
        src = Path(uri)
        if src.resolve() != local_path.resolve():
            shutil.copyfile(src, local_path)
        return
    try:
        subprocess.check_call(["gsutil", "cp", uri, str(local_path)])
        return
    except Exception:
        pass
    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(uri)
    storage.Client().bucket(bucket_name).blob(blob_name).download_to_filename(str(local_path))


def _upload(local_path: Path, uri: str) -> None:
    if not uri:
        return
    if not uri.startswith("gs://"):
        dest = Path(uri)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.resolve() != local_path.resolve():
            shutil.copyfile(local_path, dest)
        return
    from google.cloud import storage

    bucket_name, blob_name = _parse_gcs_uri(uri)
    storage.Client().bucket(bucket_name).blob(blob_name).upload_from_filename(str(local_path))


def _load_json(uri: str) -> dict:
    path = Path("_agg_tmp") / f"{abs(hash(uri))}.json"
    _download(uri, path)
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(uri: str) -> list[dict]:
    path = Path("_agg_tmp") / f"{abs(hash(uri))}.jsonl"
    _download(uri, path)
    out: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def _summary_uri_from_trials_uri(uri: str) -> str:
    return uri[: -len("trials.jsonl")] + "study_summary.json"


def _champion_trainer_overrides(champion: dict) -> dict:
    params = dict(champion.get("params", {}))
    required = [
        "learning_rate",
        "subsample",
        "colsample_bytree",
        "min_child_weight",
        "gamma",
        "reg_lambda",
        "reg_alpha",
        "num_boost_round",
    ]
    missing = [key for key in required if key not in params]
    if missing:
        raise RuntimeError(f"champion_params_missing_keys: {missing}")
    return {
        "xgb_max_depth": int(champion["max_depth"]),
        "xgb_learning_rate": float(params["learning_rate"]),
        "xgb_subsample": float(params["subsample"]),
        "xgb_colsample_bytree": float(params["colsample_bytree"]),
        "xgb_min_child_weight": float(params["min_child_weight"]),
        "xgb_gamma": float(params["gamma"]),
        "xgb_reg_lambda": float(params["reg_lambda"]),
        "xgb_reg_alpha": float(params["reg_alpha"]),
        "num_boost_round": int(params["num_boost_round"]),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Aggregate Vertex swarm Optuna results")
    ap.add_argument("--results-prefix-uri", required=True)
    ap.add_argument("--output-uri", required=True, help="Prefix for leaderboard/champion outputs")
    ap.add_argument("--simplicity-epsilon", type=float, default=0.001)
    ap.add_argument("--min-workers", type=int, default=1)
    ap.add_argument("--min-completed-trials", type=int, default=1)
    args = ap.parse_args()

    trial_uris = _list_trial_uris(str(args.results_prefix_uri))
    if not trial_uris:
        raise RuntimeError("No trials.jsonl artifacts found under results prefix.")
    if len(trial_uris) < int(args.min_workers):
        raise RuntimeError(
            f"insufficient_worker_artifacts: found={len(trial_uris)} min_workers={int(args.min_workers)}"
        )

    all_rows: list[dict] = []
    fingerprints: set[str] = set()
    summaries: list[dict] = []
    for trials_uri in trial_uris:
        summary_uri = _summary_uri_from_trials_uri(trials_uri)
        summary = _load_json(summary_uri)
        trials = _load_jsonl(trials_uri)
        summaries.append(summary)
        fingerprint = json.dumps(summary.get("canonical_fingerprint", {}), sort_keys=True)
        fingerprints.add(fingerprint)
        for row in trials:
            row = dict(row)
            row["worker_id"] = summary.get("worker_id", "")
            row["job_id"] = summary.get("job_id", "unknown")
            row["canonical_fingerprint"] = summary.get("canonical_fingerprint", {})
            all_rows.append(row)

    if len(fingerprints) != 1:
        raise RuntimeError(f"canonical_fingerprint_mismatch: count={len(fingerprints)}")
    completed_rows = [r for r in all_rows if r.get("val_auc") is not None]
    if not completed_rows:
        raise RuntimeError("No completed trial rows available for aggregation.")
    if len(completed_rows) < int(args.min_completed_trials):
        raise RuntimeError(
            "insufficient_completed_trials: "
            f"found={len(completed_rows)} min_completed_trials={int(args.min_completed_trials)}"
        )

    completed_rows.sort(
        key=lambda r: (
            -float(r["val_auc"]),
            int(r.get("max_depth", 10**9)),
            int(r.get("num_boost_round", 10**9)),
            int(r.get("trial_number", 10**9)),
        )
    )
    best_auc = float(completed_rows[0]["val_auc"])
    epsilon = float(args.simplicity_epsilon)
    champion_pool = [r for r in completed_rows if float(r["val_auc"]) >= best_auc - epsilon]
    champion_pool.sort(
        key=lambda r: (
            int(r.get("max_depth", 10**9)),
            int(r.get("num_boost_round", 10**9)),
            -float(r["val_auc"]),
            int(r.get("trial_number", 10**9)),
        )
    )
    champion = champion_pool[0]

    worker_summaries = [
        {
            "worker_id": summary.get("worker_id", ""),
            "job_id": summary.get("job_id", ""),
            "status": summary.get("status", "unknown"),
            "n_trials": int(summary.get("n_trials", 0)),
            "n_completed": int(summary.get("n_completed", 0)),
            "seconds": float(summary.get("seconds", 0.0)),
            "train_rows": int(summary.get("split_summary", {}).get("train_rows", 0)),
            "val_rows": int(summary.get("split_summary", {}).get("val_rows", 0)),
        }
        for summary in summaries
    ]
    leaderboard = {
        "status": "completed",
        "results_prefix_uri": str(args.results_prefix_uri),
        "total_workers": int(len(summaries)),
        "total_trials": int(len(all_rows)),
        "completed_trials": int(len(completed_rows)),
        "champion_pool_size": int(len(champion_pool)),
        "best_val_auc": best_auc,
        "simplicity_epsilon": epsilon,
        "canonical_fingerprint": champion["canonical_fingerprint"],
        "worker_summaries": worker_summaries,
        "leaderboard": completed_rows,
        "champion": champion,
    }
    champion_params = {
        "status": "completed",
        "best_val_auc": float(champion["val_auc"]),
        "champion_params": dict(champion["params"]),
        "trainer_overrides": _champion_trainer_overrides(champion),
        "complexity_tie_break_epsilon": epsilon,
        "canonical_fingerprint": champion["canonical_fingerprint"],
        "alpha_top_decile": float(champion.get("alpha_top_decile", 0.0)),
        "alpha_top_quintile": float(champion.get("alpha_top_quintile", 0.0)),
        "worker_id": champion.get("worker_id", ""),
        "trial_number": int(champion.get("trial_number", -1)),
    }

    local_leaderboard = Path("swarm_leaderboard.json")
    local_champion = Path("champion_params.json")
    local_leaderboard.write_text(json.dumps(leaderboard, ensure_ascii=False, indent=2), encoding="utf-8")
    local_champion.write_text(json.dumps(champion_params, ensure_ascii=False, indent=2), encoding="utf-8")

    output_prefix = str(args.output_uri).rstrip("/")
    _upload(local_leaderboard, f"{output_prefix}/swarm_leaderboard.json")
    _upload(local_champion, f"{output_prefix}/champion_params.json")
    print(json.dumps(champion_params, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
