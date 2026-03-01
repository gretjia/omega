from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import CSVParseConfig, KernelConfig
from feature_extractor import extract_features_from_window, volume_clock_aggregate_with_time
from tools.level2_7z_reader import SevenZipConfig, read_level2_quote_as_tickdata_from_7z


def main() -> int:
    archive = Path("d:/Omega_vNext/data/level2/2023/202301/20230103.7z")
    inner = "20230103/000001.SZ/行情.csv"

    tick = read_level2_quote_as_tickdata_from_7z(
        SevenZipConfig(),
        archive_path=archive,
        inner_path=inner,
        csv_cfg=CSVParseConfig(volume_mode="delta", simplified_time_is_epoch=True),
        max_rows=None,
    )

    price0 = int(np.sum(np.asarray(tick.price) <= 0))
    vol0 = int(np.sum(np.asarray(tick.volume) <= 0))
    print("rows", int(tick.price.size))
    print("price<=0", price0, f"{price0 / max(int(tick.price.size), 1) * 100:.3f}%")
    print("vol<=0", vol0, f"{vol0 / max(int(tick.volume.size), 1) * 100:.3f}%")

    kcfg = KernelConfig()
    bars = volume_clock_aggregate_with_time(
        times=tick.time,
        prices=tick.price,
        volumes=tick.volume,
        volume_per_bar=kcfg.volume_clock.volume_per_bar,
        min_ticks_per_bar=kcfg.volume_clock.min_ticks_per_bar,
        max_bars=kcfg.volume_clock.max_bars,
    )
    print("bars", int(np.asarray(bars.price).size))

    lookback = 128
    if int(np.asarray(bars.price).size) > lookback + 20:
        win_p = np.asarray(bars.price, dtype=float)[0:lookback]
        win_v = np.asarray(bars.volume, dtype=float)[0:lookback]
        pack = extract_features_from_window(win_p, win_v, kcfg)
        print("feature_dim", int(pack.values.size))
        print("feature_names_first5", pack.names[:5])
    else:
        print("not enough bars for feature probe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
