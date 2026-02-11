#!/usr/bin/env python3
"""
v40 recursive audit checks:
- Config invariants (race lanes/manifolds)
- No-literal drift for key race constants outside config.py
- Runtime smoke on recursive physics output schema
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Dict, List

import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config import L2PipelineConfig
from omega_v3_core.kernel import apply_recursive_physics


def _ok(name: str, details: str) -> Dict[str, str]:
    return {"name": name, "status": "PASS", "details": details}


def _fail(name: str, details: str) -> Dict[str, str]:
    return {"name": name, "status": "FAIL", "details": details}


def _scan_no_literal(targets: List[Path], literal: str) -> Dict[str, str]:
    offenders: List[str] = []
    for p in targets:
        text = p.read_text(encoding="utf-8")
        if literal in text:
            offenders.append(str(p))
    if offenders:
        return _fail(
            f"no_literal_{literal}",
            f"literal '{literal}' found in: {offenders}",
        )
    return _ok(f"no_literal_{literal}", f"literal '{literal}' only configured centrally")


def _runtime_smoke(cfg: L2PipelineConfig) -> Dict[str, str]:
    frames = pl.DataFrame(
        {
            "bucket_id": [0],
            "trace": [[10.0, 10.02, 10.01, 10.03, 10.05]],
            "ofi_list": [[100.0, -50.0, 80.0, 20.0]],
            "open": [10.0],
            "close": [10.05],
            "sigma": [0.02],
            "net_ofi": [150.0],
            "depth": [5000.0],
            "trade_vol": [2000.0],
            "cancel_vol": [300.0],
        }
    )
    out = apply_recursive_physics(frames, cfg)
    if out.height != 1:
        return _fail("runtime_smoke", f"unexpected row count={out.height}")

    required = [
        "epiplexity",
        "srl_resid",
        "topo_area",
        "topo_energy",
        "depth_eff",
        "spoof_ratio",
        "is_energy_active",
        "sigma_gate",
        "adaptive_y",
        "is_signal",
    ]
    required.extend([f"srl_resid_{x}" for x in cfg.srl.race_lane_names])
    required.extend(
        [
            cfg.topology_race.micro_feature,
            cfg.topology_race.classic_feature,
            cfg.topology_race.trend_feature,
        ]
    )
    missing = [c for c in required if c not in out.columns]
    if missing:
        return _fail("runtime_smoke", f"missing columns={missing}")

    numeric_cols = [c for c in required if c != "is_signal"]
    row = out.select(numeric_cols).to_dicts()[0]
    for col in numeric_cols:
        val = row[col]
        if not math.isfinite(float(val)):
            return _fail("runtime_smoke", f"non-finite value in {col}: {val}")
    return _ok("runtime_smoke", "output schema and numeric sanity passed")


def _energy_gate_smoke(cfg: L2PipelineConfig) -> Dict[str, str]:
    if not cfg.epiplexity.sigma_gate_enabled:
        return _ok("energy_gate_smoke", "sigma gate disabled by config")

    base_trace = [10.0, 10.02, 10.01, 10.03, 10.05]
    frames = pl.DataFrame(
        {
            "bucket_id": [0, 1],
            "trace": [base_trace, base_trace],
            "ofi_list": [[100.0, -50.0, 80.0, 20.0], [100.0, -50.0, 80.0, 20.0]],
            "open": [10.0, 10.0],
            "close": [10.05, 10.05],
            "sigma": [cfg.epiplexity.sigma_gate * 2.0, cfg.epiplexity.sigma_gate * 0.5],
            "net_ofi": [150.0, 150.0],
            "depth": [5000.0, 5000.0],
            "trade_vol": [2000.0, 2000.0],
            "cancel_vol": [300.0, 300.0],
        }
    )
    out = apply_recursive_physics(frames, cfg).sort("bucket_id")
    rows = out.select(["is_energy_active", "epiplexity", "adaptive_y"]).to_dicts()
    hi = rows[0]
    lo = rows[1]
    if not bool(hi["is_energy_active"]):
        return _fail("energy_gate_smoke", "high-sigma row unexpectedly gated off")
    if bool(lo["is_energy_active"]):
        return _fail("energy_gate_smoke", "low-sigma row unexpectedly passed gate")
    if abs(float(lo["epiplexity"]) - float(cfg.epiplexity.fallback_value)) > 1e-12:
        return _fail("energy_gate_smoke", "low-sigma row epiplexity not reset to fallback")
    y = float(lo["adaptive_y"])
    lo_clip = min(float(cfg.srl.anchor_clip_min), float(cfg.srl.anchor_clip_max))
    hi_clip = max(float(cfg.srl.anchor_clip_min), float(cfg.srl.anchor_clip_max))
    if not (lo_clip <= y <= hi_clip):
        return _fail("energy_gate_smoke", f"adaptive_y out of clip range: {y}")
    return _ok("energy_gate_smoke", "energy gate and anchor clipping passed")


def main() -> int:
    cfg = L2PipelineConfig()
    checks: List[Dict[str, str]] = []

    if len(cfg.srl.race_exponents) != len(cfg.srl.race_lane_names):
        checks.append(
            _fail(
                "cfg_srl_lane_alignment",
                "race_exponents length != race_lane_names length",
            )
        )
    else:
        checks.append(_ok("cfg_srl_lane_alignment", "lane names match exponents"))

    if cfg.srl.standard_lane_index < 0 or cfg.srl.standard_lane_index >= len(cfg.srl.race_exponents):
        checks.append(_fail("cfg_srl_standard_lane", "standard_lane_index out of range"))
    else:
        checks.append(_ok("cfg_srl_standard_lane", "standard lane index valid"))

    if not (0.0 <= cfg.srl.anchor_weight <= 1.0):
        checks.append(_fail("cfg_anchor_weight", "anchor_weight should be in [0,1]"))
    else:
        checks.append(_ok("cfg_anchor_weight", "anchor weight in valid range"))

    if cfg.epiplexity.sigma_gate < cfg.srl.sigma_floor:
        checks.append(_fail("cfg_sigma_gate_floor", "sigma_gate below sigma_floor"))
    else:
        checks.append(_ok("cfg_sigma_gate_floor", "sigma_gate respects floor"))

    repo = REPO_ROOT
    targets = [
        repo / "omega_v3_core" / "omega_math_core.py",
        repo / "omega_v3_core" / "kernel.py",
        repo / "omega_v3_core" / "trainer.py",
        repo / "omega_v3_core" / "physics_auditor.py",
    ]
    checks.append(_scan_no_literal(targets, "0.33"))
    checks.append(_scan_no_literal(targets, "0.66"))

    checks.append(_runtime_smoke(cfg))
    checks.append(_energy_gate_smoke(cfg))

    passed = all(c["status"] == "PASS" for c in checks)
    report = {
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
