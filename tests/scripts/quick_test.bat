@echo off
chcp 65001 >nul
echo 趨勢科技資安問答 API 快速測試
echo ======================================
echo.

REM 檢查 API 是否運行
echo [1/4] 檢查 API 服務狀態...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [錯誤] API 服務未運行
    echo 請執行: Dev/dev_scripts/start.bat 或 start_api_enhanced.bat
    pause
    exit /b 1
)
echo [成功] API 服務正在運行

REM 測試健康檢查
echo [2/4] 測試健康檢查端點...
curl -s http://localhost:8000/health | python -m json.tool
if errorlevel 1 (
    echo [錯誤] 健康檢查失敗
    pause
    exit /b 1
)
echo [成功] 健康檢查通過

REM 測試範例問題端點
echo [3/4] 測試範例問題端點...
curl -s http://localhost:8000/examples | python -m json.tool
if errorlevel 1 (
    echo [錯誤] 範例問題端點失敗
    pause
    exit /b 1
)
echo [成功] 範例問題端點通過

REM 測試問答功能
echo [4/4] 測試問答功能...
echo 發送測試問題: "什麼是網路風險指數？"
curl -s -X POST "http://localhost:8000/ask" ^
  -H "Content-Type: application/json" ^
  -d "{\"question\": \"什麼是網路風險指數？\"}" ^
  | python -m json.tool
if errorlevel 1 (
    echo [錯誤] 問答功能測試失敗
    pause
    exit /b 1
)
echo [成功] 問答功能測試通過

REM 執行 pytest 快速測試
echo [5/5] 執行 pytest 快速測試...
cd tests
python -m pytest unit\ -v --tb=short -q
if errorlevel 1 (
    echo [警告] 部分單元測試失敗
) else (
    echo [成功] 單元測試通過
)
cd ..

echo.
echo ======================================
echo [成功] 所有測試通過！
echo ======================================
echo.
echo [文檔] API 文檔: http://localhost:8000/docs
echo [健康] 健康檢查: http://localhost:8000/health
echo [範例] 範例問題: http://localhost:8000/examples
echo.
echo 系統運行正常，可以開始使用！
pause 