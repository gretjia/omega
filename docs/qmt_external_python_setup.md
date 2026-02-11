# QMT External Python Setup Guide

This guide explains how to run QMT (xtquant) scripts using an external Python environment instead of the built-in strategy editor.

## Prerequisites

- **QMT Research Terminal (投研端)** installed
- QMT must be **running and logged in** before executing scripts

## Installation Paths

| Component | Path |
|-----------|------|
| Python Interpreter | `D:\迅投极速交易终端睿智融科版\bin.x64\python.exe` |
| xtquant Library | `D:\迅投极速交易终端睿智融科版\bin.x64\因子版\Lib\site-packages` |
| Python Version | 3.6.8 |

## Method 1: PowerShell Command Line

```powershell
# Set PYTHONPATH and run script
$env:PYTHONPATH = "D:\迅投极速交易终端睿智融科版\bin.x64\因子版\Lib\site-packages"
& "D:\迅投极速交易终端睿智融科版\bin.x64\python.exe" "D:\OMEGA\versions\v1300\qmt_download_l2_ticks.py"
```

## Method 2: VS Code Configuration

### Step 1: Set Python Interpreter

1. Open Command Palette (`Ctrl+Shift+P`)
2. Select `Python: Select Interpreter`
3. Choose `Enter interpreter path...`
4. Enter: `D:\迅投极速交易终端睿智融科版\bin.x64\python.exe`

### Step 2: Configure Environment Variables

Create `.vscode/settings.json` in your project:

```json
{
  "python.defaultInterpreterPath": "D:\\迅投极速交易终端睿智融科版\\bin.x64\\python.exe",
  "python.envFile": "${workspaceFolder}/.env",
  "terminal.integrated.env.windows": {
    "PYTHONPATH": "D:\\迅投极速交易终端睿智融科版\\bin.x64\\因子版\\Lib\\site-packages"
  }
}
```

Create `.env` file in project root:

```
PYTHONPATH=D:\迅投极速交易终端睿智融科版\bin.x64\因子版\Lib\site-packages
```

## Method 3: PyCharm Configuration

1. Go to `File → Settings → Project → Python Interpreter`
2. Click gear icon → `Add...`
3. Select `System Interpreter`
4. Browse to: `D:\迅投极速交易终端睿智融科版\bin.x64\python.exe`
5. Add path to interpreter:
   - Click `Show All...` on interpreter list
   - Select interpreter → Click folder icon
   - Add: `D:\迅投极速交易终端睿智融科版\bin.x64\因子版\Lib\site-packages`

## Important Notes

1. **Start QMT First**: The MiniQMT service must be running before executing any xtquant scripts
2. **Login Required**: You must be logged into QMT with valid credentials
3. **L2 Data Permission**: Level-2 data requires appropriate permissions enabled on your account

## Common Error: Cannot Connect to xtquant Service

```
Exception: 无法连接xtquant服务，请检查QMT-投研版或QMT-极简版是否开启
```

**Solution**: 
- Ensure QMT Research Terminal is open and logged in
- Check for MiniQMT icon in system tray
- Wait a few seconds after login before running scripts

## Available xtquant Modules

```python
from xtquant import xtdata      # Market data module
from xtquant import xttrader    # Trading module (if available)
```

## Quick Test

Run this to verify setup:

```python
from xtquant import xtdata
print("xtquant connected successfully!")
print("Data dir:", xtdata.data_dir)
```

## Related Files

- `qmt_download_l2_ticks.py` - L2 tick data download script
- `qmt_tick_download.md` - Download API documentation
- `qmt_manual.md` - Backtesting documentation
- `qmt_GUI_manual.md` - Full example with backtest engine
