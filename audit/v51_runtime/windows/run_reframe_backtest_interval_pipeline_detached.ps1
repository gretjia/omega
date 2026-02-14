param(
    [string]$Root = "C:\Omega_vNext",
    [string]$OutputDir = "D:\Omega_frames\v50\output",
    [string]$StageDir = "D:\Omega_frames\v50\stage",
    [string]$ProfilePath = "configs/hardware/active_profile.yaml",
    [switch]$NoResume = $false
)

$ErrorActionPreference = "Continue"

$runtimeRoot = Join-Path $Root "audit\v51_runtime\windows\frame_pipeline"
$logPath = Join-Path $runtimeRoot "reframe_backtest_interval_pipeline.log"
$exitPath = Join-Path $runtimeRoot "reframe_backtest_interval_pipeline_exit_code.txt"
$markerPath = Join-Path $runtimeRoot "pipeline_reset_done.marker"
$pyScriptPath = Join-Path $runtimeRoot "run_pipeline_interval.py"
$py = "C:\Python314\python.exe"

New-Item -ItemType Directory -Force -Path $runtimeRoot | Out-Null

foreach ($f in @($logPath, $exitPath)) {
    if (Test-Path -LiteralPath $f) {
        Remove-Item -LiteralPath $f -Force -ErrorAction SilentlyContinue
    }
}

function Write-Log {
    param([string]$Text)
    $line = ("[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Text)
    $line | Tee-Object -FilePath $logPath -Append | Out-Null
}

function Stop-OldTasks {
    foreach ($tn in @("\OmegaV51ReframeBacktest", "\OmegaV51ReframeMonitor")) {
        try {
            cmd /c "schtasks /End /TN $tn" | Out-Null
            Write-Log ("End task requested: {0}" -f $tn)
        } catch {
            Write-Log ("End task skipped: {0}" -f $tn)
        }
    }
}

function Clear-IntervalOutputOnce {
    param([string]$Dir)
    if (Test-Path -LiteralPath $markerPath) {
        Write-Log ("Reset marker exists, keep existing outputs for resume: {0}" -f $markerPath)
        return
    }

    if (-not (Test-Path -LiteralPath $Dir)) {
        New-Item -ItemType Directory -Force -Path $Dir | Out-Null
    }

    # Clean only backtest interval files:
    # - daily files: 2025YYYY.parquet, 202601DD.parquet
    # - symbol files from previous driver: 2025*_*.parquet, 202601*_*.parquet
    $targets = @(
        "2025*.parquet",
        "202601*.parquet"
    )

    $removed = 0
    foreach ($pat in $targets) {
        $files = Get-ChildItem -LiteralPath $Dir -Filter $pat -ErrorAction SilentlyContinue
        foreach ($f in $files) {
            try {
                Remove-Item -LiteralPath $f.FullName -Force -ErrorAction Stop
                $removed += 1
            } catch {}
        }
    }
    Write-Log ("Initial cleanup removed interval parquet files: {0}" -f $removed)
    Set-Content -LiteralPath $markerPath -Value ("reset_done_at={0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss")) -Encoding UTF8
}

function Write-PythonRunner {
    @'
import os
import sys

sys.path.append(os.getcwd())

from pipeline.config.loader import ConfigLoader
from pipeline.adapters.v3_adapter import OmegaCoreAdapter
from pipeline.engine.framer import Framer
from config import load_l2_pipeline_config

def main():
    root = os.environ.get("OMEGA_ROOT", "C:/Omega_vNext")
    profile_path = os.environ.get("OMEGA_PROFILE", "configs/hardware/active_profile.yaml")
    output_dir = os.environ.get("OMEGA_OUTPUT", "D:/Omega_frames/v50/output")
    stage_dir = os.environ.get("OMEGA_STAGE", "D:/Omega_frames/v50/stage")

    os.chdir(root)
    profile = ConfigLoader.load_hardware_profile(profile_path)
    profile.storage.output_root = output_dir
    profile.storage.stage_root = stage_dir

    cfg = load_l2_pipeline_config()
    core = OmegaCoreAdapter()
    core.initialize({"pipeline_cfg": cfg})

    def logger(msg: str):
        print(msg, flush=True)

    fr = Framer(profile, core, logger=logger)
    # Backtest interval only: 2025 + 202601.
    fr.run(year_filter="2025", limit=0)
    fr.run(year_filter="202601", limit=0)

if __name__ == "__main__":
    main()
'@ | Set-Content -LiteralPath $pyScriptPath -Encoding UTF8
}

Set-Location $Root
Write-Log "START switch-to-pipeline reframe (backtest interval)"
Write-Log ("Root={0}" -f $Root)
Write-Log ("OutputDir={0}" -f $OutputDir)
Write-Log ("StageDir={0}" -f $StageDir)
Write-Log ("ProfilePath={0}" -f $ProfilePath)
Write-Log ("NoResume={0}" -f $NoResume)

try {
    Stop-OldTasks

    if (-not $NoResume) {
        Clear-IntervalOutputOnce -Dir $OutputDir
    } else {
        Write-Log "NoResume=true, skip initial cleanup by request."
    }

    Write-PythonRunner

    $env:OMEGA_ROOT = $Root
    $env:OMEGA_PROFILE = $ProfilePath
    $env:OMEGA_OUTPUT = $OutputDir
    $env:OMEGA_STAGE = $StageDir

    Write-Log ("RUN CMD={0} {1}" -f $py, $pyScriptPath)
    & $py $pyScriptPath 2>&1 | Tee-Object -FilePath $logPath -Append
    $code = $LASTEXITCODE

    Write-Log ("END switch-to-pipeline reframe EXIT={0}" -f $code)
    Set-Content -LiteralPath $exitPath -Value "$code" -Encoding UTF8
    exit $code
}
catch {
    $_ | Out-String | Tee-Object -FilePath $logPath -Append | Out-Null
    Write-Log "END switch-to-pipeline reframe EXIT=1"
    Set-Content -LiteralPath $exitPath -Value "1" -Encoding UTF8
    exit 1
}

