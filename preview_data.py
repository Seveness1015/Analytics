import os
import pandas as pd

# --- 設定區 ---
# 這次把目標改回 3.3GB 的原始大檔案 Segment.csv
# (如果你的檔案放在資料夾內，請自行加上路徑，例如 'csv_data/Segment.csv')
FILE_NAME = 'Segment.csv' 

# 我們要尋找的 4 家目標商店
TARGET_SHOPS = [
    'zXQPxhiL90nRa1XbvctRfA==',
    '3WUOySTycJTK4Yeoza4Bjg==',
    'RZSHERLBqjPGOUFO01RYew==',
    'hFwniXiB/Ev2ZPXeO630Sw=='
]

def main():
    if not os.path.exists(FILE_NAME):
        print(f"錯誤：找不到 '{FILE_NAME}'。請確認檔案是否與本程式放在同一資料夾！")
        return

    print(f"🚀 開始掃描源頭大檔：{FILE_NAME}")
    print("雷達鎖定 4 間目標商店，由於檔案有 3.3GB，這可能會花上幾分鐘，請稍候...\n")

    # 建立一個記分板，初始數量都設為 0
    shop_counts = {shop: 0 for shop in TARGET_SHOPS}
    total_rows_scanned = 0

    try:
        # 一樣使用分塊讀取，每次 10 萬筆，且只讀取 ShopId 欄位以節省記憶體
        for chunk in pd.read_csv(FILE_NAME, usecols=['ShopId'], chunksize=100000, encoding='utf-8'):
            total_rows_scanned += len(chunk)
            
            # 過濾出存在於 TARGET_SHOPS 名單中的資料
            matched_data = chunk[chunk['ShopId'].isin(TARGET_SHOPS)]
            
            # 如果有找到，就統計數量並加到記分板裡
            if not matched_data.empty:
                counts = matched_data['ShopId'].value_counts()
                for shop, count in counts.items():
                    shop_counts[shop] += count
                    
            # (可選) 印出進度條，讓你知道程式沒當機
            if total_rows_scanned % 1000000 == 0:
                print(f"已掃描 {total_rows_scanned:,} 筆...")

        print("-" * 50)
        print(f"✅ 掃描完畢！總共檢查了 {total_rows_scanned:,} 筆標籤資料。\n")
        
        # 顯示最終結果
        print("【目標商店搜尋結果】")
        for i, shop in enumerate(TARGET_SHOPS, 1):
            count = shop_counts[shop]
            if count > 0:
                print(f"第 {i} 家店：🟢 找到了！共有 {count:,} 筆資料 (ShopId: {shop[:15]}...)")
            else:
                print(f"第 {i} 家店：🔴 沒出現 (0 筆) (ShopId: {shop[:15]}...)")

    except UnicodeDecodeError:
        print("⚠️ 編碼錯誤，請嘗試在 pd.read_csv 中將 encoding 改為 'big5'")
    except ValueError as ve:
        print(f"⚠️ 找不到欄位錯誤：{ve} (請確認檔案內是否有 'ShopId' 欄位)")
    except Exception as e:
        print(f"發生未知錯誤：{e}")

if __name__ == "__main__":
    main()