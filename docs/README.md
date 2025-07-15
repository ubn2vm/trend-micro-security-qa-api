# Trend Micro 內部知識問答機器人 - 技術文檔

> **注意**：這是一份技術文檔，一般用戶請先閱讀根目錄的 [README.md](../../README.md) 了解專案概覽。

## 專案目標

建立一個快速、可驗證的本地原型，展示核心 AI 工程和自動化運營能力。目標是讓面試官能夠通過單一命令啟動 AI 問答服務並成功調用 API。

## 系統架構

### 核心組件
- **FastAPI 後端**：提供 RESTful API 服務
- **RAG 處理引擎**：檢索增強生成核心邏輯
- **FAISS 向量數據庫**：高性能相似性搜索索引
- **Gemini 2.0 API**：大語言模型響應生成
- **Gradio 前端**：Web 聊天界面

### 數據流程
用戶查詢 → Gradio UI → FastAPI 後端 → RAG 處理引擎 → FAISS 向量搜索 → Gemini 2.0 API → 結構化響應 → 用戶界面

## 技術棧詳解

### 核心技術
- **Python 3.11+**：主要開發語言
- **FastAPI**：現代化 Web 框架，提供自動 API 文檔
- **Uvicorn**：ASGI 服務器，支持異步處理
- **LangChain**：LLM 應用開發框架
- **FAISS**：Facebook AI 相似性搜索庫
- **Sentence Transformers**：文本向量化模型

### AI/ML 組件
- **Google Gemini 2.0 Flash-Lite**：雲端 AI 服務
- **向量嵌入**：文本到向量的轉換
- **語義搜索**：基於相似性的文檔檢索
- **提示工程**：自定義 CREM_PROMPT_TEMPLATE

### 容器化與部署
- **Docker**：應用容器化
- **Docker Compose**：多服務編排
- **環境變量管理**：python-dotenv

### 監控與診斷
- **psutil**：系統資源利用率追蹤
- **健康檢查**：系統狀態監控
- **審計日誌**：請求/響應記錄

## API 規格

### 端點詳解
| 端點 | 方法 | 描述 | 認證 | 響應格式 |
|------|------|------|------|----------|
| `/health` | GET | 系統健康狀態 | 無 | JSON |
| `/docs` | GET | 交互式 API 文檔 | 無 | HTML |
| `/info` | GET | 系統信息和配置 | 無 | JSON |
| `/examples` | GET | 示例查詢 | 無 | JSON |
| `/ask` | POST | 查詢處理端點 | **無（演示版）** | JSON |

### 請求/響應格式
```json
// POST /ask 請求
{
  "question": "什麼是 Cyber Risk Index (CRI)？"
}

// 響應格式
{
  "answer": "Cyber Risk Index (CRI) 是...",
  "sources": ["相關文檔引用"],
  "confidence": 0.95,
  "processing_time": 2.3
}
```

## 安全設定

### API 密鑰管理
- **環境變量存儲**：所有敏感設定通過環境變量管理
- **密鑰格式驗證**：啟動時驗證密鑰格式和長度
- **健康檢查遮罩**：API 密鑰在健康檢查中被遮罩
- **容器權限**：知識庫文件以只讀方式掛載

### 安全日誌
- **啟動日誌**：記錄系統啟動過程
- **API 請求日誌**：記錄所有 API 調用
- **錯誤追蹤**：記錄安全相關錯誤

## 性能優化

### RAG 管道優化
- **文本分塊**：512 字符塊，50 字符重疊
- **相似性閾值**：0.7 最低分數
- **頂部結果**：5 個最相關塊
- **溫度設定**：0.05（低隨機性）

### 響應時間目標
- **平均響應時間**：< 3 秒
- **向量搜索速度**：< 100ms
- **系統運行時間**：99.9%

## 開發指南

### 本地開發環境
```bash
# 創建虛擬環境
python -m venv aiops

# 激活環境
aiops\Scripts\activate.bat  # Windows
source aiops/bin/activate   # macOS/Linux

# 安裝依賴
pip install -r core_app/requirements.txt
```

### 測試框架
- **單元測試**：pytest 框架
- **集成測試**：端到端系統驗證
- **性能測試**：負載測試和響應時間分析
- **安全測試**：漏洞評估和滲透測試

### 代碼質量
- **類型提示**：使用 Python 類型註解
- **文檔字符串**：doctest 風格的函數文檔
- **錯誤處理**：統一的異常處理機制
- **日誌記錄**：結構化日誌輸出

## 部署選項

### 快速部署（推薦）
```bash
# Windows 一鍵部署
presentation/scripts/start_simple.bat
```

### 手動部署
```bash
# API 服務器啟動
python core_app/app.py

# 前端界面
python core_app/gradio_app.py
```

### 容器化部署
```bash
# Docker Compose 部署
cd containerization
docker-compose up -d
```

詳細部署步驟請參考 [Quick_Start.md](Quick_Start.md)。
