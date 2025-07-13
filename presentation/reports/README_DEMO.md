# 📁 Demo 資料夾使用說明

## 🎯 資料夾用途
Demo 資料夾包含了面試官演示所需的所有工具和文檔，提供完整的「開箱即用」體驗。

## 📁 檔案結構

```
Demo/
├── README.md                 # 面試官第一印象（主要說明）
├── README_DEMO.md           # 本說明檔案
├── DEMO_TODO.md             # 演示準備追蹤清單
├── demo_for_interviewer.bat # 一鍵演示腳本
├── start_simple.bat         # 簡化啟動腳本
├── test_startup.bat         # 啟動測試腳本
├── QUICK_TEST.md            # 快速測試指南
├── DEMO_SCRIPT.md           # 演示腳本
└── assets/                  # 演示相關資源
    ├── README.md            # 資源說明
    ├── screenshots/         # 截圖
    └── videos/             # 影片
```

## 🚀 快速使用指南

### 面試官體驗流程

1. **一鍵演示**（推薦）：
   ```bash
   # 在專案根目錄執行
   Demo/demo_for_interviewer.bat
   ```

2. **手動啟動**：
   ```bash
   # 啟動 API 服務
   Demo/start_simple.bat
   
   # 新視窗啟動聊天介面
   aiops\Scripts\activate.bat
   python core_app/gradio_app.py
   ```

3. **預先測試**：
   ```bash
   # 測試啟動流程（不實際啟動 API）
   Demo/test_startup.bat
   ```

## 📋 檔案說明

### 核心腳本
- **`start_simple.bat`**：簡化版啟動腳本，專門為面試官設計
- **`test_startup.bat`**：測試腳本，驗證環境設定
- **`demo_for_interviewer.bat`**：一鍵演示腳本，自動啟動所有服務

### 文檔指南
- **`README.md`**：面試官第一印象，專案介紹和快速開始
- **`QUICK_TEST.md`**：5 分鐘快速測試指南
- **`DEMO_SCRIPT.md`**：完整演示腳本和話術
- **`DEMO_TODO.md`**：演示準備追蹤清單

### 資源檔案
- **`assets/`**：演示相關的截圖和影片

## 🎯 使用場景

### 面試官演示
1. 執行 `Demo/demo_for_interviewer.bat`
2. 按照 `DEMO_SCRIPT.md` 進行演示
3. 使用 `QUICK_TEST.md` 進行功能測試

### 開發者測試
1. 執行 `Demo/test_startup.bat` 驗證環境
2. 執行 `Demo/start_simple.bat` 啟動服務
3. 參考 `QUICK_TEST.md` 進行測試

### 故障排除
1. 檢查 `QUICK_TEST.md` 中的故障排除指南
2. 使用 `test_startup.bat` 診斷問題
3. 參考 `README.md` 中的支援資訊

## 💡 設計理念

### 開箱即用
- 所有工具都在 Demo 資料夾中
- 一鍵啟動，無需複雜設定
- 清晰的文檔和指南

### 面試官友好
- 簡化的操作流程
- 詳細的測試指南
- 完整的演示腳本

### 技術展示
- 展示完整的技術棧
- 體現工程實踐能力
- 突出自動化部署

## 🔄 更新記錄

### 2024-07-12
- ✅ 建立完整的 Demo 資料夾結構
- ✅ 移動啟動腳本到 Demo 資料夾
- ✅ 更新所有文檔引用
- ✅ 建立使用說明

---

**🎯 目標：讓面試官在 5 分鐘內體驗完整的 AI 資安問答系統！** 