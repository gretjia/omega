# Level-2 逐日 .7z 分批解压（安全版）

目标：在 D 盘空间不足以一次性解压全部 `./data/level2` 的情况下，按批次（按天）逐个解压 `.7z`，严格校验解压结果后再处理原始压缩包，并将最终 CSV 落盘到 `./data/leve2_csv`。

脚本：`tools/level2_batch_extract.py`

## 1) 先做实验（不删除压缩包）

查看某天解压后大概有多大：

```powershell
python tools/level2_batch_extract.py --batch-count 1 --limit-archives 1 --dry-run
```

做一次完整“解压->校验CRC->复制到 ./data/leve2_csv”，但不删除压缩包：

```powershell
python tools/level2_batch_extract.py --batch-count 1 --limit-archives 1 --verify-crc --strict-size --archive-disposition keep
```

## 2) 正式跑：推荐“隔离备份”（quarantine）

把压缩包从 `./data/level2` 移到 `C:\Omega_level2_quarantine`（释放 D 盘空间且保留可恢复备份），再把 CSV 落盘到 `./data/leve2_csv`：

```powershell
python tools/level2_batch_extract.py --batch-count 2 --verify-crc --strict-size --archive-disposition quarantine
```

后续你确认无误后，可以再手动清理 `C:\Omega_level2_quarantine`。

## 3) 正式跑：严格删除（delete）

只有在通过校验后才会删除原始 `.7z`，并且需要显式确认 token：

```powershell
python tools/level2_batch_extract.py --batch-count 2 --verify-crc --strict-size --archive-disposition delete --confirm-delete-token DELETE_AFTER_VERIFY
```

## 4) 断点续做 / 状态文件

默认在 `./data/leve2_csv/_batch_extract_state.jsonl` 记录每个 `.7z` 的处理状态（追加写，断点后可继续）。

## 5) 常用参数

- `--src-root`：默认 `./data/level2`
- `--dest-root`：默认 `./data/leve2_csv`
- `--stage-root`：默认 `C:\Omega_level2_stage`（中转盘）
- `--batch-count`：一次处理多少个 `.7z`（仍是逐个执行，失败会停止）
- `--min-free-c-gb / --min-free-d-gb`：安全余量阈值（默认 30GB）

