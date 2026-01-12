# 信用卡回饋 RAG Agent

## 🎯 兩種使用模式

### 🧪 測試模式 (不需要 LINE Bot)
適合開發測試,提供 CLI 和 Web UI 介面

### 📱 正式模式 (LINE Bot)
適合正式上線,透過 LINE 提供服務

---

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

建立 `.env` 檔案:

```env
# 必填 (測試模式和正式模式都需要)
GOOGLE_API_KEY=your_google_gemini_api_key

# 選填 (只有正式 LINE Bot 模式需要)
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
```

### 3. 初始化資料庫

```bash
cd src
python init_db.py
```

---

## 🧪 測試模式 (推薦先測試)

### 方式 1: 命令列介面

```bash
cd src
python test_cli.py
```

### 方式 2: 網頁介面

```bash
cd src
python test_web.py
# 開啟瀏覽器: http://localhost:8000
```

**詳細測試指南**: 請參考 [TEST_GUIDE.md](TEST_GUIDE.md)

---

## 📱 正式模式 (LINE Bot)

### 啟動 LINE Bot

```bash
cd src
python main.py
```

### 5. 測試 (使用 ngrok)

```bash
# 另開一個終端機
ngrok http 8000

# 將 ngrok 提供的 URL 設定到 LINE Developers Console
# Webhook URL: https://your-ngrok-url.ngrok-free.app/webhook
```

---

## 📱 LINE Bot 使用方式

### 管理信用卡

```
/add 台新Richart卡      # 新增信用卡
/remove 台新Richart卡   # 移除信用卡
/list                  # 查看持有卡片
```

### 查詢推薦

```
我要去加油
網購要用哪張卡
餐廳吃飯推薦
```

---

## 📂 專案結構

```
creditCard/
├── src/
│   ├── config.py           # 設定管理
│   ├── data_processor.py   # 資料處理
│   ├── vector_store.py     # 向量資料庫
│   ├── rag_engine.py       # RAG 查詢引擎
│   ├── user_manager.py     # 使用者管理
│   ├── line_bot.py         # LINE Bot 整合
│   ├── prompt_templates.py # 提示詞模板
│   ├── main.py            # 主程式
│   └── init_db.py         # 資料庫初始化
├── tests/
│   └── test_data_processor.py
├── 信用卡資料模板.csv      # 信用卡資料
├── requirements.txt       # Python 依賴
├── .env.example          # 環境變數範本
├── Dockerfile            # Docker 設定
├── README.md             # 專案說明
└── DEPLOYMENT.md         # 部署指南
```

---

## 🔑 取得 API Keys

### Google Gemini API Key

1. 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 點擊 "Create API Key"
3. 複製 API Key

### LINE Bot Credentials

1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
2. 建立 Messaging API Channel
3. 取得 Channel Secret 和 Channel Access Token

---

## 📖 詳細文件

- [部署指南](DEPLOYMENT.md) - 完整的部署說明
- [實作計畫](implementation_plan.md) - 技術架構和設計

---

## 💡 功能特色

✅ 智能推薦 - 根據消費場景推薦最佳信用卡  
✅ 個人化管理 - 每位使用者管理自己的卡片  
✅ APP 切換提醒 - 自動提醒需要切換方案的卡片  
✅ Top 3 排名 - 顯示回饋由高到低的前三名  
✅ RAG 技術 - 使用向量搜尋和 LLM 生成推薦  

---

## 🛠️ 技術棧

- **Backend**: Python 3.10+ / FastAPI
- **RAG**: LangChain + ChromaDB
- **LLM**: Google Gemini API
- **LINE Bot**: line-bot-sdk
- **Database**: SQLite

---

## 📝 授權

MIT License

---

## 🎯 下一步

1. 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 了解部署選項
2. 自訂 `信用卡資料模板.csv` 新增更多信用卡
3. 調整 `prompt_templates.py` 自訂回覆格式
4. 部署到雲端服務

開始使用吧! 🚀
