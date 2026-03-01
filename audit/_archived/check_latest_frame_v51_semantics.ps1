param(
    [string]$OutputDir = "D:\Omega_frames\v50\output"
)

$ErrorActionPreference = "Stop"

$latest = Get-ChildItem -LiteralPath $OutputDir -Filter "2025*.parquet" -ErrorAction Stop |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if ($null -eq $latest) {
    Write-Output "NO_2025_PARQUET_FOUND"
    exit 2
}

Write-Output ("LATEST_FILE={0}" -f $latest.FullName)
Write-Output ("LATEST_WRITE_TIME={0}" -f $latest.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss"))

$py = "C:\Python314\python.exe"
$code = @'
import polars as pl
import numpy as np
import sys

p = sys.argv[1]
df = pl.read_parquet(p)
required = ["epiplexity", "srl_resid", "direction", "is_signal", "adaptive_y", "topo_area", "topo_energy"]
missing = [c for c in required if c not in df.columns]
print("missing_columns=" + str(missing))
df = df.select(["direction", "srl_resid"]).drop_nulls()
if df.height == 0:
    print("rows=0 checked=0 mismatch=0")
    sys.exit(0)

d = np.sign(df["direction"].to_numpy())
r = np.sign(df["srl_resid"].to_numpy())
mask = (d != 0.0) & (r != 0.0)
mismatch = int(np.sum(d[mask] != (-r[mask])))
checked = int(np.sum(mask))
print(f"rows={int(df.height)} checked={checked} mismatch={mismatch}")
'@
$tmpPy = Join-Path $env:TEMP "omega_v51_semantics_check.py"
Set-Content -LiteralPath $tmpPy -Value $code -Encoding UTF8
& $py $tmpPy $latest.FullName
