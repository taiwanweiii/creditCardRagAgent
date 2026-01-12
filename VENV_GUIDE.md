# Python 虛擬環境設定指南 (venv)

本指南說明如何使用 Python venv 建立虛擬環境。

---

## 🐍 建立虛擬環境

### Windows

```bash
# 進入專案目錄
cd d:\creditCard

# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
venv\Scripts\activate

# 確認虛擬環境已啟動 (命令列前面會顯示 (venv))
```

### macOS / Linux

```bash
# 進入專案目錄
cd /path/to/creditCard

# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate

# 確認虛擬環境已啟動 (命令列前面會顯示 (venv))
```

---

## 📦 安裝依賴套件

啟動虛擬環境後,安裝所需套件:

```bash
# 確認 pip 版本
pip --version

# 升級 pip (建議)
python -m pip install --upgrade pip

# 安裝專案依賴
pip install -r requirements.txt
```

---

## ✅ 驗證安裝

```bash
# 查看已安裝的套件
pip list

# 應該會看到以下主要套件:
# - fastapi
# - uvicorn
# - langchain
# - langchain-google-genai
# - chromadb
# - line-bot-sdk
# - pandas
# - sqlalchemy
```

---

## 🚀 執行專案

虛擬環境啟動後,就可以執行專案:

### 初始化向量資料庫

```bash
cd src
python init_db.py
```

### 測試模式

```bash
# 命令列介面
python test_cli.py

# 或網頁介面
python test_web.py
```

### LINE Bot 模式

```bash
python main.py
```

---

## 🔄 日常使用流程

### 每次開發前

```bash
# 1. 進入專案目錄
cd d:\creditCard

# 2. 啟動虛擬環境
venv\Scripts\activate

# 3. 開始開發或執行程式
cd src
python test_cli.py
```

### 開發完成後

```bash
# 停用虛擬環境
deactivate
```

---

## 📝 常用指令

### 虛擬環境管理

```bash
# 啟動虛擬環境 (Windows)
venv\Scripts\activate

# 啟動虛擬環境 (macOS/Linux)
source venv/bin/activate

# 停用虛擬環境
deactivate

# 刪除虛擬環境 (如需重建)
rmdir /s venv  # Windows
rm -rf venv    # macOS/Linux
```

### 套件管理

```bash
# 安裝新套件
pip install package_name

# 更新 requirements.txt
pip freeze > requirements.txt

# 從 requirements.txt 安裝
pip install -r requirements.txt

# 升級特定套件
pip install --upgrade package_name

# 移除套件
pip uninstall package_name
```

---

## 🎯 IDE 設定

### Visual Studio Code

1. 開啟專案資料夾 `d:\creditCard`
2. 按 `Ctrl+Shift+P` 開啟命令面板
3. 輸入 `Python: Select Interpreter`
4. 選擇 `.\venv\Scripts\python.exe`

VS Code 會自動偵測虛擬環境並在終端機中啟動。

### PyCharm

1. 開啟專案
2. File → Settings → Project → Python Interpreter
3. 點擊齒輪圖示 → Add
4. 選擇 Existing environment
5. 選擇 `d:\creditCard\venv\Scripts\python.exe`

---

## ❓ 常見問題

### Q1: 無法啟動虛擬環境 (Windows)

**錯誤訊息**: `無法載入檔案,因為這個系統上已停用指令碼執行`

**解決方法**:
```powershell
# 以系統管理員身分執行 PowerShell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 然後再次嘗試啟動虛擬環境
venv\Scripts\activate
```

### Q2: pip 安裝套件很慢

**解決方法**: 使用國內鏡像源
```bash
# 臨時使用
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 永久設定
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 虛擬環境佔用空間太大

虛擬環境通常會佔用 200-500 MB,這是正常的。如果需要節省空間:
- 不要將 `venv/` 資料夾加入版本控制 (已在 `.gitignore` 中)
- 其他開發者可以自行建立虛擬環境

### Q4: 如何在不同專案間切換

```bash
# 停用當前虛擬環境
deactivate

# 切換到其他專案
cd d:\other_project

# 啟動該專案的虛擬環境
venv\Scripts\activate
```

---

## 🔒 .gitignore 設定

虛擬環境資料夾已經加入 `.gitignore`,不會被提交到 Git:

```gitignore
# Virtual Environment
venv/
env/
ENV/
```

---

## 📊 虛擬環境 vs 全域安裝

### 使用虛擬環境的優點

✅ **隔離性**: 不同專案使用不同版本的套件  
✅ **乾淨**: 不會污染全域 Python 環境  
✅ **可重現**: 透過 `requirements.txt` 確保環境一致  
✅ **安全**: 測試新套件不會影響其他專案  

### 全域安裝的缺點

❌ 套件版本衝突  
❌ 難以管理依賴  
❌ 無法確保環境一致性  

---

## 🎉 完成!

現在您已經設定好虛擬環境,可以開始開發了!

**下一步**:
1. ✅ 確認虛擬環境已啟動 (命令列前面有 `(venv)`)
2. ✅ 執行 `cd src && python init_db.py` 初始化資料庫
3. ✅ 執行 `python test_cli.py` 或 `python test_web.py` 開始測試

祝您開發順利! 🚀
