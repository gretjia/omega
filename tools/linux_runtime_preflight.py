#!/usr/bin/env python3
"""
Linux runtime preflight for Omega v62 pipeline jobs.

Goal:
- Catch known high-probability Linux failure modes *before* Stage1/Stage2 starts.
- Enforce runtime guardrails at the host boundary (slice budget, mount state,
  venv dependencies, process placement, and cache capacity).

This script does not alter feature math or output schema.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


STAGE_PATTERNS = (
    "stage1_linux_base_etl.py",
    "stage2_physics_compute.py",
    "stage2_targeted_resume.py",
)


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str
    evidence: str = ""


def _cmd(args: list[str]) -> tuple[int, str, str]:
    cp = subprocess.run(args, text=True, capture_output=True, check=False)
    return cp.returncode, cp.stdout.strip(), cp.stderr.strip()


def _bytes_to_gb(value: int) -> float:
    return value / (1024**3)


def _parse_systemctl_int(raw: str) -> int | None:
    raw = raw.strip()
    if raw == "" or raw.lower() in {"infinity", "[not set]"}:
        return None
    if raw.endswith("s") and raw[:-1].isdigit():
        # CPUQuotaPerSecUSec (for example "24s")
        return int(raw[:-1])
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return None


def _read_slice_properties(unit: str, props: Iterable[str]) -> dict[str, str]:
    cmd = ["systemctl", "show", unit]
    for prop in props:
        cmd.extend(["-p", prop])
    cmd.append("--no-pager")
    rc, out, _ = _cmd(cmd)
    values: dict[str, str] = {}
    if rc != 0:
        return values
    for line in out.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value
    return values


def _read_cgroup_path(pid: int) -> str:
    cgroup_file = Path(f"/proc/{pid}/cgroup")
    if not cgroup_file.exists():
        return ""
    try:
        for line in cgroup_file.read_text(encoding="utf-8").splitlines():
            parts = line.split(":", 2)
            if len(parts) == 3 and parts[2]:
                return parts[2]
    except Exception:
        return ""
    return ""


def _list_stage_processes() -> list[tuple[int, str, str]]:
    rc, out, _ = _cmd(["ps", "-eo", "pid=,args="])
    if rc != 0:
        return []
    rows: list[tuple[int, str, str]] = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue
        if not parts[0].isdigit():
            continue
        pid = int(parts[0])
        cmd = parts[1]
        if "linux_runtime_preflight.py" in cmd:
            continue
        if any(pat in cmd for pat in STAGE_PATTERNS):
            rows.append((pid, cmd, _read_cgroup_path(pid)))
    return rows


def _kill_pids(pids: list[int]) -> None:
    if not pids:
        return
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        except PermissionError:
            pass
    time.sleep(1.0)
    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except PermissionError:
            pass


def main() -> int:
    ap = argparse.ArgumentParser(description="Linux preflight checks for Omega Stage1/Stage2")
    ap.add_argument("--repo-root", default="/home/zepher/work/Omega_vNext")
    ap.add_argument("--python-bin", default="", help="Python path for dependency checks")
    ap.add_argument("--cache-dir", default="/home/zepher/framing_cache")
    ap.add_argument("--min-cache-free-gb", type=float, default=300.0)
    ap.add_argument("--require-heavy-memory-max-gb", type=float, default=100.0)
    ap.add_argument("--require-heavy-memory-high-gb", type=float, default=90.0)
    ap.add_argument("--require-heavy-cpu-quota", type=int, default=24)
    ap.add_argument("--auto-fix", action="store_true", help="Apply safe fixes (currently cache-dir create).")
    ap.add_argument("--kill-user-slice-stage-procs", action="store_true")
    ap.add_argument("--json-out", default="", help="Optional output file path for machine-readable report")
    args = ap.parse_args()

    checks: list[CheckResult] = []

    if sys.platform != "linux":
        checks.append(
            CheckResult(
                name="platform",
                status="FAIL",
                detail="This preflight must run on Linux.",
                evidence=f"platform={sys.platform}",
            )
        )
        report = {"ok": False, "checks": [asdict(c) for c in checks]}
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 2

    repo_root = Path(args.repo_root)
    python_bin = args.python_bin.strip()
    if not python_bin:
        candidate = repo_root / ".venv/bin/python"
        python_bin = str(candidate if candidate.exists() else Path(sys.executable))

    # 1) Mount and path checks
    omega_pool = Path("/omega_pool")
    raw_root = Path("/omega_pool/raw_7z_archives")
    base_l1 = Path("/omega_pool/parquet_data/v62_base_l1/host=linux1")
    feat_l2 = Path("/omega_pool/parquet_data/v62_feature_l2/host=linux1")

    mounted = os.path.ismount(str(omega_pool))
    checks.append(
        CheckResult(
            name="mount_/omega_pool",
            status="PASS" if mounted else "FAIL",
            detail="omega_pool must be a mounted filesystem.",
            evidence=f"mounted={mounted}",
        )
    )

    for path in (raw_root, base_l1, feat_l2, repo_root):
        checks.append(
            CheckResult(
                name=f"path_exists:{path}",
                status="PASS" if path.exists() else "FAIL",
                detail="Required path must exist.",
                evidence=str(path),
            )
        )

    # 2) Slice policy checks
    heavy_props = _read_slice_properties(
        "heavy-workload.slice",
        ("MemoryHigh", "MemoryMax", "CPUQuotaPerSecUSec"),
    )
    user_props = _read_slice_properties("user-1000.slice", ("MemoryHigh", "MemoryMax"))

    heavy_mem_high = _parse_systemctl_int(heavy_props.get("MemoryHigh", ""))
    heavy_mem_max = _parse_systemctl_int(heavy_props.get("MemoryMax", ""))
    heavy_cpu = _parse_systemctl_int(heavy_props.get("CPUQuotaPerSecUSec", ""))

    user_mem_max = _parse_systemctl_int(user_props.get("MemoryMax", ""))

    heavy_mem_high_ok = heavy_mem_high is not None and heavy_mem_high >= int(
        args.require_heavy_memory_high_gb * (1024**3)
    )
    heavy_mem_max_ok = heavy_mem_max is not None and heavy_mem_max >= int(
        args.require_heavy_memory_max_gb * (1024**3)
    )
    heavy_cpu_ok = heavy_cpu is not None and heavy_cpu >= args.require_heavy_cpu_quota

    checks.append(
        CheckResult(
            name="slice_heavy_memoryhigh",
            status="PASS" if heavy_mem_high_ok else "FAIL",
            detail="heavy-workload.slice MemoryHigh must stay at protected baseline.",
            evidence=f"MemoryHigh={heavy_props.get('MemoryHigh', '<missing>')}",
        )
    )
    checks.append(
        CheckResult(
            name="slice_heavy_memorymax",
            status="PASS" if heavy_mem_max_ok else "FAIL",
            detail="heavy-workload.slice MemoryMax must stay at protected baseline.",
            evidence=f"MemoryMax={heavy_props.get('MemoryMax', '<missing>')}",
        )
    )
    checks.append(
        CheckResult(
            name="slice_heavy_cpuquota",
            status="PASS" if heavy_cpu_ok else "FAIL",
            detail="heavy-workload.slice CPU quota must remain uncapped for throughput.",
            evidence=f"CPUQuotaPerSecUSec={heavy_props.get('CPUQuotaPerSecUSec', '<missing>')}",
        )
    )
    checks.append(
        CheckResult(
            name="slice_user_memorymax_info",
            status="INFO",
            detail="user-1000.slice MemoryMax is informational (OOM risk context).",
            evidence=f"MemoryMax={user_mem_max if user_mem_max is not None else '<missing>'}",
        )
    )

    # 3) Python runtime dependency checks
    dep_cmd = [
        python_bin,
        "-c",
        "import polars,pyarrow,numba; print('deps_ok')",
    ]
    dep_rc, dep_out, dep_err = _cmd(dep_cmd)
    checks.append(
        CheckResult(
            name="python_deps",
            status="PASS" if dep_rc == 0 else "FAIL",
            detail="Python runtime must import polars/pyarrow/numba.",
            evidence=dep_out if dep_rc == 0 else dep_err,
        )
    )

    # 4) Cache free-space check
    cache_dir = Path(args.cache_dir)
    if cache_dir.exists():
        usage = shutil.disk_usage(cache_dir)
        free_gb = _bytes_to_gb(usage.free)
        cache_ok = free_gb >= args.min_cache_free_gb
        checks.append(
            CheckResult(
                name="cache_free_space",
                status="PASS" if cache_ok else "FAIL",
                detail="framing_cache free space must exceed threshold.",
                evidence=f"free_gb={free_gb:.2f}, threshold_gb={args.min_cache_free_gb:.2f}",
            )
        )
    else:
        created = False
        if args.auto_fix:
            try:
                cache_dir.mkdir(parents=True, exist_ok=True)
                created = True
            except Exception:
                created = False
        if created:
            usage = shutil.disk_usage(cache_dir)
            free_gb = _bytes_to_gb(usage.free)
            cache_ok = free_gb >= args.min_cache_free_gb
            checks.append(
                CheckResult(
                    name="cache_free_space",
                    status="PASS" if cache_ok else "FAIL",
                    detail="framing_cache auto-created; free-space threshold check applied.",
                    evidence=f"free_gb={free_gb:.2f}, threshold_gb={args.min_cache_free_gb:.2f}",
                )
            )
        else:
            checks.append(
                CheckResult(
                    name="cache_free_space",
                    status="FAIL",
                    detail="framing_cache directory is missing.",
                    evidence=str(cache_dir),
                )
            )
    # 5) Running stage process placement check
    stage_rows = _list_stage_processes()
    bad_pids = [pid for pid, _, cg in stage_rows if "heavy-workload.slice" not in cg]
    if args.kill_user_slice_stage_procs and bad_pids:
        _kill_pids(bad_pids)
        stage_rows = _list_stage_processes()
        bad_pids = [pid for pid, _, cg in stage_rows if "heavy-workload.slice" not in cg]

    if stage_rows:
        evidence = "\n".join(
            f"pid={pid} cgroup={cg or '<unknown>'} cmd={cmd}" for pid, cmd, cg in stage_rows
        )
    else:
        evidence = "no stage process detected"

    checks.append(
        CheckResult(
            name="stage_process_cgroup",
            status="PASS" if not bad_pids else "FAIL",
            detail="All running stage processes must be in heavy-workload.slice.",
            evidence=evidence,
        )
    )

    # 6) Previous boot OOM context (warning only)
    oom_rc, oom_out, _ = _cmd(
        [
            "journalctl",
            "-b",
            "-1",
            "-k",
            "-g",
            "oom-killer|mem_cgroup_out_of_memory",
            "-n",
            "20",
            "--no-pager",
        ]
    )
    if oom_rc == 0 and oom_out:
        checks.append(
            CheckResult(
                name="prev_boot_oom_context",
                status="WARN",
                detail="Previous boot includes kernel OOM signatures; verify launch path is guarded.",
                evidence=oom_out,
            )
        )
    else:
        checks.append(
            CheckResult(
                name="prev_boot_oom_context",
                status="PASS",
                detail="No previous-boot kernel OOM signature found in sampled logs.",
            )
        )

    fail_count = sum(1 for c in checks if c.status == "FAIL")
    warn_count = sum(1 for c in checks if c.status == "WARN")
    ok = fail_count == 0

    report = {
        "ok": ok,
        "fail_count": fail_count,
        "warn_count": warn_count,
        "checks": [asdict(c) for c in checks],
    }

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
