# 📥 Google Drive 自動下載設定指南

## 🎯 功能說明

每次執行 `python init_db.py` 重建向量資料庫時,會自動從 Google Drive 下載最新的信用卡資料 CSV,確保資料永遠是最新的!

---

## 📋 設定步驟

### 步驟 1: 上傳 CSV 到 Google Drive

1. 登入 [Google Drive](https://drive.google.com)
2. 上傳您的信用卡資料 CSV 檔案
3. 記住上傳的位置

### 步驟 2: 設定為公開分享

1. 在 Google Drive 中,右鍵點擊您的 CSV 檔案
2. 選擇 **"共用"** 或 **"取得連結"**
3. 將權限設定為 **"知道連結的任何人都可以檢視"**
4. 複製分享連結

範例連結:
```
https://drive.google.com/file/d/1ABC123xyz_這是檔案ID_456/view?usp=sharing
```

### 步驟 3: 取得檔案 ID

從分享連結中提取檔案 ID:

```
https://drive.google.com/file/d/1ABC123xyz_這是檔案ID_456/view?usp=sharing
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                              這就是你的檔案 ID
```

### 步驟 4: 設定環境變數

編輯 `.env` 檔案,加入以下設定:

```env
# Google Drive Integration
GOOGLE_DRIVE_ENABLED=True
GOOGLE_DRIVE_FILE_ID=1ABC123xyz_這是檔案ID_456
```

**重要提醒:**
- `GOOGLE_DRIVE_ENABLED=True` - 啟用自動下載
- `GOOGLE_DRIVE_FILE_ID` - 填入你的檔案 ID (不是完整 URL)

### 步驟 5: 測試下載

```bash
cd src
python init_db.py
```

你應該會看到:
```
🌐 Google Drive 整合已啟用
🔄 從 Google Drive 下載檔案...
   檔案 ID: 1ABC123xyz...
✅ 下載完成 (Google Sheets): 信用卡資料模板_YYYYMMDD_HHMMSS.csv
✅ 已從 Google Drive 更新資料
```

---

## 🔄 使用流程

### 更新信用卡資料

1. **在 Google Drive 編輯 CSV**
   - 直接在 Google Drive 編輯檔案
   - 或上傳新版本覆蓋舊檔案

2. **重建向量資料庫**
   ```bash
   cd src
   python init_db.py
   ```
   
3. **自動完成!**
   - 系統會自動下載最新的 CSV
   - 重建向量資料庫
   - 更新完成

---

## ⚙️ 進階設定

### 關閉自動下載

如果暫時不想從 Google Drive 下載,只需在 `.env` 設定:

```env
GOOGLE_DRIVE_ENABLED=False
```

### 使用本地檔案

如果下載失敗,系統會自動使用本地的 CSV 檔案作為備份。

---

## 🔐 安全性說明

### ⚠️ 注意事項

使用公開連結方式:
- ✅ 簡單易用,不需要 API 認證
- ⚠️ 任何人都能透過連結下載檔案
- ⚠️ 不適合存放敏感資料

### 💡 建議

如果信用卡資料包含敏感資訊:
1. 不要使用公開連結
2. 考慮使用 Google Drive API (方案 2)
3. 或將敏感資料移除後再上傳

---

## 🆘 常見問題

### Q: 下載失敗怎麼辦?

**可能原因:**
1. 檔案 ID 錯誤
2. 檔案未設為公開
3. 網路連線問題

**解決方法:**
1. 檢查 `.env` 中的 `GOOGLE_DRIVE_FILE_ID` 是否正確
2. 確認 Google Drive 檔案權限為 "知道連結的任何人都可以檢視"
3. 檢查網路連線

### Q: 如何確認檔案 ID 正確?

在瀏覽器開啟以下網址:
```
https://drive.google.com/uc?export=download&id=你的檔案ID
```

如果能下載檔案,表示 ID 正確!

### Q: 可以用 Excel 檔案嗎?

不行,系統只支援 CSV 格式。請確保上傳的是 `.csv` 檔案。

### Q: 每次都要下載嗎?

是的,每次執行 `init_db.py` 都會下載。這確保你永遠使用最新的資料。

---

## 📝 完整範例

### .env 設定範例

```env
# Google Gemini API
GOOGLE_API_KEY=AIzaSyBXS4gmSrIwH3ANx2Caq0O2P2_riAAE5Wo

# LINE Bot Configuration
LINE_CHANNEL_SECRET=your_line_channel_secret_here
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here

# Database
DATABASE_URL=sqlite:///./creditcard.db

# Application Settings
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Vector Database
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Google Drive Integration
GOOGLE_DRIVE_ENABLED=True
GOOGLE_DRIVE_FILE_ID=1ABC123xyz456def789
```

---

## 🎉 完成!

現在你可以:
1. ✅ 在 Google Drive 編輯信用卡資料
2. ✅ 執行 `python init_db.py` 自動更新
3. ✅ 不用手動下載和上傳檔案

享受自動化的便利吧! 🚀
