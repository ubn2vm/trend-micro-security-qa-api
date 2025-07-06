@echo off
echo 趨勢科技資安問答 API 啟動腳本
echo ================================
echo.

REM 檢查 Python 是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 找不到 Python
    echo 請先安裝 Python 3.11 或更新版本
    pause
    exit /b 1
)

REM 檢查虛擬環境
if not exist "aiops\Scripts\activate.bat" (
    echo 警告: 找不到虛擬環境 aiops
    echo 正在建立虛擬環境...
    python -m venv aiops
    if errorlevel 1 (
        echo 錯誤: 建立虛擬環境失敗
        pause
        exit /b 1
    )
    echo 虛擬環境建立成功
)

REM 啟動虛擬環境
echo 啟動虛擬環境...
call aiops\Scripts\activate.bat

REM 檢查 .env 檔案
if not exist ".env" (
    echo 警告: 找不到 .env 檔案
    echo 請複製 env.example 並設定您的 Google API Key
    echo.
    if exist "env.example" (
        echo 正在複製 env.example 到 .env...
        copy env.example .env
        echo.
        echo 請編輯 .env 檔案並設定您的 Google API Key
        echo 然後重新執行此腳本
        echo.
        echo 按任意鍵開啟 .env 檔案...
        pause
        notepad .env
        exit /b 1
    ) else (
        echo 錯誤: 找不到 env.example 檔案
        pause
        exit /b 1
    )
)

REM 驗證環境變數
echo 驗證環境變數...
python -c "import os; from dotenv import load_dotenv; load_dotenv(); api_key=os.getenv('GOOGLE_API_KEY'); print('API Key 狀態:', '已設定' if api_key else '未設定')" 2>nul
if errorlevel 1 (
    echo 錯誤: 無法讀取 .env 檔案
    echo 請檢查 .env 檔案格式是否正確
    pause
    exit /b 1
)

REM 檢查 API Key 格式
python -c "import os; from dotenv import load_dotenv; load_dotenv(); api_key=os.getenv('GOOGLE_API_KEY'); exit(0 if api_key and len(api_key) >= 20 and api_key.startswith('AI') else 1)" 2>nul
if errorlevel 1 (
    echo 警告: Google API Key 格式可能不正確
    echo 請確認 API Key 以 'AI' 開頭且長度至少 20 字符
    echo.
    echo 按任意鍵繼續或 Ctrl+C 取消...
    pause
)

REM 安裝依賴套件
echo 檢查並安裝依賴套件...
pip install -r requirements.txt
if errorlevel 1 (
    echo 錯誤: 安裝依賴套件失敗
    echo 請檢查網路連線或 requirements.txt 檔案
    pause
    exit /b 1
)
echo 依賴套件安裝完成

REM 檢查知識庫檔案
if not exist "summary.txt" (
    echo 警告: 找不到 summary.txt 檔案
    if exist "knowledgebase.txt" (
        echo 使用 knowledgebase.txt 作為知識庫
        copy knowledgebase.txt summary.txt
        echo 知識庫檔案複製完成
    ) else (
        echo 錯誤: 找不到知識庫檔案
        echo 請確認 knowledgebase.txt 或 summary.txt 檔案存在
        pause
        exit /b 1
    )
) else (
    echo 知識庫檔案檢查完成
)

REM 檢查端口是否被佔用
echo 檢查端口 8000 是否可用...
netstat -an | findstr ":8000" >nul 2>&1
if not errorlevel 1 (
    echo 警告: 端口 8000 已被佔用
    echo 請關閉其他使用該端口的程式或修改 API_PORT 環境變數
    echo.
    echo 按任意鍵繼續或 Ctrl+C 取消...
    pause
)

REM 啟動 API 服務
echo.
echo ================================
echo 啟動趨勢科技資安問答 API
echo ================================
echo.
echo API 文檔: http://localhost:8000/docs
echo 健康檢查: http://localhost:8000/health
echo 範例問題: http://localhost:8000/examples
echo 根路徑: http://localhost:8000/
echo.
echo 按 Ctrl+C 停止服務
echo.

REM 啟動服務並處理錯誤
python app.py
if errorlevel 1 (
    echo.
    echo 錯誤: API 服務啟動失敗
    echo 請檢查錯誤訊息並修正問題
    echo.
    pause
    exit /b 1
)

pause 