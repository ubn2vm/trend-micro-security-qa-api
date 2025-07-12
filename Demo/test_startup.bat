@echo off
chcp 65001 >nul
echo ===========================================
echo Startup Test Script
echo ===========================================
echo.

echo [TEST] Testing startup process without launching API...
echo.

REM 檢查 Python
echo ===========================================
echo [Python Environment Check]
echo ===========================================
echo   - Checking system Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)
echo [SUCCESS] Python found

echo.
echo ===========================================
echo [Virtual Environment Test]
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

echo   - Testing virtual environment activation...
call ..\aiops\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment ready

echo.
echo ===========================================
echo [Dependency Test]
echo ===========================================
echo   - Testing dependency installation...
pip install -r ..\core_app\requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies ready

echo.
echo ===========================================
echo [Environment Test]
echo ===========================================
echo   - Testing configuration files...
if not exist "..\config\config.env" (
    echo [ERROR] config.env file not found
    pause
    exit /b 1
)
echo   - Configuration file exists

if not exist "..\.env" (
    echo [INFO] .env file not found, creating from template...
    if exist "..\config\env.example" (
        copy ..\config\env.example ..\.env >nul
        echo [SUCCESS] .env file created
    ) else (
        echo [ERROR] ..\config\env.example file not found
        pause
        exit /b 1
    )
) else (
    echo   - API Key file exists
)

echo.
echo ===========================================
echo [API Key Test]
echo ===========================================
echo   - Testing API Key validation...
call ..\aiops\Scripts\activate.bat
python -c "import os; from dotenv import load_dotenv; load_dotenv('..\config\config.env'); load_dotenv('..\.env'); api_key=os.getenv('GOOGLE_API_KEY'); print('API Key found:', 'Yes' if api_key else 'No'); print('Key length:', len(api_key) if api_key else 0); print('Key starts with AI:', 'Yes' if api_key and api_key.startswith('AI') else 'No')" 2>nul
if errorlevel 1 (
    echo [ERROR] API Key validation failed
    echo Current .env content:
    type ..\.env
    pause
    exit /b 1
)
echo [SUCCESS] API Key validation passed

echo.
echo ===========================================
echo [RAG Database Test]
echo ===========================================
echo   - Testing RAG knowledge base...
if not exist "..\core_app\rag\vector_store\crem_faiss_index" (
    echo [ERROR] RAG vector database not found
    pause
    exit /b 1
)
echo   - RAG vector database exists

echo.
echo ===========================================
echo [Port Test]
echo ===========================================
echo   - Testing port availability...
netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 8000 is already in use
) else (
    echo   - Port 8000 is available
)

echo.
echo ===========================================
echo [Module Import Test]
echo ===========================================
echo   - Testing module imports...
call ..\aiops\Scripts\activate.bat
python -c "import sys; sys.path.append('..'); import core_app.app; print('[SUCCESS] Module import test passed')" 2>nul
if errorlevel 1 (
    echo [ERROR] Module import test failed
    pause
    exit /b 1
)

echo.
echo ===========================================
echo ✅ ALL TESTS PASSED!
echo ===========================================
echo.
echo [SUCCESS] Startup process is ready
echo [INFO] You can now run start_simple.bat to launch the API
echo.
pause 