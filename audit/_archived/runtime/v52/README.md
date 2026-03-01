# v52 Runtime Metadata

This folder stores small, version-controlled metadata needed to make distributed runs reproducible.

## Files

- `run_meta.template.json`: Copy per run (per node) and fill in:
  - `git_commit` and/or `git_tag` (the exact code version pinned for the run)
  - `config_hash` (hash of `config.py` plus the active hardware profile YAML)
  - `node`/`shard` (which worker ran which slice)

## Policy

- Keep this repo **code only**. Do not commit raw data (`.7z`), frames (`.parquet`), or model artifacts (`.pkl`).

