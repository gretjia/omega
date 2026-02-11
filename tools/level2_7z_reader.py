from __future__ import annotations

import csv
import io
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Tuple

import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1]))

from data_adapter import TickData, _normalize_volume
from config import CSVParseConfig


@dataclass(frozen=True)
class SevenZipConfig:
    exe_path: str = ""


def _find_7z_exe(cfg: SevenZipConfig) -> Path:
    if cfg.exe_path:
        p = Path(cfg.exe_path)
        if p.exists():
            return p
        raise FileNotFoundError(str(p))
    env = os.environ.get("SEVEN_ZIP_EXE", "")
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
    raise FileNotFoundError("7z.exe not found. Set SEVEN_ZIP_EXE or pass SevenZipConfig(exe_path=...).")


def _popen_7z_stream_text(seven_zip: Path, archive_path: Path, inner_path: str) -> Tuple[subprocess.Popen, io.TextIOBase]:
    cmd = [str(seven_zip), "e", str(archive_path), inner_path, "-so", "-y"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.stdout is None:
        p.kill()
        raise RuntimeError("Failed to open 7z stdout pipe")
    text = io.TextIOWrapper(p.stdout, encoding="gb18030", errors="replace", newline="")
    return p, text


def iter_level2_quote_rows_from_7z(cfg: SevenZipConfig, archive_path: str | Path, inner_path: str) -> Iterator[Dict[str, str]]:
    seven_zip = _find_7z_exe(cfg)
    ap = Path(archive_path)
    proc, text = _popen_7z_stream_text(seven_zip, ap, inner_path)
    try:
        reader = csv.reader(text)
        header = next(reader, None)
        if header is None:
            return
        cols = [h.strip() for h in header]
        for row in reader:
            if not row:
                continue
            yield {cols[i]: (row[i] if i < len(row) else "") for i in range(len(cols))}
    finally:
        try:
            text.close()
        except Exception:
            pass
        try:
            if proc.stderr is not None:
                try:
                    _ = proc.stderr.read()
                except Exception:
                    pass
            proc.wait(timeout=10)
        except Exception:
            proc.kill()


def _parse_time_to_datetime64(day: str, hhmmssmmm: str) -> np.datetime64:
    day_s = str(day).strip()
    t_s = str(hhmmssmmm).strip()
    if not day_s.isdigit():
        return np.datetime64("NaT")
    if not t_s.isdigit():
        return np.datetime64("NaT")
    y = int(day_s[0:4])
    m = int(day_s[4:6])
    d = int(day_s[6:8])
    t9 = t_s.zfill(9)
    hh = int(t9[0:2])
    mm = int(t9[2:4])
    ss = int(t9[4:6])
    ms = int(t9[6:9])
    dt = datetime(y, m, d, hh, mm, ss, ms * 1000)
    return np.datetime64(dt, "ns")


def read_level2_quote_as_tickdata_from_7z(
    cfg_7z: SevenZipConfig,
    archive_path: str | Path,
    inner_path: str,
    csv_cfg: Optional[CSVParseConfig] = None,
    max_rows: Optional[int] = None,
) -> TickData:
    csv_cfg = csv_cfg or CSVParseConfig()

    times: List[np.datetime64] = []
    prices: List[float] = []
    vols: List[float] = []
    ask1: List[float] = []
    bid1: List[float] = []

    day_col = "自然日"
    time_col = "时间"
    price_col = "成交价"
    vol_col = "成交量"
    ask1_col = "申卖价1"
    bid1_col = "申买价1"

    n = 0
    for row in iter_level2_quote_rows_from_7z(cfg_7z, archive_path, inner_path):
        if max_rows is not None and n >= int(max_rows):
            break
        n += 1
        t = _parse_time_to_datetime64(row.get(day_col, ""), row.get(time_col, ""))
        try:
            p = float(row.get(price_col, "") or "nan")
        except Exception:
            p = float("nan")
        try:
            v = float(row.get(vol_col, "") or "nan")
        except Exception:
            v = float("nan")
        try:
            a1 = float(row.get(ask1_col, "") or "nan")
        except Exception:
            a1 = float("nan")
        try:
            b1 = float(row.get(bid1_col, "") or "nan")
        except Exception:
            b1 = float("nan")

        times.append(t)
        prices.append(p)
        vols.append(v)
        ask1.append(a1)
        bid1.append(b1)

    t_np = np.asarray(times, dtype="datetime64[ns]")
    p_np = np.asarray(prices, dtype=float)
    v_raw = np.asarray(vols, dtype=float)
    a_np = np.asarray(ask1, dtype=float)
    b_np = np.asarray(bid1, dtype=float)

    if csv_cfg.sort_by_time and t_np.size > 0:
        order = np.argsort(t_np)
        t_np = t_np[order]
        p_np = p_np[order]
        v_raw = v_raw[order]
        a_np = a_np[order]
        b_np = b_np[order]

    vol = _normalize_volume(v_raw, csv_cfg.volume_mode)

    return TickData(
        time=t_np,
        price=p_np,
        volume=np.asarray(vol, dtype=float),
        ask1=a_np,
        bid1=b_np,
        source_path=f"{Path(archive_path)}::{inner_path}",
    )
