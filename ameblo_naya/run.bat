@echo off
setlocal

REM One-click entry for ameblo_naya crawler
set "TARGET_DIR=%~dp0"

echo [INFO] Working dir: %TARGET_DIR%

if not exist "%TARGET_DIR%\crawl_url.py" (
    echo [ERROR] Missing file: "%TARGET_DIR%\crawl_url.py"
    pause
    exit /b 1
)

if not exist "%TARGET_DIR%\crawl_image.py" (
    echo [ERROR] Missing file: "%TARGET_DIR%\crawl_image.py"
    pause
    exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found in PATH.
    echo [HINT] Install Python or add it to PATH.
    pause
    exit /b 1
)

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMddHHmmss"') do set "CRAWL_RUN_TS=%%i"
echo [INFO] Run timestamp: %CRAWL_RUN_TS%

pushd "%TARGET_DIR%"

echo.
echo [STEP 1/2] Crawling entry URLs...
python "crawl_url.py"
if errorlevel 1 (
    echo [ERROR] crawl_url.py failed.
    popd
    pause
    exit /b 1
)

echo.
echo [STEP 2/2] Crawling entry images...
python "crawl_image.py"
if errorlevel 1 (
    echo [ERROR] crawl_image.py failed.
    popd
    pause
    exit /b 1
)

popd
echo.
echo [DONE] All tasks finished.
pause
exit /b 0
