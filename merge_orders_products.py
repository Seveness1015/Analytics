import pandas as pd
import os

# ================= 🎯 設定區 =================
# 讀 Order_TS.csv + SalePage.csv
ORDER_FILE = 'Order_TS.csv'
SALEPAGE_FILE = 'SalePage.csv'   
OUTPUT_FILE = 'Top15_Shop_zXQP_Report.txt' # 產出的是 TXT 檔
TARGET_SHOP = 'zXQPxhiL90nRa1XbvctRfA=='
# ============================================

def process_data():
    if not os.path.exists(ORDER_FILE) or not os.path.exists(SALEPAGE_FILE):
        print(f"❌ 找不到檔案！請確認 {ORDER_FILE} 和 {SALEPAGE_FILE} 都在同一個資料夾。")
        return

    print("掃描子單，計算這家店的總銷量...")
    shop_items = {}
    total_sales_qty = 0

    try:
        # 分塊讀取
        for chunk in pd.read_csv(ORDER_FILE, chunksize=100000, encoding='utf-8', low_memory=False):
            matched = chunk[chunk['ShopId'] == TARGET_SHOP]
            if not matched.empty:
                # 處理數量
                if 'Qty' in matched.columns:
                    agg = matched.groupby('SalePageId')['Qty'].sum()
                else:
                    agg = matched.groupby('SalePageId').size()
                
                for sp_id, qty in agg.items():
                    shop_items[sp_id] = shop_items.get(sp_id, 0) + qty
                    total_sales_qty += qty
                    
    except Exception as e:
        print(f"❌ 讀取訂單時發生錯誤：{e}")
        return

    if not shop_items:
        print("⚠️ 在訂單檔中找不到這家店的資料！")
        return

    print(f"✅ 統計完成！準備為前 15 名商品進行翻譯...")

    # 排序並只取前 15 名
    df_items = pd.DataFrame(list(shop_items.items()), columns=['SalePageId', '銷售數量'])
    df_items = df_items.sort_values(by='銷售數量', ascending=False).head(15)
    
    # 計算百分比
    df_items['百分比'] = (df_items['銷售數量'] / total_sales_qty * 100).round(2)

    print("📝 第二步：正在按照你的完美格式產出 TXT 檔案...")
    try:
        salepage_df = pd.read_csv(SALEPAGE_FILE, encoding='utf-8', low_memory=False)
        salepage_dict = salepage_df[['SalePageId', 'SalePageTitle', 'SaleProductDescShortContent']].drop_duplicates(subset=['SalePageId'])

        # 合併資料
        final_df = pd.merge(df_items, salepage_dict, on='SalePageId', how='left')
        
        # 處理如果商品名稱或描述是空的狀況
        final_df['SalePageTitle'] = final_df['SalePageTitle'].fillna('(無商品名稱)')
        final_df['SaleProductDescShortContent'] = final_df['SaleProductDescShortContent'].fillna('(無商品描述)')

        # ================= 開始寫入 TXT 檔案 =================
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            # 1. 寫入表頭 (ShopId 與 Data)
            f.write(f"ShopId: {TARGET_SHOP}\n")
            f.write(f"Data: {ORDER_FILE}, {SALEPAGE_FILE}\n")
            f.write("\n" + "="*40 + "\n\n") 

            # 2. 依序寫入第 1 名到第 15 名的資料
            for index, row in final_df.iterrows():
                rank = index + 1
                sp_id = row['SalePageId']
                title = row['SalePageTitle']
                qty = row['銷售數量']
                pct = row['百分比']
                desc = str(row['SaleProductDescShortContent']).strip()

                f.write(f"第{rank}名\n")
                f.write(f"SalePageId: {sp_id}\n")
                f.write(f"SalePageTitle: {title}\n")
                # {qty:,} 會自動幫數字加上千分位逗號
                f.write(f"銷售數量: {qty:,}佔比{pct}%\n")
                f.write(f"SaleProductDescShortContent:\n{desc}\n\n")
                
                f.write("-" * 40 + "\n\n")

        print("-" * 60)
        print(f"📁 最終檔案已儲存為：{OUTPUT_FILE}")

    except Exception as e:
        print(f"❌ 讀取商品頁或產出檔案時發生錯誤：{e}")

if __name__ == "__main__":
    process_data()