# 🚀 Git 上傳與部署指南

## 📋 前置檢查

在上傳到 Git 之前,確認以下事項:

### ✅ 確認 .gitignore 設定正確
已經設定好忽略敏感資料和不必要的檔案:
- `.env` (包含 API Keys,**絕對不能上傳**)
- `venv/` (虛擬環境)
- `*.db` (資料庫檔案)
- `chroma_db/` (向量資料庫)
- `__pycache__/` (Python 快取)

### ⚠️ 重要提醒
**絕對不要上傳以下檔案:**
- `.env` - 包含你的 Google API Key 和 LINE Bot 憑證
- `creditcard.db` - 使用者資料
- `chroma_db/` - 向量資料庫

---

## 🔧 Git 上傳流程

### 步驟 1: 初始化 Git 儲存庫 (如果還沒有)

```bash
cd d:\creditCard
git init
```

### 步驟 2: 檢查要上傳的檔案

```bash
# 查看哪些檔案會被上傳
git status

# 確認 .env 和敏感資料不在列表中
```

### 步驟 3: 加入檔案到 Git

```bash
# 加入所有檔案 (.gitignore 會自動過濾)
git add .

# 或者選擇性加入
git add src/
git add requirements.txt
git add README.md
git add 檔案說明.md
```

### 步驟 4: 提交變更

```bash
git commit -m "Initial commit: 信用卡 RAG Agent 系統"
```

### 步驟 5: 連結遠端儲存庫

```bash
# 在 GitHub/GitLab 建立新的 repository 後
git remote add origin https://github.com/你的帳號/creditCard.git

# 或使用 SSH
git remote add origin git@github.com:你的帳號/creditCard.git
```

### 步驟 6: 推送到遠端

```bash
# 第一次推送
git push -u origin main

# 或如果分支名稱是 master
git push -u origin master
```

---

## 🌐 部署到伺服器流程

### 方案 1: 使用 Render/Railway (推薦新手)

#### 1. 準備部署檔案

確認專案包含:
- ✅ `requirements.txt`
- ✅ `Dockerfile` (已有)
- ✅ `.env.example` (範例設定)

#### 2. 在 Render.com 部署

1. 註冊 [Render.com](https://render.com)
2. 點擊 "New +" → "Web Service"
3. 連結你的 GitHub repository
4. 設定:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd src && python main.py`
   - **Environment Variables**: 
     - `GOOGLE_API_KEY`: 你的 API Key
     - `LINE_CHANNEL_SECRET`: 你的 LINE Secret
     - `LINE_CHANNEL_ACCESS_TOKEN`: 你的 LINE Token

#### 3. 部署
點擊 "Create Web Service",等待部署完成

---

### 方案 2: 使用自己的 VPS (進階)

#### 1. 連線到伺服器

```bash
ssh user@your-server-ip
```

#### 2. Clone 專案

```bash
git clone https://github.com/你的帳號/creditCard.git
cd creditCard
```

#### 3. 設定環境

```bash
# 安裝 Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-venv

# 建立虛擬環境
python3.11 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

#### 4. 設定環境變數

```bash
# 建立 .env 檔案
nano .env

# 貼上你的設定:
GOOGLE_API_KEY=你的API_KEY
LINE_CHANNEL_SECRET=你的SECRET
LINE_CHANNEL_ACCESS_TOKEN=你的TOKEN
```

#### 5. 初始化資料庫

```bash
cd src
python init_db.py
```

#### 6. 使用 systemd 設定自動啟動

建立服務檔案:
```bash
sudo nano /etc/systemd/system/creditcard-bot.service
```

內容:
```ini
[Unit]
Description=Credit Card RAG Agent
After=network.target

[Service]
Type=simple
User=你的使用者名稱
WorkingDirectory=/home/你的使用者名稱/creditCard/src
Environment="PATH=/home/你的使用者名稱/creditCard/venv/bin"
ExecStart=/home/你的使用者名稱/creditCard/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

啟動服務:
```bash
sudo systemctl daemon-reload
sudo systemctl enable creditcard-bot
sudo systemctl start creditcard-bot
sudo systemctl status creditcard-bot
```

#### 7. 設定 Nginx 反向代理 (選用)

```bash
sudo apt install nginx

sudo nano /etc/nginx/sites-available/creditcard
```

內容:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

啟用:
```bash
sudo ln -s /etc/nginx/sites-available/creditcard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔄 日常更新流程

### 本地開發完成後

```bash
# 1. 檢查變更
git status

# 2. 加入變更
git add .

# 3. 提交
git commit -m "描述你的變更"

# 4. 推送
git push
```

### 伺服器更新

```bash
# SSH 到伺服器
ssh user@your-server-ip

# 進入專案目錄
cd creditCard

# 拉取最新程式碼
git pull

# 重啟服務
sudo systemctl restart creditcard-bot
```

---

## 📝 常用 Git 指令

```bash
# 查看狀態
git status

# 查看提交歷史
git log --oneline

# 建立新分支
git checkout -b feature/新功能

# 切換分支
git checkout main

# 合併分支
git merge feature/新功能

# 查看遠端儲存庫
git remote -v

# 拉取最新程式碼
git pull
```

---

## 🔐 安全檢查清單

上傳前務必確認:

- [ ] `.env` 檔案已在 `.gitignore` 中
- [ ] 沒有硬編碼 API Keys 在程式碼中
- [ ] `.gitignore` 包含所有敏感檔案
- [ ] 執行 `git status` 確認沒有敏感資料
- [ ] README.md 中沒有真實的 API Keys

---

## 💡 建議的分支策略

```
main (生產環境)
  ↑
develop (開發環境)
  ↑
feature/新功能 (功能開發)
```

---

## 🆘 常見問題

### Q: 不小心上傳了 .env 怎麼辦?

```bash
# 1. 從 Git 歷史中移除
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 2. 強制推送
git push origin --force --all

# 3. 立即更換所有 API Keys!
```

### Q: 如何查看哪些檔案會被上傳?

```bash
git status
git ls-files
```

### Q: 推送失敗怎麼辦?

```bash
# 先拉取遠端變更
git pull --rebase origin main

# 再推送
git push
```

---

## 🎯 快速開始

最簡單的上傳流程:

```bash
cd d:\creditCard
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的帳號/creditCard.git
git push -u origin main
```

完成! 🎉
