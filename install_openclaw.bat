@echo off
setlocal

REM Add local MinGit to PATH
set "MINGIT_CMD=%~dp0tools\MinGit\cmd"
echo [DEBUG] Checking MinGit path: "%MINGIT_CMD%"
if exist "%MINGIT_CMD%\" (
    echo [INFO] Adding MinGit to PATH: %MINGIT_CMD%
    set "PATH=%MINGIT_CMD%;%PATH%"
) else (
    echo [WARN] MinGit directory not found.
)

REM Debug git availability
git --version
echo ==========================================
echo      OpenClaw Node Installation Script
echo ==========================================

REM Check for Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in PATH.
    echo OpenClaw requires Git to install dependencies.
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo After installing, please restart this script.
    echo.
    pause
    exit /b 1
)

echo [INFO] Git found. Proceeding with installation...

REM Install OpenClaw globally
echo [INFO] Running: npm install -g openclaw@latest
call npm install -g openclaw@latest
if %errorlevel% neq 0 (
    echo [ERROR] Installation failed. Please check the logs above.
    pause
    exit /b 1
)

echo [INFO] OpenClaw installed successfully.

REM Configure OpenClaw
echo [INFO] Configuring OpenClaw Node...
set "USER_HOME=%USERPROFILE%"
set "CONFIG_DIR=%USER_HOME%\.openclaw"
set "CONFIG_FILE=%CONFIG_DIR%\openclaw.json"

if not exist "%CONFIG_DIR%" (
    echo [INFO] Creating config directory: %CONFIG_DIR%
    mkdir "%CONFIG_DIR%"
)

echo [INFO] Copying configuration file...
copy /Y "openclaw_config.json" "%CONFIG_FILE%"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to copy configuration file.
    echo Please manually copy openclaw_config.json to %CONFIG_DIR%\openclaw.json
) else (
    echo [SUCCESS] Configuration updated.
)

REM Verify Connection
echo [INFO] Running Doctor to fix local state...
call openclaw doctor --fix

echo [INFO] Verifying connection to Remote Gateway (43.139.33.186)...
call openclaw gateway health

echo.
echo ==========================================
echo      Installation ^& Setup Complete!
echo ==========================================
echo.
echo [IMPORTANT] If you see "pairing required" error:
echo 1. Run 'run_node.bat' to start the node and trigger a pairing request.
echo 2. Go to your OpenClaw Gateway Dashboard to approve the request.
echo.
echo You can now use 'openclaw' commands in your terminal.
pause
