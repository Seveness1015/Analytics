import pandas as pd

# 你可以把這裡換成 Order_TG.csv 或 Order_TS.csv 試試看
TARGET_FILE = 'Order_TG.csv' 
unique_shops = set() # 用集合(set)來儲存，確保不會重複

print(f"正在掃描 {TARGET_FILE} 中的商店清單，請稍候...")

try:
    # 一樣每次讀取 10 萬筆，但這次我們只讀 'ShopId' 這一欄，速度會極快
    for chunk in pd.read_csv(TARGET_FILE, usecols=['ShopId'], chunksize=100000):
        # 將這 10 萬筆裡面出現過的不重複 ShopId 加入集合中
        unique_shops.update(chunk['ShopId'].dropna().unique())

    print("\n掃描完成！發現以下商店：")
    for i, shop in enumerate(unique_shops, 1):
        print(f"{i}. {shop}")
    print(f"\n總共找到 {len(unique_shops)} 家商店。")

except Exception as e:
    print(f"發生錯誤：{e}")