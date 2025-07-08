# Docker 部署與維護文檔

## 📋 目錄
- [環境需求](#環境需求)
- [容器化架構](#容器化架構)
- [部署與執行](#部署與執行)
- [故障排除](#故障排除)
- [版本管理](#版本管理)
- [最佳實踐](#最佳實踐)

---

## 🖥️ 環境需求

### 系統要求
- **Docker**: 版本 20.10 或更高
- **Docker Compose**: 版本 2.0 或更高
- **記憶體**: 最少 2GB RAM
- **磁碟空間**: 最少 1GB 可用空間
- **網路**: 需要網際網路連線以安裝依賴套件

### 驗證安裝
```bash
# 檢查 Docker 版本
docker --version

# 檢查 Docker Compose 版本
docker-compose --version

# 檢查 Docker 服務狀態
docker info
```

---

## 🏗️ 容器化架構

### Dockerfile 詳細解析

#### 基礎映像選擇
```dockerfile
FROM python:3.11-slim
```
- **選擇原因**: Python 3.11 提供良好的效能與穩定性
- **slim 版本**: 減少映像大小，提高安全性

#### 系統依賴安裝
```dockerfile
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*
```
- **gcc/g++**: 編譯某些 Python 套件所需
- **git**: 某些套件可能需要從 Git 安裝
- **清理快取**: 減少映像大小

#### 安全性設定
```dockerfile
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app
```
- **非 root 使用者**: 提高容器安全性
- **最小權限原則**: 避免以 root 身份執行應用程式

#### 健康檢查機制
```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```
- **檢查間隔**: 每 30 秒檢查一次
- **超時設定**: 30 秒內必須回應
- **啟動寬限期**: 容器啟動後 5 秒開始檢查
- **重試次數**: 失敗 3 次後標記為不健康

### docker-compose.yml 配置說明

#### 服務定義
```yaml
services:
  aiops-api:
    build: .
    ports:
      - "8000:8000"
```
- **服務名稱**: `aiops-api`
- **端口映射**: 主機 8000 端口映射到容器 8000 端口

#### 環境變數配置
```yaml
environment:
  - GOOGLE_API_KEY=${GOOGLE_API_KEY}
  - GEMINI_MODEL=${GEMINI_MODEL:-gemini-1.5-pro}
  - GEMINI_TEMPERATURE=${GEMINI_TEMPERATURE:-0.1}
  - GEMINI_MAX_TOKENS=${GEMINI_MAX_TOKENS:-500}
  - API_HOST=0.0.0.0
  - API_PORT=8000
  - KNOWLEDGE_FILE=${KNOWLEDGE_FILE:-summary.txt}
  - LOG_LEVEL=${LOG_LEVEL:-INFO}
```
- **必要變數**: `GOOGLE_API_KEY`（必須設定）
- **可選變數**: 其他變數都有預設值
- **API 設定**: 綁定到所有網路介面（0.0.0.0）

#### 檔案掛載策略
```yaml
volumes:
  - ./summary.txt:/app/summary.txt:ro
  - ./knowledgebase.txt:/app/knowledgebase.txt:ro
```
- **唯讀掛載**: 知識庫檔案以唯讀方式掛載
- **即時更新**: 修改主機檔案可即時反映到容器

#### 健康檢查配置
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```
- **檢查端點**: `/health` 健康檢查端點
- **重啟策略**: `unless-stopped` 自動重啟

---

## 🚀 部署與執行

### 本地開發環境

#### 快速啟動
```bash
# 建立並啟動服務
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f aiops-api
```

#### 環境變數設定
1. 複製環境變數範例檔案：
   ```bash
   cp env.example .env
   ```

2. 編輯 `.env` 檔案，設定必要的 API Key：
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   GEMINI_MODEL=gemini-1.5-pro
   GEMINI_TEMPERATURE=0.1
   GEMINI_MAX_TOKENS=500
   ```

#### 常用命令
```bash
# 停止服務
docker-compose down

# 重新建置映像
docker-compose build --no-cache

# 重新啟動服務
docker-compose restart

# 進入容器
docker-compose exec aiops-api bash

# 查看容器資源使用
docker stats
```

### 生產環境部署

#### 環境變數最佳實踐
```env
# 必要設定
GOOGLE_API_KEY=your_production_api_key

# 模型設定
GEMINI_MODEL=gemini-1.5-pro
GEMINI_TEMPERATURE=0.1
GEMINI_MAX_TOKENS=500

# 應用程式設定
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# 知識庫設定
KNOWLEDGE_FILE=summary.txt
```

#### 網路配置
```yaml
# 自定義網路（可選）
networks:
  aiops-network:
    driver: bridge

services:
  aiops-api:
    networks:
      - aiops-network
```

#### 監控與日誌
```bash
# 查看即時日誌
docker-compose logs -f --tail=100 aiops-api

# 查看健康檢查狀態
docker-compose ps

# 監控資源使用
docker stats aiops-api
```

---

## 🔧 故障排除

### 常見問題與解決方案

#### 1. 容器無法啟動
**症狀**: `docker-compose up` 失敗
**可能原因**:
- 環境變數未設定
- 端口被佔用
- 映像建置失敗

**解決方案**:
```bash
# 檢查環境變數
cat .env

# 檢查端口使用
netstat -tulpn | grep 8000

# 重新建置映像
docker-compose build --no-cache
```

#### 2. API 無法回應
**症狀**: 健康檢查失敗
**可能原因**:
- Google API Key 無效
- 網路連線問題
- 應用程式錯誤

**解決方案**:
```bash
# 檢查容器日誌
docker-compose logs aiops-api

# 進入容器檢查
docker-compose exec aiops-api bash

# 測試 API Key
curl -X GET "http://localhost:8000/health"
```

#### 3. 記憶體不足
**症狀**: 容器頻繁重啟
**解決方案**:
```bash
# 增加 Docker 記憶體限制
# 在 Docker Desktop 設定中調整

# 或使用 docker-compose 限制
services:
  aiops-api:
    deploy:
      resources:
        limits:
          memory: 2G
```

#### 4. 知識庫檔案問題
**症狀**: 問答功能異常
**解決方案**:
```bash
# 檢查檔案掛載
docker-compose exec aiops-api ls -la /app/

# 重新掛載檔案
docker-compose down
docker-compose up -d
```

### 日誌分析

#### 日誌級別
- **DEBUG**: 詳細除錯資訊
- **INFO**: 一般資訊
- **WARNING**: 警告訊息
- **ERROR**: 錯誤訊息

#### 關鍵日誌模式
```bash
# 查看錯誤日誌
docker-compose logs aiops-api | grep ERROR

# 查看 API 請求日誌
docker-compose logs aiops-api | grep "API request"

# 查看健康檢查日誌
docker-compose logs aiops-api | grep health
```

---

## 📦 版本管理

### 映像版本標籤策略
```bash
# 建置特定版本
docker build -t aiops-api:v1.0.0 .

# 使用 git commit hash
docker build -t aiops-api:$(git rev-parse --short HEAD) .

# 標籤為最新版本
docker tag aiops-api:v1.0.0 aiops-api:latest
```

### 依賴更新流程
1. **更新 requirements.txt**
2. **重新建置映像**
3. **測試新版本**
4. **部署到生產環境**

```bash
# 更新依賴
pip freeze > requirements.txt

# 重新建置
docker-compose build --no-cache

# 測試
docker-compose up -d
curl http://localhost:8000/health
```

### 向後相容性
- **API 端點**: 保持向後相容
- **環境變數**: 新增變數時提供預設值
- **資料格式**: 保持知識庫格式相容

---

## 🛡️ 最佳實踐

### 安全性
- ✅ 使用非 root 使用者執行
- ✅ 唯讀掛載知識庫檔案
- ✅ 定期更新基礎映像
- ✅ 使用環境變數管理敏感資訊
- ✅ 啟用健康檢查

### 效能優化
- ✅ 使用多階段建置（如需要）
- ✅ 清理不必要的檔案
- ✅ 設定適當的記憶體限制
- ✅ 使用 .dockerignore 排除檔案

### 監控與維護
- ✅ 定期檢查容器健康狀態
- ✅ 監控資源使用情況
- ✅ 備份重要資料
- ✅ 記錄部署和變更日誌

### 災難恢復
```bash
# 備份重要檔案
cp .env .env.backup
cp docker-compose.yml docker-compose.yml.backup

# 恢復服務
docker-compose down
docker-compose up -d

# 驗證恢復
curl http://localhost:8000/health
```

---

## 📚 參考資源

- [Docker 官方文檔](https://docs.docker.com/)
- [Docker Compose 文檔](https://docs.docker.com/compose/)
- [Python Docker 最佳實踐](https://docs.docker.com/language/python/)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)

---

## 📞 支援

如遇到問題，請：
1. 檢查本文件的故障排除章節
2. 查看容器日誌：`docker-compose logs aiops-api`
3. 確認環境變數設定
4. 驗證網路連線狀態
