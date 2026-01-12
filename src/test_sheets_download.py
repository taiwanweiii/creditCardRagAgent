"""
測試直接從 Google Sheets 下載
"""
import requests

file_id = "1EeGtNT1kQUOBQnUl8vqgEG4aXJU0Kb4d8XdAWlVDRNI"
sheets_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"

print(f"🔍 測試 Google Sheets 下載")
print(f"URL: {sheets_url}\n")

response = requests.get(sheets_url)

print(f"狀態碼: {response.status_code}")
print(f"內容長度: {len(response.content)} bytes")
print(f"前 200 字元:")
print(response.text[:200])

if response.status_code == 200 and len(response.content) > 100:
    print(f"\n✅ 下載成功!")
    with open("test_download.csv", "wb") as f:
        f.write(response.content)
    print(f"已儲存到 test_download.csv")
else:
    print(f"\n❌ 下載失敗或檔案為空")
    print(f"完整回應:")
    print(response.text[:500])
