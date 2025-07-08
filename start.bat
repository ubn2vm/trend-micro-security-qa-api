@echo off
chcp 65001 >nul
echo ===========================================
echo Trend Micro Security QA API - Quick Start
echo ===========================================
echo.

REM 檢查 Python
echo ===========================================
echo [Python Environment Check]
echo ===========================================
echo   - Checking system Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   - System Python not found, checking project configuration...
    if exist "python_config\python.bat" (
        echo   - Testing project Python configuration...
        call python_config\python.bat --version
        if errorlevel 1 (
            echo [ERROR] Python not found. Please install Python 3.8+
            echo Download from: https://www.python.org/downloads/
            echo.
            echo Make sure to check "Add Python to PATH" during installation
            pause
            exit /b 1
        ) else (
            echo [SUCCESS] Using project Python configuration
            set "PYTHON_CMD=python_config\python.bat"
            set "PIP_CMD=python_config\pip.bat"
        )
    ) else (
        echo [ERROR] Python not found. Please install Python 3.8+
        echo Download from: https://www.python.org/downloads/
        echo.
        echo Make sure to check "Add Python to PATH" during installation
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] Using system Python
    set "PYTHON_CMD=python"
    set "PIP_CMD=pip"
)

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
        echo Please check Python installation
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
%PIP_CMD% install -r core_app\requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo Please check network connection
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed

echo.
echo ===========================================
echo [Environment & API Key Validation]
echo ===========================================
echo   - Checking configuration files...
if not exist "config\config.env" (
    echo [ERROR] config.env file not found
    echo Please ensure config\config.env exists with all configuration parameters
    pause
    exit /b 1
) else (
    echo   - Configuration file exists
)

REM 修復：先檢查 .env 檔案，如果不存在則執行 setup_env.bat
if not exist ".env" (
    echo [INFO] .env file not found, running setup_env.bat...
    if exist "setup_env.bat" (
        call setup_env.bat
        REM 再次檢查 .env 是否已建立
        if not exist ".env" (
            echo [ERROR] .env file still not found after running setup_env.bat
            echo Please manually create .env file with your Google API Key
            pause
            exit /b 1
        )
    ) else (
        echo [ERROR] setup_env.bat file not found
        echo Please manually create .env file with your Google API Key
        pause
        exit /b 1
    )
) else (
    echo   - API Key file exists
)

REM 修復：在虛擬環境中驗證 API Key（確保 python-dotenv 已安裝）
echo   - Validating API Key...
call aiops\Scripts\activate.bat
python -c "import os; from dotenv import load_dotenv; load_dotenv('config\config.env'); load_dotenv('.env'); api_key=os.getenv('GOOGLE_API_KEY'); exit(0 if api_key and len(api_key) >= 20 and api_key.startswith('AI') else 1)" 2>nul
if errorlevel 1 (
    echo [ERROR] Invalid or missing Google API Key
    echo Please check your .env file and ensure:
    echo - GOOGLE_API_KEY is set
    echo - Key starts with 'AI'
    echo - Key is at least 20 characters long
    echo.
    echo Opening .env file for editing...
    notepad .env
    pause
    exit /b 1
)
echo   - API Key validation passed

echo   - Checking knowledge base files...
set "KNOWLEDGE_FILE=%KNOWLEDGE_FILE%"
if "%KNOWLEDGE_FILE%"=="" set "KNOWLEDGE_FILE=summary.txt"

if not exist "%KNOWLEDGE_FILE%" (
    if exist "core_app\knowledgebase.txt" (
        echo   - Creating %KNOWLEDGE_FILE% from knowledgebase.txt...
        copy core_app\knowledgebase.txt %KNOWLEDGE_FILE%
        echo   - Knowledge base file created
    ) else (
        echo [ERROR] Knowledge base file not found
        echo Please ensure core_app\knowledgebase.txt exists
        pause
        exit /b 1
    )
) else (
    echo   - Knowledge base file exists
)
echo   - Checking port availability...
netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo   - Port 8000 is already in use
    echo [WARNING] Port 8000 is already in use
    echo Please close other programs using port 8000
    echo.
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

REM 確保在虛擬環境中啟動 API - 修復：直接執行 app.py
call aiops\Scripts\activate.bat
python core_app\app.py
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start API server
    echo Please check error messages above
    pause
    exit /b 1
)

pause
