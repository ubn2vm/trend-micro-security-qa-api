@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   趨勢RAG活字典 - Marp 演示文稿啟動器
echo ========================================
echo.

:: 檢查 Node.js 是否安裝
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未找到 Node.js
    echo 請先安裝 Node.js：https://nodejs.org/
    pause
    exit /b 1
)

:: 檢查 Marp CLI 是否安裝
marp --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  警告：未找到 Marp CLI
    echo 正在安裝 Marp CLI...
    npm install -g @marp-team/marp-cli
    if errorlevel 1 (
        echo ❌ 安裝失敗，請手動安裝：npm install -g @marp-team/marp-cli
        pause
        exit /b 1
    )
)

echo ✅ 環境檢查完成
echo.

:: 切換到演示文稿目錄
cd /d "%~dp0.."

echo 📋 可用的操作：
echo.
echo 1. 預覽演示文稿 (推薦)
echo 2. 生成 HTML 檔案
echo 3. 生成 PDF 檔案
echo 4. 啟動開發伺服器
echo 5. 退出
echo.

set /p choice="請選擇操作 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🚀 啟動預覽模式...
    echo 瀏覽器將自動開啟，按 Ctrl+C 停止
    echo.
    marp demo_slides.md --preview
) else if "%choice%"=="2" (
    echo.
    echo 📄 生成 HTML 檔案...
    marp demo_slides.md --html
    if errorlevel 1 (
        echo ❌ 生成失敗
    ) else (
        echo ✅ HTML 檔案已生成：demo_slides.html
    )
) else if "%choice%"=="3" (
    echo.
    echo 📄 生成 PDF 檔案...
    marp demo_slides.md --pdf
    if errorlevel 1 (
        echo ❌ 生成失敗
    ) else (
        echo ✅ PDF 檔案已生成：demo_slides.pdf
    )
) else if "%choice%"=="4" (
    echo.
    echo 🌐 啟動開發伺服器...
    echo 伺服器將在 http://localhost:8080 啟動
    echo 按 Ctrl+C 停止
    echo.
    marp demo_slides.md --server
) else if "%choice%"=="5" (
    echo.
    echo 👋 再見！
    exit /b 0
) else (
    echo.
    echo ❌ 無效的選擇
)

echo.
pause 