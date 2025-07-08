@echo off
chcp 65001 >nul
echo ===========================================
echo Environment Setup Script
echo ===========================================
echo.

REM 檢查 .env 檔案是否存在
if exist ".env" (
    echo [INFO] .env file already exists
    echo Current content:
    type .env
    echo.
    echo Do you want to recreate it? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        echo Recreating .env file...
    ) else (
        echo Keeping existing .env file
        pause
        exit /b 0
    )
)

REM 從 env.example 複製
if exist "config\env.example" (
    copy config\env.example .env >nul
    if errorlevel 1 (
        echo [ERROR] Failed to copy config\env.example to .env
        pause
        exit /b 1
    )
    echo [SUCCESS] .env file created from config\env.example
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
    echo [SUCCESS] Environment setup completed
    echo Returning to start.bat...
    exit /b 0
) else (
    echo [ERROR] config\env.example file not found
    echo Please ensure config\env.example exists
    pause
    exit /b 1
)
