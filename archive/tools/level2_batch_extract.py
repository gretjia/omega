from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class ArchiveEntry:
    path: str
    size: int
    crc: Optional[str]
    is_dir: bool


def _now_ms() -> int:
    return int(time.time() * 1000)


def _norm_relpath(p: str) -> str:
    p = p.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p.strip("/")


def _is_windows_abs_path(p: str) -> bool:
    if len(p) >= 2 and p[1] == ":":
        return True
    return p.startswith("\\\\")


def _find_7z_exe(user_path: Optional[str]) -> Path:
    if user_path:
        p = Path(user_path)
        if p.exists():
            return p
        raise FileNotFoundError(f"7z.exe not found: {user_path}")
    env = os.environ.get("SEVEN_ZIP_EXE")
    if env:
        p = Path(env)
        if p.exists():
            return p
    candidates = [
        Path(r"C:\Program Files\7-Zip\7z.exe"),
        Path(r"C:\Program Files (x86)\7-Zip\7z.exe"),
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("7z.exe not found. Provide --seven-zip or set SEVEN_ZIP_EXE.")


def _disk_usage_bytes(path: Path) -> Tuple[int, int, int]:
    usage = shutil.disk_usage(str(path))
    return int(usage.total), int(usage.used), int(usage.free)


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    _ensure_dir(path.parent)
    tmp = path.with_suffix(path.suffix + f".tmp.{_now_ms()}")
    with open(tmp, "w", encoding=encoding, newline="\n") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _append_jsonl(path: Path, obj: Dict) -> None:
    _ensure_dir(path.parent)
    line = json.dumps(obj, ensure_ascii=False)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())


def _run_7z(seven_zip: Path, args: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    cmd = [str(seven_zip)] + args
    cp = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=False,
        capture_output=True,
        text=False,
    )
    stdout_b = cp.stdout if isinstance(cp.stdout, (bytes, bytearray)) else b""
    stderr_b = cp.stderr if isinstance(cp.stderr, (bytes, bytearray)) else b""

    def _decode(b: bytes) -> str:
        if not b:
            return ""
        for enc in ("utf-8", "gb18030", "cp936", "mbcs"):
            try:
                s = b.decode(enc, errors="replace")
            except Exception:
                continue
            if "\ufffd" not in s:
                return s
        return b.decode("gb18030", errors="replace")

    return subprocess.CompletedProcess(
        args=cp.args,
        returncode=cp.returncode,
        stdout=_decode(stdout_b),
        stderr=_decode(stderr_b),
    )


def _parse_7z_slt_list(output: str) -> List[ArchiveEntry]:
    entries: List[ArchiveEntry] = []
    current: Dict[str, str] = {}
    for raw_line in output.splitlines():
        line = raw_line.strip("\r\n")
        if not line:
            if current:
                path = current.get("Path")
                if path is not None:
                    size_str = current.get("Size", "0")
                    folder = current.get("Folder")
                    is_dir = (folder == "+") or (current.get("Attributes", "").startswith("D"))
                    crc = current.get("CRC")
                    try:
                        size = int(size_str)
                    except Exception:
                        size = 0
                    entries.append(ArchiveEntry(path=_norm_relpath(path), size=size, crc=crc, is_dir=is_dir))
                current = {}
            continue
        if " = " in line:
            k, v = line.split(" = ", 1)
            current[k.strip()] = v.strip()
    if current:
        path = current.get("Path")
        if path is not None:
            size_str = current.get("Size", "0")
            folder = current.get("Folder")
            is_dir = (folder == "+") or (current.get("Attributes", "").startswith("D"))
            crc = current.get("CRC")
            try:
                size = int(size_str)
            except Exception:
                size = 0
            entries.append(ArchiveEntry(path=_norm_relpath(path), size=size, crc=crc, is_dir=is_dir))
    entries = [e for e in entries if e.path not in ("", ".", "..")]
    return entries


def _list_archive_entries(seven_zip: Path, archive_path: Path) -> List[ArchiveEntry]:
    cp = _run_7z(seven_zip, ["l", "-slt", str(archive_path)])
    if cp.returncode != 0:
        raise RuntimeError(f"7z list failed: {archive_path}\n{cp.stdout}\n{cp.stderr}")
    entries = _parse_7z_slt_list(cp.stdout)
    ap_norm = _norm_relpath(str(archive_path).replace("\\", "/")).lower()
    cleaned: List[ArchiveEntry] = []
    for e in entries:
        p_norm = e.path.replace("\\", "/").lower()
        if p_norm == ap_norm and e.size == 0 and not e.is_dir:
            continue
        if _is_windows_abs_path(e.path) and e.size == 0 and not e.is_dir:
            continue
        cleaned.append(e)
    return cleaned


def _test_archive(seven_zip: Path, archive_path: Path) -> None:
    cp = _run_7z(seven_zip, ["t", str(archive_path), "-y"])
    if cp.returncode != 0:
        raise RuntimeError(f"7z test failed: {archive_path}\n{cp.stdout}\n{cp.stderr}")


def _extract_archive(seven_zip: Path, archive_path: Path, stage_dir: Path) -> None:
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    _ensure_dir(stage_dir)
    cp = _run_7z(seven_zip, ["x", str(archive_path), f"-o{stage_dir}", "-y"])
    if cp.returncode != 0:
        raise RuntimeError(f"7z extract failed: {archive_path}\n{cp.stdout}\n{cp.stderr}")


def _crc32_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    crc = 0
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            crc = zlib.crc32(b, crc)
    return f"{crc & 0xFFFFFFFF:08X}"


def _sha256_file(path: Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _verify_stage(
    entries: List[ArchiveEntry],
    stage_dir: Path,
    verify_crc: bool,
    verify_sha256: bool,
    strict_size: bool,
) -> Dict[str, int]:
    files = [e for e in entries if not e.is_dir]
    missing = 0
    size_mismatch = 0
    crc_mismatch = 0
    sha_mismatch = 0
    total_bytes_expected = 0
    total_bytes_seen = 0

    for e in files:
        total_bytes_expected += int(e.size)
        p = stage_dir / Path(e.path)
        if not p.exists():
            missing += 1
            continue
        if p.is_dir():
            missing += 1
            continue
        st = p.stat()
        total_bytes_seen += int(st.st_size)
        if strict_size and int(st.st_size) != int(e.size):
            size_mismatch += 1
        if verify_crc and e.crc:
            got = _crc32_file(p)
            if got.upper() != e.crc.upper():
                crc_mismatch += 1
        if verify_sha256:
            got = _sha256_file(p)
            expected_sha_path = p.with_suffix(p.suffix + ".sha256")
            if expected_sha_path.exists():
                expected = expected_sha_path.read_text(encoding="utf-8").strip()
                if got != expected:
                    sha_mismatch += 1

    return {
        "files_expected": len(files),
        "bytes_expected": total_bytes_expected,
        "files_missing": missing,
        "size_mismatch": size_mismatch,
        "crc_mismatch": crc_mismatch,
        "sha_mismatch": sha_mismatch,
        "bytes_seen": total_bytes_seen,
    }


def _copy_one_file(src: Path, dst: Path) -> None:
    _ensure_dir(dst.parent)
    tmp = dst.with_suffix(dst.suffix + f".tmp.{_now_ms()}")
    shutil.copy2(src, tmp)
    os.replace(tmp, dst)


def _copy_stage_to_dest(entries: List[ArchiveEntry], stage_dir: Path, dest_dir: Path) -> None:
    files = [e for e in entries if not e.is_dir]
    for e in files:
        src = stage_dir / Path(e.path)
        dst = dest_dir / Path(e.path)
        _copy_one_file(src, dst)


def _verify_dest(entries: List[ArchiveEntry], dest_dir: Path, verify_crc: bool, strict_size: bool) -> Dict[str, int]:
    files = [e for e in entries if not e.is_dir]
    missing = 0
    size_mismatch = 0
    crc_mismatch = 0
    total_bytes_expected = 0
    total_bytes_seen = 0

    for e in files:
        total_bytes_expected += int(e.size)
        p = dest_dir / Path(e.path)
        if not p.exists():
            missing += 1
            continue
        if p.is_dir():
            missing += 1
            continue
        st = p.stat()
        total_bytes_seen += int(st.st_size)
        if strict_size and int(st.st_size) != int(e.size):
            size_mismatch += 1
        if verify_crc and e.crc:
            got = _crc32_file(p)
            if got.upper() != e.crc.upper():
                crc_mismatch += 1

    return {
        "files_expected": len(files),
        "bytes_expected": total_bytes_expected,
        "files_missing": missing,
        "size_mismatch": size_mismatch,
        "crc_mismatch": crc_mismatch,
        "bytes_seen": total_bytes_seen,
    }


def _move_to_quarantine(src_archive: Path, quarantine_root: Path, src_root: Path) -> Path:
    rel = src_archive.relative_to(src_root)
    dst = quarantine_root / rel
    _ensure_dir(dst.parent)
    if dst.exists():
        dst = dst.with_suffix(dst.suffix + f".dup.{_now_ms()}")
    os.replace(src_archive, dst)
    return dst


def _format_gb(n: int) -> str:
    return f"{n / (1024**3):.3f} GB"


def _scan_archives(src_root: Path) -> List[Path]:
    return sorted([p for p in src_root.rglob("*.7z") if p.is_file()])


def _load_done_set(state_path: Path) -> Dict[str, str]:
    done: Dict[str, str] = {}
    if not state_path.exists():
        return done
    with open(state_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            ap = obj.get("archive_path")
            st = obj.get("status")
            if isinstance(ap, str) and isinstance(st, str):
                done[ap] = st
    return done


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    default_stage_root = r"D:\Omega_level2_stage" if (os.name == "nt" and Path(r"D:\\").exists()) else r"C:\Omega_level2_stage"
    ap.add_argument("--src-root", default="./data/level2")
    ap.add_argument("--dest-root", default="./data/leve2_csv")
    ap.add_argument("--stage-root", default=default_stage_root)
    ap.add_argument("--seven-zip", default=None)
    ap.add_argument("--batch-count", type=int, default=1)
    ap.add_argument("--state-jsonl", default=None)
    ap.add_argument("--archive-disposition", choices=["keep", "delete", "quarantine"], default="keep")
    ap.add_argument("--quarantine-root", default=r"C:\Omega_level2_quarantine")
    ap.add_argument("--verify-crc", action="store_true")
    ap.add_argument("--allow-weak-verify", action="store_true")
    ap.add_argument("--strict-size", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--min-free-c-gb", type=float, default=30.0)
    ap.add_argument("--min-free-d-gb", type=float, default=30.0)
    ap.add_argument("--confirm-delete-token", default="")
    ap.add_argument("--start-at", default="")
    ap.add_argument("--limit-archives", type=int, default=0)
    args = ap.parse_args(argv)

    src_root = Path(args.src_root).resolve()
    dest_root = Path(args.dest_root).resolve()
    stage_root = Path(args.stage_root).resolve()
    quarantine_root = Path(args.quarantine_root).resolve()
    seven_zip = _find_7z_exe(args.seven_zip)

    if args.archive_disposition == "delete":
        if args.confirm_delete_token != "DELETE_AFTER_VERIFY":
            raise RuntimeError("Refusing to delete archives without --confirm-delete-token DELETE_AFTER_VERIFY")
        if not (args.verify_crc or args.allow_weak_verify):
            raise RuntimeError("Refusing to delete archives without --verify-crc (or --allow-weak-verify).")
    if args.archive_disposition in ("delete", "quarantine") and args.dry_run:
        pass

    if not src_root.exists():
        raise FileNotFoundError(f"src_root not found: {src_root}")
    _ensure_dir(dest_root)
    _ensure_dir(stage_root)
    if args.archive_disposition == "quarantine":
        _ensure_dir(quarantine_root)

    state_path = Path(args.state_jsonl).resolve() if args.state_jsonl else (dest_root / "_batch_extract_state.jsonl")
    done = _load_done_set(state_path)

    archives = _scan_archives(src_root)
    if args.start_at:
        start = Path(args.start_at)
        start_s = str(start)
        archives = [p for p in archives if str(p) >= start_s]
    if args.limit_archives and args.limit_archives > 0:
        archives = archives[: int(args.limit_archives)]

    pending = [
        p
        for p in archives
        if done.get(str(p))
        not in (
            "archive_deleted",
            "archive_quarantined",
            "done_archive_deleted",
            "done_archive_quarantined",
            "done_archive_kept",
        )
    ]
    if args.batch_count <= 0:
        raise ValueError("--batch-count must be positive")
    pending = pending[: int(args.batch_count)]

    if not pending:
        print("No pending .7z archives to process.")
        return 0

    min_free_c = int(args.min_free_c_gb * (1024**3))
    min_free_d = int(args.min_free_d_gb * (1024**3))

    for idx, archive_path in enumerate(pending, start=1):
        archive_path = archive_path.resolve()
        archive_size = int(archive_path.stat().st_size)
        stage_dir = stage_root / (archive_path.stem + f".{_now_ms()}")

        _append_jsonl(
            state_path,
            {
                "ts_ms": _now_ms(),
                "archive_path": str(archive_path),
                "status": "start",
                "batch_index": idx,
                "batch_total": len(pending),
                "archive_size_bytes": archive_size,
            },
        )

        total_c, used_c, free_c = _disk_usage_bytes(stage_root)
        total_d, used_d, free_d = _disk_usage_bytes(dest_root)
        if free_c < min_free_c:
            raise RuntimeError(f"Low free space on C stage drive: free={_format_gb(free_c)} < min={_format_gb(min_free_c)}")
        if free_d < min_free_d:
            raise RuntimeError(f"Low free space on dest drive: free={_format_gb(free_d)} < min={_format_gb(min_free_d)}")

        entries = _list_archive_entries(seven_zip, archive_path)
        file_entries = [e for e in entries if not e.is_dir]
        bytes_expected = sum(int(e.size) for e in file_entries)
        _append_jsonl(
            state_path,
            {
                "ts_ms": _now_ms(),
                "archive_path": str(archive_path),
                "status": "listed",
                "files_expected": len(file_entries),
                "bytes_expected": bytes_expected,
            },
        )

        if args.dry_run:
            print(f"[DRY RUN] {archive_path}")
            print(f"  archive_size={_format_gb(archive_size)} extracted_bytes={_format_gb(bytes_expected)} files={len(file_entries)}")
            _append_jsonl(state_path, {"ts_ms": _now_ms(), "archive_path": str(archive_path), "status": "dry_run_done"})
            continue

        _test_archive(seven_zip, archive_path)
        _append_jsonl(state_path, {"ts_ms": _now_ms(), "archive_path": str(archive_path), "status": "tested_ok"})

        total_c, used_c, free_c = _disk_usage_bytes(stage_root)
        if free_c - bytes_expected < min_free_c:
            raise RuntimeError(
                f"Insufficient C staging space: free={_format_gb(free_c)} need~={_format_gb(bytes_expected)} min_free={_format_gb(min_free_c)}"
            )

        _extract_archive(seven_zip, archive_path, stage_dir)
        _append_jsonl(state_path, {"ts_ms": _now_ms(), "archive_path": str(archive_path), "status": "extracted_to_stage", "stage_dir": str(stage_dir)})

        verify_crc = bool(args.verify_crc)
        strict_size = bool(args.strict_size)
        stage_metrics = _verify_stage(entries, stage_dir, verify_crc=verify_crc, verify_sha256=False, strict_size=strict_size)
        _append_jsonl(state_path, {"ts_ms": _now_ms(), "archive_path": str(archive_path), "status": "stage_verified", **stage_metrics})
        if stage_metrics["files_missing"] or stage_metrics["size_mismatch"] or stage_metrics["crc_mismatch"]:
            raise RuntimeError(f"Stage verification failed for {archive_path}: {stage_metrics}")

        total_d, used_d, free_d = _disk_usage_bytes(dest_root)
        free_after_archive_removed = free_d + archive_size
        if free_after_archive_removed - bytes_expected < min_free_d:
            raise RuntimeError(
                f"Insufficient dest space after archive removal: free_after_remove={_format_gb(free_after_archive_removed)} need~={_format_gb(bytes_expected)} min_free={_format_gb(min_free_d)}"
            )

        quarantined_to = None
        if args.archive_disposition == "quarantine":
            qp = _move_to_quarantine(archive_path, quarantine_root, src_root)
            quarantined_to = str(qp)
            _append_jsonl(state_path, {"ts_ms": _now_ms(), "archive_path": str(archive_path), "status": "archive_quarantined", "quarantine_path": quarantined_to})
        elif args.archive_disposition == "delete":
            archive_path.unlink()
            _append_jsonl(state_path, {"ts_ms": _now_ms(), "archive_path": str(archive_path), "status": "archive_deleted"})

        _copy_stage_to_dest(entries, stage_dir, dest_root)
        _append_jsonl(state_path, {"ts_ms": _now_ms(), "archive_path": str(archive_path), "status": "copied_to_dest", "dest_root": str(dest_root)})

        dest_metrics = _verify_dest(entries, dest_root, verify_crc=verify_crc, strict_size=strict_size)
        _append_jsonl(state_path, {"ts_ms": _now_ms(), "archive_path": str(archive_path), "status": "dest_verified", **dest_metrics})
        if dest_metrics["files_missing"] or dest_metrics["size_mismatch"] or dest_metrics["crc_mismatch"]:
            raise RuntimeError(f"Dest verification failed for {archive_path}: {dest_metrics}")

        shutil.rmtree(stage_dir)
        _append_jsonl(state_path, {"ts_ms": _now_ms(), "archive_path": str(archive_path), "status": "stage_cleaned"})

        if args.archive_disposition == "keep":
            _append_jsonl(state_path, {"ts_ms": _now_ms(), "archive_path": str(archive_path), "status": "done_archive_kept"})
        elif args.archive_disposition == "quarantine":
            _append_jsonl(
                state_path,
                {"ts_ms": _now_ms(), "archive_path": str(archive_path), "status": "done_archive_quarantined", "quarantine_path": quarantined_to},
            )
        elif args.archive_disposition == "delete":
            _append_jsonl(state_path, {"ts_ms": _now_ms(), "archive_path": str(archive_path), "status": "done_archive_deleted"})

        print(f"[OK] {archive_path} -> {dest_root} (archive={args.archive_disposition})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
