@echo off
chcp 65001 >nul
echo Trend Micro Security QA API Project Validation
echo ==============================================
echo.

REM 設定 Python 路徑
set "PYTHON_EXE=python_config\python.bat"
set "PIP_EXE=python_config\pip.bat"

echo [INFO] Using Python: %PYTHON_EXE%
echo [INFO] Using pip: %PIP_EXE%
echo.

REM 檢查 Python 是否可用
echo [1/6] Checking Python availability...
%PYTHON_EXE% --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not available
    echo Please check python_config\.python_config file
    pause
    exit /b 1
)
echo [SUCCESS] Python is available

REM 檢查虛擬環境
echo [2/6] Checking virtual environment...
if not exist "aiops\Scripts\activate.bat" (
    echo [WARNING] Virtual environment not found
    echo Creating virtual environment...
    %PYTHON_EXE% -m venv aiops
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
) else (
    echo [SUCCESS] Virtual environment exists
)

REM 啟動虛擬環境
echo [3/6] Activating virtual environment...
call aiops\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment activated

REM 檢查依賴套件
echo [4/6] Checking dependencies...
%PIP_EXE% install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed

REM 檢查 API 服務
echo [5/6] Checking API service...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] API service is not running
    echo Please start the API service first:
    echo   start.bat
    echo   or
    echo   start_api_enhanced.bat
    echo.
    echo Press any key to continue validation...
    pause
) else (
    echo [SUCCESS] API service is running
)

REM 執行 Python 驗證腳本
echo [6/6] Running comprehensive validation...
%PYTHON_EXE% validate_project.py
if errorlevel 1 (
    echo [ERROR] Validation failed
    pause
    exit /b 1
)

echo.
echo ==============================================
echo [SUCCESS] Project validation completed!
echo ==============================================
echo.
echo Check validation_results.json for detailed results
pause 