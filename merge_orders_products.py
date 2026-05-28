import pandas as pd
import os

# ================= 🎯 設定區 =================
ORDER_FILE = 'Order_TS.csv'      
SALEPAGE_FILE = 'SalePage.csv'   
TARGET_SHOP = 'zXQPxhiL90nRa1XbvctRfA=='
TOP_K = 25  # 🚀 直接改成前 25 名
# ============================================

def main():
    if not os.path.exists(ORDER_FILE) or not os.path.exists(SALEPAGE_FILE):
        print("❌ 錯誤：找不到 CSV 檔案，請確認檔案與程式碼在同一個資料夾！")
        return

    print("🔄 步驟一：正在分塊讀取大檔案 Order_TS.csv 並計算銷量...")
    product_sales = {}
    total_shop_sales = 0

    # 分塊讀取（避免記憶體爆炸）
    for chunk in pd.read_csv(ORDER_FILE, chunksize=100000, encoding='utf-8', low_memory=False):
        matched = chunk[chunk['ShopId'] == TARGET_SHOP]
        if not matched.empty:
            # 如果有 Qty 欄位就加總，沒有就計算出現次數
            if 'Qty' in matched.columns:
                agg = matched.groupby('SalePageId')['Qty'].sum()
            else:
                agg = matched.groupby('SalePageId').size()
            
            for pid, qty in agg.items():
                product_sales[pid] = product_sales.get(pid, 0) + qty
                total_shop_sales += qty

    if not product_sales:
        print(f"⚠️ 找不到商店 {TARGET_SHOP} 的任何銷售紀錄。")
        return

    print("🔄 步驟二：正在載入商品資訊 SalePage.csv...")
    salepage_df = pd.read_csv(SALEPAGE_FILE, encoding='utf-8', low_memory=False)
    salepage_filtered = salepage_df[['SalePageId', 'SalePageTitle', 'SaleProductDescShortContent']].drop_duplicates(subset=['SalePageId'])

    # 建立銷量 DataFrame
    sales_df = pd.DataFrame(list(product_sales.items()), columns=['SalePageId', '銷售數量'])
    
    # 合併商品名稱
    final_df = pd.merge(sales_df, salepage_filtered, on='SalePageId', how='left')
    
    # 排序並取前 K 名
    top_products = final_df.sort_values(by='銷售數量', ascending=False).head(TOP_K)

    # 輸出結果
    print("\n" + "="*50)
    print(f"🏆 商店 {TARGET_SHOP} 熱銷商品排行榜 (Top {TOP_K}) 🏆")
    print("="*50 + "\n")

    for rank, (_, row) in enumerate(top_products.iterrows(), 1):
        pct = (row['銷售數量'] / total_shop_sales * 100)
        desc = str(row['SaleProductDescShortContent']).replace('\n', ' ').strip()
        if desc == 'nan' or not desc:
            desc = "(無商品描述)"
            
        print(f"第 {rank} 名")
        print(f"SalePageId: {row['SalePageId']}")
        print(f"SalePageTitle: {row['SalePageTitle']}")
        print(f"銷售數量: {row['銷售數量']:,} 佔比: {pct:.2f}%")
        print(f"商品描述: {desc[:100]}...") # 稍作截斷保持畫面乾淨
        print("-" * 50)

if __name__ == "__main__":
    main()