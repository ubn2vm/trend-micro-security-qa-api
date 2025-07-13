---
marp: true
---

# Marp 演示文稿使用說明

## 📋 檔案說明

- `demo_slides.md` - 主要的 Marp 演示文稿檔案
- `marp.config.js` - Marp 配置檔案
- `BACKUP_VIDEO_SCRIPT.md` - 原始影片腳本參考

## 🚀 快速開始

### 1. 安裝 Marp CLI

```bash
# 使用 npm 安裝
npm install -g @marp-team/marp-cli

# 或使用 yarn
yarn global add @marp-team/marp-cli
```

### 2. 預覽演示文稿

```bash
# 在 presentation 目錄下執行
marp demo_slides.md --preview
```

### 3. 生成 HTML 檔案

```bash
# 生成 HTML 檔案
marp demo_slides.md --html

# 生成 PDF 檔案
marp demo_slides.md --pdf
```

### 4. 使用自訂配置

```bash
# 使用自訂配置檔案
marp demo_slides.md --config-file marp.config.js --preview
```

## 🎨 自訂主題

### 修改樣式
編輯 `marp.config.js` 中的 CSS 部分來自訂：
- 字體和顏色
- 版面配置
- 動畫效果
- 響應式設計

### 新增主題
1. 在 `themes/` 目錄下創建新的 CSS 檔案
2. 在 `marp.config.js` 中設定 `themeSet` 路徑
3. 在 `demo_slides.md` 中使用 `theme: your-theme-name`

## 📱 響應式設計

演示文稿已包含響應式設計，支援：
- 桌面螢幕 (1920x1080)
- 平板螢幕 (768px)
- 手機螢幕 (480px)

## 🎬 與影片腳本搭配

### 時間軸對應
- **0:00-0:20** - 標題頁面
- **0:20-0:50** - 專案概述
- **0:50-1:20** - 技術棧
- **1:20-1:50** - 系統架構
- **1:50-2:20** - 資料流程
- **2:20-3:50** - 一鍵啟動流程
- **3:50-4:20** - API 服務啟動
- **4:20-4:50** - Gradio 前端介面
- **4:50-5:50** - 現場互動測試
- **5:50-6:20** - 技術亮點
- **6:20-6:50** - 系統監控
- **6:50-7:20** - 核心優勢
- **7:20-7:50** - 未來發展
- **7:50-8:20** - 效能指標
- **8:20-8:50** - Demo 重點
- **8:50-9:10** - 結尾

### 同步建議
1. 在影片播放時同步切換投影片
2. 使用投影片作為影片的背景或補充
3. 在關鍵技術點暫停影片，詳細說明投影片內容

## 🔧 進階功能

### 自訂動畫
```markdown
<!-- _class: fade -->
# 淡入效果

<!-- _class: slide-up -->
# 滑入效果
```

### 背景圖片
```markdown
---
backgroundColor: #fff
backgroundImage: url('path/to/image.jpg')
---
```

### 程式碼高亮
```markdown
```python
def hello_world():
    print("Hello, World!")
```
```

## 📊 圖表支援

### Mermaid 圖表
```markdown
```mermaid
flowchart TB
    A[開始] --> B[處理]
    B --> C[結束]
```
```

### 數學公式
```markdown
$$
E = mc^2
$$
```

## 🎯 最佳實踐

### 內容組織
1. 每頁投影片專注於一個主題
2. 使用簡潔的標題和要點
3. 避免過多的文字內容
4. 善用圖表和視覺元素

### 設計原則
1. 保持一致的視覺風格
2. 使用適當的顏色對比
3. 確保文字可讀性
4. 支援無障礙設計

### 技術考量
1. 測試不同瀏覽器的相容性
2. 確保 PDF 輸出品質
3. 優化檔案大小
4. 備份重要檔案

## 🚨 故障排除

### 常見問題

**Q: Marp CLI 無法安裝**
```bash
# 檢查 Node.js 版本
node --version

# 使用管理員權限安裝
sudo npm install -g @marp-team/marp-cli
```

**Q: 圖表無法顯示**
```bash
# 確保已安裝 Mermaid 支援
npm install -g @marp-team/marp-cli-mermaid
```

**Q: 自訂 CSS 無效**
```bash
# 檢查配置檔案路徑
marp demo_slides.md --config-file ./marp.config.js
```

**Q: PDF 輸出失敗**
```bash
# 安裝 Chromium 依賴
npm install -g puppeteer
```

## 📞 支援

如需技術支援，請參考：
- [Marp 官方文檔](https://marp.app/)
- [Marp CLI GitHub](https://github.com/marp-team/marp-cli)
- 專案文檔和 README 檔案 