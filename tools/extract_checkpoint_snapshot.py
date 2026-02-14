#!/usr/bin/env python3
"""
Extract a JSON snapshot from a training checkpoint.

Example:
  python tools/extract_checkpoint_snapshot.py \
    --checkpoint artifacts/checkpoint_rows_55039250.pkl \
    --output audit/v5_runtime/windows/pipeline/checkpoint_rows_55039250_snapshot.json
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import pickle
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

# Ensure repository root is importable for pickle modules (e.g., config).
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _to_builtin(obj: Any, depth: int = 0) -> Any:
    if depth > 6:
        return str(type(obj))
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if dataclasses.is_dataclass(obj):
        return {f.name: _to_builtin(getattr(obj, f.name), depth + 1) for f in dataclasses.fields(obj)}
    if isinstance(obj, dict):
        return {str(k): _to_builtin(v, depth + 1) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_to_builtin(v, depth + 1) for v in obj]
    if hasattr(obj, "__dict__"):
        out = {}
        for k, v in vars(obj).items():
            if k.startswith("_"):
                continue
            out[k] = _to_builtin(v, depth + 1)
        if out:
            return out
    return str(obj)


def _safe_get_attr(obj: Any, path: str, default: Any = None) -> Any:
    cur = obj
    for token in path.split("."):
        if not hasattr(cur, token):
            return default
        cur = getattr(cur, token)
    return cur


def extract(checkpoint_path: Path) -> Dict[str, Any]:
    with checkpoint_path.open("rb") as f:
        ckpt = pickle.load(f)

    model = ckpt.get("model")
    scaler = ckpt.get("scaler")
    feature_cols: List[str] = list(ckpt.get("feature_cols", []))

    coef = np.asarray(getattr(model, "coef_", np.array([])), dtype=float)
    if coef.ndim == 1:
        coef = coef.reshape(1, -1)
    intercept = np.asarray(getattr(model, "intercept_", np.array([])), dtype=float).tolist()
    classes = _to_builtin(getattr(model, "classes_", []))

    # Binary classifier stores one row of coefficients.
    weight_vec: List[float] = []
    if coef.size > 0:
        if coef.shape[0] == 1:
            weight_vec = coef[0].tolist()
        else:
            # Multi-class fallback: use mean absolute effect proxy by class-mean signless.
            weight_vec = np.mean(np.abs(coef), axis=0).tolist()

    feature_weights: List[Dict[str, Any]] = []
    for i, feat in enumerate(feature_cols):
        w = float(weight_vec[i]) if i < len(weight_vec) else None
        feature_weights.append(
            {
                "feature": feat,
                "coef": w,
                "abs_coef": abs(w) if isinstance(w, float) else None,
                "scaler_mean": float(scaler.mean_[i]) if scaler is not None and hasattr(scaler, "mean_") and i < len(scaler.mean_) else None,
                "scaler_scale": float(scaler.scale_[i]) if scaler is not None and hasattr(scaler, "scale_") and i < len(scaler.scale_) else None,
            }
        )

    feature_weights_sorted = sorted(
        feature_weights,
        key=lambda x: (x["abs_coef"] if isinstance(x["abs_coef"], float) else -1.0),
        reverse=True,
    )

    cfg = ckpt.get("cfg")
    cfg_snapshot = {
        "train": {
            "label_horizon_buckets": _safe_get_attr(cfg, "train.label_horizon_buckets"),
            "label_sigma_mult": _safe_get_attr(cfg, "train.label_sigma_mult"),
            "drop_neutral_labels": _safe_get_attr(cfg, "train.drop_neutral_labels"),
            "min_epiplexity_gate": _safe_get_attr(cfg, "train.min_epiplexity_gate"),
            "winsor_features": _to_builtin(_safe_get_attr(cfg, "train.winsor_features")),
            "winsor_q_low": _safe_get_attr(cfg, "train.winsor_q_low"),
            "winsor_q_high": _safe_get_attr(cfg, "train.winsor_q_high"),
            "decision_margin": _safe_get_attr(cfg, "train.decision_margin"),
        },
        "validation": {
            "topo_snr_min": _safe_get_attr(cfg, "validation.topo_snr_min"),
            "orthogonality_max_abs": _safe_get_attr(cfg, "validation.orthogonality_max_abs"),
            "vector_alignment_min": _safe_get_attr(cfg, "validation.vector_alignment_min"),
            "forward_return_horizon_buckets": _safe_get_attr(cfg, "validation.forward_return_horizon_buckets"),
            "min_samples": _safe_get_attr(cfg, "validation.min_samples"),
        },
        "split": {
            "test_years": _to_builtin(_safe_get_attr(cfg, "split.test_years")),
            "test_year_months": _to_builtin(_safe_get_attr(cfg, "split.test_year_months")),
        },
    }

    model_hparams = {}
    for attr in [
        "loss",
        "penalty",
        "alpha",
        "average",
        "learning_rate",
        "eta0",
        "power_t",
        "fit_intercept",
    ]:
        if hasattr(model, attr):
            model_hparams[attr] = _to_builtin(getattr(model, attr))

    summary = {
        "checkpoint_path": str(checkpoint_path),
        "checkpoint_keys": sorted([str(k) for k in ckpt.keys()]),
        "model_class": type(model).__name__ if model is not None else None,
        "model_hyperparams": model_hparams,
        "classes": classes,
        "coef_shape": list(coef.shape) if coef.size > 0 else [0, 0],
        "intercept": intercept,
        "feature_count": len(feature_cols),
        "feature_cols": feature_cols,
        "feature_weights": feature_weights,
        "feature_weights_abs_desc": feature_weights_sorted,
        "cfg_snapshot": cfg_snapshot,
        "checkpoint_meta": {
            "total_rows": ckpt.get("total_rows"),
            "processed_files_count": len(ckpt.get("processed_files", []))
            if isinstance(ckpt.get("processed_files", []), (list, set, tuple))
            else None,
        },
    }
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    ckpt_path = Path(args.checkpoint)
    out_path = Path(args.output)

    data = extract(ckpt_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(out_path))
    print(
        json.dumps(
            {
                "feature_count": data["feature_count"],
                "coef_shape": data["coef_shape"],
                "classes": data["classes"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
