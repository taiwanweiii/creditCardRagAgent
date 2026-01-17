# 信用卡回饋 RAG Agent 🎯

智能信用卡推薦系統，使用 RAG（檢索增強生成）技術，根據消費場景推薦最適合的信用卡。

---

## 📋 目錄

- [功能特色](#-功能特色)
- [系統需求](#-系統需求)
- [快速開始](#-快速開始)
- [完整安裝教學](#-完整安裝教學)
- [使用方式](#-使用方式)
- [管理 API](#-管理-api)
- [更新信用卡資料](#-更新信用卡資料)
- [專案結構](#-專案結構)
- [技術棧](#️-技術棧)
- [常見問題](#-常見問題)

---

## 💡 功能特色

- ✅ **智能推薦** - 根據消費場景（加油、網購、餐廳等）推薦最佳信用卡
- ✅ **個人化管理** - 每位使用者管理自己持有的卡片
- ✅ **APP 切換提醒** - 自動提醒需要在銀行 APP 切換方案的卡片
- ✅ **Top 3 排名** - 顯示回饋由高到低的前三名推薦
- ✅ **RAG 技術** - 使用向量搜尋 + LLM 生成精準推薦
- ✅ **自動備份** - CSV 資料自動版本控制，保留最近 30 個版本
- ✅ **管理 API** - 支援遠端更新向量資料庫

---

## 📦 系統需求

- Python 3.10+
- Google Gemini API Key（必須）
- LINE Bot Channel（LINE Bot 模式需要）
- Docker（Docker 部署需要）

---

## 🚀 快速開始

### 方式一：5 分鐘快速測試（推薦新手）

不需要 LINE Bot，馬上可以試用！

```bash
# 1. 複製專案並進入目錄
cd creditCardRagAgent

# 2. 建立虛擬環境
python -m venv myenv
source myenv/bin/activate  # macOS/Linux
# myenv\Scripts\activate   # Windows

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 設定環境變數
cp .env.example .env
# 編輯 .env，填入 GOOGLE_API_KEY

# 5. 初始化向量資料庫
cd src
python init_db.py

# 6. 啟動命令列測試
python test_cli.py
```

### 方式二：Docker 一鍵部署（推薦生產環境）

```bash
# 1. 設定環境變數
cp .env.example .env
# 編輯 .env 填入所有必要的 API Keys

# 2. 啟動服務
docker-compose up -d

# 3. 查看日誌
docker-compose logs -f

# 4. 停止服務
docker-compose down
```

---

## 📖 完整安裝教學

### 步驟 1：取得 API Keys

#### Google Gemini API Key（必須）

1. 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 點擊「Create API Key」
3. 複製生成的 API Key

#### LINE Bot（LINE Bot 模式需要）

1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
2. 建立 Provider（如果沒有）
3. 建立 Messaging API Channel
4. 取得 **Channel Secret** 和 **Channel Access Token**

### 步驟 2：設定環境變數

編輯 `.env` 檔案：

```env
# ========== 必填 ==========
# Google Gemini API
GOOGLE_API_KEY=你的_Gemini_API_Key

# ========== LINE Bot 模式必填 ==========
LINE_CHANNEL_SECRET=你的_Channel_Secret
LINE_CHANNEL_ACCESS_TOKEN=你的_Access_Token

# ========== 生產環境必填 ==========
# 管理 API 金鑰（用於遠端更新資料庫）
ADMIN_API_KEY=設定一個強密碼

# ========== 選填（建議啟用）==========
# Google Drive 整合（自動下載最新 CSV）
GOOGLE_DRIVE_ENABLED=True
GOOGLE_DRIVE_FILE_ID=你的_Google_Drive_檔案ID

# ========== 進階設定 ==========
DEBUG=True
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./creditcard.db
CHROMA_PERSIST_DIRECTORY=./chroma_db
DATA_DIR=./data
BACKUP_DIR=./backups
MAX_BACKUPS=30
```

### 步驟 3：初始化系統

```bash
# 進入 src 目錄
cd src

# 初始化向量資料庫
python init_db.py
```

成功會看到：
```
📊 Vector Database Initialization
✅ Prepared 15 documents for RAG
✅ Vector store created and persisted
✅ Vector database initialization complete!
```

---

## 🎮 使用方式

### 🖥️ 方式一：命令列測試（test_cli.py）

適合快速測試和個人使用。

```bash
cd src
python test_cli.py
```

操作範例：
```
🤖 信用卡回饋 RAG 測試系統

請選擇操作:
1. 新增信用卡
2. 查詢回饋推薦
3. 查看持有卡片
4. 移除信用卡
5. 清除所有卡片
6. 退出

請輸入選項 (1-6): 1
請輸入信用卡名稱: 台新Richart卡
✅ 已新增「台新Richart卡」

請輸入選項 (1-6): 2
請輸入消費場景: 我要去加油

🏆 推薦加油卡片 Top 3:
1. 中國信託中油聯名卡 - 3%
   ✅ 無需切換
2. 台新Richart卡 - 2%
   ⚠️ 需在 APP 切換至「生活消費」
```

### 🌐 方式二：網頁測試（test_web.py）

適合需要圖形介面的使用者。

```bash
cd src
python test_web.py
```

然後打開瀏覽器：http://localhost:8000

### 📱 方式三：LINE Bot 正式模式

適合分享給朋友使用。

**啟動服務：**
```bash
cd src
python main.py
```

**設定 Webhook：**
1. 使用 ngrok 建立公開網址：`ngrok http 8000`
2. 在 LINE Developers Console 設定 Webhook URL：`https://xxx.ngrok.io/webhook`
3. 啟用 Webhook，關閉自動回覆

**LINE Bot 指令：**

| 指令 | 說明 | 範例 |
|------|------|------|
| `/start` | 查看歡迎訊息 | `/start` |
| `/help` | 查看使用說明 | `/help` |
| `/add [卡名]` | 新增信用卡 | `/add 台新Richart卡` |
| `/remove [卡名]` | 移除信用卡 | `/remove 台新Richart卡` |
| `/list` | 查看持有卡片 | `/list` |
| `/clear` | 清除所有卡片 | `/clear` |
| `[消費場景]` | 查詢推薦 | `我要去加油` |

**使用範例：**
```
使用者: /add 台新Richart卡
Bot: ✅ 已新增「台新Richart卡」，您現在有 1 張信用卡。

使用者: 網購要用哪張卡
Bot: 🏆 推薦網購卡片 Top 3:
     1. 台新Richart卡 - 3.5%
        ⚠️ 需在 APP 切換至「網購回饋」
        📅 優惠至 2024-12-31
```

---

## 🔐 管理 API

系統提供兩個管理端點，需要在 Header 中提供 `X-API-Key`。

### 端點 1：更新向量資料庫

**用途：** 當 Google Drive 上的 CSV 更新後，重新建立向量資料庫

**macOS/Linux：**
```bash
curl -X POST http://localhost:8000/admin/refresh-vectordb \
  -H "X-API-Key: 你的_ADMIN_API_KEY"
```

**Windows PowerShell：**
```powershell
curl.exe -X POST http://localhost:8000/admin/refresh-vectordb -H "X-API-Key: 你的_ADMIN_API_KEY"
```

**成功回應：**
```json
{
  "status": "success",
  "message": "Vector database refreshed successfully",
  "csv_filename": "信用卡資料模板_20260117_143022.csv",
  "documents_count": 15,
  "expired_cards_count": 0,
  "backup_count": 6
}
```

### 端點 2：查詢系統狀態

**macOS/Linux：**
```bash
curl http://localhost:8000/admin/status \
  -H "X-API-Key: 你的_ADMIN_API_KEY"
```

**回應範例：**
```json
{
  "status": "healthy",
  "rag_initialized": true,
  "vector_store_exists": true,
  "documents_in_vectordb": 15,
  "users_count": 3,
  "expired_cards_count": 0,
  "google_drive_enabled": true
}
```

### 端點 3：健康檢查（不需要 API Key）

```bash
curl http://localhost:8000/health
```

---

## 🔄 更新信用卡資料

### 方法一：透過 Google Drive（推薦）

**前置設定：**
1. 將 CSV 上傳到 Google Drive
2. 設定為「知道連結的任何人都可以檢視」
3. 在 `.env` 設定 `GOOGLE_DRIVE_ENABLED=True` 和 `GOOGLE_DRIVE_FILE_ID`

**更新流程：**
1. 在 Google Drive 編輯/替換 CSV 檔案
2. 呼叫管理 API：
   ```bash
   curl -X POST http://localhost:8000/admin/refresh-vectordb \
     -H "X-API-Key: 你的_ADMIN_API_KEY"
   ```

系統會自動：
- 📥 從 Google Drive 下載最新 CSV
- 💾 備份當前 CSV 到 `backups/` 目錄
- 📝 儲存新 CSV 到 `data/` 目錄（帶時間戳記）
- 🗑️ 清理超過 30 個的舊備份
- 🔄 重建向量資料庫

### 方法二：手動更新

```bash
cd src
python init_db.py
```

---

## 📂 專案結構

```
creditCardRagAgent/
├── src/                        # 原始碼
│   ├── main.py                # 主程式入口（LINE Bot 模式）
│   ├── line_bot.py            # LINE Bot 整合 + FastAPI 路由
│   ├── rag_engine.py          # RAG 推薦引擎
│   ├── vector_store.py        # ChromaDB 向量資料庫管理
│   ├── data_processor.py      # CSV 資料處理
│   ├── user_manager.py        # 使用者資料管理（SQLAlchemy）
│   ├── file_manager.py        # CSV 檔案版本管理
│   ├── config.py              # 設定管理
│   ├── prompt_templates.py    # LLM 提示詞模板
│   ├── google_drive_downloader.py  # Google Drive 下載工具
│   ├── init_db.py             # 向量資料庫初始化腳本
│   ├── test_cli.py            # 命令列測試介面
│   └── test_web.py            # 網頁測試介面
│
├── data/                       # 當前使用的 CSV 檔案（1 個最新版本）
│   └── 信用卡資料模板_YYYYMMDD_HHMMSS.csv
│
├── backups/                    # 歷史版本備份（最多 30 個）
│   └── 信用卡資料模板_YYYYMMDD_HHMMSS.csv
│
├── chroma_db/                  # ChromaDB 向量資料庫
├── tests/                      # 測試檔案
├── .env                        # 環境變數設定（不納入版本控制）
├── .env.example                # 環境變數範例
├── docker-compose.yml          # Docker Compose 配置
├── Dockerfile                  # Docker 映像檔配置
├── requirements.txt            # Python 依賴
└── README.md                   # 本文件
```

---

## 🛠️ 技術棧

| 類別 | 技術 |
|------|------|
| **後端框架** | Python 3.11 / FastAPI |
| **RAG 框架** | LangChain |
| **向量資料庫** | ChromaDB |
| **嵌入模型** | sentence-transformers (多語言) |
| **LLM** | Google Gemini 2.5 Flash |
| **LINE Bot** | line-bot-sdk |
| **資料庫** | SQLite + SQLAlchemy |
| **容器化** | Docker + Docker Compose |

---

## ❓ 常見問題

### Q1: 初始化時找不到 CSV 檔案

**錯誤訊息：** `FileNotFoundError: 找不到 CSV 檔案於 ./data`

**解決方案：**
1. 確認 `data/` 目錄存在且有 CSV 檔案
2. 或啟用 Google Drive，讓系統自動下載

### Q2: Google API 額度用完

**錯誤訊息：** `API 額度已用盡`

**解決方案：**
1. 等待第二天額度重置（免費版每日限制）
2. 申請新的 Google API Key
3. 升級到付費方案

### Q3: LINE Bot 沒有回應

**檢查清單：**
1. 確認服務運行中：`curl http://localhost:8000/health`
2. 確認 Webhook URL 設定正確
3. 確認已啟用 Webhook，關閉自動回覆
4. 查看日誌：`docker-compose logs -f` 或終端機輸出

### Q4: 更新資料庫時出現錯誤

**錯誤訊息：** `更新向量資料庫需要啟用 Google Drive`

**解決方案：**
在 `.env` 設定：
```env
GOOGLE_DRIVE_ENABLED=True
GOOGLE_DRIVE_FILE_ID=你的檔案ID
```

### Q5: 測試該從哪個目錄執行？

**答案：**
- 執行測試：從專案根目錄 `python -m pytest tests/ -v`
- 執行程式：從 `src/` 目錄 `python main.py`

---

## 📖 詳細文件

- [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - Docker 部署與管理完整指南
- [TEST_GUIDE.md](TEST_GUIDE.md) - 測試功能說明
- [VENV_GUIDE.md](VENV_GUIDE.md) - 虛擬環境設定
- [GOOGLE_DRIVE_設定.md](GOOGLE_DRIVE_設定.md) - Google Drive 整合設定

---

## 📝 授權

MIT License

---

## 🎯 使用流程總覽

```
┌─────────────────────────────────────────────────────────────────┐
│                    信用卡回饋 RAG Agent                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 設定環境                                                    │
│     └─→ 編輯 .env 填入 API Keys                                │
│                                                                 │
│  2. 初始化                                                      │
│     └─→ python init_db.py                                      │
│                                                                 │
│  3. 選擇使用方式                                                │
│     ├─→ 快速測試: python test_cli.py                           │
│     ├─→ 網頁測試: python test_web.py                           │
│     ├─→ LINE Bot: python main.py                               │
│     └─→ Docker:   docker-compose up -d                         │
│                                                                 │
│  4. 更新資料（定期）                                            │
│     └─→ curl -X POST .../admin/refresh-vectordb                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

開始使用吧！🚀

如有問題，歡迎提出 Issue。
