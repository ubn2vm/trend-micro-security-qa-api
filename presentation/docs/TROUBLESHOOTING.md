# 🛠️ 故障排除指南（Day14）

## 🚨 常見問題與解決方案

### 1. API Key 相關問題

#### 問題：GOOGLE_API_KEY 未設定
**症狀**：
- 錯誤訊息：`請設定 GOOGLE_API_KEY 環境變數`
- 系統無法啟動

**解決方案**：
```bash
# 1. 建立 .env 檔案
echo GOOGLE_API_KEY=your_actual_api_key > .env

# 2. 或編輯現有 .env 檔案
notepad .env
```

**驗證**：
```bash
# 檢查 API Key 格式
# 正確格式：AIzaSyC...（以 AI 開頭）
```

#### 問題：API Key 格式錯誤
**症狀**：
- 錯誤訊息：`GOOGLE_API_KEY 格式不正確`
- 連線失敗

**解決方案**：
1. 確認 API Key 以 `AI` 開頭
2. 檢查是否有多餘的空格或換行
3. 重新從 Google AI Studio 複製 API Key

### 2. 端口衝突問題

#### 問題：端口 8000 被佔用
**症狀**：
- 錯誤訊息：`Address already in use`
- 服務無法啟動

**解決方案**：
```bash
# 1. 檢查端口使用情況
netstat -an | findstr ":8000"

# 2. 終止佔用端口的程序
taskkill /F /PID <PID>

# 3. 或修改端口設定
# 編輯 core_app/app.py，修改 uvicorn.run 的 port 參數
```

#### 問題：端口 7860 被佔用
**症狀**：
- Gradio 介面無法啟動
- 錯誤訊息：`Port 7860 is already in use`

**解決方案**：
```bash
# 1. 檢查端口使用情況
netstat -an | findstr ":7860"

# 2. 終止佔用端口的程序
taskkill /F /PID <PID>

# 3. 或修改 Gradio 端口
# 編輯 core_app/gradio_app.py，修改 demo.launch 的 server_port 參數
```

### 3. 依賴套件問題

#### 問題：模組找不到
**症狀**：
- 錯誤訊息：`ModuleNotFoundError: No module named 'fastapi'`
- 導入失敗

**解決方案**：
```bash
# 1. 啟動虛擬環境
aiops\Scripts\activate.bat

# 2. 安裝依賴套件
pip install -r core_app/requirements.txt

# 3. 或手動安裝核心套件
pip install fastapi uvicorn gradio langchain google-generativeai
```

#### 問題：版本衝突
**症狀**：
- 錯誤訊息：`Version conflict`
- 功能異常

**解決方案**：
```bash
# 1. 清理虛擬環境
deactivate
rmdir /s aiops

# 2. 重新建立虛擬環境
python -m venv aiops
aiops\Scripts\activate.bat

# 3. 重新安裝依賴
pip install -r core_app/requirements.txt
```

### 4. 檔案路徑問題

#### 問題：找不到向量資料庫
**症狀**：
- 錯誤訊息：`RAG 向量資料庫不存在`
- 系統初始化失敗

**解決方案**：
```bash
# 1. 檢查檔案結構
dir core_app\rag\vector_store\crem_faiss_index

# 2. 如果不存在，重新建立向量資料庫
cd core_app\rag
python crem_knowledge.py
```

#### 問題：找不到 PDF 檔案
**症狀**：
- 錯誤訊息：`PDF 檔案不存在`
- 資料處理失敗

**解決方案**：
```bash
# 1. 檢查 PDF 檔案
dir core_app\rag\data\sb-crem.pdf

# 2. 如果不存在，重新下載或複製檔案
```

### 5. 網路連線問題

#### 問題：無法連線 Google API
**症狀**：
- 錯誤訊息：`連線失敗`
- API 請求超時

**解決方案**：
1. 檢查網路連線
2. 確認防火牆設定
3. 檢查代理伺服器設定
4. 嘗試使用 VPN

#### 問題：下載模型失敗
**症狀**：
- 錯誤訊息：`模型下載失敗`
- 嵌入模型無法載入

**解決方案**：
```bash
# 1. 手動下載模型
pip install sentence-transformers

# 2. 設定離線模式（如果可用）
export HF_OFFLINE=1
```

### 6. 記憶體不足問題

#### 問題：記憶體不足
**症狀**：
- 錯誤訊息：`Out of memory`
- 系統變慢或崩潰

**解決方案**：
1. 關閉其他應用程式
2. 增加虛擬記憶體
3. 使用較小的模型
4. 分批處理資料

### 7. 權限問題

#### 問題：檔案權限不足
**症狀**：
- 錯誤訊息：`Permission denied`
- 無法寫入檔案

**解決方案**：
1. 以管理員身份執行命令提示字元
2. 檢查檔案權限設定
3. 確保有寫入權限

## 🔧 系統診斷工具

### 快速診斷腳本
```bash
# 執行診斷
Demo\test_all_scripts.bat
```

### 手動診斷步驟
1. **環境檢查**：
   ```bash
   python --version
   pip list
   ```

2. **API 測試**：
   ```bash
   curl http://localhost:8000/health
   ```

3. **依賴檢查**：
   ```bash
   python -c "import fastapi, gradio, langchain; print('All modules OK')"
   ```

## 📞 支援聯絡

### 即時支援
- **GitHub Issues**：提交問題報告
- **技術文檔**：查看詳細文檔
- **社群論壇**：尋求社群幫助

### 問題報告格式
```
**問題描述**：
[詳細描述問題]

**錯誤訊息**：
[完整的錯誤訊息]

**環境資訊**：
- 作業系統：Windows 10
- Python 版本：3.8+
- 專案版本：Day14

**重現步驟**：
1. [步驟1]
2. [步驟2]
3. [步驟3]

**預期行為**：
[描述預期的正常行為]

**實際行為**：
[描述實際發生的行為]
```

## 🎯 預防措施

### 定期維護
1. **更新依賴套件**：
   ```bash
   pip install --upgrade -r core_app/requirements.txt
   ```

2. **清理快取**：
   ```bash
   pip cache purge
   ```

3. **備份配置**：
   ```bash
   copy .env .env.backup
   ```

### 最佳實踐
1. 使用虛擬環境
2. 定期更新 API Key
3. 監控系統資源使用
4. 保持網路連線穩定

---

**💡 提示**：如果問題持續存在，請嘗試重新啟動系統或重新安裝專案。 