@echo off
chcp 65001 >nul
echo ===========================================
echo 🎯 面試官專用演示腳本
echo ===========================================
echo.

echo [INFO] 正在準備演示環境...
echo.

REM 檢查必要檔案
if not exist "start.bat" (
    echo [ERROR] start.bat 不存在
    echo 請確保在專案根目錄執行此腳本
    pause
    exit /b 1
)

if not exist "core_app\app.py" (
    echo [ERROR] 核心應用程式不存在
    echo 請確保專案結構完整
    pause
    exit /b 1
)

echo [SUCCESS] 環境檢查通過
echo.

echo ===========================================
echo 🚀 啟動 AI 資安問答系統
echo ===========================================
echo.

echo [STEP 1] 執行自動化啟動腳本...
echo [INFO] 系統將自動：
echo   - 建立虛擬環境
echo   - 安裝依賴套件
echo   - 引導設定 API Key
echo   - 啟動 API 服務
echo.

echo [STEP 2] 啟動聊天介面...
echo [INFO] 新視窗將自動啟動聊天介面
echo.

echo [STEP 3] 測試功能...
echo [INFO] 可測試以下功能：
echo   - API 文檔：http://localhost:8000/docs
echo   - 健康檢查：http://localhost:8000/health
echo   - 聊天介面：http://127.0.0.1:7860
echo.

echo [READY] 準備開始演示！
echo.
echo 按任意鍵啟動系統...
pause

REM 啟動主系統
echo [INFO] 啟動主系統...
start "AI 資安問答系統" cmd /k "Demo\start_simple.bat"

REM 等待 5 秒後啟動聊天介面
echo [INFO] 等待系統初始化...
timeout /t 5 /nobreak >nul

REM 啟動聊天介面
echo [INFO] 啟動聊天介面...
start "聊天介面" cmd /k "aiops\Scripts\activate.bat && python core_app/gradio_app.py"

echo.
echo ===========================================
echo ✅ 系統啟動完成！
echo ===========================================
echo.
echo 🎯 測試端點：
echo   - API 文檔：http://localhost:8000/docs
echo   - 健康檢查：http://localhost:8000/health
echo   - 聊天介面：http://127.0.0.1:7860
echo.
echo 🧪 建議測試問題：
echo   - "什麼是 CRI？"
echo   - "2025年主要資安威脅有哪些？"
echo   - "CREM 技術如何運作？"
echo.
echo 💡 演示要點：
echo   - 展示 AI 回答的準確性
echo   - 展示系統響應速度
echo   - 展示專業的資安知識
echo.
echo 📊 技術亮點：
echo   - Google Gemini 2.0 Flash Lite
echo   - RAG 技術 + FAISS 向量資料庫
echo   - FastAPI + Gradio 整合
echo   - 自動化部署腳本
echo.
echo 按任意鍵結束演示...
pause 