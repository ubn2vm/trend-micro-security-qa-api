@echo off
REM Python 執行器 - 使用絕對路徑
if exist "C:\Python313\python.exe" (
    C:\Python313\python.exe %*
) else (
    echo [ERROR] Python not found at C:\Python313\python.exe
) 