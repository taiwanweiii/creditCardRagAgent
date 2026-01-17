# Docker 部署與管理指南

本指南說明如何使用 Docker 和 Docker Compose 部署信用卡 RAG Agent,以及如何使用管理 API。

---

## 📋 前置需求

- Docker (版本 20.10+)
- Docker Compose (版本 2.0+)
- `.env` 檔案 (從 `.env.example` 複製並填入真實資料)

---

## 🚀 快速開始

### 1. 準備環境變數

```bash
# 複製範例檔案
cp .env.example .env

# 編輯 .env 並填入真實資料
# 必填項目:
# - GOOGLE_API_KEY
# - LINE_CHANNEL_SECRET
# - LINE_CHANNEL_ACCESS_TOKEN
# - ADMIN_API_KEY (請使用強密碼)
```

### 2. 建置並啟動服務

```bash
# 建置 Docker 映像檔
docker-compose build

# 啟動服務 (背景執行)
docker-compose up -d

# 查看日誌
docker-compose logs -f
```

### 3. 驗證服務運行

```bash
# 檢查健康狀態
curl http://localhost:8000/health

# 預期回應:
# {
#   "status": "healthy",
#   "rag_initialized": true,
#   "users_count": 0
# }
```

---

## 🔧 常用指令

### 服務管理

```bash
# 啟動服務
docker-compose up -d

# 停止服務
docker-compose down

# 重啟服務 (修改 .env 後使用)
docker-compose restart

# 查看服務狀態
docker-compose ps

# 查看即時日誌
docker-compose logs -f

# 停止並刪除所有資料 (包含 volumes)
docker-compose down -v
```

### 重新建置

```bash
# 修改程式碼後重新建置
docker-compose build

# 強制重新建置 (不使用快取)
docker-compose build --no-cache

# 重新建置並啟動
docker-compose up -d --build
```

---

## 🔐 管理 API 使用

### API 認證

所有管理端點需要在 HTTP Header 中提供 API Key:

```
X-API-Key: your_admin_api_key
```

### 端點 1: 更新向量資料庫

**用途:** 當 CSV 資料更新後,重新建立向量資料庫

**請求:**
```bash
curl -X POST http://localhost:8000/admin/refresh-vectordb \
  -H "X-API-Key: your_admin_api_key"
```

**回應範例:**
```json
{
  "status": "success",
  "message": "Vector database refreshed successfully",
  "documents_count": 150,
  "expired_cards_count": 2
}
```

**功能:**
1. 如果啟用 Google Drive,自動下載最新 CSV
2. 重新載入信用卡資料
3. 刪除舊的向量資料庫
4. 建立新的向量資料庫
5. 重新初始化 RAG 引擎

### 端點 2: 查詢系統狀態

**用途:** 獲取系統詳細狀態資訊

**請求:**
```bash
curl http://localhost:8000/admin/status \
  -H "X-API-Key: your_admin_api_key"
```

**回應範例:**
```json
{
  "status": "healthy",
  "rag_initialized": true,
  "vector_store_exists": true,
  "documents_in_vectordb": 150,
  "users_count": 5,
  "expired_cards_count": 2,
  "expired_cards": ["卡片A", "卡片B"],
  "google_drive_enabled": true,
  "debug_mode": false
}
```

---

## 💾 資料持久化

### Volume 掛載

Docker Compose 會自動掛載以下目錄/檔案:

```yaml
volumes:
  - ./chroma_db:/app/chroma_db                    # 向量資料庫
  - ./src/creditcard.db:/app/src/creditcard.db    # SQLite 資料庫
  - ./data:/app/data                              # CSV 資料目錄
  - ./backups:/app/backups                        # CSV 備份目錄
```

### 資料備份

```bash
# 備份向量資料庫
tar -czf chroma_db_backup_$(date +%Y%m%d).tar.gz chroma_db/

# 備份 SQLite 資料庫
cp src/creditcard.db creditcard_backup_$(date +%Y%m%d).db

# CSV 備份由系統自動管理於 backups/ 目錄
```

### 資料還原

```bash
# 停止服務
docker-compose down

# 還原資料
tar -xzf chroma_db_backup_20260113.tar.gz
cp creditcard_backup_20260113.db src/creditcard.db

# 重新啟動
docker-compose up -d
```

---

## 🔄 更新工作流程

### 情境 1: 修改環境變數

```bash
# 1. 編輯 .env 檔案
nano .env

# 2. 重啟服務 (不需要重新建置)
docker-compose restart
```

### 情境 2: 更新信用卡資料

**方法 A: 使用管理 API (推薦)**
```bash
# 1. 更新 CSV 檔案或確保 Google Drive 有最新資料
# 2. 呼叫更新 API
curl -X POST http://localhost:8000/admin/refresh-vectordb \
  -H "X-API-Key: your_admin_api_key"
```

**方法 B: 手動執行**
```bash
# 1. 進入容器
docker-compose exec credit-card-bot bash

# 2. 執行初始化腳本
python init_db.py

# 3. 退出容器
exit

# 4. 重啟服務
docker-compose restart
```

### 情境 3: 更新程式碼

```bash
# 1. 修改程式碼
# 2. 重新建置並啟動
docker-compose up -d --build
```

---

## 🐛 疑難排解

### 問題 1: 容器無法啟動

```bash
# 查看詳細日誌
docker-compose logs

# 檢查環境變數
docker-compose config
```

### 問題 2: 向量資料庫初始化失敗

```bash
# 刪除舊的向量資料庫
rm -rf chroma_db/

# 重新啟動服務
docker-compose restart

# 或使用管理 API 重新初始化
curl -X POST http://localhost:8000/admin/refresh-vectordb \
  -H "X-API-Key: your_admin_api_key"
```

### 問題 3: 端口被佔用

```bash
# 修改 .env 中的 PORT
PORT=8001

# 重啟服務
docker-compose restart
```

### 問題 4: 權限問題

```bash
# 修正檔案權限
chmod -R 755 chroma_db/
chmod 644 src/creditcard.db
```

---

## 🔒 安全性建議

1. **保護 API Key**
   - 使用強密碼作為 `ADMIN_API_KEY`
   - 不要將 `.env` 提交到版本控制
   - 定期更換 API Key

2. **網路安全**
   - 在生產環境使用反向代理 (nginx)
   - 啟用 HTTPS
   - 限制管理端點的 IP 存取

3. **資料備份**
   - 定期備份資料庫
   - 使用 cron job 自動化備份

---

## 📊 監控與日誌

### 查看日誌

```bash
# 即時日誌
docker-compose logs -f

# 最近 100 行日誌
docker-compose logs --tail=100

# 特定服務日誌
docker-compose logs credit-card-bot
```

### 資源使用

```bash
# 查看容器資源使用
docker stats

# 查看磁碟使用
docker system df
```

---

## 🌐 生產環境部署

### 使用 nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 限制管理端點存取
    location /admin/ {
        allow 192.168.1.0/24;  # 允許的 IP 範圍
        deny all;
        proxy_pass http://localhost:8000;
    }
}
```

### 環境變數設定

```bash
# 生產環境 .env 範例
DEBUG=False
HOST=0.0.0.0
PORT=8000
ADMIN_API_KEY=use_very_strong_password_here
```

---

## 📝 附註

- 首次啟動時,如果向量資料庫不存在,系統會自動建立
- 修改 `.env` 後只需重啟,不需要重新建置
- 資料持久化在本地,刪除容器不會遺失資料
- 使用 `docker-compose down -v` 會刪除所有資料,請謹慎使用
