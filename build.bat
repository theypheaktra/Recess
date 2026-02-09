@echo off
title RECESS IMS - Build Installer

echo.
echo   ==========================================
echo      RECESS IMS v3.0 - Windows Build
echo   ==========================================
echo.

:: Check Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ERROR] Node.js is NOT installed.
    echo   https://nodejs.org
    pause
    exit /b 1
)

:: Install dependencies
if not exist "node_modules\electron-builder" (
    echo   [SETUP] Installing build tools...
    call npm install
)

echo.
echo   Select build option:
echo.
echo     1. Installer (.exe Setup) - creates desktop shortcut
echo     2. Portable (.exe) - no install needed, run directly
echo     3. Both
echo     4. Cancel
echo.

set /p choice="   Choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo   [BUILD] Creating installer... 5-10 min
    call npm run build:win
) else if "%choice%"=="2" (
    echo.
    echo   [BUILD] Creating portable... 5-10 min
    call npm run build:portable
) else if "%choice%"=="3" (
    echo.
    echo   [BUILD] Creating both... 10-15 min
    call npm run build:win
    call npm run build:portable
) else (
    echo   Cancelled.
    pause
    exit /b 0
)

if %errorlevel% equ 0 (
    echo.
    echo   ==========================================
    echo      Build Complete!
    echo   ==========================================
    echo.
    echo   Output: dist\
    echo.
    explorer dist
) else (
    echo.
    echo   [ERROR] Build failed. Check the log above.
)

echo.
pause
