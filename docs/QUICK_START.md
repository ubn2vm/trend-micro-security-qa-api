# Trend Micro 內部知識問答機器人 - 快速開始指南

> **重要提醒**：本指南提供詳細的部署步驟和故障排除。如需了解專案概覽，請先閱讀根目錄的 [README.md](../../README.md)。

## 概述

本指南提供三種不同的部署方法：
1. **Windows 一鍵部署**
2. **手動 Python 虛擬環境設置**
3. **Docker 容器部署**

## 快速開始 - Windows 一鍵部署

### 前置需求
- Windows 10/11
- Python 3.8+ 已安裝
- 網路連接（用於 API 密鑰和依賴）

### 步驟 1：獲取 Google API 密鑰
1. 訪問 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 使用 Google 帳戶登入
3. 點擊「Create API Key」
4. 複製生成的密鑰（以 'AI' 開頭）

### 步驟 2：一鍵啟動
```bash
# 執行主要啟動腳本
presentation/scripts/start_simple.bat
```

**自動執行的操作：**
- Python 環境檢測
- 虛擬環境創建（`aiops/`）
- 從 `core_app/requirements.txt` 安裝依賴
- 環境配置設置
- API 密鑰驗證
- 知識庫初始化
- 端口可用性檢查
- API 服務器啟動

### 步驟 3：驗證部署
成功啟動後，您將看到：
```
===========================================
正在啟動 Trend Micro 內部知識問答機器人
===========================================

[DOCS] API 文檔：http://localhost:8000/docs
[HEALTH] 健康檢查：http://localhost:8000/health
[EXAMPLES] 示例問題：http://localhost:8000/examples
[ROOT] 根路徑：http://localhost:8000/

按 Ctrl+C 停止服務器
```

### 步驟 4：測試 API
在瀏覽器中訪問：
- **API 文檔**：http://localhost:8000/docs
- **健康檢查**：http://localhost:8000/health
- **示例問題**：http://localhost:8000/examples

## 手動設置（替代方法）

### 步驟 1：環境設置
```bash
# 運行環境設置腳本
Dev/dev_scripts/setup_env.bat
```

此腳本將：
- 從 `config/env.example` 創建 `.env` 文件
- 打開記事本進行 API 密鑰配置
- 指導您完成 Google API 密鑰設置

### 步驟 2：配置 API 密鑰
編輯 `.env` 文件：
```env
# Google API 密鑰 - 替換為您的實際 API 密鑰
# 從 https://makersuite.google.com/app/apikey 獲取
GOOGLE_API_KEY=your_actual_api_key_here

# 其他設定從 config.env 自動加載
# 如需覆蓋，請在此處設置：
# GEMINI_MODEL=gemini-2.0-flash-lite
# GEMINI_TEMPERATURE=0.1
# GEMINI_MAX_TOKENS=200
```

### 步驟 3：手動虛擬環境設置
```bash
# 創建虛擬環境
python -m venv aiops

# 激活虛擬環境
call aiops\Scripts\activate.bat

# 安裝依賴
pip install -r core_app\requirements.txt
```

### 步驟 4：啟動 API 服務器
```bash
# 確保虛擬環境已激活
call aiops\Scripts\activate.bat

# 啟動 API 服務器
python core_app\app.py
```

## Docker 部署

### 前置需求
- Docker Desktop 已安裝
- Docker Compose 可用

### 步驟 1：配置環境
```bash
# 複製環境模板
copy config\env.example .env

# 編輯 .env 文件添加您的 API 密鑰
notepad .env
```

### 步驟 2：Docker Compose 部署
```bash
# 啟動服務
docker-compose up -d

# 檢查服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
```

### 步驟 3：驗證 Docker 部署
- **API 文檔**：http://localhost:8000/docs
- **健康檢查**：http://localhost:8000/health
- **容器狀態**：`docker-compose ps`

## API 端點參考

| 端點 | 用途 | URL | 方法 |
|------|------|-----|------|
| API 文檔 | Swagger UI | http://localhost:8000/docs | GET |
| 健康檢查 | 系統狀態 | http://localhost:8000/health | GET |
| API 信息 | 詳細信息 | http://localhost:8000/info | GET |
| 示例問題 | 測試問題 | http://localhost:8000/examples | GET |
| 提問 | 問答服務 | http://localhost:8000/ask | POST |

## 測試與驗證

### 快速測試腳本
```bash
# 自動化綜合測試
tests\scripts\quick_test.bat

# 專案驗證
tests\scripts\validate_project.bat

# 安全測試
python tests\security\test_security.py
```

### 手動 API 測試
```bash
# 健康檢查
curl http://localhost:8000/health

# 提問
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "什麼是 Cyber Risk Index (CRI)？"}'
```

### 綜合測試
```bash
# 運行所有測試套件
cd tests
python -m pytest

# 運行特定測試類型
python -m pytest unit/        # 單元測試
python -m pytest integration/ # 集成測試
python -m pytest performance/ # 性能測試
python -m pytest security/    # 安全測試
```

## 故障排除

### 連接被拒絕
**症狀**：瀏覽器顯示「無法連接到此網站」
**原因**：API 服務未啟動
**解決方案**：
1. 檢查命令行是否有 `(aiops)` 虛擬環境
2. 查找錯誤消息
3. 重新運行 `python core_app\app.py`

### 模組未找到錯誤
**症狀**：「No module named 'xxx'」錯誤
**原因**：缺少依賴
**解決方案**：
```bash
# 重新安裝依賴
pip install -r core_app\requirements.txt
```

### API 密鑰驗證失敗
**症狀**：啟動時 API 密鑰錯誤
**原因**：無效或缺少 API 密鑰
**解決方案**：
1. 檢查 `.env` 文件是否存在
2. 驗證 `GOOGLE_API_KEY` 格式（以 'AI' 開頭，最少 20 字符）
3. 如需要，重新運行 `Dev/dev_scripts/setup_env.bat`

### 端口已被使用
**症狀**：端口 8000 已被使用
**原因**：其他服務正在使用端口 8000
**解決方案**：
1. 在 `config/config.env` 中更改端口：`API_PORT=8001`
2. 或關閉使用端口 8000 的其他應用程序

### Docker 問題
**症狀**：Docker 容器啟動失敗
**原因**：配置或資源問題
**解決方案**：
```bash
# 檢查 Docker 日誌
docker-compose logs

# 重建容器
docker-compose down
docker-compose up --build -d
```

## 系統需求

### 最低需求
- **操作系統**：Windows 10/11、Linux、macOS
- **Python**：3.8+
- **記憶體**：4GB
- **儲存空間**：2GB 可用空間
- **網路**：API 調用的網路連接

### 推薦需求
- **操作系統**：Windows 11、Ubuntu 20.04+、macOS 12+
- **Python**：3.11+
- **記憶體**：8GB
- **儲存空間**：5GB 可用空間
- **網路**：穩定的網路連接

## 與根目錄 README.md 對齊的更新

### 部署腳本路徑
- 更新為 `presentation/scripts/start_simple.bat`（與根目錄一致）
- 保留對 `Dev/dev_scripts/setup_env.bat` 的引用（用於手動設置）

### 技術規格
- 保持與根目錄 README.md 中的技術棧描述一致
- 更新 Python 版本要求為 3.11+
- 保持相同的 API 端點描述

### 安全注意事項
- 強調 `/ask` 端點目前沒有認證（演示版）
- 提醒這是演示/開發版本，不適合生產部署
- 與根目錄 README.md 中的安全警告保持一致 