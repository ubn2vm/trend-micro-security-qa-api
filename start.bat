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

REM 改進：檢查 .env 檔案，如果不存在則手動建立
if not exist ".env" (
    echo [INFO] .env file not found, creating from template...
    if exist "config\env.example" (
        copy config\env.example .env >nul
        if errorlevel 1 (
            echo [ERROR] Failed to copy config\env.example to .env
            pause
            exit /b 1
        )
        echo [SUCCESS] .env file created from template
        echo.
        echo [IMPORTANT] Please edit .env file and set your Google API Key
        echo.
        echo Steps to get Google API Key:
        echo 1. Go to https://makersuite.google.com/app/apikey
        echo 2. Create a new API key
        echo 3. Copy the key (starts with 'AI')
        echo 4. Edit .env file and replace 'your_google_api_key_here' with your key
        echo.
        echo Opening .env file for editing...
        notepad .env
        echo.
        echo [INFO] After editing .env file, press any key to continue...
        pause
        echo [INFO] Continuing with API Key validation...
    ) else (
        echo [ERROR] config\env.example file not found
        echo Please manually create .env file with your Google API Key
        pause
        exit /b 1
    )
) else (
    echo   - API Key file exists
)

REM 改進：在虛擬環境中驗證 API Key（更健壯的驗證）
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
    echo Current .env content:
    type .env
    echo.
    echo Do you want to edit the .env file now? (Y/N)
    set /p edit_choice=
    if /i "%edit_choice%"=="Y" (
        echo Opening .env file for editing...
        notepad .env
        echo.
        echo [INFO] After editing, press any key to retry validation...
        pause
        echo [INFO] Retrying API Key validation...
        python -c "import os; from dotenv import load_dotenv; load_dotenv('config\config.env'); load_dotenv('.env'); api_key=os.getenv('GOOGLE_API_KEY'); exit(0 if api_key and len(api_key) >= 20 and api_key.startswith('AI') else 1)" 2>nul
        if errorlevel 1 (
            echo [ERROR] API Key validation still failed
            echo Please ensure you have a valid Google API Key
            pause
            exit /b 1
        )
    ) else (
        echo [ERROR] API Key validation failed
        echo Please manually fix the .env file and run start.bat again
        pause
        exit /b 1
    )
)
echo   - API Key validation passed

echo   - Checking RAG knowledge base...
set "RAG_VECTOR_DIR=%RAG_VECTOR_DIR%"
if "%RAG_VECTOR_DIR%"=="" set "RAG_VECTOR_DIR=core_app\rag\vector_store\crem_faiss_index"

if not exist "%RAG_VECTOR_DIR%" (
    echo [ERROR] RAG vector database not found: %RAG_VECTOR_DIR%
    echo Please ensure the RAG vector database exists
    echo You may need to run RAG processing first
    pause
    exit /b 1
) else (
    echo   - RAG vector database exists: %RAG_VECTOR_DIR%
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

REM 確保在虛擬環境中啟動 API - 修復：使用模組方式執行
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
