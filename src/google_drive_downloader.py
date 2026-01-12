"""
Google Drive 檔案下載工具
支援從公開連結下載檔案
"""
import requests
from pathlib import Path
from typing import Optional


def download_from_google_drive(file_id: str, destination: str) -> bool:
    """
    從 Google Drive 下載公開檔案
    支援一般檔案和 Google Sheets
    
    Args:
        file_id: Google Drive 檔案 ID 或 Sheets ID
        destination: 儲存路徑
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"🔄 從 Google Drive 下載檔案...")
        print(f"   檔案 ID: {file_id}")
        
        # 先嘗試 Google Sheets 匯出 CSV 格式
        sheets_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"
        
        print(f"   嘗試 Google Sheets 匯出...")
        session = requests.Session()
        response = session.get(sheets_url, stream=True)
        
        # 如果 Sheets 匯出成功
        if response.status_code == 200:
            # 儲存檔案
            destination_path = Path(destination)
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(destination_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size = destination_path.stat().st_size
            print(f"✅ 下載完成 (Google Sheets): {destination_path.name} ({file_size:,} bytes)")
            return True
        
        # 如果不是 Sheets,嘗試一般檔案下載
        print(f"   嘗試一般檔案下載...")
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = session.get(url, stream=True)
        
        # 處理大檔案的確認頁面
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                params = {'id': file_id, 'confirm': value}
                url = "https://drive.google.com/uc?export=download"
                response = session.get(url, params=params, stream=True)
                break
        
        # 檢查回應
        if response.status_code != 200:
            print(f"❌ 下載失敗: HTTP {response.status_code}")
            return False
        
        # 儲存檔案
        destination_path = Path(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(destination_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = destination_path.stat().st_size
        print(f"✅ 下載完成 (一般檔案): {destination_path.name} ({file_size:,} bytes)")
        return True
        
    except Exception as e:
        print(f"❌ 下載失敗: {e}")
        return False


def get_file_id_from_url(url: str) -> Optional[str]:
    """
    從 Google Drive URL 提取檔案 ID
    
    Args:
        url: Google Drive 分享連結
    
    Returns:
        檔案 ID 或 None
    
    Examples:
        >>> get_file_id_from_url("https://drive.google.com/file/d/1ABC123/view")
        '1ABC123'
    """
    import re
    
    # 匹配各種 Google Drive URL 格式
    patterns = [
        r'/file/d/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
        r'/d/([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


if __name__ == "__main__":
    # 測試用
    print("🧪 Google Drive 下載工具測試\n")
    
    # 範例: 從 URL 提取檔案 ID
    test_url = "https://drive.google.com/file/d/1ABC123xyz/view?usp=sharing"
    file_id = get_file_id_from_url(test_url)
    print(f"URL: {test_url}")
    print(f"檔案 ID: {file_id}\n")
    
    # 使用說明
    print("📝 使用方式:")
    print("1. 上傳檔案到 Google Drive")
    print("2. 設定為公開分享")
    print("3. 複製分享連結")
    print("4. 在 .env 設定 GOOGLE_DRIVE_FILE_ID")
