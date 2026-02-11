#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pickle
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Sequence

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


SRL_CANDIDATES = ("srl_resid_033", "srl_resid_050", "srl_resid_066")
TOPO_CANDIDATES = ("topo_classic", "topo_micro", "topo_trend")


@dataclass
class RankedWeight:
    feature: str
    weight: float
    abs_weight: float

    def to_dict(self) -> Dict[str, float | str]:
        return {
            "feature": self.feature,
            "weight": self.weight,
            "abs_weight": self.abs_weight,
        }


def _resolve_checkpoint(path_arg: str) -> Path:
    if path_arg:
        path = Path(path_arg)
        if not path.exists():
            raise FileNotFoundError(f"checkpoint not found: {path}")
        return path
    artifacts = Path("artifacts")
    candidates = sorted(
        artifacts.glob("checkpoint_rows_*.pkl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(
            "no checkpoint_rows_*.pkl found under ./artifacts, please pass --checkpoint"
        )
    return candidates[0]


def _extract_coef_1d(model: object, n_features: int) -> np.ndarray:
    coef = getattr(model, "coef_", None)
    if coef is None:
        raise ValueError("checkpoint model has no coef_")
    arr = np.asarray(coef, dtype=float)
    if arr.ndim == 1:
        if arr.shape[0] != n_features:
            raise ValueError("coef shape mismatch with feature list")
        return arr
    if arr.ndim == 2:
        if arr.shape[1] != n_features:
            raise ValueError("coef shape mismatch with feature list")
        return arr[0]
    raise ValueError(f"unsupported coef ndim: {arr.ndim}")


def _rank_from_features(
    feature_index: Dict[str, int],
    coef: np.ndarray,
    candidates: Sequence[str],
    fallback_prefix: str | None = None,
) -> List[RankedWeight]:
    names: List[str] = [f for f in candidates if f in feature_index]
    if not names and fallback_prefix:
        names = [f for f in feature_index.keys() if f.startswith(fallback_prefix)]
    ranked: List[RankedWeight] = []
    for name in names:
        w = float(coef[feature_index[name]])
        ranked.append(RankedWeight(feature=name, weight=w, abs_weight=abs(w)))
    ranked.sort(key=lambda x: x.abs_weight, reverse=True)
    return ranked


def _winner_payload(ranked: List[RankedWeight]) -> Dict[str, object]:
    if not ranked:
        return {"winner_by_abs_weight": None, "weights": []}
    return {
        "winner_by_abs_weight": ranked[0].feature,
        "weights": [x.to_dict() for x in ranked],
    }


def _build_markdown(payload: Dict[str, object]) -> str:
    srl = payload["srl_race"]
    topo = payload["topology_race"]
    lines: List[str] = []
    lines.append("# v40 Race Winner Summary")
    lines.append("")
    lines.append(f"- timestamp: {payload['timestamp']}")
    lines.append(f"- checkpoint: {payload['policy']}")
    lines.append(f"- rows_trained: {payload['rows_trained']}")
    lines.append(f"- n_features: {payload['n_features']}")
    lines.append(f"- srl winner: {srl['winner_by_abs_weight']}")
    lines.append(f"- topology winner: {topo['winner_by_abs_weight']}")
    lines.append("")
    lines.append("## SRL weights (abs desc)")
    lines.append("")
    lines.append("| feature | weight | abs_weight |")
    lines.append("|---|---:|---:|")
    for row in srl["weights"]:
        lines.append(
            f"| {row['feature']} | {row['weight']:.10g} | {row['abs_weight']:.10g} |"
        )
    lines.append("")
    lines.append("## Topology weights (abs desc)")
    lines.append("")
    lines.append("| feature | weight | abs_weight |")
    lines.append("|---|---:|---:|")
    for row in topo["weights"]:
        lines.append(
            f"| {row['feature']} | {row['weight']:.10g} | {row['abs_weight']:.10g} |"
        )
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Extract v40 race winners from a training checkpoint."
    )
    p.add_argument("--checkpoint", default="", help="Path to checkpoint .pkl")
    p.add_argument(
        "--out-json",
        default="audit/v40_runtime/windows/backtest/race_winner_summary.json",
        help="Output JSON path.",
    )
    p.add_argument(
        "--out-md",
        default="audit/v40_runtime/windows/backtest/race_winner_summary.md",
        help="Output markdown path.",
    )
    return p.parse_args()


def _install_pickle_compat_shims() -> None:
    # Some checkpoints were serialized with numpy 2.x module paths (numpy._core.*).
    # Keep loading robust across numpy minor versions/environments.
    try:
        import numpy.core as np_core  # type: ignore

        sys.modules.setdefault("numpy._core", np_core)
        for sub in ("numeric", "multiarray", "_multiarray_umath", "umath"):
            legacy = f"numpy._core.{sub}"
            if legacy in sys.modules:
                continue
            try:
                mod = __import__(f"numpy.core.{sub}", fromlist=["*"])
                sys.modules[legacy] = mod
            except Exception:
                pass
    except Exception:
        pass


def main() -> int:
    args = parse_args()
    ckpt = _resolve_checkpoint(args.checkpoint)
    _install_pickle_compat_shims()
    with ckpt.open("rb") as f:
        payload = pickle.load(f)

    model = payload.get("model")
    feature_cols = payload.get("feature_cols", [])
    total_rows = int(payload.get("total_rows", 0))
    if model is None or not feature_cols:
        raise ValueError("checkpoint missing model or feature_cols")

    feature_cols = [str(x) for x in feature_cols]
    feature_index = {name: idx for idx, name in enumerate(feature_cols)}
    coef = _extract_coef_1d(model, len(feature_cols))

    srl_ranked = _rank_from_features(
        feature_index, coef, SRL_CANDIDATES, fallback_prefix="srl_resid_"
    )
    topo_ranked = _rank_from_features(
        feature_index, coef, TOPO_CANDIDATES, fallback_prefix="topo_"
    )

    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "policy": str(ckpt.resolve()),
        "rows_trained": total_rows,
        "n_features": len(feature_cols),
        "srl_race": _winner_payload(srl_ranked),
        "topology_race": _winner_payload(topo_ranked),
    }

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    out_md.write_text(_build_markdown(result), encoding="utf-8")
    print(f"[ok] race winner json: {out_json}")
    print(f"[ok] race winner md: {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
