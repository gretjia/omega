# v34 Epiplexity Race Summary (2026-02-08)

## Experiment Setup
- Mode: non-full training, algorithm derby (`epiplexity_zlib`, `epiplexity_lz76`, `epiplexity_perm`)
- Execution host: Mac Studio M4 Max, 32GB
- Constraint handling: switched to file-list mode to avoid shared-directory `opendir/stat` blocking
- Manifest: `audit/v34_epi_manifest_round1.txt` (280 real parquet file paths)

## Round 1
- Report: `audit/v34_epi_race_round1_final_report.json`
- Rows trained: 293
- Winner: `epiplexity_lz76`
- |w(zlib)| = 0.232354
- |w(lz76)| = 7.186527
- |w(perm)| = 2.926741
- LZ76 vs zlib = 30.93x

## Round 2 (expanded)
- Report: `audit/v34_epi_race_round2_final_report.json`
- Rows trained: 3262
- Winner: `epiplexity_lz76`
- |w(zlib)| = 1.233399
- |w(lz76)| = 4.108227
- |w(perm)| = 0.057447
- LZ76 vs zlib = 3.33x
- LZ76 vs perm = 71.51x

## Decision Signal
1. Winner is stable across two rounds: `epiplexity_lz76`.
2. In expanded round, `|w_lz76|` is significantly larger than `|w_zlib|` and `|w_perm|`.
3. Current evidence supports promoting LZ76 as the primary Epiplexity compression path for the next full training cycle.

## Logging Artifacts
- `audit/v34_epi_race_round1_final.log`
- `audit/v34_epi_race_round2_final.log`
- `audit/v34_epi_race_round1_final_report.json`
- `audit/v34_epi_race_round2_final_report.json`
