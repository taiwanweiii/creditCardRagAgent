# 信用卡回饋 RAG Agent 🎯

智能信用卡推薦系統,使用 RAG 技術根據消費場景推薦最佳信用卡。

## 🚀 快速開始

### 使用 Docker (推薦)

```bash
# 1. 設定環境變數
cp .env.example .env
# 編輯 .env 填入 API Keys

# 2. 啟動服務
docker-compose up -d

# 3. 查看日誌
docker-compose logs -f
```

詳細說明請參考 [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

### 本地開發

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 設定環境變數
cp .env.example .env
# 編輯 .env 填入必要的 API Keys

# 3. 初始化向量資料庫
cd src
python init_db.py

# 4. 啟動服務
python main.py
```

---

## 🧪 測試模式

不需要 LINE Bot 設定,快速測試功能:

### 命令列介面
```bash
cd src
python test_cli.py
```

### 網頁介面
```bash
cd src
python test_web.py
# 開啟瀏覽器: http://localhost:8000
```

詳細測試說明請參考 [TEST_GUIDE.md](TEST_GUIDE.md)

---

## 📱 LINE Bot 使用

### 管理信用卡
```
/add 台新Richart卡      # 新增信用卡
/remove 台新Richart卡   # 移除信用卡
/list                  # 查看持有卡片
/clear                 # 清除所有卡片
```

### 查詢推薦
```
我要去加油
網購要用哪張卡
餐廳吃飯推薦
```

---

## 🔐 管理 API

更新向量資料庫 (當信用卡資料更新時):

```bash
# Windows PowerShell
curl.exe -X POST http://localhost:8000/admin/refresh-vectordb -H "X-API-Key: your_api_key"

# 查詢系統狀態
curl.exe http://localhost:8000/admin/status -H "X-API-Key: your_api_key"
```

---

## 🔑 環境變數設定

必填項目 (在 `.env` 中設定):

```env
# Google Gemini API (必填)
GOOGLE_API_KEY=your_gemini_api_key

# LINE Bot (正式模式必填)
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token

# 管理 API (生產環境必填)
ADMIN_API_KEY=your_strong_password

# Google Drive 整合 (選填)
GOOGLE_DRIVE_ENABLED=True
GOOGLE_DRIVE_FILE_ID=your_file_id
```

### 取得 API Keys

- **Google Gemini**: [Google AI Studio](https://makersuite.google.com/app/apikey)
- **LINE Bot**: [LINE Developers Console](https://developers.line.biz/console/)

---

## 💡 功能特色

- ✅ **智能推薦** - 根據消費場景推薦最佳信用卡
- ✅ **個人化管理** - 每位使用者管理自己的卡片
- ✅ **APP 切換提醒** - 自動提醒需要切換方案的卡片
- ✅ **Top 3 排名** - 顯示回饋由高到低的前三名
- ✅ **RAG 技術** - 使用向量搜尋和 LLM 生成推薦
- ✅ **管理 API** - 遠端更新向量資料庫

---

## 🛠️ 技術棧

- **Backend**: Python 3.10+ / FastAPI
- **RAG**: LangChain + ChromaDB
- **LLM**: Google Gemini 2.5 Flash
- **LINE Bot**: line-bot-sdk
- **Database**: SQLite
- **Container**: Docker + Docker Compose

---

## 📂 專案結構

```
creditCard/
├── src/                    # 原始碼
│   ├── main.py            # 主程式入口
│   ├── line_bot.py        # LINE Bot 整合
│   ├── rag_engine.py      # RAG 推薦引擎
│   ├── vector_store.py    # 向量資料庫
│   ├── config.py          # 設定管理
│   └── ...
├── 信用卡資料模板.csv      # 信用卡資料
├── docker-compose.yml     # Docker Compose 配置
├── Dockerfile            # Docker 映像檔
├── requirements.txt      # Python 依賴
├── .env.example         # 環境變數範例
├── README.md            # 本文件
├── DOCKER_GUIDE.md      # Docker 詳細指南
└── TEST_GUIDE.md        # 測試指南
```

---

## 📖 詳細文件

- [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - Docker 部署與管理完整指南
- [TEST_GUIDE.md](TEST_GUIDE.md) - 測試功能說明
- [VENV_GUIDE.md](VENV_GUIDE.md) - 虛擬環境設定
- [GOOGLE_DRIVE_設定.md](GOOGLE_DRIVE_設定.md) - Google Drive 整合設定

---

## 🔄 更新資料流程

### 方法 1: 使用管理 API (推薦)

```bash
# 1. 更新 CSV 檔案或 Google Drive 資料
# 2. 呼叫更新 API
curl.exe -X POST http://localhost:8000/admin/refresh-vectordb -H "X-API-Key: your_api_key"
```

### 方法 2: 手動執行

```bash
cd src
python init_db.py
```

---

## 🎯 使用場景

1. **快速測試** → 使用 `test_cli.py` 或 `test_web.py`
2. **本地開發** → 使用 `python main.py` + ngrok
3. **Docker 部署** → 使用 `docker-compose up -d`
4. **更新資料** → 使用管理 API `/admin/refresh-vectordb`

---

## 📝 授權

MIT License

---

開始使用吧! 🚀
