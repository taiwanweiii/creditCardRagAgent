# AGENTS.md - AI 程式代理指南

本文件為 AI 程式代理在此專案中工作時提供必要資訊。

## 專案概述

**信用卡回饋 RAG Agent** - 一個使用 RAG（檢索增強生成）技術的 LINE Bot，根據消費場景推薦最佳信用卡。使用 Python 3.11+、FastAPI、LangChain、ChromaDB 和 Google Gemini 建構。

---

## 建置/測試指令

### 環境設定
```bash
python -m venv myenv && source myenv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 執行應用程式
```bash
cd src && python main.py       # 本地執行
docker-compose up -d           # Docker 執行
```

### 執行測試
```bash
cd src && python -m pytest ../tests/ -v                              # 所有測試
python -m pytest ../tests/test_data_processor.py -v                  # 單一檔案
python -m pytest ../tests/test_data_processor.py::test_load_data -v  # 單一測試
```

### 初始化資料庫
```bash
cd src && python init_db.py
```

---

## 程式碼風格指南

### 匯入順序
```python
"""模組說明文件 - 所有模組必須包含"""
# 1. 標準函式庫
import os
from pathlib import Path
from typing import List, Dict, Optional

# 2. 第三方套件
import pandas as pd
from fastapi import FastAPI, Request, HTTPException

# 3. 本地模組
from config import Config
from vector_store import VectorStoreManager
```

### 型別提示
函式參數和回傳值必須使用型別提示：
```python
def recommend_cards(self, query: str, user_cards: List[str], top_k: int = 3) -> str:
    ...
def get_card_by_name(self, card_name: str) -> Optional[Dict]:
    ...
```

### 文件字串
類別和公開方法使用三引號文件字串：
```python
class RAGEngine:
    """基於 RAG 的信用卡推薦引擎"""
    
    def __init__(self, vector_store_manager: VectorStoreManager):
        """初始化 RAG 引擎
        
        Args:
            vector_store_manager: 向量資料庫管理器實例
        """
```

### 命名規範
- **類別**: PascalCase（`CreditCardDataProcessor`、`VectorStoreManager`）
- **函式/方法**: snake_case（`prepare_documents`、`get_user_cards`）
- **變數**: snake_case（`user_cards`、`csv_path`）
- **常數**: UPPER_SNAKE_CASE（`SYSTEM_PROMPT`、`DATABASE_URL`）
- **私有方法**: 底線前綴（`_prepare_context`、`_detect_category`）

### 錯誤處理
```python
if not self.csv_path.exists():
    raise FileNotFoundError(f"找不到 CSV 檔案: {self.csv_path}")

if self.vectorstore is None:
    raise ValueError("向量資料庫尚未初始化，請先呼叫 load_vectorstore()")

try:
    response = self.llm.invoke(messages)
    return response.content
except Exception as e:
    error_msg = str(e)
    if "quota" in error_msg.lower() or "429" in error_msg:
        return "API 額度已用盡..."
```

### 設定管理
所有設定透過 `Config` 類別存取環境變數：
```python
from config import Config
api_key = Config.GOOGLE_API_KEY
csv_path = Config.get_latest_csv_path()
```

### 資料庫模式
使用 SQLAlchemy ORM：
```python
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    line_user_id = Column(String, unique=True, nullable=False, index=True)
```

### 日誌輸出
使用帶有 emoji 前綴的 print 語句：
```python
print("🔄 載入資料中...")    # 操作進行中
print("✅ 資料載入完成")     # 成功
print("⚠️ 警告: ...")       # 警告
print("❌ 錯誤: ...")       # 錯誤
```

---

## 語言與本地化
- **程式碼註解**: 英文或繁體中文（zh-TW）
- **使用者訊息**: 繁體中文（zh-TW）
- **CSV 編碼**: UTF-8 with BOM（`utf-8-sig`）

---

## 關鍵架構模式

### RAG 流程
1. `CreditCardDataProcessor` 載入 CSV -> `List[Dict]`
2. `VectorStoreManager` 從文件建立 ChromaDB
3. `RAGEngine` 搜尋向量 + 生成 LLM 回應
4. `CreditCardLineBot` 處理 LINE webhook + 路由

### 檔案管理
- **當前使用的 CSV**：`data/信用卡資料模板_YYYYMMDD_HHMMSS.csv`（永遠只有 1 個最新檔案）
- **歷史備份**：`backups/信用卡資料模板_YYYYMMDD_HHMMSS.csv`（保留最近 30 個版本）
- **檔案管理工具**：`CSVFileManager` 自動處理備份和清理
- **更新機制**：透過管理 API 從 Google Drive 下載最新資料（必須啟用 Google Drive）

---

## 環境變數

必填：
- `GOOGLE_API_KEY` - Google Gemini API 金鑰

選填：
- `LINE_CHANNEL_SECRET`、`LINE_CHANNEL_ACCESS_TOKEN` - LINE Bot 憑證
- `ADMIN_API_KEY` - 管理 API 認證金鑰
- `GOOGLE_DRIVE_ENABLED`、`GOOGLE_DRIVE_FILE_ID` - Google Drive 整合
- `DEBUG` - 啟用除錯模式（預設: True）

---

## 測試注意事項
- 測試檔案位於 `tests/` 目錄，使用 `test_` 前綴
- 從 `src/` 目錄執行以正確解析匯入
- 使用 `pytest -v` 顯示詳細輸出
