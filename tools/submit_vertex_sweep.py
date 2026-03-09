#!/usr/bin/env python3
"""
OMEGA v5.2 Vertex AI Sweep Submitter (With Code Injection)
----------------------------------------------------------
1. Zips the local 'omega_core' module.
2. Uploads it to GCS.
3. Submits the 'run_optuna_sweep.py' payload to Vertex AI.

Usage:
    python tools/submit_vertex_sweep.py --script tools/run_optuna_sweep.py
"""

import argparse
import sys
import shutil
import os
import zipfile
import time
import shlex
import subprocess
import tempfile
import textwrap
import warnings
# Suppress annoying Google Cloud Python 3.9 deprecation warnings
warnings.filterwarnings("ignore", ".*Python version 3.9 past its end of life.*")
warnings.filterwarnings("ignore", ".*non-supported Python version.*")

from datetime import datetime
from google.cloud import aiplatform
from google.cloud import storage
from google.cloud.aiplatform_v1.types import custom_job as custom_job_types
from google.api_core import exceptions as gax_exceptions

# Defaults
PROJECT_ID = "gen-lang-client-0250995579"
REGION = "us-central1"
STAGING_BUCKET = "gs://omega_v52_central/staging"
CODE_BUCKET_PATH = "gs://omega_v52_central/staging/code/omega_core.zip"
PAYLOAD_BUCKET_PREFIX = "gs://omega_v52_central/staging/code/payloads"

def zip_and_upload_code(repo_root, gcs_uri):
    """
    Builds a self-contained bundle with the modules required by cloud payloads.
    Includes:
      - omega_core/
      - tools/
      - config.py
    """
    print(f"[*] Packaging code from repo root: {repo_root}", flush=True)

    include_paths = ["omega_core", "tools", "config.py"]
    archive_path = os.path.join(repo_root, "omega_core.zip")
    if os.path.exists(archive_path):
        os.remove(archive_path)

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in include_paths:
            abs_path = os.path.join(repo_root, rel)
            if not os.path.exists(abs_path):
                print(f"[!] Warning: missing bundle path: {abs_path}", flush=True)
                continue

            if os.path.isdir(abs_path):
                for dirpath, _, filenames in os.walk(abs_path):
                    for fn in filenames:
                        if fn.endswith((".pyc", ".pyo")):
                            continue
                        if fn == ".DS_Store":
                            continue
                        full = os.path.join(dirpath, fn)
                        arcname = os.path.relpath(full, repo_root)
                        zf.write(full, arcname=arcname)
            else:
                zf.write(abs_path, arcname=rel)

    print(f"    Created archive: {archive_path}", flush=True)
    
    # Upload
    print(f"[*] Uploading to {gcs_uri}...", flush=True)
    storage_client = storage.Client(project=PROJECT_ID)
    
    # Parse bucket/blob
    bucket_name = gcs_uri.replace("gs://", "").split("/")[0]
    blob_name = "/".join(gcs_uri.replace("gs://", "").split("/")[1:])
    
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(archive_path)
    
    print("[+] Code bundle uploaded successfully.", flush=True)
    
    # Cleanup local zip
    os.remove(archive_path)

def _is_transient_submit_error(exc: Exception) -> bool:
    if isinstance(exc, (gax_exceptions.ServiceUnavailable, gax_exceptions.DeadlineExceeded)):
        return True
    msg = str(exc).lower()
    if "statuscode.unavailable" in msg or "failed to connect to all addresses" in msg:
        return True
    return False


def _gcs_parse(uri: str) -> tuple[str, str]:
    clean = uri.replace("gs://", "", 1)
    bucket = clean.split("/", 1)[0]
    blob = clean.split("/", 1)[1]
    return bucket, blob


def _upload_payload_script(script_path: str, job_name: str) -> str:
    stem = os.path.splitext(os.path.basename(script_path))[0]
    payload_uri = f"{PAYLOAD_BUCKET_PREFIX}/{job_name}_{stem}.py"
    bucket_name, blob_name = _gcs_parse(payload_uri)
    client = storage.Client(project=PROJECT_ID)
    client.bucket(bucket_name).blob(blob_name).upload_from_filename(script_path)
    return payload_uri


def _render_fallback_shell(code_bundle_uri: str, payload_uri: str, script_args: list[str]) -> str:
    args_joined = " ".join(shlex.quote(str(x)) for x in script_args)
    return textwrap.dedent(
        f"""
        set -euxo pipefail
        python3 -m pip install --quiet google-cloud-storage
        python3 - <<'PY'
        from google.cloud import storage
        import shutil

        def dl(uri: str, out: str) -> None:
            clean = uri.replace("gs://", "", 1)
            bucket, blob = clean.split("/", 1)
            storage.Client().bucket(bucket).blob(blob).download_to_filename(out)

        dl("{code_bundle_uri}", "omega_core.zip")
        dl("{payload_uri}", "payload.py")
        shutil.unpack_archive("omega_core.zip", extract_dir=".")
        PY
        python3 -u payload.py {args_joined}
        """
    ).strip()


def _submit_via_gcloud_fallback(
    script_path: str,
    machine_type: str,
    script_args: list[str],
    sync: bool,
    job_name: str,
    code_bundle_uri: str,
    spot: bool = False,
    sync_timeout_sec: int = 0,
) -> dict:
    payload_uri = _upload_payload_script(script_path, job_name)
    shell_script = _render_fallback_shell(code_bundle_uri, payload_uri, script_args)
    cfg = textwrap.dedent(
        f"""
        workerPoolSpecs:
        - machineSpec:
            machineType: {machine_type}
          replicaCount: 1
          diskSpec:
            bootDiskType: pd-ssd
            bootDiskSizeGb: 100
          containerSpec:
            imageUri: us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-17.py310:latest
            command:
            - /bin/bash
            - -lc
            args:
            - |
        """
    ).rstrip("\n")
    indented_shell = "\n".join(("      " + line) if line else "      " for line in shell_script.splitlines())
    cfg = cfg + "\n" + indented_shell + "\n"
    if spot:
        cfg += "scheduling:\n  strategy: SPOT\n"

    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as tf:
        tf.write(cfg)
        cfg_path = tf.name

    try:
        cmd = [
            "gcloud",
            "ai",
            "custom-jobs",
            "create",
            f"--project={PROJECT_ID}",
            f"--region={REGION}",
            f"--display-name={job_name}",
            f"--config={cfg_path}",
            "--format=value(name)",
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[!] Fallback submit failed. stderr:\n{e.stderr}", flush=True)
            raise e

        resource_name = (res.stdout or "").strip().splitlines()[-1]
        print(f"[+] Fallback submit succeeded: {resource_name}", flush=True)

        if not sync:
            return {
                "display_name": job_name,
                "resource_name": resource_name,
                "dashboard_uri": "",
                "submission_backend": "gcloud_fallback",
                "sync": False,
                "spot": bool(spot),
                "machine_type": str(machine_type),
                "payload_uri": payload_uri,
            }

        terminal_ok = {"JOB_STATE_SUCCEEDED"}
        terminal_fail = {
            "JOB_STATE_FAILED",
            "JOB_STATE_CANCELLED",
            "JOB_STATE_EXPIRED",
            "JOB_STATE_PAUSED",
        }
        started_at = time.time()
        describe_fail_streak = 0
        max_describe_fail_streak = 10
        last_state = "JOB_STATE_UNKNOWN"
        while True:
            elapsed = int(max(0, time.time() - started_at))
            if int(sync_timeout_sec) > 0 and elapsed >= int(sync_timeout_sec):
                cancel_cmd = [
                    "gcloud",
                    "ai",
                    "custom-jobs",
                    "cancel",
                    resource_name,
                    f"--project={PROJECT_ID}",
                    f"--region={REGION}",
                ]
                try:
                    subprocess.run(cancel_cmd, capture_output=True, text=True, check=False)
                except Exception:
                    pass
                raise RuntimeError(
                    f"Fallback custom job timed out after {elapsed}s (timeout={sync_timeout_sec}s), "
                    f"resource={resource_name}, last_state={last_state}"
                )

            state_cmd = [
                "gcloud",
                "ai",
                "custom-jobs",
                "describe",
                resource_name,
                f"--project={PROJECT_ID}",
                f"--region={REGION}",
                "--format=value(state)",
            ]
            sres = subprocess.run(state_cmd, capture_output=True, text=True, check=False)
            if sres.returncode != 0:
                describe_fail_streak += 1
                err_tail = ((sres.stderr or "").strip().splitlines() or [""])[-1]
                print(
                    f"    [Fallback] describe error rc={sres.returncode} "
                    f"streak={describe_fail_streak}/{max_describe_fail_streak} elapsed={elapsed}s "
                    f"msg={err_tail}",
                    flush=True,
                )
                if describe_fail_streak >= max_describe_fail_streak:
                    raise RuntimeError(
                        f"Fallback custom job state polling failed {describe_fail_streak} times in a row "
                        f"for resource={resource_name}; last_error={err_tail or 'unknown'}"
                    )
                time.sleep(30)
                continue

            state = (sres.stdout or "").strip()
            if not state:
                describe_fail_streak += 1
                print(
                    f"    [Fallback] describe returned empty state "
                    f"streak={describe_fail_streak}/{max_describe_fail_streak} elapsed={elapsed}s",
                    flush=True,
                )
                if describe_fail_streak >= max_describe_fail_streak:
                    raise RuntimeError(
                        f"Fallback custom job state polling returned empty state "
                        f"{describe_fail_streak} times in a row for resource={resource_name}"
                    )
                time.sleep(30)
                continue

            describe_fail_streak = 0
            last_state = state
            print(f"    [Fallback] state={state} elapsed={elapsed}s", flush=True)
            if state in terminal_ok:
                return {
                    "display_name": job_name,
                    "resource_name": resource_name,
                    "dashboard_uri": "",
                    "submission_backend": "gcloud_fallback",
                    "sync": True,
                    "terminal_state": state,
                    "spot": bool(spot),
                    "machine_type": str(machine_type),
                    "payload_uri": payload_uri,
                }
            if state in terminal_fail:
                raise RuntimeError(f"Fallback custom job failed with state={state} resource={resource_name}")
            time.sleep(30)
    finally:
        try:
            os.remove(cfg_path)
        except Exception:
            pass


def submit_job(
    script_path,
    machine_type="c2-standard-60",
    script_args=None,
    sync=False,
    spot: bool = False,
    force_gcloud_fallback: bool = False,
    max_submit_retries: int = 5,
    sync_timeout_sec: int = 0,
    code_bundle_uri: str = "",
):
    """Submits the job."""
    if script_args is None:
        script_args = []
    if not script_args and os.path.basename(script_path) == "run_optuna_sweep.py":
        script_args = ["--n-trials", "50"]
    if not str(code_bundle_uri).strip():
        raise ValueError("--code-bundle-uri is required.")
    
    aiplatform.init(
        project=PROJECT_ID,
        location=REGION,
        staging_bucket=STAGING_BUCKET
    )

    script_stem = os.path.splitext(os.path.basename(script_path))[0]
    job_name = f"omega-v60-{script_stem}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    print(f"[*] Submitting Custom Job: {job_name}", flush=True)
    if spot:
        print("[*] Scheduling strategy: SPOT", flush=True)
    if force_gcloud_fallback:
        print("[*] Forcing gcloud fallback submission path.", flush=True)
        return _submit_via_gcloud_fallback(
            script_path=script_path,
            machine_type=machine_type,
            script_args=list(script_args),
            sync=bool(sync),
            job_name=job_name,
            code_bundle_uri=str(code_bundle_uri),
            spot=bool(spot),
            sync_timeout_sec=int(sync_timeout_sec),
        )

    job = aiplatform.CustomJob.from_local_script(
        display_name=job_name,
        script_path=script_path,
        container_uri="us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-17.py310:latest",
        replica_count=1,
        machine_type=machine_type,
        args=script_args,
    )

    for attempt in range(1, int(max_submit_retries) + 1):
        try:
            run_kwargs = {"sync": bool(sync)}
            if spot:
                run_kwargs["scheduling_strategy"] = custom_job_types.Scheduling.Strategy.SPOT
            job.run(**run_kwargs)
            break
        except Exception as exc:
            transient = _is_transient_submit_error(exc)
            if not transient:
                raise
            if attempt >= int(max_submit_retries):
                print("[Warn] Vertex SDK submit retries exhausted. Switching to gcloud fallback submit...", flush=True)
                return _submit_via_gcloud_fallback(
                    script_path=script_path,
                    machine_type=machine_type,
                    script_args=list(script_args),
                    sync=bool(sync),
                    job_name=job_name,
                    code_bundle_uri=str(code_bundle_uri),
                    spot=bool(spot),
                    sync_timeout_sec=int(sync_timeout_sec),
                )
            sleep_sec = min(120, 10 * attempt)
            print(
                f"[Warn] Vertex submit transient failure ({attempt}/{max_submit_retries}): {exc}. "
                f"Retrying in {sleep_sec}s...",
                flush=True,
            )
            time.sleep(sleep_sec)
    
    print(f"\n[+] Job submitted! Check Cloud Console.", flush=True)
    try:
        dashboard = getattr(job, "dashboard_uri", "")
    except Exception:
        dashboard = ""
    resource = ""
    try:
        resource = job.resource_name or ""
    except Exception:
        resource = ""
    if not resource:
        try:
            resource = getattr(job, "name", "") or ""
        except Exception:
            resource = ""
    if dashboard:
        print(f"    Dashboard: {dashboard}", flush=True)
    if resource:
        print(f"    Resource : {resource}", flush=True)
    return {
        "display_name": job_name,
        "resource_name": resource,
        "dashboard_uri": dashboard,
        "submission_backend": "vertex_sdk",
        "sync": bool(sync),
        "spot": bool(spot),
        "machine_type": str(machine_type),
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True, help="Payload script")
    parser.add_argument("--machine-type", default="c2-standard-60")
    parser.add_argument(
        "--code-bundle-uri",
        required=True,
        help="GCS URI to upload and use for omega_core bundle (run-pinned).",
    )
    parser.add_argument("--max-submit-retries", type=int, default=5)
    parser.add_argument("--spot", action="store_true", help="Use Spot scheduling strategy for lower cost.")
    parser.add_argument(
        "--force-gcloud-fallback",
        action="store_true",
        help="Skip Vertex SDK submission and submit directly via gcloud custom-jobs create.",
    )
    parser.add_argument(
        "--script-arg",
        action="append",
        default=[],
        help="Argument forwarded to payload script (repeatable).",
    )
    parser.add_argument("--sync", action="store_true", help="Wait until Vertex job completes")
    parser.add_argument(
        "--sync-timeout-sec",
        type=int,
        default=0,
        help="When --sync is set, cancel and fail if terminal state not reached within timeout seconds (0=disabled).",
    )
    args = parser.parse_args()

    # 1. Inject Code
    # Assumes omega_core is in CWD or ../omega_core
    # We look for it relative to this script or CWD
    repo_root = os.getcwd() # Assumption: running from repo root
    code_path = os.path.join(repo_root, "omega_core")
    
    if not os.path.exists(code_path):
        print(f"[!] Error: omega_core not found at {code_path}")
        sys.exit(1)
        
    zip_and_upload_code(repo_root, args.code_bundle_uri)

    # 2. Submit Job
    submit_job(
        args.script,
        args.machine_type,
        script_args=args.script_arg,
        sync=args.sync,
        spot=bool(args.spot),
        force_gcloud_fallback=bool(args.force_gcloud_fallback),
        max_submit_retries=int(args.max_submit_retries),
        sync_timeout_sec=int(args.sync_timeout_sec),
        code_bundle_uri=str(args.code_bundle_uri),
    )
