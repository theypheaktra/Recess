@echo off
title RECESS IMS v3.0

echo.
echo   ==========================================
echo      RECESS IMS v3.0 Desktop Application
echo      1CUT = 1NFT = 1BLOCK
echo   ==========================================
echo.

:: Step 1: Check Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ERROR] Node.js is NOT installed.
    echo.
    echo   Please install Node.js first:
    echo   https://nodejs.org
    echo.
    echo   Download LTS version and install, then run this file again.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('node --version') do echo   [OK] Node.js %%v

:: Step 2: Install Electron (first run only)
if not exist "node_modules\electron" (
    echo.
    echo   [SETUP] Installing Electron... first run only, 2-5 min
    echo   Internet connection required.
    echo.
    call npm install --loglevel=error
    if %errorlevel% neq 0 (
        echo.
        echo   [ERROR] Install failed. Check your internet connection.
        pause
        exit /b 1
    )
    echo.
    echo   [OK] Installation complete!
)

:: Step 3: Launch App
echo.
echo   [START] Launching RECESS IMS...
echo.

:: Create cache directory (fixes permission errors)
if not exist "%~dp0cache" mkdir "%~dp0cache"

call npx electron . --disk-cache-dir="%~dp0cache" --gpu-disk-cache-dir="%~dp0cache\gpu"

echo.
echo   RECESS IMS closed.
timeout /t 2 >nul
