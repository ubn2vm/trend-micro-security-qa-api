# 🚀 快速啟動參考卡片

## 📋 標準啟動流程

### **Windows 環境**
```bash
# 方法 1: 使用啟動腳本 (推薦)
start.bat

# 方法 2: 手動啟動
call aiops\Scripts\activate.bat
python app.py
```

### **Linux/Mac 環境**
```bash
# 啟動虛擬環境
source aiops/bin/activate

# 啟動 API 服務
python app.py
```

### **Docker 環境**
```bash
# 一鍵啟動
docker-compose up -d

# 查看狀態
docker-compose ps
```

## 🌐 API 端點快速訪問

| 端點 | 用途 | URL |
|------|------|-----|
| 📚 API 文檔 | Swagger UI | http://localhost:8000/docs |
| 💚 健康檢查 | 系統狀態 | http://localhost:8000/health |
| ℹ️ API 資訊 | 詳細資訊 | http://localhost:8000/info |
| 📝 範例問題 | 測試問題 | http://localhost:8000/examples |

## 🔧 常見問題快速解決

### **❌ 拒絕連線 (Connection Refused)**
**症狀**: 瀏覽器顯示 "無法連接到此網站"
**原因**: API 服務未啟動
**解決**:
1. 確認命令列顯示 `(aiops)` 虛擬環境
2. 檢查是否有錯誤訊息
3. 重新執行 `python app.py`

### **📦 ModuleNotFoundError: No module named 'psutil'**
**症狀**: 啟動時出現模組找不到錯誤
**原因**: 缺少依賴套件
**解決**:
```bash
pip install psutil
# 或使用專案腳本
python_config\pip.bat install psutil
```

### **🔑 API Key 驗證失敗**
**症狀**: 啟動時顯示 API Key 錯誤
**原因**: 環境變數設定錯誤
**解決**:
1. 檢查 `.env` 檔案是否存在
2. 確認 `GOOGLE_API_KEY` 格式正確
3. API Key 應以 "AI" 開頭且長度至少 20 字符

### **🔌 端口被佔用**
**症狀**: 啟動時顯示端口已被使用
**原因**: 其他服務使用端口 8000
**解決**:
1. 修改 `.env` 檔案中的 `API_PORT`
2. 或關閉其他使用該端口的程式

### **📝 測試腳本亂碼問題**
**症狀**: 執行 `quick_test.bat` 時顯示亂碼
**原因**: Windows 命令列編碼問題
**解決**:
1. **方案 1**: 使用修改後的 `quick_test.bat` (已修正編碼)
2. **方案 2**: 使用英文版 `quick_test_en.bat` (避免編碼問題)

### **🚀 啟動腳本亂碼問題**
**症狀**: 執行 `start.bat` 時顯示亂碼
**原因**: Windows 命令列編碼問題
**解決**:
1. **方案 1**: 使用修改後的 `start.bat` (已修正編碼，使用英文)
2. **方案 2**: 使用增強版 `start_api_enhanced.bat` (包含重試機制)
3. **方案 3**: 手動啟動 (避免編碼問題)
   ```bash
   call aiops\Scripts\activate.bat
   python app.py
   ```

## 🧪 快速測試

### **自動化測試腳本**
```bash
# 方法 1: 使用修正版批次檔 (推薦)
quick_test.bat

# 方法 2: 使用英文版 (避免編碼問題)
quick_test_en.bat
```

### **手動測試 API**
```bash
# 健康檢查
curl http://localhost:8000/health

# 或直接在瀏覽器訪問
http://localhost:8000/health
```

### **測試問答功能**
```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "什麼是網路安全風險指數？"}'
```

### **綜合測試**
```bash
# 執行完整的邊界情況、性能、安全性測試
python tests/test_comprehensive.py
```

## 📞 緊急聯絡

如果以上方法都無法解決問題：
1. 檢查 `README.md` 中的詳細故障排除指南
2. 查看 `README.md` 中的完整設定說明
3. 確認所有必要檔案都存在且格式正確

---

**最後更新**: 2025-01-XX  
**版本**: 1.0.0 