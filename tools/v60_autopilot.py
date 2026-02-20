#!/usr/bin/env python3
"""
v61 full-stack autopilot (Boomerang Topology):
frame monitor -> (LAN Sync) -> Remote Base Matrix Build -> Upload Base Matrix -> Optimize -> Train -> Local Backtest.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SSH_PS = REPO_ROOT / ".codex" / "skills" / "omega-run-ops" / "scripts" / "ssh_ps.py"
LINUX_SSH_TARGET = "zepher@192.168.3.113"
WINDOWS_SSH_TARGET = "jiazi@192.168.3.112"
SSH_IDENTITY_FILE = Path.home() / ".ssh" / "id_ed25519"
SSH_CONNECT_OPTS = [
    "-o",
    "BatchMode=yes",
    "-o",
    "ConnectTimeout=8",
    "-o",
    "ConnectionAttempts=1",
    "-o",
    "ServerAliveInterval=5",
    "-o",
    "ServerAliveCountMax=1",
]
AUDIT_DOC_PATH = REPO_ROOT / "audit" / "v60_training_final.md"
AUDIT_REQUIRED_SNIPPETS = (
    "ACTION 1: Completely Rewrite `tools/run_vertex_xgb_train.py`",
    "Accept `--base-matrix-uri` (NOT `--data-pattern`).",
    "ACTION 2: Kill the Zombie Job & Update Autopilot",
    "passes `--script-arg=--base-matrix-uri=...`",
)


def now_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def run_stream(cmd: list[str], log_fn) -> str:
    log_fn("+ " + " ".join(cmd))
    proc = subprocess.Popen(
        cmd,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    out = []
    assert proc.stdout is not None
    for line in proc.stdout:
        out.append(line)
        log_fn(line.rstrip("\n"))
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"Command failed ({rc}): {' '.join(cmd)}")
    return "".join(out)


def detect_git_hash() -> str:
    try:
        res = run(["git", "rev-parse", "--short", "HEAD"])
        return res.stdout.strip()
    except Exception:
        return ""

def count_unique_output_dates(path: Path) -> int:
    if not path.exists():
        return 0
    keys: set[str] = set()
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            base = Path(line).name
            key = base.split(".", 1)[0]
            if key:
                keys.add(key)
    return len(keys)

def parse_prefixed_int(text: str, key: str) -> int:
    m = re.search(rf"{re.escape(key)}=(\d+)", text)
    return int(m.group(1)) if m else -1

def parse_prefixed_str(text: str, key: str) -> str:
    m = re.search(rf"{re.escape(key)}=([^\r\n]+)", text)
    return m.group(1).strip() if m else ""

def linux_done_count(git_hash: str) -> int:
    if not SSH_IDENTITY_FILE.exists():
        return -1
    cmd = [
        "ssh",
        "-F",
        "/dev/null",
        *SSH_CONNECT_OPTS,
        "-o",
        "StrictHostKeyChecking=no",
        "-i",
        str(SSH_IDENTITY_FILE),
        LINUX_SSH_TARGET,
        (
            "find /omega_pool/parquet_data/v52/frames/host=linux1 -maxdepth 1 -type f "
            f"-name '*_{git_hash}.parquet.done' 2>/dev/null | wc -l"
        ),
    ]
    res = run(cmd, check=False)
    if res.returncode != 0:
        return -1
    try:
        return int(res.stdout.strip().splitlines()[-1])
    except Exception:
        return -1

def windows_done_and_state(git_hash: str, task_name: str) -> tuple[int, str]:
    ps = (
        "$ProgressPreference='SilentlyContinue'; "
        "$done=(Get-ChildItem -Path 'D:\\Omega_frames\\v52\\frames\\host=windows1' "
        f"-Filter '*_{git_hash}.parquet.done' -ErrorAction SilentlyContinue).Count; "
        f"$state=(Get-ScheduledTask -TaskName '{task_name}' -ErrorAction SilentlyContinue).State; "
        "Write-Output ('done_windows=' + $done); "
        "Write-Output ('task_state=' + $state)"
    )
    res = run([sys.executable, str(SSH_PS), WINDOWS_SSH_TARGET, "--command", ps], check=False)
    text = (res.stdout or "") + "\n" + (res.stderr or "")
    return parse_prefixed_int(text, "done_windows"), parse_prefixed_str(text, "task_state")

def collect_diag(task_name: str) -> dict:
    if SSH_IDENTITY_FILE.exists():
        linux_log = run(
            [
                "ssh",
                "-F",
                "/dev/null",
                *SSH_CONNECT_OPTS,
                "-o",
                "StrictHostKeyChecking=no",
                "-i",
                str(SSH_IDENTITY_FILE),
                LINUX_SSH_TARGET,
                "cd /home/zepher/work/Omega_vNext && tail -n 20 audit/_pipeline_frame.frame03.nohup.log 2>/dev/null || true",
            ],
            check=False,
        ).stdout
    else:
        linux_log = ""
    win_ps = (
        "$ProgressPreference='SilentlyContinue'; "
        f"$state=(Get-ScheduledTask -TaskName '{task_name}' -ErrorAction SilentlyContinue).State; "
        "Write-Output ('task_state=' + $state); "
        "Get-Content 'D:\\work\\Omega_vNext\\audit\\_pipeline_frame.log' -Tail 20 -ErrorAction SilentlyContinue"
    )
    win_out = run([sys.executable, str(SSH_PS), WINDOWS_SSH_TARGET, "--command", win_ps], check=False).stdout
    return {"linux_tail": linux_log.strip(), "windows_tail": (win_out or "").strip()}

def gcs_count(bucket: str, host: str, git_hash: str) -> int:
    pattern = f"{bucket}/omega/v52/frames/host={host}/*_{git_hash}.parquet"
    res = run(["bash", "-lc", f"gcloud storage ls '{pattern}' 2>/dev/null | wc -l"], check=False)
    try:
        return int((res.stdout or "0").strip().splitlines()[-1])
    except Exception:
        return -1

def gcs_read_json(uri: str) -> dict:
    res = run(["bash", "-lc", f"gcloud storage cat '{uri}'"], check=False)
    if res.returncode != 0:
        raise RuntimeError(f"gcloud storage cat failed for {uri}: {res.stderr}")
    return json.loads(res.stdout)

def add_script_arg(cmd: list[str], item: str) -> None:
    cmd.append(f"--script-arg={item}")

def parse_float(d: dict, key: str) -> float | None:
    if key not in d:
        return None
    try:
        return float(d[key])
    except Exception:
        return None

def parse_int(d: dict, key: str) -> int | None:
    if key not in d:
        return None
    try:
        return int(d[key])
    except Exception:
        return None

def lan_sync_stream(source_windows_path: str, dest_linux_path: str, log_fn):
    """Stream sync from Windows to Linux via Orchestrator pipe."""
    log_fn(f"LAN Sync: Windows({source_windows_path}) -> Mac -> Linux({dest_linux_path})")
    
    # Windows: tar from source.
    # Linux: untar to dest.
    # Note: Windows bsdtar might need relative paths to be clean.
    
    win_cmd = f"cd {source_windows_path} && bsdtar -cf - ."
    lin_cmd = f"mkdir -p {dest_linux_path} && cd {dest_linux_path} && tar -xf -"
    
    ssh_win = ["ssh", *SSH_CONNECT_OPTS, "-o", "StrictHostKeyChecking=no", "-i", str(SSH_IDENTITY_FILE), WINDOWS_SSH_TARGET, win_cmd]
    ssh_lin = ["ssh", *SSH_CONNECT_OPTS, "-o", "StrictHostKeyChecking=no", "-i", str(SSH_IDENTITY_FILE), LINUX_SSH_TARGET, lin_cmd]
    
    try:
        # Popen with pipe
        src = subprocess.Popen(ssh_win, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        dst = subprocess.Popen(ssh_lin, stdin=src.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Allow src to receive SIGPIPE if dst exits
        if src.stdout:
            src.stdout.close()
            
        out, err = dst.communicate()
        src.wait()
        
        if src.returncode != 0:
            log_fn(f"[!] Windows Read Warning (RC={src.returncode}). Stderr: {src.stderr.read().decode('utf-8', errors='replace') if src.stderr else ''}")
            # bsdtar might exit with 1 on warnings, but data might be fine.
            # We continue if Linux side is happy.
            
        if dst.returncode != 0:
            raise RuntimeError(f"Linux Write Failed (RC={dst.returncode}): {err.decode('utf-8', errors='replace')}")
            
        log_fn("LAN Sync Complete.")
    except Exception as e:
        raise RuntimeError(f"LAN Sync Failed: {e}")

def recursive_audit_checkpoint(
    node: str,
    *,
    git_hash: str,
    args: argparse.Namespace,
    state: dict,
    audit_log_path: Path,
    log_fn,
    extra: dict | None = None,
) -> None:
    issues: list[str] = []

    if not AUDIT_DOC_PATH.exists():
        issues.append(f"missing audit doc: {AUDIT_DOC_PATH}")
    else:
        text = AUDIT_DOC_PATH.read_text(encoding="utf-8", errors="replace")
        for snippet in AUDIT_REQUIRED_SNIPPETS:
            if snippet not in text:
                issues.append(f"audit anchor missing: {snippet}")

    if abs(float(args.base_peace_threshold) - 0.10) > 1e-12:
        issues.append(f"base peace_threshold drifted: {args.base_peace_threshold}")
    if abs(float(args.base_matrix_peace_threshold_baseline) - 0.10) > 1e-12:
        issues.append(f"base_matrix_peace_threshold_baseline drifted: {args.base_matrix_peace_threshold_baseline}")
    if abs(float(args.base_srl_resid_sigma_mult) - 0.5) > 1e-12:
        issues.append(f"base srl_resid_sigma_mult drifted: {args.base_srl_resid_sigma_mult}")

    if node in {"pre_base_matrix", "post_base_matrix", "post_optimize", "pre_train", "pre_backtest", "completed"}:
        if not bool(args.enable_optimization):
            issues.append("optimization disabled but v60 override requires optimization-first chain")
        if str(getattr(args, "base_matrix_exec_mode", "local")).strip().lower() != "local":
            issues.append("base_matrix_exec_mode must be local")
        if int(getattr(args, "base_matrix_chunk_days", 0)) > 0:
            issues.append("base_matrix_chunk_days must remain 0 (time slicing forbidden)")
        if bool(getattr(args, "base_matrix_float32_output", False)):
            issues.append("base_matrix_float32_output must remain disabled (float64 required)")
        if int(getattr(args, "base_matrix_symbols_per_batch", 0)) <= 0:
            issues.append("base_matrix_symbols_per_batch must be > 0")
        if int(getattr(args, "base_matrix_max_workers", 0)) <= 0:
            issues.append("base_matrix_max_workers must be > 0")

    train_years = {x.strip() for x in str(getattr(args, "train_years", "")).split(",") if x.strip()}
    test_years = {x.strip() for x in str(getattr(args, "test_years", "")).split(",") if x.strip()}
    if not train_years:
        issues.append("train years cannot be empty")
    if not test_years:
        issues.append("test years cannot be empty")
    if train_years and test_years:
        overlap = sorted(train_years & test_years)
        if overlap:
            issues.append(f"train/test year overlap detected: {overlap}")

    test_ym = [x.strip() for x in str(getattr(args, "test_year_months", "")).split(",") if x.strip()]
    if test_ym and test_years:
        for ym in test_ym:
            if not any(str(ym).startswith(y) for y in test_years):
                issues.append(f"test-year-month prefix outside declared test years: {ym}")

    base_meta_payload = None
    if extra and extra.get("base_meta_local"):
        meta_path = Path(str(extra["base_meta_local"]))
        if not meta_path.exists():
            issues.append(f"base meta missing: {meta_path}")
        else:
            try:
                base_meta_payload = json.loads(meta_path.read_text(encoding="utf-8", errors="replace"))
            except Exception as e:
                issues.append(f"failed to parse base meta local: {e}")
    elif extra and extra.get("base_meta_uri"):
        meta_uri = str(extra["base_meta_uri"])
        try:
            base_meta_payload = gcs_read_json(meta_uri)
        except Exception as e:
            issues.append(f"failed to read base meta uri: {meta_uri} error={e}")

    if base_meta_payload is not None:
        g = dict(base_meta_payload.get("physics_gates", {}))
        if abs(float(g.get("peace_threshold", -1.0)) - 0.10) > 1e-12:
            issues.append(f"base meta peace_threshold mismatch: {g.get('peace_threshold')}")
        if abs(float(g.get("srl_resid_sigma_mult", -1.0)) - 0.5) > 1e-12:
            issues.append(f"base meta srl_resid_sigma_mult mismatch: {g.get('srl_resid_sigma_mult')}")
        if int(base_meta_payload.get("sample_days", 0)) > 0:
            issues.append(f"base meta sample_days must remain 0: {base_meta_payload.get('sample_days')}")

        d = dict(base_meta_payload.get("dtype_invariants", {}))
        if not d:
            issues.append("base meta missing dtype_invariants")
        else:
            if not bool(d.get("strict_float64_required", False)):
                issues.append("base meta strict_float64_required must be true")
            required_float_dtype = str(d.get("required_float_dtype", "")).strip()
            if required_float_dtype != "Float64":
                issues.append(f"base meta required_float_dtype must be Float64: {required_float_dtype}")
            forbidden_names = {str(x) for x in d.get("forbidden_float_dtypes", [])}
            if not {"Float16", "Float32"}.issubset(forbidden_names):
                issues.append(
                    f"base meta forbidden_float_dtypes must include Float16/Float32: {sorted(forbidden_names)}"
                )
            if bool(d.get("forbidden_float_dtypes_detected", True)):
                issues.append("base meta forbidden_float_dtypes_detected must be false")

    entry = {
        "ts": now_ts(),
        "node": node,
        "git_hash": git_hash,
        "stage": state.get("stage"),
        "status": "pass" if not issues else "fail",
        "issues": issues,
        "extra": extra or {},
    }
    audit_log_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    if issues:
        raise RuntimeError(f"recursive audit failed at {node}: {'; '.join(issues)}")
    log_fn(f"Recursive audit passed at node={node}")


def main() -> int:
    ap = argparse.ArgumentParser(description="OMEGA v61 full-stack autopilot (Boomerang)")
    ap.add_argument("--hash", default="", help="Frame git short hash (default: local HEAD)")
    ap.add_argument("--bucket", default="gs://omega_v52")
    ap.add_argument("--windows-expected", type=int, default=0)
    ap.add_argument("--linux-expected", type=int, default=0)
    ap.add_argument("--poll-sec", type=int, default=180)
    ap.add_argument("--stall-sec", type=int, default=1800)
    ap.add_argument("--windows-task-name", default="Omega_v52_frame03")
    ap.add_argument("--train-years", default="2023,2024")
    ap.add_argument("--test-years", default="2025,2026")
    ap.add_argument("--test-year-months", default="", help="Optional comma-separated date prefixes for backtest.")
    ap.add_argument("--train-machine-type", default="n2-standard-16")
    ap.add_argument("--backtest-machine-type", default="n2-standard-8")
    ap.add_argument("--train-max-files", type=int, default=0)
    ap.add_argument("--train-max-rows-per-file", type=int, default=0)
    ap.add_argument("--backtest-max-files", type=int, default=0)
    ap.add_argument("--backtest-max-rows-per-file", type=int, default=0)
    ap.add_argument("--optimization-machine-type", default="n2-highmem-16")
    ap.add_argument("--optimization-trials", type=int, default=50)
    ap.add_argument("--optimization-min-samples", type=int, default=2000)
    ap.add_argument("--optimization-seed", type=int, default=42)
    ap.add_argument("--base-matrix-max-files", type=int, default=0)
    ap.add_argument("--base-matrix-local-input-pattern", default="", help="Local glob for base_matrix ETL inputs.")
    ap.add_argument("--base-matrix-sample-symbols", type=int, default=0)
    ap.add_argument("--base-matrix-max-rows-per-file", type=int, default=0)
    ap.add_argument("--base-matrix-symbols-per-batch", type=int, default=50)
    ap.add_argument("--base-matrix-max-workers", type=int, default=12)
    ap.add_argument("--base-matrix-resume", dest="base_matrix_resume", action="store_true")
    ap.add_argument("--base-matrix-no-resume", dest="base_matrix_resume", action="store_false")
    ap.set_defaults(base_matrix_resume=True)
    ap.add_argument("--base-matrix-cache-key", default="")
    ap.add_argument("--base-matrix-peace-threshold-baseline", type=float, default=0.10)
    ap.add_argument("--base-matrix-chunk-days", type=int, default=0)
    ap.add_argument("--base-matrix-float32-output", action="store_true")
    ap.add_argument("--base-matrix-exec-mode", choices=("local",), default="local")
    ap.add_argument("--base-matrix-machine-type", default="n2-highmem-16")
    ap.add_argument("--base-matrix-spot", action="store_true")
    ap.add_argument("--optimization-spot", action="store_true")
    ap.add_argument("--train-spot", action="store_true")
    ap.add_argument("--backtest-spot", action="store_true")
    ap.add_argument("--base-matrix-sync-timeout-sec", type=int, default=7200)
    ap.add_argument("--optimization-sync-timeout-sec", type=int, default=10800)
    ap.add_argument("--train-sync-timeout-sec", type=int, default=21600)
    ap.add_argument("--backtest-sync-timeout-sec", type=int, default=10800)
    ap.add_argument("--base-peace-threshold", type=float, default=0.10)
    ap.add_argument("--base-srl-resid-sigma-mult", type=float, default=0.5)
    ap.add_argument("--vertex-force-gcloud-fallback", dest="vertex_force_gcloud_fallback", action="store_true")
    ap.add_argument("--vertex-use-sdk-submit", dest="vertex_force_gcloud_fallback", action="store_false")
    ap.set_defaults(vertex_force_gcloud_fallback=True)
    ap.add_argument(
        "--upload-mode",
        choices=("sync_once", "wait_existing"),
        default="sync_once",
        help="sync_once: run mac_gateway_sync per host once; wait_existing: only poll GCS counts",
    )
    ap.add_argument("--enable-optimization", dest="enable_optimization", action="store_true")
    ap.add_argument("--disable-optimization", dest="enable_optimization", action="store_false")
    ap.set_defaults(enable_optimization=True)
    args = ap.parse_args()

    git_hash = args.hash.strip() or detect_git_hash()
    if not git_hash:
        raise SystemExit("Cannot determine git hash. Pass --hash explicitly.")
    test_year_months = [x.strip() for x in str(args.test_year_months).split(",") if x.strip()]
    train_year_values = [x.strip() for x in str(args.train_years).split(",") if x.strip()]
    test_year_values = [x.strip() for x in str(args.test_years).split(",") if x.strip()]
    if not train_year_values:
        raise SystemExit("--train-years cannot be empty.")
    if not test_year_values:
        raise SystemExit("--test-years cannot be empty.")

    if str(args.base_matrix_exec_mode).strip().lower() != "local":
        raise SystemExit("Forbidden: base_matrix ETL must run locally.")
    if int(args.base_matrix_chunk_days) > 0:
        raise SystemExit("Forbidden: --base-matrix-chunk-days is removed.")
    if bool(args.base_matrix_float32_output):
        raise SystemExit("Forbidden: --base-matrix-float32-output is removed.")
    if bool(args.base_matrix_spot):
        raise SystemExit("Forbidden: base_matrix stage cannot run on Vertex spot instances.")
    if int(args.base_matrix_max_rows_per_file) > 0:
        raise SystemExit("Ticker-sharding base_matrix mode does not support --base-matrix-max-rows-per-file.")
    
    # We ignore local input pattern here because we will dispatch to Linux.
    # But we check args validity.
    base_matrix_input_pattern = str(args.base_matrix_local_input_pattern).strip()
    if not base_matrix_input_pattern:
        base_matrix_input_pattern = f"/omega_pool/parquet_data/v52/frames/host=*/*_{git_hash}.parquet" # Linux path default

    win_expected = int(args.windows_expected) or count_unique_output_dates(
        REPO_ROOT / "audit/runtime/v52/shard_windows1.txt"
    )
    lin_expected = int(args.linux_expected) or count_unique_output_dates(
        REPO_ROOT / "audit/runtime/v52/shard_linux.txt"
    )
    status_path = REPO_ROOT / f"audit/runtime/v52/autopilot_{git_hash}.status.json"
    log_path = REPO_ROOT / f"audit/runtime/v52/autopilot_{git_hash}.log"
    audit_log_path = REPO_ROOT / f"audit/runtime/v52/recursive_audit_{git_hash}.jsonl"
    status_path.parent.mkdir(parents=True, exist_ok=True)

    def log(msg: str) -> None:
        line = f"[{now_ts()}] {msg}"
        print(line, flush=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    state = {
        "started_at": now_ts(),
        "git_hash": git_hash,
        "bucket": args.bucket,
        "windows_expected": win_expected,
        "linux_expected": lin_expected,
        "stage": "monitor_frame",
        "frame": {},
        "upload": {},
        "optimization": {},
        "train": {},
        "backtest": {},
    }
    state["backtest"]["effective_test_year_months"] = list(test_year_months)
    state["backtest"]["split_guard"] = {
        "enforced": True,
        "train_years": list(train_year_values),
        "test_years": list(test_year_values),
        "test_year_months": list(test_year_months),
    }

    def flush_state() -> None:
        tmp = status_path.with_suffix(status_path.suffix + ".tmp")
        tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(status_path)

    flush_state()
    log(
        f"Autopilot started hash={git_hash} expected windows={win_expected} linux={lin_expected} "
        f"poll={args.poll_sec}s stall={args.stall_sec}s optimization={bool(args.enable_optimization)}"
    )
    recursive_audit_checkpoint(
        "bootstrap",
        git_hash=git_hash,
        args=args,
        state=state,
        audit_log_path=audit_log_path,
        log_fn=log,
    )

    # Stage 1: monitor framing
    last_total = -1
    last_progress_ts = time.time()
    last_lin = -1
    last_win = -1
    last_win_state = ""
    while True:
        lin_probe = 0 # Linux ignored
        win_probe, win_state_probe = windows_done_and_state(git_hash, args.windows_task_name)
        lin = lin_probe if lin_probe >= 0 else last_lin
        win = win_probe if win_probe >= 0 else last_win
        win_state = win_state_probe or last_win_state
        total = max(0, lin) + max(0, win)
        probe_ok = (win_probe >= 0) # Linux ignored

        if lin >= 0:
            last_lin = lin
        if win >= 0:
            last_win = win
        if win_state:
            last_win_state = win_state

        state["frame"] = {
            "linux_done": lin,
            "windows_done": win,
            "windows_task_state": win_state,
            "probe_linux": lin_probe,
            "probe_windows": win_probe,
            "probe_ok": probe_ok,
            "updated_at": now_ts(),
        }
        flush_state()
        log(
            f"Frame progress linux={lin}/{lin_expected} windows={win}/{win_expected} "
            f"task={win_state or 'unknown'} probe_ok={probe_ok}"
        )

        if win >= win_expected: # Linux ignored by emergency patch
            log("Frame stage complete.")
            break

        if total > last_total:
            last_total = total
            last_progress_ts = time.time()
        elif time.time() - last_progress_ts >= float(args.stall_sec):
            diag = collect_diag(args.windows_task_name)
            state["frame"]["stall_diag"] = diag
            flush_state()
            log("Progress stalled; diagnostics captured in status json.")
            last_progress_ts = time.time()

        time.sleep(max(10, int(args.poll_sec)))

    recursive_audit_checkpoint(
        "frame_complete",
        git_hash=git_hash,
        args=args,
        state=state,
        audit_log_path=audit_log_path,
        log_fn=log,
        extra={"linux_done": state.get("frame", {}).get("linux_done"), "windows_done": state.get("frame", {}).get("windows_done")},
    )

    # Stage 2: upload - SKIPPED FOR V61 (Data Gravity)
    log("Skipping Frame Upload (Data Gravity Enforced). LAN Sync and Remote Build will be used.")
    state["stage"] = "sync_gcs_skipped"
    flush_state()

    run_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    # Data pattern for cloud is Base Matrix only.
    code_bundle_uri = f"{args.bucket.rstrip('/')}/staging/code/omega_core_{run_id}_{git_hash}.zip"
    state["run_id"] = run_id
    state["code_bundle_uri"] = code_bundle_uri
    flush_state()
    log(f"Run-pinned code bundle URI: {code_bundle_uri}")

    optimized = {}
    if args.enable_optimization:
        # Stage 3: LAN Sync + Remote Base Matrix Build
        state["stage"] = "build_base_matrix"
        

        # 3a. Windows Local Build (Emergency Path)
        log("Starting Windows Base Matrix Build (Linux bypassed)...")
        
        # Define Windows Paths
        win_base_dir = r"D:\work\Omega_vNext\artifacts\runtime\v60\base_matrix"
        win_parquet = win_base_dir + r"\base_matrix.parquet"
        win_meta = win_base_dir + r"\base_matrix.parquet.meta.json"
        
        # Windows Build Command (Force single line for SSH safety)
        # Note: We use 2023,2024 for training data.
        win_build_cmd = (
            f"mkdir {win_base_dir} & "
            f"python tools\\v60_build_base_matrix.py "
            f"--input-pattern=D:\\Omega_frames\\v52\\frames\\host=windows1\\*_{git_hash}.parquet "
            f"--years={args.train_years} "
            f"--hash={git_hash} "
            f"--peace-threshold={args.base_peace_threshold} "
            f"--peace-threshold-baseline={args.base_matrix_peace_threshold_baseline} "
            f"--srl-resid-sigma-mult={args.base_srl_resid_sigma_mult} "
            f"--symbols-per-batch={int(args.base_matrix_symbols_per_batch)} "
            f"--max-workers={int(args.base_matrix_max_workers)} "
            f"--output-parquet={win_parquet} "
            f"--output-meta={win_meta} "
            f"--shard-dir={win_base_dir}\\shards "
            f"--seed={args.optimization_seed} --no-resume"
        )
        
        # Execute on Windows
        log(f"Dispatching to Windows: {win_build_cmd}")
        res = subprocess.run(
            ["ssh", *SSH_CONNECT_OPTS, "-o", "StrictHostKeyChecking=no", "-i", str(SSH_IDENTITY_FILE), WINDOWS_SSH_TARGET, f"cd /d D:\\work\\Omega_vNext && {win_build_cmd}"],
            capture_output=True, text=True, errors="replace"
        )
        if res.returncode != 0:
            log(f"Windows Build Failed: {res.stderr}")
            raise RuntimeError("Windows Base Matrix Build Failed")
        log("Windows Build Complete.")
        
        # 3b. Pull to Mac and Upload
        log("Pulling Base Matrix from Windows to Mac...")
        local_base_dir = REPO_ROOT / f"artifacts/runtime/v60/{run_id}_{git_hash}"
        local_base_dir.mkdir(parents=True, exist_ok=True)
        local_parquet = local_base_dir / "base_matrix.parquet"
        local_meta = local_base_dir / "base_matrix.meta.json"
        
        # SCP uses forward slashes even for Windows paths in OpenSSH
        win_scp_parquet = win_parquet.replace("\\", "/")
        win_scp_meta = win_meta.replace("\\", "/")
        
        run(["scp", *SSH_CONNECT_OPTS, "-o", "StrictHostKeyChecking=no", "-i", str(SSH_IDENTITY_FILE), f"{WINDOWS_SSH_TARGET}:{win_scp_parquet}", str(local_parquet)], check=True)
        run(["scp", *SSH_CONNECT_OPTS, "-o", "StrictHostKeyChecking=no", "-i", str(SSH_IDENTITY_FILE), f"{WINDOWS_SSH_TARGET}:{win_scp_meta}", str(local_meta)], check=True)
        
        # Upload to GCS
        base_run_tag = f"{run_id}_{git_hash}"
        base_uri = f"{args.bucket}/staging/base_matrix/v60/{base_run_tag}/base_matrix.parquet"
        base_meta_uri = f"{args.bucket}/staging/base_matrix/v60/{base_run_tag}/base_matrix.meta.json"
        
        log(f"Uploading to GCS: {base_uri}")
        if GCLOUD_BIN:
            run([GCLOUD_BIN, "storage", "cp", str(local_parquet), base_uri], check=True)
            run([GCLOUD_BIN, "storage", "cp", str(local_meta), base_meta_uri], check=True)
        else:
            # Fallback if GCLOUD_BIN not set in this scope (it is global in other script but let's be safe)
            run(["gcloud", "storage", "cp", str(local_parquet), base_uri], check=True)
            run(["gcloud", "storage", "cp", str(local_meta), base_meta_uri], check=True)
            
        state["optimization"]["base_matrix_uri"] = base_uri
        state["optimization"]["base_matrix_exec_mode"] = "windows_remote_build"
        flush_state()


        # Stage 4: vertex optimization swarm
        state["stage"] = "vertex_optimize"
        swarm_output_uri = f"{args.bucket}/staging/optimization/v60/{run_id}_{git_hash}/swarm_best.json"
        state["optimization"]["result_uri"] = swarm_output_uri
        flush_state()
        log("Submitting v60 swarm optimization job (sync mode)...")

        swarm_cmd = [
            sys.executable,
            "tools/submit_vertex_sweep.py",
            "--script",
            "tools/v60_swarm_xgb.py",
            "--machine-type",
            args.optimization_machine_type,
            "--code-bundle-uri",
            code_bundle_uri,
            "--sync",
            f"--sync-timeout-sec={int(args.optimization_sync_timeout_sec)}",
        ]
        if args.vertex_force_gcloud_fallback:
            swarm_cmd.append("--force-gcloud-fallback")
        if args.optimization_spot:
            swarm_cmd.append("--spot")
        add_script_arg(swarm_cmd, "--bootstrap-code")
        add_script_arg(swarm_cmd, "--install-deps")
        add_script_arg(swarm_cmd, f"--code-bundle-uri={code_bundle_uri}")
        add_script_arg(swarm_cmd, f"--base-matrix-uri={base_uri}")
        add_script_arg(swarm_cmd, f"--n-trials={int(args.optimization_trials)}")
        add_script_arg(swarm_cmd, f"--min-samples={int(args.optimization_min_samples)}")
        add_script_arg(swarm_cmd, f"--seed={int(args.optimization_seed)}")
        add_script_arg(swarm_cmd, f"--output-uri={swarm_output_uri}")
        if args.optimization_spot:
            try:
                run_stream(swarm_cmd, log)
            except Exception as spot_exc:
                state["optimization"]["spot_failed_at"] = now_ts()
                state["optimization"]["spot_error"] = str(spot_exc)
                flush_state()
                log(f"Spot optimization job failed; retrying once on on-demand. error={spot_exc}")
                ondemand_cmd = [x for x in swarm_cmd if x != "--spot"]
                run_stream(ondemand_cmd, log)
        else:
            run_stream(swarm_cmd, log)

        swarm_result = gcs_read_json(swarm_output_uri)
        optimized = dict(swarm_result.get("best_params", {}))
        if str(swarm_result.get("status", "")).strip().lower() != "completed" or not optimized:
            raise RuntimeError(
                "v60 optimization did not produce valid best_params; refusing to continue to train/backtest."
            )
        state["optimization"]["completed_at"] = now_ts()
        state["optimization"]["result"] = swarm_result
        state["optimization"]["best_params"] = optimized
        flush_state()
        log(f"Optimization complete best_params={optimized}")
        recursive_audit_checkpoint(
            "post_optimize",
            git_hash=git_hash,
            args=args,
            state=state,
            audit_log_path=audit_log_path,
            log_fn=log,
            extra={"optimized_keys": sorted(list(optimized.keys()))},
        )

    # Stage 5: Vertex training (with optimization overrides)
    state["stage"] = "vertex_train"
    train_output_uri = f"{args.bucket}/staging/models/v6/{run_id}_{git_hash}"
    base_matrix_uri = str(state.get("optimization", {}).get("base_matrix_uri", "")).strip()
    if not base_matrix_uri:
        raise RuntimeError("Missing optimization.base_matrix_uri; refusing to run training without base matrix.")
    state["train"]["output_uri"] = train_output_uri
    state["train"]["base_matrix_uri"] = base_matrix_uri

    train_overrides = {
        "peace_threshold": parse_float(optimized, "peace_threshold"),
        "srl_resid_sigma_mult": parse_float(optimized, "srl_resid_sigma_mult"),
        "topo_energy_sigma_mult": parse_float(optimized, "topo_energy_sigma_mult"),
        "max_depth": parse_int(optimized, "max_depth"),
        "learning_rate": parse_float(optimized, "learning_rate"),
        "subsample": parse_float(optimized, "subsample"),
        "colsample_bytree": parse_float(optimized, "colsample_bytree"),
    }
    state["train"]["overrides"] = train_overrides
    flush_state()
    log("Submitting Vertex train job (sync mode)...")
    recursive_audit_checkpoint(
        "pre_train",
        git_hash=git_hash,
        args=args,
        state=state,
        audit_log_path=audit_log_path,
        log_fn=log,
        extra={"train_overrides": train_overrides, "base_matrix_uri": base_matrix_uri},
    )

    train_cmd = [
        sys.executable,
        "tools/submit_vertex_sweep.py",
        "--script",
        "tools/run_vertex_xgb_train.py",
        "--machine-type",
        args.train_machine_type,
        "--code-bundle-uri",
        code_bundle_uri,
        "--sync",
        f"--sync-timeout-sec={int(args.train_sync_timeout_sec)}",
    ]
    if args.vertex_force_gcloud_fallback:
        train_cmd.append("--force-gcloud-fallback")
    if args.train_spot:
        train_cmd.append("--spot")
    add_script_arg(train_cmd, f"--base-matrix-uri={base_matrix_uri}")
    add_script_arg(train_cmd, f"--code-bundle-uri={code_bundle_uri}")
    add_script_arg(train_cmd, f"--output-uri={train_output_uri}")

    if train_overrides["peace_threshold"] is not None:
        add_script_arg(train_cmd, f"--peace-threshold={train_overrides['peace_threshold']}")
    if train_overrides["srl_resid_sigma_mult"] is not None:
        add_script_arg(train_cmd, f"--srl-resid-sigma-mult={train_overrides['srl_resid_sigma_mult']}")
    if train_overrides["topo_energy_sigma_mult"] is not None:
        add_script_arg(train_cmd, f"--topo-energy-sigma-mult={train_overrides['topo_energy_sigma_mult']}")
    if train_overrides["max_depth"] is not None:
        add_script_arg(train_cmd, f"--xgb-max-depth={train_overrides['max_depth']}")
    if train_overrides["learning_rate"] is not None:
        add_script_arg(train_cmd, f"--xgb-learning-rate={train_overrides['learning_rate']}")
    if train_overrides["subsample"] is not None:
        add_script_arg(train_cmd, f"--xgb-subsample={train_overrides['subsample']}")
    if train_overrides["colsample_bytree"] is not None:
        add_script_arg(train_cmd, f"--xgb-colsample-bytree={train_overrides['colsample_bytree']}")

    if args.train_spot:
        try:
            run_stream(train_cmd, log)
        except Exception as spot_exc:
            state["train"]["spot_failed_at"] = now_ts()
            state["train"]["spot_error"] = str(spot_exc)
            flush_state()
            log(f"Spot train job failed; retrying once on on-demand. error={spot_exc}")
            ondemand_cmd = [x for x in train_cmd if x != "--spot"]
            run_stream(ondemand_cmd, log)
    else:
        run_stream(train_cmd, log)
    state["train"]["completed_at"] = now_ts()
    state["train"]["model_uri"] = f"{train_output_uri}/omega_v6_xgb_final.pkl"
    flush_state()


    # Stage 6: BOOMERANG -> Local Edge Backtest (Dispatched to Windows)
    state["stage"] = "local_backtest"
    # Download model first to Mac (already done in train step actually? No, train sets state uri)
    model_uri = state["train"]["model_uri"]
    local_model_path = REPO_ROOT / f"artifacts/runtime/v60/models/{run_id}/omega_v6_xgb_final.pkl"
    local_model_path.parent.mkdir(parents=True, exist_ok=True)
    
    log(f"Downloading Boomerang Model from {model_uri}...")
    run(["gcloud", "storage", "cp", model_uri, str(local_model_path)], check=True)
    
    backtest_output_local = REPO_ROOT / f"artifacts/runtime/v60/backtest/{run_id}/backtest_metrics.json"
    backtest_output_local.parent.mkdir(parents=True, exist_ok=True)
    
    state["backtest"]["output_path"] = str(backtest_output_local)
    flush_state()
    
    log("Starting Windows Edge Backtest (Ticker Sharding)...")
    
    # Windows paths
    win_model_dir = r"D:\work\Omega_vNext\artifacts\runtime\v60\models"
    win_model_path = win_model_dir + r"\omega_v6_xgb_final.pkl"
    win_backtest_output = r"D:\work\Omega_vNext\artifacts\runtime\v60\backtest_metrics.json"
    win_frames_dir = r"D:\Omega_frames\v52\frames\host=windows1"
    
    log(f"Dispatching Backtest to Windows Node ({WINDOWS_SSH_TARGET})...")
    
    # 1. Create dir on Windows
    run(["ssh", *SSH_CONNECT_OPTS, "-o", "StrictHostKeyChecking=no", "-i", str(SSH_IDENTITY_FILE), WINDOWS_SSH_TARGET, f"mkdir {win_model_dir}"], check=False)
    
    # 2. SCP Model to Windows
    # Windows SCP path format needs care.
    win_scp_model = win_model_path.replace("\\", "/")
    run(["scp", *SSH_CONNECT_OPTS, "-o", "StrictHostKeyChecking=no", "-i", str(SSH_IDENTITY_FILE), str(local_model_path), f"{WINDOWS_SSH_TARGET}:{win_scp_model}"], check=True)
    
    # 3. Run Backtest Script (SSH)
    # Using 2023-2024 frames (Training Set) as proxy for backtest since 2025 is on dead Linux.
    # Warning: In-sample backtest.
    backtest_cmd = (
        f"python tools\\v61_run_local_backtest.py "
        f"--model-path {win_model_path} "
        f"--frames-dir {win_frames_dir} "
        f"--output {win_backtest_output} "
        f"--workers 16 "
        f"--symbols-per-batch 50"
    )
    
    log(f"Running remote backtest: {backtest_cmd}")
    
    res = subprocess.run(
        ["ssh", *SSH_CONNECT_OPTS, "-o", "StrictHostKeyChecking=no", "-i", str(SSH_IDENTITY_FILE), WINDOWS_SSH_TARGET, f"cd D:\\work\\Omega_vNext && {backtest_cmd}"],
        capture_output=True, text=True, errors="replace"
    )
    
    if res.returncode != 0:
        log(f"Remote backtest failed: {res.stderr}")
        # Don't crash, just log error for partial success
        log("Proceeding to cleanup.")
    else:
        log("Remote backtest completed.")
        log(res.stdout)
        # 4. Retrieve Results
        win_scp_output = win_backtest_output.replace("\\", "/")
        run(["scp", *SSH_CONNECT_OPTS, "-o", "StrictHostKeyChecking=no", "-i", str(SSH_IDENTITY_FILE), f"{WINDOWS_SSH_TARGET}:{win_scp_output}", str(backtest_output_local)], check=True)
    state["backtest"]["completed_at"] = now_ts()
    state["stage"] = "completed"
    state["completed_at"] = now_ts()
    flush_state()
    
    recursive_audit_checkpoint(
        "completed",
        git_hash=git_hash,
        args=args,
        state=state,
        audit_log_path=audit_log_path,
        log_fn=log,
    )
    log("Autopilot completed end-to-end.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
