# 信用卡回饋 RAG Agent - 部署指南

## 📋 前置準備

### 1. 安裝 Python 依賴套件

```bash
cd d:\creditCard
pip install -r requirements.txt
```

### 2. 設定環境變數

複製 `.env.example` 為 `.env`:

```bash
copy .env.example .env
```

編輯 `.env` 檔案,填入您的 API Keys:

```env
# Google Gemini API (必填)
GOOGLE_API_KEY=your_google_gemini_api_key_here

# LINE Bot Configuration (必填,用於 LINE Bot 功能)
LINE_CHANNEL_SECRET=your_line_channel_secret_here
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here

# Database (可選,預設使用 SQLite)
DATABASE_URL=sqlite:///./creditcard.db

# Application Settings
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### 3. 初始化向量資料庫

```bash
cd src
python init_db.py
```

這會從 `信用卡資料模板.csv` 建立向量資料庫。

---

## 🚀 本地測試

### 方法 1: 直接執行

```bash
cd src
python main.py
```

伺服器會在 `http://localhost:8000` 啟動。

### 方法 2: 使用 uvicorn

```bash
cd src
uvicorn main:bot.get_app() --host 0.0.0.0 --port 8000 --reload
```

### 測試 API

1. **健康檢查**:
   ```
   http://localhost:8000/health
   ```

2. **Webhook 測試**:
   ```
   http://localhost:8000/webhook
   ```

---

## 📱 LINE Bot 設定

### 1. 建立 LINE Bot

1. 前往 [LINE Developers Console](https://developers.line.biz/console/)
2. 建立新的 Provider (如果還沒有)
3. 建立 Messaging API Channel
4. 取得以下資訊:
   - **Channel Secret**: 在 "Basic settings" 頁面
   - **Channel Access Token**: 在 "Messaging API" 頁面,點擊 "Issue" 按鈕

### 2. 設定 Webhook URL

#### 本地測試 (使用 ngrok)

1. **安裝 ngrok**:
   - 下載: https://ngrok.com/download
   - 解壓縮到任意位置

2. **啟動 ngrok**:
   ```bash
   ngrok http 8000
   ```

3. **取得公開 URL**:
   - ngrok 會顯示類似 `https://xxxx-xx-xx-xx-xx.ngrok-free.app` 的網址
   - 複製這個網址

4. **設定 LINE Webhook**:
   - 在 LINE Developers Console 的 "Messaging API" 頁面
   - Webhook URL 設定為: `https://your-ngrok-url.ngrok-free.app/webhook`
   - 啟用 "Use webhook"
   - 點擊 "Verify" 測試連線

### 3. 其他 LINE Bot 設定

在 "Messaging API" 頁面:
- **Auto-reply messages**: 停用 (Disabled)
- **Greeting messages**: 可選
- **Allow bot to join group chats**: 依需求設定

---

## ☁️ 雲端部署

### 選項 1: Heroku

1. **安裝 Heroku CLI**:
   ```bash
   # 下載並安裝 Heroku CLI
   # https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **建立 Procfile**:
   ```bash
   echo "web: cd src && uvicorn main:bot.get_app() --host 0.0.0.0 --port $PORT" > Procfile
   ```

3. **部署**:
   ```bash
   heroku login
   heroku create your-app-name
   heroku config:set GOOGLE_API_KEY=your_key
   heroku config:set LINE_CHANNEL_SECRET=your_secret
   heroku config:set LINE_CHANNEL_ACCESS_TOKEN=your_token
   git push heroku main
   ```

4. **設定 LINE Webhook**:
   ```
   https://your-app-name.herokuapp.com/webhook
   ```

### 選項 2: Google Cloud Run

1. **建立 Dockerfile** (已包含在專案中)

2. **部署**:
   ```bash
   gcloud run deploy creditcard-bot \
     --source . \
     --platform managed \
     --region asia-east1 \
     --allow-unauthenticated \
     --set-env-vars GOOGLE_API_KEY=your_key,LINE_CHANNEL_SECRET=your_secret,LINE_CHANNEL_ACCESS_TOKEN=your_token
   ```

3. **設定 LINE Webhook**:
   ```
   https://creditcard-bot-xxxxx-xx.a.run.app/webhook
   ```

### 選項 3: AWS Lambda (進階)

需要使用 Mangum 將 FastAPI 轉換為 Lambda handler。

---

## 🧪 測試 LINE Bot

### 1. 加入好友

在 LINE Developers Console 的 "Messaging API" 頁面,掃描 QR Code 加入 Bot 為好友。

### 2. 測試指令

```
/start          # 查看歡迎訊息
/help           # 查看說明
/add 台新Richart卡    # 新增信用卡
/list           # 查看持有卡片
我要去加油        # 查詢推薦
```

### 3. 預期回覆

Bot 應該會回覆推薦的信用卡清單,包含回饋率和 APP 切換提醒。

---

## 🔧 維護與更新

### 更新信用卡資料

1. 編輯 `信用卡資料模板.csv`
2. 重新初始化向量資料庫:
   ```bash
   cd src
   python init_db.py
   ```
3. 重啟服務

### 查看日誌

```bash
# 本地
# 直接在終端機查看

# Heroku
heroku logs --tail

# Google Cloud Run
gcloud run logs read creditcard-bot --limit 50
```

### 備份資料庫

```bash
# SQLite 資料庫
copy creditcard.db creditcard.db.backup

# 向量資料庫
xcopy /E /I chroma_db chroma_db_backup
```

---

## ❓ 常見問題

### Q1: 向量資料庫初始化失敗

**A**: 檢查 `GOOGLE_API_KEY` 是否正確設定。

### Q2: LINE Bot 無法回覆

**A**: 
1. 檢查 Webhook URL 是否正確
2. 檢查 LINE Channel Secret 和 Access Token
3. 查看伺服器日誌確認錯誤訊息

### Q3: 推薦結果不準確

**A**: 
1. 確認 CSV 資料格式正確
2. 重新初始化向量資料庫
3. 調整 `rag_engine.py` 中的 `top_k` 參數

### Q4: ngrok 連線中斷

**A**: ngrok 免費版會在 2 小時後中斷,需要重新啟動並更新 LINE Webhook URL。建議升級到付費版或部署到雲端。

---

## 📞 技術支援

如有問題,請檢查:
1. 環境變數設定
2. API Key 額度
3. 伺服器日誌
4. LINE Developers Console 的錯誤訊息

---

## 🎉 完成!

您的信用卡回饋 RAG Agent 已經準備就緒!

開始使用 LINE Bot 查詢最划算的信用卡吧! 💳✨
