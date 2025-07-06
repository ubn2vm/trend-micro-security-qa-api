@echo off
REM 僅在當前會話中設定Python路徑，不影響系統環境變數
echo 正在設定Python環境...

REM 讀取配置檔案
for /f "tokens=1,2 delims==" %%a in (.python_config) do (
    if "%%a"=="PYTHON_DIR" set PYTHON_DIR=%%b
    if "%%a"=="PYTHON_SCRIPTS" set PYTHON_SCRIPTS=%%b
)

REM 只在當前會話中設定PATH
set PATH=%PYTHON_DIR%;%PYTHON_SCRIPTS%;%PATH%

echo Python環境已設定完成！
echo 現在可以使用 python 和 pip 命令了
echo.
echo 測試Python版本：
python --version
echo.
echo 測試pip版本：
pip --version 