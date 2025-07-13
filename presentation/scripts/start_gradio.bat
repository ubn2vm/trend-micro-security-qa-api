@echo off
cd /d "%~dp0\..\.."
chcp 65001 >nul
echo ===========================================
echo Trend Micro Security QA - Gradio Interface
echo ===========================================
echo.

REM 檢查虛擬環境
echo ===========================================
echo [Environment Check]
echo ===========================================
if not exist "aiops\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found
    echo Please run start_simple.bat first to setup the environment
    pause
    exit /b 1
)

echo   - Activating virtual environment...
call aiops\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment activated

echo.
echo ===========================================
echo [Dependency Check]
echo ===========================================
echo   - Checking Gradio installation...
python -c "import gradio; print('Gradio version:', gradio.__version__)" 2>nul
if errorlevel 1 (
    echo [WARNING] Gradio not found, installing...
    pip install gradio
    if errorlevel 1 (
        echo [ERROR] Failed to install Gradio
        pause
        exit /b 1
    )
    echo [SUCCESS] Gradio installed
) else (
    echo [SUCCESS] Gradio is available
)

echo.
echo ===========================================
echo [API Service Check]
echo ===========================================
echo   - Checking if API service is running...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [ERROR] API service is not running on port 8000
    echo.
    echo [REQUIRED] Please start the API service first:
    echo   1. Open a new command window
    echo   2. Navigate to: C:\MyVS\AIOps\presentation\scripts
    echo   3. Run: start_simple.bat
    echo   4. Wait for API service to start
    echo   5. Then return here and run this script again
    echo.
    echo [MANUAL API START]
    echo Or manually start API service:
    echo   cd C:\MyVS\AIOps
    echo   call aiops\Scripts\activate.bat
    echo   python -m core_app.app
    echo.
    pause
    exit /b 1
) else (
    echo [SUCCESS] API service is running
)

echo.
echo ===========================================
echo [Starting Gradio Interface]
echo ===========================================
echo.
echo [INFO] Gradio will be available at: http://127.0.0.1:7860
echo [INFO] API service is running at: http://localhost:8000
echo.
echo [IMPORTANT] Keep this window open while using Gradio
echo [INFO] Press Ctrl+C to stop Gradio
echo.

REM 啟動 Gradio
python core_app/gradio_app.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start Gradio
    echo.
    echo [TROUBLESHOOTING]
    echo 1. Ensure API service is running on port 8000
    echo 2. Check if port 7860 is available
    echo 3. Verify all dependencies are installed
    echo 4. Check Python environment
    echo.
    echo [MANUAL START]
    echo If automatic start fails, try:
    echo   cd C:\MyVS\AIOps
    echo   call aiops\Scripts\activate.bat
    echo   python core_app/gradio_app.py
    pause
    exit /b 1
)

pause 