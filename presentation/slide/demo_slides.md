---
marp: true
theme: default
paginate: true
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
---

# 趨勢RAG活字典
## Trend Micro RAG Walking Dictionary

### 一鍵啟動 Demo 演示


### Tech
#API, #RAG, #LLM, #Docker, #Docker



---
### 痛點 vs 解方
| <img src="tired.png" width="500"> | <img src="robot.png" width="500"> |
|:--:|:--:|
| 工人智慧 | 人工智慧 |


---
### 一鍵啟動腳本執行
**畫面**：
- 開啟終端機
- 執行 `cd presentation\scripts && start_simple.bat`
- 自動化流程展示

---

### API 服務啟動確認（30 秒）
- 開啟瀏覽器
- 訪問 `http://localhost:8000/docs`
- 展示 FastAPI 自動生成的文檔頁面

<img src="api.png" width="1000">

---

### Gradio 前端啟動（30 秒）
- 開啟新的終端機視窗
- 執行 `cd presentation\scripts && start_gradio.bat`
- 展示啟動過程

---

### Gradio 介面展示（30 秒）
- 開啟瀏覽器訪問 `http://localhost:7860`
- 展示聊天介面
- 展示建議問題按鈕


<img src="gradio.png" width="700">


---

### 現場互動測試
- 切換到現場的 Gradio 介面 
- 測試預設問題和客製化問題


> **測試 1 - 預設問題**：
> 點擊建議問題按鈕，測試系統對預設問題的回答能力。

> **測試 2 - 客製化問題**：
> 輸入一個關於 CREM 技術細節的問題，展示系統的智能回答能力。

---

### 技術亮點總結（30 秒）
**畫面**：
- 技術能力總結
- 工程實踐展示



### 結尾（20 秒）
**畫面**：
- 專案資訊
- 技術標籤







---



# 🛠️ 技術棧

- **後端框架**：FastAPI + Uvicorn
- **AI 服務**：Google Gemini 2.0 API
- **向量資料庫**：FAISS
- **前端介面**：Gradio
- **容器化**：Docker + Docker Compose
- **監控**：psutil

---

# 🏗️ 系統架構

<img src="system.png" width="500"> 

---

# 📊 資料流程

|  |
|:--:|
| <img src="data flow 1.png" width="500"> |

| <img src="data flow 2.png" width="500"> |


---

# 🚀 一鍵啟動流程

## 自動化部署腳本

```bash
cd presentation\scripts && start_simple.bat
```

**執行步驟**：
1. 建立 Python 虛擬環境
2. 安裝所需依賴套件
3. 引導設定 API Key
4. 啟動 FastAPI 後端服務

---

# 🔧 API 服務啟動

## FastAPI 自動文檔

訪問：`http://localhost:8000/docs`

**特色**：
- 自動生成互動式 API 文檔
- 可直接在瀏覽器中測試端點
- 完整的請求/回應範例

---

# 🎨 Gradio 前端介面

## 啟動命令
```bash
cd presentation\scripts && start_gradio.bat
```

## 介面特色
- 直觀的聊天功能
- 建議問題按鈕
- 即時互動支援
- 響應式設計

---

# 🧪 現場互動測試

## 測試案例

**預設問題測試**：
- 點擊建議問題按鈕
- 驗證系統基本功能

**客製化問題測試**：
- 輸入 CREM 技術細節問題
- 展示智能回答能力

---

# 📈 技術亮點

## 工程實踐
- **RAG 管道優化**：512 字元分塊，50 字元重疊
- **提示工程**：溫度 0.05，最小化幻覺
- **向量搜尋**：Top-5 相似度匹配，0.7 閾值

---

# 🔍 系統監控

## 健康檢查端點
- `/health`：系統健康狀態
- `/info`：系統資訊和配置
- `/examples`：查詢範例

## 監控功能
- 資源利用率追蹤
- 系統診斷
- 審計日誌

---

# 🎯 核心優勢

## 效率提升
- **時間節省**：從數小時縮短到數秒
- **即時性**：即時存取最新資訊

## 使用者體驗
- **一鍵部署**：完全自動化流程
- **直觀介面**：Gradio 聊天介面
- **API 文檔**：FastAPI 自動生成

---

# 🚀 未來發展

## RAG測試
## CI/CD 管道
- GitHub Actions 自動化測試
- 每次提交自動執行測試

---



---


---

<!-- _class: lead -->

# 謝謝觀看！

## 趨勢RAG活字典
### 從自動化部署到實際互動測試

**聯絡資訊**：請參考專案文檔或聯絡開發團隊 