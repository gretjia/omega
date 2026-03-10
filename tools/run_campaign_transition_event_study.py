#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import polars as pl

from tools.run_campaign_event_study import compute_event_study_for_signal

DEFAULT_SIGNAL_COLS = [
    "dPsiAmpE_10d",
    "dPsiAmpE_20d",
    "dPsiAmpStar_10d",
    "dPsiAmpStar_20d",
    "FreshAmpE_10d",
    "FreshAmpE_20d",
    "FreshAmpStar_10d",
    "FreshAmpStar_20d",
]


def _sign_expr(col_name: str) -> pl.Expr:
    return (
        pl.when(pl.col(col_name) > 0.0)
        .then(pl.lit(1.0))
        .when(pl.col(col_name) < 0.0)
        .then(pl.lit(-1.0))
        .otherwise(pl.lit(0.0))
    )


def derive_transition_columns(df: pl.DataFrame) -> pl.DataFrame:
    required = {
        "symbol",
        "pure_date",
        "PsiAmpE_10d",
        "PsiAmpE_20d",
        "PsiAmpStar_10d",
        "PsiAmpStar_20d",
        "OmegaAmpE_10d",
        "OmegaAmpE_20d",
        "OmegaAmpStar_10d",
        "OmegaAmpStar_20d",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"missing required V656 transition columns: {sorted(missing)}")

    work = df.sort(["symbol", "pure_date"])
    exprs: list[pl.Expr] = []

    for tau in (10, 20):
        psi_e = f"PsiAmpE_{tau}d"
        psi_star = f"PsiAmpStar_{tau}d"
        omega_e = f"OmegaAmpE_{tau}d"
        omega_star = f"OmegaAmpStar_{tau}d"

        prev_psi_e = pl.col(psi_e).shift(1).over("symbol")
        prev_psi_star = pl.col(psi_star).shift(1).over("symbol")
        prev_omega_e = pl.col(omega_e).shift(1).over("symbol")
        prev_omega_star = pl.col(omega_star).shift(1).over("symbol")

        exprs.extend(
            [
                (pl.col(psi_e) - prev_psi_e).alias(f"dPsiAmpE_{tau}d"),
                (pl.col(psi_star) - prev_psi_star).alias(f"dPsiAmpStar_{tau}d"),
                (
                    _sign_expr(psi_e)
                    * (pl.col(psi_e).abs() - prev_psi_e.abs()).clip(lower_bound=0.0)
                    * (pl.col(omega_e) - prev_omega_e).clip(lower_bound=0.0)
                ).alias(f"FreshAmpE_{tau}d"),
                (
                    _sign_expr(psi_star)
                    * (pl.col(psi_star).abs() - prev_psi_star.abs()).clip(lower_bound=0.0)
                    * (pl.col(omega_star) - prev_omega_star).clip(lower_bound=0.0)
                ).alias(f"FreshAmpStar_{tau}d"),
            ]
        )

    return work.with_columns(exprs)


def run_transition_event_study(
    campaign_path: str,
    signal_cols: Iterable[str] | None = None,
    signal_floor: float = 1e-12,
) -> dict[str, object]:
    df = pl.read_parquet(campaign_path)
    derived = derive_transition_columns(df)
    active_signal_cols = list(signal_cols) if signal_cols else list(DEFAULT_SIGNAL_COLS)
    results = [
        compute_event_study_for_signal(derived, signal_col=signal_col, signal_floor=signal_floor)
        for signal_col in active_signal_cols
    ]
    return {
        "campaign_path": str(campaign_path),
        "signal_cols": active_signal_cols,
        "signal_floor": float(signal_floor),
        "results": results,
    }


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run V656 transition event study on an existing V655B campaign-state matrix.")
    ap.add_argument("--campaign-path", required=True, help="Campaign-state parquet path.")
    ap.add_argument(
        "--signal-col",
        action="append",
        default=[],
        help="Optional transition signal column(s) to test. Defaults to the canonical V656 eight-signal set.",
    )
    ap.add_argument("--output-json", default="", help="Optional JSON output path.")
    ap.add_argument("--signal-floor", type=float, default=1e-12, help="Absolute signal floor; rows at or below this are dropped before deciling.")
    return ap.parse_args()


def main() -> None:
    args = _parse_args()
    result = run_transition_event_study(
        campaign_path=args.campaign_path,
        signal_cols=args.signal_col,
        signal_floor=float(args.signal_floor),
    )
    if args.output_json:
        out = Path(args.output_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
