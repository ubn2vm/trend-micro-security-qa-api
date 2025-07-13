# 🤖 Trend Micro 資安報告智能問答系統

> **開箱即用** - 一鍵啟動 AI 資安問答服務

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini-2.0-orange.svg)](https://ai.google.dev/)
[![RAG](https://img.shields.io/badge/RAG-FAISS-red.svg)](https://faiss.ai/)

## 🎯 專案特色

- 🤖 **AI 驅動**：整合 Google Gemini 2.0 Flash Lite
- 🔍 **RAG 技術**：基於趨勢科技 CREM 技術文檔
- ⚡ **快速部署**：一鍵啟動，無需複雜設定
- 🛡️ **專業領域**：專注於資安風險管理與威脅情報
- 🧪 **完整測試**：包含單元、整合、效能、安全測試

## 🚀 快速開始（面試官專用）

### 方法一：一鍵啟動（推薦）

```bash
# 1. 克隆專案
git clone <your-repo-url>
cd AIOps

# 2. 一鍵啟動（自動設定環境）
Demo/start_simple.bat
```

### 方法二：Docker 部署

```bash
# 1. 進入容器化目錄
cd containerization

# 2. 啟動服務
docker-compose up -d
```

## 🧪 測試指南

### 第一步：啟動服務
執行 `Demo/start_simple.bat` 後，系統會：
1. ✅ 自動建立虛擬環境
2. ✅ 安裝所需套件
3. ✅ 引導設定 API Key
4. ✅ 啟動 API 服務

### 第二步：測試 API
- **API 文檔**：http://localhost:8000/docs
- **健康檢查**：http://localhost:8000/health
- **範例問題**：http://localhost:8000/examples

### 第三步：測試聊天介面
```bash
# 新開終端視窗
aiops\Scripts\activate.bat
python core_app/gradio_app.py
```
- **聊天介面**：http://127.0.0.1:7860

## 🎯 測試問題範例

### 基礎問題
- "什麼是 CRI？"
- "2025年主要資安威脅有哪些？"
- "如何防護勒索軟體攻擊？"

### 進階問題
- "CREM 技術如何運作？"
- "零信任架構的核心原則？"
- "AI 在資安中的應用？"

## 🏗️ 技術架構

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gradio UI     │    │   FastAPI       │    │   RAG System    │
│   (Port 7860)   │◄──►│   (Port 8000)   │◄──►│   FAISS +       │
│                 │    │                 │    │   Gemini        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 核心技術棧
- **後端框架**：FastAPI + Uvicorn
- **前端介面**：Gradio
- **AI 模型**：Google Gemini 2.0 Flash Lite
- **向量資料庫**：FAISS
- **嵌入模型**：HuggingFace Sentence Transformers
- **RAG 框架**：LangChain
- **容器化**：Docker + Docker Compose

## 📊 系統狀態檢查

啟動後檢查以下端點：
- ✅ **API 服務**：http://localhost:8000/health
- ✅ **聊天介面**：http://127.0.0.1:7860
- ✅ **API 文檔**：http://localhost:8000/docs

## 🛠️ 故障排除

### 常見問題

1. **API Key 錯誤**
   ```bash
   # 編輯 .env 檔案
   notepad .env
   # 設定：GOOGLE_API_KEY=your_actual_key
   ```

2. **端口被佔用**
   ```bash
   # 檢查端口使用
   netstat -an | findstr ":8000"
   ```

3. **依賴安裝失敗**
   ```bash
   # 重新安裝
   pip install -r core_app/requirements.txt
   ```

## 📈 效能指標

- **啟動時間**：< 30 秒
- **API 響應**：< 5 秒
- **記憶體使用**：< 2GB
- **支援並發**：10+ 同時請求

## 🎯 面試重點展示

### 技術能力
- ✅ **AI/ML 整合**：Gemini API + RAG 技術
- ✅ **後端開發**：FastAPI + 非同步處理
- ✅ **前端介面**：Gradio + 響應式設計
- ✅ **資料處理**：PDF 解析 + 向量化
- ✅ **系統架構**：微服務 + 容器化

### 工程實踐
- ✅ **自動化部署**：一鍵啟動腳本
- ✅ **測試框架**：完整測試覆蓋
- ✅ **文檔管理**：API 文檔 + 使用指南
- ✅ **錯誤處理**：優雅降級 + 日誌記錄

## 📚 詳細文檔

- [📖 快速開始指南](docs/Quick_Start.md)
- [🧪 測試框架說明](tests/README.md)
- [🔧 技術開發規劃](RAG_DEVELOPMENT_PLAN.md)
- [📊 專案狀態追蹤](PROJECT_STATUS.md)

## 🤝 支援

如有問題，請檢查：
1. [docs/Quick_Start.md](docs/Quick_Start.md) - 詳細啟動指南
2. [tests/README.md](tests/README.md) - 測試說明
3. [RAG_DEVELOPMENT_PLAN.md](RAG_DEVELOPMENT_PLAN.md) - 技術規劃

---

**🎯 準備好體驗 AI 驅動的資安問答系統了嗎？執行 `Demo/start_simple.bat` 開始吧！**

> 💡 **提示**：整個測試流程只需 5 分鐘，讓您快速體驗完整的 AI 資安問答系統！ 