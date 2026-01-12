"""
從 Excel 恢復 CSV 檔案
"""
import pandas as pd

# 讀取 Excel
df = pd.read_excel("../信用卡資料模板.xlsx")

# 儲存為 CSV
df.to_csv("../信用卡資料模板.csv", index=False, encoding='utf-8-sig')

print(f"✅ 已從 Excel 恢復 CSV 檔案")
print(f"載入 {len(df)} 張信用卡資料")
