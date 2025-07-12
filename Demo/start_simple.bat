@echo off
chcp 65001 >nul
echo ===========================================
echo Trend Micro Security QA API - Simple Start
echo ===========================================
echo.

REM 檢查 Python
echo ===========================================
echo [Python Environment Check]
echo ===========================================
echo   - Checking system Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [SUCCESS] Using system Python

echo.
echo ===========================================
echo [Virtual Environment Setup]
echo ===========================================
echo   - Checking virtual environment...
if not exist "..\aiops\Scripts\activate.bat" (
    echo   - Creating virtual environment...
    python -m venv ..\aiops
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo   - Virtual environment created
) else (
    echo   - Virtual environment exists
)
echo   - Activating virtual environment...
call ..\aiops\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment ready

echo.
echo ===========================================
echo [Dependency Installation]
echo ===========================================
echo   - Installing required packages...
pip install -r ..\core_app\requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed

echo.
echo ===========================================
echo [Environment Setup]
echo ===========================================
echo   - Checking configuration files...
if not exist "..\config\config.env" (
    echo [ERROR] config.env file not found
    pause
    exit /b 1
) else (
    echo   - Configuration file exists
)

REM 簡化的 .env 檢查
if not exist "..\.env" (
    echo [INFO] .env file not found, creating from template...
    if exist "..\config\env.example" (
        copy ..\config\env.example ..\.env >nul
        echo [SUCCESS] .env file created
        echo.
        echo [IMPORTANT] 請貼上您的 Google API Key：
        set /p USER_API_KEY=請貼上 GOOGLE_API_KEY 並按 Enter：
        echo GOOGLE_API_KEY=%USER_API_KEY%>>..\.env
        echo.
        echo [INFO] 已將 API Key 寫入 .env 檔案
        echo [INFO] 若要修改，請直接編輯 .env 檔案
        pause
    ) else (
        echo [ERROR] config\env.example file not found
        pause
        exit /b 1
    )
) else (
    echo   - API Key file exists
)

REM 簡化的 API Key 驗證
echo   - Validating API Key...
call ..\aiops\Scripts\activate.bat
python -c "import os; from dotenv import load_dotenv; load_dotenv('..\\config\\config.env'); load_dotenv('..\\.env'); api_key=os.getenv('GOOGLE_API_KEY'); exit(0 if api_key and len(api_key) >= 20 and api_key.startswith('AI') else 1)" 2>nul
if errorlevel 1 (
    echo [ERROR] Invalid or missing Google API Key
    echo 請重新貼上您的 Google API Key：
    set /p USER_API_KEY=請貼上 GOOGLE_API_KEY 並按 Enter：
    (for /f "delims=" %%i in ('findstr /v "^GOOGLE_API_KEY=" ..\.env') do @echo %%i)>..\.env.tmp
    move /y ..\.env.tmp ..\.env >nul
    echo GOOGLE_API_KEY=%USER_API_KEY%>>..\.env
    echo [INFO] 已更新 .env 檔案
    echo [INFO] 重新驗證 API Key...
    python -c "import os; from dotenv import load_dotenv; load_dotenv('..\\config\\config.env'); load_dotenv('..\\.env'); api_key=os.getenv('GOOGLE_API_KEY'); exit(0 if api_key and len(api_key) >= 20 and api_key.startswith('AI') else 1)" 2>nul
    if errorlevel 1 (
        echo [ERROR] API Key validation failed
        echo 請確認您貼上的 Google API Key 正確無誤
        pause
        exit /b 1
    )
)
echo   - API Key validation passed

echo   - Checking RAG knowledge base...
if not exist "..\core_app\rag\vector_store\crem_faiss_index" (
    echo [ERROR] RAG vector database not found
    echo Please ensure the RAG vector database exists
    pause
    exit /b 1
) else (
    echo   - RAG vector database exists
)

echo   - Checking port availability...
netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 8000 is already in use
    echo Press any key to continue anyway...
    pause
) else (
    echo   - Port 8000 is available
)
echo [SUCCESS] Environment and configuration validated

REM 啟動 API
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
echo Press Ctrl+C to stop the server
echo.

REM 啟動 API
call ..\aiops\Scripts\activate.bat
cd ..
python -m core_app.app
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start API server
    echo Please check error messages above
    pause
    exit /b 1
)

pause 