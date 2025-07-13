@echo off
chcp 65001 >nul
echo 趨勢科技資安問答 API 完整測試套件
echo ======================================
echo.

REM 設定 Python 路徑
set "PYTHON_EXE=python"
set "PIP_EXE=pip"

echo [INFO] 使用 Python: %PYTHON_EXE%
echo [INFO] 使用 pip: %PIP_EXE%
echo.

REM 檢查 Python 是否可用
echo [1/7] 檢查 Python 可用性...
%PYTHON_EXE% --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] Python 不可用
    echo 請檢查 Python 安裝和環境變數設定
    pause
    exit /b 1
)
echo [成功] Python 可用

REM 檢查虛擬環境
echo [2/7] 檢查虛擬環境...
if not exist "aiops\Scripts\activate.bat" (
    echo [警告] 虛擬環境不存在
    echo 建立虛擬環境...
    %PYTHON_EXE% -m venv aiops
    if errorlevel 1 (
        echo [錯誤] 建立虛擬環境失敗
        pause
        exit /b 1
    )
    echo [成功] 虛擬環境已建立
) else (
    echo [成功] 虛擬環境存在
)

REM 啟動虛擬環境
echo [3/7] 啟動虛擬環境...
call aiops\Scripts\activate.bat
if errorlevel 1 (
    echo [錯誤] 啟動虛擬環境失敗
    pause
    exit /b 1
)
echo [成功] 虛擬環境已啟動

REM 檢查依賴套件
echo [4/7] 檢查依賴套件...
%PIP_EXE% install -r core_app\requirements.txt
if errorlevel 1 (
    echo [錯誤] 安裝依賴套件失敗
    pause
    exit /b 1
)
echo [成功] 依賴套件已安裝

REM 安裝測試依賴
echo [5/7] 安裝測試依賴...
%PIP_EXE% install pytest requests psutil
if errorlevel 1 (
    echo [警告] 安裝測試依賴失敗，繼續執行...
) else (
    echo [成功] 測試依賴已安裝
)

REM 檢查 API 服務
echo [6/7] 檢查 API 服務...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [警告] API 服務未運行
    echo 請先啟動 API 服務:
    echo   Dev/dev_scripts/start.bat
    echo   or
    echo   start_api_enhanced.bat
    echo.
    echo 按任意鍵繼續測試...
    pause
) else (
    echo [成功] API 服務正在運行
)

REM 執行完整測試套件
echo [7/7] 執行完整測試套件...
echo.

echo ======================================
echo 開始執行測試...
echo ======================================

REM 切換到測試目錄
cd tests

REM 執行單元測試
echo.
echo [單元測試]
echo ----------
%PYTHON_EXE% -m pytest unit\ -v --tb=short
if errorlevel 1 (
    echo [警告] 部分單元測試失敗
) else (
    echo [成功] 單元測試通過
)

REM 執行整合測試
echo.
echo [整合測試]
echo ----------
%PYTHON_EXE% -m pytest integration\ -v --tb=short
if errorlevel 1 (
    echo [警告] 部分整合測試失敗
) else (
    echo [成功] 整合測試通過
)

REM 執行性能測試
echo.
echo [性能測試]
echo ----------
%PYTHON_EXE% -m pytest performance\ -v --tb=short
if errorlevel 1 (
    echo [警告] 部分性能測試失敗
) else (
    echo [成功] 性能測試通過
)

REM 執行安全測試
echo.
echo [安全測試]
echo ----------
%PYTHON_EXE% -m pytest security\ -v --tb=short
if errorlevel 1 (
    echo [警告] 部分安全測試失敗
) else (
    echo [成功] 安全測試通過
)

REM 回到根目錄
cd ..

REM 生成測試報告
echo.
echo [生成測試報告]
echo --------------
%PYTHON_EXE% -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath('.'))))
from tests.utils.test_helpers import TestReportGenerator
from tests.utils.mock_data import MockDataGenerator
from tests.utils.test_helpers import TestClient

# 執行一些基本測試並生成報告
client = TestClient()
report_generator = TestReportGenerator()
mock_data = MockDataGenerator()

# 基本功能測試
health_result = client.health_check()
report_generator.add_result(health_result)

examples_result = client.get_examples()
report_generator.add_result(examples_result)

# 問答測試
for question in mock_data.generate_test_questions()[:3]:
    qa_result = client.ask_question(question)
    report_generator.add_result(qa_result)

# 生成並儲存報告
report_file = report_generator.save_report('test_report.json')
print(f'測試報告已儲存至: {report_file}')

# 列印摘要
report_generator.print_summary()
"

echo.
echo ======================================
echo 測試完成！
echo ======================================
echo.
echo [文檔] API 文檔: http://localhost:8000/docs
echo [健康] 健康檢查: http://localhost:8000/health
echo [報告] 測試報告: test_report.json
echo.
echo 所有測試已執行完成！
pause 