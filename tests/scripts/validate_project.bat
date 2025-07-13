@echo off
chcp 65001 >nul
echo 趨勢科技資安問答 API 專案驗證
echo ======================================
echo.

REM 設定 Python 路徑
set "PYTHON_EXE=python"
set "PIP_EXE=pip"

echo [INFO] 使用 Python: %PYTHON_EXE%
echo [INFO] 使用 pip: %PIP_EXE%
echo.

REM 檢查 Python 是否可用
echo [1/6] 檢查 Python 可用性...
%PYTHON_EXE% --version >nul 2>&1
if errorlevel 1 (
    echo [錯誤] Python 不可用
    echo 請檢查 Python 安裝和環境變數設定
    pause
    exit /b 1
)
echo [成功] Python 可用

REM 檢查虛擬環境
echo [2/6] 檢查虛擬環境...
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
echo [3/6] 啟動虛擬環境...
call aiops\Scripts\activate.bat
if errorlevel 1 (
    echo [錯誤] 啟動虛擬環境失敗
    pause
    exit /b 1
)
echo [成功] 虛擬環境已啟動

REM 檢查依賴套件
echo [4/6] 檢查依賴套件...
%PIP_EXE% install -r core_app\requirements.txt
if errorlevel 1 (
    echo [錯誤] 安裝依賴套件失敗
    pause
    exit /b 1
)
echo [成功] 依賴套件已安裝

REM 檢查 API 服務
echo [5/6] 檢查 API 服務...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [警告] API 服務未運行
    echo 請先啟動 API 服務:
    echo   Dev/dev_scripts/start.bat
    echo   or
    echo   start_api_enhanced.bat
    echo.
    echo 按任意鍵繼續驗證...
    pause
) else (
    echo [成功] API 服務正在運行
)

REM 執行 Python 驗證腳本
echo [6/6] 執行完整驗證...
%PYTHON_EXE% -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath('.'))))
from tests.utils.test_helpers import TestClient, TestReportGenerator
from tests.utils.mock_data import MockDataGenerator

print('開始執行專案驗證...')

# 初始化測試工具
client = TestClient()
report_generator = TestReportGenerator()
mock_data = MockDataGenerator()

# 1. 檔案結構檢查
print('\\n[1/4] 檢查檔案結構...')
required_files = [
    'core_app/app.py',
    'core_app/main.py', 
    'core_app/requirements.txt',
    'config/env.example',
    'containerization/Dockerfile',
    'containerization/docker-compose.yml',
    'Dev/dev_scripts/start.bat',
    'docs/README.md'
]

missing_files = []
for file in required_files:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f'  ✅ {file} ({size} bytes)')
    else:
        print(f'  ❌ {file} (缺失)')
        missing_files.append(file)

if missing_files:
    print(f'\\n[警告] 缺少 {len(missing_files)} 個檔案')
else:
    print('\\n[成功] 所有必要檔案都存在')

# 2. 環境配置檢查
print('\\n[2/4] 檢查環境配置...')
if os.path.exists('.env'):
    print('  ✅ .env 檔案存在')
else:
    print('  ⚠️  .env 檔案不存在')

if os.path.exists('aiops/Scripts/activate.bat'):
    print('  ✅ 虛擬環境存在')
else:
    print('  ⚠️  虛擬環境不存在')

# 3. API 功能測試
print('\\n[3/4] 測試 API 功能...')
try:
    # 健康檢查
    health_result = client.health_check()
    report_generator.add_result(health_result)
    if health_result.status == 'success':
        print('  ✅ 健康檢查通過')
    else:
        print(f'  ❌ 健康檢查失敗: {health_result.error_message}')
    
    # 範例問題
    examples_result = client.get_examples()
    report_generator.add_result(examples_result)
    if examples_result.status == 'success':
        print('  ✅ 範例問題端點通過')
    else:
        print(f'  ❌ 範例問題端點失敗: {examples_result.error_message}')
    
    # 問答功能
    qa_result = client.ask_question('什麼是網路風險指數？')
    report_generator.add_result(qa_result)
    if qa_result.status == 'success':
        print('  ✅ 問答功能通過')
    else:
        print(f'  ❌ 問答功能失敗: {qa_result.error_message}')
        
except Exception as e:
    print(f'  ❌ API 測試錯誤: {e}')

# 4. 生成驗證報告
print('\\n[4/4] 生成驗證報告...')
report_file = report_generator.save_report('validation_report.json')
print(f'  驗證報告已儲存至: {report_file}')

# 列印摘要
report_generator.print_summary()

print('\\n專案驗證完成！')
"

echo.
echo ======================================
echo [成功] 專案驗證完成！
echo ======================================
echo.
echo 檢查 validation_report.json 了解詳細結果
pause 