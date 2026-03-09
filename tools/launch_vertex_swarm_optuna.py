#!/usr/bin/env python3
"""
Launch many independent single-replica Vertex workers for the v643 Optuna swarm.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


STRUCTURAL_TAIL_OBJECTIVE = "structural_tail_monotonicity_gate"
STRUCTURAL_TAIL_REQUIRED_WEIGHT_MODE = "sqrt_abs_excess_return"
STRUCTURAL_TAIL_REQUIRED_LEARNER_MODE = "binary_logistic_sign"
STRUCTURAL_TAIL_MIN_AUC_FLOOR = 0.505


def _write_manifest(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_submitters(repo_root: Path):
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
    try:
        from tools.submit_vertex_sweep import submit_job, zip_and_upload_code
    except ModuleNotFoundError as exc:
        missing = getattr(exc, "name", "") or "google-cloud dependencies"
        if missing == "tools":
            raise RuntimeError(
                "launch_vertex_swarm_optuna.py could not import the local repo package `tools`. "
                "Run it from the repo checkout and keep the repo root readable."
            ) from exc
        raise RuntimeError(
            "launch_vertex_swarm_optuna.py requires the Vertex submit dependencies on the controller. "
            "Run it with `uv run --with google-cloud-aiplatform --with google-cloud-storage python ...` "
            f"(missing import: {missing})."
        ) from exc
    return submit_job, zip_and_upload_code


def _uri_has_existing_outputs(uri: str) -> bool:
    clean = str(uri or "").strip().rstrip("/")
    if not clean:
        return False
    if not clean.startswith("gs://"):
        path = Path(clean)
        if not path.exists():
            return False
        if path.is_file():
            return True
        return any(path.iterdir())
    listing = subprocess.run(
        ["gsutil", "ls", f"{clean}/**"],
        capture_output=True,
        text=True,
        check=False,
    )
    if listing.returncode == 0 and bool((listing.stdout or "").strip()):
        return True
    try:
        from google.cloud import storage

        bucket_name, prefix = clean.replace("gs://", "", 1).split("/", 1)
        blobs = storage.Client().bucket(bucket_name).list_blobs(prefix=prefix.rstrip("/") + "/", max_results=1)
        return any(True for _ in blobs)
    except Exception:
        return False


def _assert_empty_output_uri(uri: str, *, label: str) -> None:
    if _uri_has_existing_outputs(uri):
        raise RuntimeError(f"{label}_not_empty: {uri}")


def _submit_one_worker(*, submit_job, args: argparse.Namespace, script_path: str, worker_id: str, output_uri: str, spot: bool) -> dict:
    worker_seed = int(args.base_seed) + int(worker_id.replace("w", ""))
    submit_result = submit_job(
        script_path=script_path,
        machine_type=str(args.machine_type),
        script_args=[
            "--base-matrix-uri",
            str(args.base_matrix_uri),
            "--output-uri",
            output_uri,
            "--worker-id",
            worker_id,
            "--n-trials",
            str(args.n_trials_per_worker),
            "--train-year",
            str(args.train_year),
            "--val-year",
            str(args.val_year),
            "--seed",
            str(worker_seed),
            "--objective-metric",
            str(args.objective_metric),
            "--min-val-auc",
            str(args.min_val_auc),
            "--weight-mode",
            str(args.weight_mode),
            "--learner-mode",
            str(args.learner_mode),
            "--code-bundle-uri",
            str(args.code_bundle_uri),
        ],
        sync=bool(args.sync),
        spot=bool(spot),
        force_gcloud_fallback=bool(args.force_gcloud_fallback),
        sync_timeout_sec=int(args.sync_timeout_sec),
        code_bundle_uri=str(args.code_bundle_uri),
    )
    return {
        "submitted_at_utc": int(time.time()),
        "spot": bool(spot),
        "seed": worker_seed,
        "output_uri": output_uri,
        "submit_result": submit_result,
    }


def _describe_job_state(resource_name: str, *, project_id: str, region: str) -> str:
    cmd = [
        "gcloud",
        "ai",
        "custom-jobs",
        "describe",
        resource_name,
        f"--project={project_id}",
        f"--region={region}",
        "--format=value(state)",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        err_tail = ((res.stderr or "").strip().splitlines() or [""])[-1]
        raise RuntimeError(
            f"gcloud_describe_failed resource={resource_name} rc={res.returncode} msg={err_tail or 'unknown'}"
        )
    return (res.stdout or "").strip() or "JOB_STATE_UNKNOWN"


def _aggregate_results(*, repo_root: Path, args: argparse.Namespace) -> None:
    if not str(args.aggregate_output_uri).strip():
        return
    cmd = [
        sys.executable,
        str(repo_root / "tools" / "aggregate_vertex_swarm_results.py"),
        "--results-prefix-uri",
        str(args.results_prefix_uri),
        "--output-uri",
        str(args.aggregate_output_uri),
        "--objective-metric",
        str(args.objective_metric),
        "--min-val-auc",
        str(args.min_val_auc),
        "--min-workers",
        str(args.min_workers),
        "--min-completed-trials",
        str(args.min_completed_trials),
    ]
    if args.objective_epsilon is not None:
        cmd.extend(["--objective-epsilon", str(args.objective_epsilon)])
    subprocess.run(cmd, check=True)


def _validate_launch_contract(args: argparse.Namespace) -> None:
    if str(args.objective_metric) == STRUCTURAL_TAIL_OBJECTIVE:
        if str(args.weight_mode) != STRUCTURAL_TAIL_REQUIRED_WEIGHT_MODE:
            raise RuntimeError(
                "structural_tail_objective_requires_weight_mode:"
                f"{STRUCTURAL_TAIL_REQUIRED_WEIGHT_MODE}"
            )
        if str(args.learner_mode) != STRUCTURAL_TAIL_REQUIRED_LEARNER_MODE:
            raise RuntimeError(
                "structural_tail_objective_requires_learner_mode:"
                f"{STRUCTURAL_TAIL_REQUIRED_LEARNER_MODE}"
            )
        if float(args.min_val_auc) < STRUCTURAL_TAIL_MIN_AUC_FLOOR:
            raise RuntimeError(
                "structural_tail_objective_requires_min_val_auc_at_least:"
                f"{STRUCTURAL_TAIL_MIN_AUC_FLOOR}"
            )


def main() -> None:
    ap = argparse.ArgumentParser(description="Launch Vertex swarm Optuna workers")
    ap.add_argument("--base-matrix-uri", required=True)
    ap.add_argument("--results-prefix-uri", required=True)
    ap.add_argument("--code-bundle-uri", required=True)
    ap.add_argument("--worker-count", type=int, default=4)
    ap.add_argument("--n-trials-per-worker", type=int, default=25)
    ap.add_argument("--machine-type", default="n2-standard-16")
    ap.add_argument("--spot", action="store_true")
    ap.add_argument("--sync", action="store_true", help="Wait per submission until terminal state.")
    ap.add_argument("--sync-timeout-sec", type=int, default=0)
    ap.add_argument("--force-gcloud-fallback", action="store_true")
    ap.add_argument("--submit-spacing-sec", type=float, default=2.0)
    ap.add_argument("--train-year", default="2023")
    ap.add_argument("--val-year", default="2024")
    ap.add_argument("--base-seed", type=int, default=42)
    ap.add_argument("--manifest-path", default="vertex_swarm_launch_manifest.json")
    ap.add_argument("--watch", action="store_true", help="Poll all submitted jobs to terminal state after async launch.")
    ap.add_argument("--poll-sec", type=float, default=30.0)
    ap.add_argument("--aggregate-output-uri", default="", help="When set with --watch, run aggregation after polling.")
    ap.add_argument("--min-workers", type=int, default=1)
    ap.add_argument("--min-completed-trials", type=int, default=1)
    ap.add_argument("--objective-metric", default="val_auc")
    ap.add_argument("--min-val-auc", type=float, default=0.0)
    ap.add_argument("--objective-epsilon", type=float, default=None)
    ap.add_argument("--weight-mode", default="physics_abs_singularity")
    ap.add_argument("--learner-mode", default="binary_logistic_sign")
    ap.add_argument("--require-empty-results-prefix", action="store_true")
    ap.add_argument("--require-empty-aggregate-output-uri", action="store_true")
    args = ap.parse_args()
    if bool(args.sync) and bool(args.watch):
        raise RuntimeError("--sync and --watch are mutually exclusive. Use async submit + --watch for real fan-out.")
    if str(args.objective_metric) != "val_auc" and float(args.min_val_auc) <= 0.0:
        raise RuntimeError("alpha_first_requires_positive_min_val_auc")
    if bool(args.require_empty_results_prefix):
        _assert_empty_output_uri(str(args.results_prefix_uri), label="results_prefix_uri")
    if bool(args.require_empty_aggregate_output_uri) and str(args.aggregate_output_uri).strip():
        _assert_empty_output_uri(str(args.aggregate_output_uri), label="aggregate_output_uri")
    _validate_launch_contract(args)

    repo_root = Path(__file__).resolve().parent.parent
    submit_job, zip_and_upload_code = _load_submitters(repo_root)
    zip_and_upload_code(str(repo_root), str(args.code_bundle_uri))

    launch_rows: list[dict] = []
    script_path = str(repo_root / "tools" / "run_optuna_sweep.py")
    for idx in range(int(args.worker_count)):
        worker_id = f"w{idx:02d}"
        worker_output = f"{str(args.results_prefix_uri).rstrip('/')}/workers/{worker_id}"
        launch_rows.append(
            {
                "worker_id": worker_id,
                "output_uri": worker_output,
                "machine_type": str(args.machine_type),
                "requested_spot": bool(args.spot),
                "n_trials": int(args.n_trials_per_worker),
                "seed": int(args.base_seed) + idx,
                "attempts": [
                    _submit_one_worker(
                        submit_job=submit_job,
                        args=args,
                        script_path=script_path,
                        worker_id=worker_id,
                        output_uri=worker_output,
                        spot=bool(args.spot),
                    )
                ],
            }
        )
        time.sleep(float(args.submit_spacing_sec))

    manifest = {
        "status": "submitted",
        "base_matrix_uri": str(args.base_matrix_uri),
        "results_prefix_uri": str(args.results_prefix_uri),
        "code_bundle_uri": str(args.code_bundle_uri),
        "worker_count": int(args.worker_count),
        "n_trials_per_worker": int(args.n_trials_per_worker),
        "machine_type": str(args.machine_type),
        "spot": bool(args.spot),
        "weight_mode": str(args.weight_mode),
        "learner_mode": str(args.learner_mode),
        "workers": launch_rows,
    }
    manifest_path = Path(str(args.manifest_path))

    if bool(args.watch):
        terminal_ok = {"JOB_STATE_SUCCEEDED"}
        terminal_fail = {
            "JOB_STATE_FAILED",
            "JOB_STATE_CANCELLED",
            "JOB_STATE_EXPIRED",
            "JOB_STATE_PAUSED",
        }
        project_id = "gen-lang-client-0250995579"
        region = "us-central1"
        while True:
            unfinished = 0
            for worker in launch_rows:
                last_attempt = worker["attempts"][-1]
                submit_result = dict(last_attempt.get("submit_result", {}))
                resource_name = str(submit_result.get("resource_name", "")).strip()
                if not resource_name:
                    worker["terminal_state"] = "UNKNOWN_NO_RESOURCE"
                    continue
                state = _describe_job_state(resource_name, project_id=project_id, region=region)
                last_attempt["terminal_state"] = state
                if state in terminal_ok:
                    worker["terminal_state"] = state
                    continue
                if state in terminal_fail:
                    worker["terminal_state"] = state
                    if bool(last_attempt.get("spot")) and len(worker["attempts"]) == 1:
                        retry_attempt = _submit_one_worker(
                            submit_job=submit_job,
                            args=args,
                            script_path=script_path,
                            worker_id=str(worker["worker_id"]),
                            output_uri=str(worker["output_uri"]),
                            spot=False,
                        )
                        retry_attempt["retry_reason"] = state
                        worker["attempts"].append(retry_attempt)
                        unfinished += 1
                        time.sleep(float(args.submit_spacing_sec))
                    continue
                unfinished += 1
            manifest["status"] = "watching" if unfinished > 0 else "terminal"
            _write_manifest(manifest_path, manifest)
            if unfinished <= 0:
                break
            time.sleep(float(args.poll_sec))

        if str(args.aggregate_output_uri).strip():
            _aggregate_results(repo_root=repo_root, args=args)
            manifest["aggregation_output_uri"] = str(args.aggregate_output_uri)
            manifest["status"] = "aggregated"

    _write_manifest(manifest_path, manifest)
    print(json.dumps(manifest, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
