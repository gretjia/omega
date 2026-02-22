#!/usr/bin/env python3
"""
Run v60 micro-batch dry-run:
1) Build base_matrix from sampled symbols with bounded file count.
2) Upload base_matrix to GCS.
3) Submit Vertex v60 swarm with 3 trials.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=check)


def run_stream(cmd: list[str]) -> str:
    print("+ " + " ".join(cmd), flush=True)
    proc = subprocess.Popen(
        cmd,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    out = []
    assert proc.stdout is not None
    for line in proc.stdout:
        out.append(line)
        print(line.rstrip("\n"), flush=True)
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"Command failed ({rc}): {' '.join(cmd)}")
    return "".join(out)


def gcs_read_json(uri: str) -> dict:
    res = run(["bash", "-lc", f"gcloud storage cat '{uri}'"], check=False)
    if res.returncode != 0:
        raise RuntimeError(f"gcloud storage cat failed: {uri}\n{res.stderr}")
    return json.loads(res.stdout)


def add_script_arg(cmd: list[str], item: str) -> None:
    cmd.append(f"--script-arg={item}")


def main() -> int:
    ap = argparse.ArgumentParser(description="v60 micro dry-run: base_matrix + 3-trial swarm")
    ap.add_argument("--hash", required=True)
    ap.add_argument("--bucket", default="gs://omega_v52_central")
    ap.add_argument("--local-input-pattern", required=True)
    ap.add_argument("--years", default="")
    ap.add_argument("--sample-symbols", type=int, default=10)
    ap.add_argument("--max-files", type=int, default=24)
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--machine-type", default="n1-standard-8")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    run_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    hashv = args.hash.strip()
    data_pattern = args.local_input_pattern.strip()
    if data_pattern.startswith("gs://"):
        raise SystemExit("Forbidden by v60 objection: --local-input-pattern must be local, not gs://")

    base_local = REPO_ROOT / f"artifacts/runtime/v60/micro_{run_id}_{hashv}/base_matrix.parquet"
    base_meta_local = base_local.with_suffix(base_local.suffix + ".meta.json")
    base_uri = f"{args.bucket}/staging/smoke/v60/{run_id}_{hashv}/base_matrix.parquet"
    base_meta_uri = f"{args.bucket}/staging/smoke/v60/{run_id}_{hashv}/base_matrix.meta.json"
    swarm_uri = f"{args.bucket}/staging/smoke/v60/{run_id}_{hashv}/swarm_best.json"

    build_cmd = [
        sys.executable,
        "tools/v60_build_base_matrix.py",
        f"--input-pattern={data_pattern}",
        f"--hash={hashv}",
        f"--sample-symbols={int(args.sample_symbols)}",
        f"--max-files={int(args.max_files)}",
        "--peace-threshold=0.10",
        "--srl-resid-sigma-mult=0.5",
        f"--seed={int(args.seed)}",
        f"--output-parquet={str(base_local)}",
        f"--output-meta={str(base_meta_local)}",
        f"--output-uri={base_uri}",
        f"--output-meta-uri={base_meta_uri}",
    ]
    if args.years.strip():
        build_cmd.append(f"--years={args.years.strip()}")
    run_stream(build_cmd)

    swarm_cmd = [
        sys.executable,
        "tools/submit_vertex_sweep.py",
        "--script",
        "tools/v60_swarm_xgb.py",
        "--machine-type",
        args.machine_type,
        "--sync",
    ]
    add_script_arg(swarm_cmd, "--bootstrap-code")
    add_script_arg(swarm_cmd, "--install-deps")
    add_script_arg(swarm_cmd, f"--base-matrix-uri={base_uri}")
    add_script_arg(swarm_cmd, f"--n-trials={int(args.trials)}")
    add_script_arg(swarm_cmd, f"--min-samples=200")
    add_script_arg(swarm_cmd, f"--seed={int(args.seed)}")
    add_script_arg(swarm_cmd, f"--output-uri={swarm_uri}")
    run_stream(swarm_cmd)

    result = gcs_read_json(swarm_uri)
    print(json.dumps({
        "status": "ok",
        "run_id": run_id,
        "base_uri": base_uri,
        "base_meta_uri": base_meta_uri,
        "swarm_uri": swarm_uri,
        "swarm_result": result,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
