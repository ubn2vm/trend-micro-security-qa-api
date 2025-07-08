@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo Trend Micro Security QA API Enhanced Startup Script
echo ===================================================
echo.

REM 設定 Python 路徑
set "PYTHON_EXE=python_config\python.bat"
set "PIP_EXE=python_config\pip.bat"

REM 記錄啟動時間
set "start_time=%time%"
echo Startup Time: %start_time%
echo.

REM 設定重試次數
set "max_retries=3"
set "retry_count=0"

REM 檢查 Python 是否安裝
echo [1/8] Checking Python environment...
%PYTHON_EXE% --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Please check python_config\.python_config file
    echo Current Python path: %PYTHON_EXE%
    pause
    exit /b 1
)
echo [SUCCESS] Python environment check completed

REM 檢查虛擬環境
echo [2/8] Checking virtual environment...
if not exist "aiops\Scripts\activate.bat" (
    echo [WARNING] Virtual environment aiops not found
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
echo [3/8] Activating virtual environment...
call aiops\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment activated

REM 檢查設定檔案
echo [4/8] Checking configuration files...
if not exist "config.env" (
    echo [ERROR] config.env file not found
    echo Please ensure config.env exists with all configuration parameters
    pause
    exit /b 1
) else (
    echo [SUCCESS] Configuration file exists
)

if not exist ".env" (
    echo [WARNING] .env file not found
    echo Creating .env file for API Key...
    echo GOOGLE_API_KEY=your_google_api_key_here > .env
    echo.
    echo Please edit .env file and set your Google API Key
    echo Then run this script again
    echo.
    echo Press any key to open .env file...
    pause
    notepad .env
    exit /b 1
) else (
    echo [SUCCESS] API Key file exists
)

REM 驗證環境變數
echo Validating environment variables...
%PYTHON_EXE% -c "import os; from dotenv import load_dotenv; load_dotenv('config.env'); load_dotenv('.env'); api_key=os.getenv('GOOGLE_API_KEY'); print('API Key Status:', 'Set' if api_key else 'Not Set')" 2>nul
if errorlevel 1 (
    echo [ERROR] Cannot read .env file
    echo Please check .env file format
    pause
    exit /b 1
)

REM 檢查 API Key 格式
%PYTHON_EXE% -c "import os; from dotenv import load_dotenv; load_dotenv('config.env'); load_dotenv('.env'); api_key=os.getenv('GOOGLE_API_KEY'); exit(0 if api_key and len(api_key) >= 20 and api_key.startswith('AI') else 1)" 2>nul
if errorlevel 1 (
    echo [WARNING] Google API Key format may be incorrect
    echo Please ensure API Key starts with 'AI' and is at least 20 characters
    echo.
    echo Press any key to continue or Ctrl+C to cancel...
    pause
)

echo [SUCCESS] Environment variables validated

REM 安裝依賴套件
echo [5/8] Checking and installing dependencies...
%PIP_EXE% install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo Please check network connection or requirements.txt file
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed

REM 檢查知識庫檔案
echo [6/8] Checking knowledge base files...
set "KNOWLEDGE_FILE=%KNOWLEDGE_FILE%"
if "%KNOWLEDGE_FILE%"=="" set "KNOWLEDGE_FILE=summary.txt"

if not exist "%KNOWLEDGE_FILE%" (
    echo [WARNING] %KNOWLEDGE_FILE% file not found
    if exist "knowledgebase.txt" (
        echo Using knowledgebase.txt as knowledge base
        copy knowledgebase.txt %KNOWLEDGE_FILE%
        echo [SUCCESS] Knowledge base file copied
    ) else (
        echo [ERROR] Knowledge base file not found
        echo Please ensure knowledgebase.txt or %KNOWLEDGE_FILE% exists
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] Knowledge base file check completed: %KNOWLEDGE_FILE%
)

REM 檢查端口是否被佔用
echo [7/8] Checking if port 8000 is available...
netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 8000 is already in use
    echo Please close other programs using this port or modify API_PORT in .env
    echo.
    echo Press any key to continue or Ctrl+C to cancel...
    pause
) else (
    echo [SUCCESS] Port 8000 is available
)

REM 啟動 API 服務
echo [8/8] Starting API service...
echo.
echo ===========================================
echo Starting Trend Micro Security QA API
echo ===========================================
echo.
echo [DOCS] API Documentation: http://localhost:8000/docs
echo [HEALTH] Health Check: http://localhost:8000/health
echo [EXAMPLES] Example Questions: http://localhost:8000/examples
echo [ROOT] Root Path: http://localhost:8000/
echo.
echo Startup Time: %start_time%
echo Press Ctrl+C to stop service
echo.

REM 啟動服務並處理錯誤
:start_service
set /a retry_count+=1
echo [RETRY] Attempting to start service (Attempt !retry_count!)...

%PYTHON_EXE% -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
if errorlevel 1 (
    echo.
    echo [ERROR] API service startup failed (Attempt !retry_count!)
    
    if !retry_count! lss !max_retries! (
        echo.
        echo [RETRY] Waiting 5 seconds before retry...
        timeout /t 5 /nobreak >nul
        echo.
        goto start_service
    ) else (
        echo.
        echo [ERROR] Maximum retry attempts reached (!max_retries!)
        echo Please check error messages and fix issues
        echo.
        echo Common troubleshooting steps:
        echo 1. Check if API Key in .env file is correct
        echo 2. Ensure knowledge base file exists and format is correct
        echo 3. Check network connection is normal
        echo 4. Ensure no other programs are using port 8000
        echo.
        pause
        exit /b 1
    )
) else (
    echo.
    echo [SUCCESS] API service started successfully!
    echo [INFO] Service running time: Started at %start_time%
)

pause 