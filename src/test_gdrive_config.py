"""
測試 Google Drive 設定是否正確載入
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config

print("=" * 60)
print("🔍 Google Drive 設定檢查")
print("=" * 60)

print(f"\n📋 環境變數狀態:")
print(f"   GOOGLE_DRIVE_ENABLED: {Config.GOOGLE_DRIVE_ENABLED}")
print(f"   GOOGLE_DRIVE_FILE_ID: {Config.GOOGLE_DRIVE_FILE_ID}")

if Config.GOOGLE_DRIVE_ENABLED:
    print(f"\n✅ Google Drive 整合已啟用")
    if Config.GOOGLE_DRIVE_FILE_ID:
        print(f"✅ 檔案 ID 已設定: {Config.GOOGLE_DRIVE_FILE_ID[:20]}...")
    else:
        print(f"❌ 檔案 ID 未設定!")
else:
    print(f"\n⚠️  Google Drive 整合未啟用")
    print(f"   請在 .env 設定:")
    print(f"   GOOGLE_DRIVE_ENABLED=True")
    print(f"   GOOGLE_DRIVE_FILE_ID=你的檔案ID")

print("\n" + "=" * 60)
