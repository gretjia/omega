---
name: omega_data
description: Understanding the OMEGA data structure and file formats
---

# OMEGA Data Structure

The OMEGA project stores market data in `./data/`.

## Directory Layout

### `history_ticks` (Aggregated Tick Data)
- **Path**: `data/history_ticks/`
- **Format**: `{stock_code}.csv` (e.g., `000032.csv`)
- **Description**: Contains aggregated tick data for a stock across multiple days. Primary source for backtesting.
- **Schema**:
  - `time` (int64): Timestamp in milliseconds
  - `price` (float): Last price
  - `open`, `high`, `low` (float): OHLC data
  - `vol` (float): Volume
  - `amount` (float): Turnover

### `history_ticks_full` (Daily Tick Data)
- **Path**: `data/history_ticks_full/`
- **Format**: `{stock_code}_{date}.csv` (e.g., `000004_20250813.csv`)
- **Description**: Raw tick data for a single stock on a single day. Used for Maxwell model training.

### `level2` (L2 High-Frequency Archives)
- **Path**: `data/level2/`
- **Format**: `.7z` compressed archives by date
- **Description**: Level-2 tick-by-tick data. Very large (~2TB total). Do NOT decompress fully.

### `level2_frames_*` (L2 Training Output)
- **Path**: `data/level2_frames_win2023/`, `data/level2_frames_mac2024/`
- **Format**: `.parquet`
- **Description**: Processed L2 frames from parallel training. Rebuildable.

### `binary_ticks` (High-Speed Cache)
- **Path**: `data/binary_ticks/`
- **Format**: `.npy` (memory-mapped)
- **Description**: High-speed cache converted from `history_ticks`. Rebuildable via `tools/bake_ticks.py`.

## Usage Guidelines
- For long-term analysis/training: use `history_ticks` or `level2_frames_*`
- For debugging specific dates: check `history_ticks_full`
- For L2 data: use streaming tools (`tools/level2_7z_reader.py`)
- See `data/README.md` for cleanup policies
