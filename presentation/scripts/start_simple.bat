@echo off
cd /d "%~dp0\..\.."
chcp 65001 >nul
echo ===========================================
echo Trend Micro Security QA API - Simple Start
echo ===========================================
echo.

REM 自動偵測 Python 指令
echo ===========================================
echo [Python Environment Detection]
echo ===========================================
echo   - Detecting Python installation...

REM 設定預設的 Python 指令
set "PYTHON_CMD="
set "PIP_CMD="

REM 依優先順序檢查 Python 指令
echo   - Checking 'python' command...
python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    set "PIP_CMD=pip"
    for /f "tokens=*" %%i in ('python --version 2^>nul') do (
        echo [SUCCESS] Found: %%i
    )
    goto :python_found
)

echo   - Checking 'py' command...
py --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py"
    set "PIP_CMD=py -m pip"
    for /f "tokens=*" %%i in ('py --version 2^>nul') do (
        echo [SUCCESS] Found: %%i
    )
    goto :python_found
)

echo   - Checking 'python3' command...
python3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python3"
    set "PIP_CMD=pip3"
    for /f "tokens=*" %%i in ('python3 --version 2^>nul') do (
        echo [SUCCESS] Found: %%i
    )
    goto :python_found
)

echo [ERROR] No Python installation found
echo Please install Python 3.8+ manually from https://www.python.org/downloads/
pause
exit /b 1

:python_found
echo [SUCCESS] Using Python command: %PYTHON_CMD%
echo [SUCCESS] Using pip command: %PIP_CMD%
echo.

echo ===========================================
echo [Virtual Environment Setup]
echo ===========================================
echo   - Checking virtual environment...
if not exist "aiops\Scripts\activate.bat" (
    echo   - Creating virtual environment...
    %PYTHON_CMD% -m venv aiops
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
call aiops\Scripts\activate.bat
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
pip install -r "%~dp0\..\..\core_app\requirements.txt"
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
if not exist "config\config.env" (
    echo [ERROR] config.env file not found
    pause
    exit /b 1
) else (
    echo   - Configuration file exists
)

REM 修正的 .env 檢查和建立
if not exist ".env" (
    echo [INFO] .env file not found, creating from template...
    if exist "config\env.example" (
        copy config\env.example .env >nul
        echo [SUCCESS] .env file created
        goto :get_api_key
    ) else (
        echo [ERROR] config\env.example file not found
        pause
        exit /b 1
    )
) else (
    echo   - API Key file exists
)

REM 檢查 .env 檔案中是否有有效的 API Key
call aiops\Scripts\activate.bat
python -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); api_key=os.getenv('GOOGLE_API_KEY'); exit(0 if api_key and len(api_key) > 20 and api_key.startswith('AI') else 1)" 2>nul
if errorlevel 1 (
    echo [WARNING] Invalid or missing API Key in .env file
    goto :get_api_key
) else (
    echo   - API Key validation passed
    goto :continue_setup
)

:get_api_key
echo.
echo [IMPORTANT] Please enter your Google API Key:
echo Format example: AIzaSyC... (starts with AI)
echo.
set /p USER_API_KEY="Enter GOOGLE_API_KEY: "

REM 使用簡單的方法寫入 .env 檔案
echo # Google API Key - 請替換為您的實際 API Key > .env
echo # 前往 https://makersuite.google.com/app/apikey 取得 API Key >> .env
echo GOOGLE_API_KEY=%USER_API_KEY% >> .env
echo. >> .env
echo # 其他設定會從 config.env 自動載入 >> .env

echo.
echo [INFO] API Key has been written to .env file
echo [INFO] To modify, edit .env file directly

REM 驗證 API Key 是否正確寫入
echo   - Verifying API Key...
call aiops\Scripts\activate.bat
python -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); api_key=os.getenv('GOOGLE_API_KEY'); print('API Key found:', 'Yes' if api_key else 'No'); print('Key length:', len(api_key) if api_key else 0); print('Key starts with AI:', 'Yes' if api_key and api_key.startswith('AI') else 'No')" 2>nul

if errorlevel 1 (
    echo [ERROR] Failed to write API Key to .env file
    echo Please check file permissions and try again
    pause
    exit /b 1
)

echo [SUCCESS] API Key verification passed

:continue_setup
echo   - Checking RAG knowledge base...
if not exist "core_app\rag\vector_store\crem_faiss_index" (
    echo [ERROR] RAG vector database not found
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
call aiops\Scripts\activate.bat
python -m core_app.app
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start API server
    echo Please check error messages above
    pause
    exit /b 1
)

pause 