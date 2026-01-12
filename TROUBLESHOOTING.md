# 磁碟空間不足問題解決方案

## ❌ 問題描述

安裝依賴時出現錯誤:
```
ERROR: Could not install packages due to an OSError: [Errno 28] No space left on device
```

這是因為 pandas 需要編譯 numpy,會在臨時目錄佔用大量空間(約 1-2 GB)。

---

## ✅ 解決方案

### 方案 1: 清理磁碟空間 (推薦)

#### Windows 清理步驟

1. **清理臨時檔案**
   ```powershell
   # 清理 Windows 臨時檔案
   cleanmgr
   
   # 或手動刪除
   del /q /f /s %TEMP%\*
   ```

2. **清理 pip 快取**
   ```bash
   pip cache purge
   ```

3. **清理 Python 編譯檔案**
   ```bash
   # 在專案目錄執行
   del /s /q __pycache__
   del /s /q *.pyc
   ```

4. **檢查磁碟空間**
   ```bash
   # 查看 C 槽空間
   wmic logicaldisk get size,freespace,caption
   ```

### 方案 2: 使用預編譯的套件 (已更新)

我已經更新 `requirements.txt`,移除 pandas 的固定版本,讓 pip 自動選擇預編譯的 wheel 版本,避免編譯。

重新安裝:
```bash
pip install -r requirements.txt
```

### 方案 3: 分批安裝

如果空間仍然不足,可以分批安裝:

```bash
# 1. 先安裝基礎套件
pip install fastapi uvicorn python-dotenv pydantic

# 2. 安裝 LINE Bot SDK
pip install line-bot-sdk

# 3. 安裝 LangChain (核心)
pip install langchain langchain-google-genai langchain-community

# 4. 安裝向量資料庫
pip install chromadb

# 5. 安裝資料處理 (使用預編譯版本)
pip install pandas openpyxl

# 6. 安裝資料庫
pip install sqlalchemy

# 7. 安裝測試工具 (可選)
pip install pytest pytest-asyncio python-multipart
```

### 方案 4: 更換安裝位置

如果 C 槽空間不足,可以將虛擬環境建立在其他磁碟:

```bash
# 刪除現有虛擬環境
rmdir /s venv

# 在其他磁碟建立虛擬環境 (例如 D 槽)
python -m venv D:\venv_creditcard

# 啟動虛擬環境
D:\venv_creditcard\Scripts\activate

# 安裝依賴
pip install -r requirements.txt
```

### 方案 5: 使用 --no-cache-dir

避免 pip 快取佔用空間:

```bash
pip install -r requirements.txt --no-cache-dir
```

---

## 🔍 檢查磁碟空間

### Windows

```powershell
# 查看所有磁碟空間
Get-PSDrive -PSProvider FileSystem

# 或使用 wmic
wmic logicaldisk get size,freespace,caption
```

### 建議保留空間

- **最小需求**: 3 GB 可用空間
- **建議**: 5 GB 以上可用空間

---

## 📊 套件大小參考

| 套件 | 大小 (約) |
|------|----------|
| numpy | 50-100 MB |
| pandas | 30-50 MB |
| chromadb | 100-150 MB |
| langchain | 20-30 MB |
| fastapi | 10-20 MB |
| **總計** | **300-500 MB** |

編譯時臨時空間需求: **1-2 GB**

---

## ✅ 驗證安裝

安裝完成後,驗證套件:

```bash
# 檢查已安裝套件
pip list

# 檢查關鍵套件
python -c "import pandas; print('pandas:', pandas.__version__)"
python -c "import langchain; print('langchain:', langchain.__version__)"
python -c "import chromadb; print('chromadb:', chromadb.__version__)"
```

---

## 🎯 下一步

安裝成功後:

1. ✅ 執行 `cd src && python init_db.py` 初始化資料庫
2. ✅ 執行 `python test_cli.py` 開始測試

---

## ❓ 常見問題

### Q: 如何釋放更多空間?

**A**: 
1. 刪除不需要的檔案和程式
2. 清空資源回收筒
3. 使用磁碟清理工具
4. 移除舊的 Python 虛擬環境

### Q: 可以不安裝 pandas 嗎?

**A**: 不行,pandas 是必要的依賴,用於讀取 CSV 檔案。但我們已經優化安裝方式,使用預編譯版本。

### Q: 安裝很慢怎麼辦?

**A**: 使用國內鏡像源加速:
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 🆘 仍然無法解決?

如果以上方案都無法解決,請:

1. 檢查 C 槽可用空間是否 > 3 GB
2. 清理 Windows 更新檔案
3. 考慮升級硬碟或清理大型檔案
4. 使用外接硬碟建立虛擬環境
