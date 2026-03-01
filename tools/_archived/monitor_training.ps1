# OMEGA Training Monitor v4 (Ultra Robust Mode)
$ErrorActionPreference = "SilentlyContinue"
Clear-Host
Write-Host "Starting Ultra Robust Monitor..." -ForegroundColor Cyan

while($true) {
    $Timestamp = Get-Date -Format "HH:mm:ss"
    
    # 1. CPU - 使用基础 LoadPercentage (所有 Windows 必有)
    $CpuInfo = Get-CimInstance Win32_Processor
    $Cpu = ($CpuInfo | Measure-Object -Property LoadPercentage -Average).Average
    if ($null -eq $Cpu) { $Cpu = "N/A" } else { $Cpu = [Math]::Round($Cpu, 1) }
    
    # 2. RAM - 基础内存查询
    $OS = Get-CimInstance Win32_OperatingSystem
    $TotalMem = [Math]::Round($OS.TotalVisibleMemorySize / (1024*1024), 1)
    $FreeMem = [Math]::Round($OS.FreePhysicalMemory / (1024*1024), 1)
    $UsedMem = [Math]::Round($TotalMem - $FreeMem, 1)
    $MemPct = [Math]::Round(($UsedMem / $TotalMem) * 100, 1)
    
    # 3. Python 进程
    $PyProcs = Get-Process python -ErrorAction SilentlyContinue
    $PyCount = if ($PyProcs) { ($PyProcs | Measure-Object).Count } else { 0 }

    # 4. 获取最新的训练日志 (直接显示在窗口)
    $LogFile = "audit/v40_runtime/windows/train/train.log"
    $LastLog = if (Test-Path $LogFile) { Get-Content $LogFile -Tail 1 } else { "Waiting for logs..." }

    # --- 渲染界面 (使用更显眼的格式) ---
    Clear-Host
    Write-Host "========================================" -ForegroundColor Gray
    Write-Host " OMEGA v40 TRAINING MONITOR (V4)" -ForegroundColor Cyan
    Write-Host " Time: $Timestamp" -ForegroundColor Gray
    Write-Host "========================================" -ForegroundColor Gray
    
    Write-Host " [CPU] Usage:    $Cpu %" -ForegroundColor Cyan
    Write-Host " [RAM] Usage:    $UsedMem GB / $TotalMem GB ($MemPct%)" -ForegroundColor Yellow
    Write-Host " [PY ] Procs:    $PyCount Processes Active" -ForegroundColor White
    
    Write-Host "----------------------------------------" -ForegroundColor Gray
    if ($PyCount -gt 1) {
        Write-Host " STATUS: TRAINING IN PROGRESS" -ForegroundColor Green
    } else {
        Write-Host " STATUS: SCANNING / PREPARING" -ForegroundColor White
    }
    Write-Host "----------------------------------------" -ForegroundColor Gray
    Write-Host " LATEST LOG:" -ForegroundColor Gray
    Write-Host " $LastLog" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Gray
    
    Start-Sleep -Seconds 5
}