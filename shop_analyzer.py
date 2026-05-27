import os
import pandas as pd
from collections import defaultdict, Counter

# --- 設定區 ---
TARGET_FILE = 'Segment.csv'     # 你找到的 3.3GB 原始檔案
OUTPUT_FILE = 'result_all.txt'  # 輸出的結果檔案名稱
CHUNK_SIZE = 100000             # 每次處理 10 萬筆資料

def new_shop_stat():
    return {
        'total_count': 0,
        'main_categories': defaultdict(lambda: {'count': 0, 'sub_categories': Counter()})
    }

shop_stats = defaultdict(new_shop_stat)

def main():
    if not os.path.exists(TARGET_FILE):
        print(f"錯誤：找不到 '{TARGET_FILE}' 檔案，請確認它是否與本程式放在同一資料夾！")
        return

    print(f"開始分析超大檔案 {TARGET_FILE}，這可能會花上幾分鐘，請稍候...")
    
    chunk_count = 0
    try:
        # --- 核心優化：使用 chunksize 進行分塊讀取 ---
        # 這樣就不會一次把 3.3GB 塞進記憶體導致當機
        for chunk in pd.read_csv(TARGET_FILE, usecols=['ShopId', 'CategorySegment'], encoding='utf-8', chunksize=CHUNK_SIZE):
            chunk_count += 1
            print(f"正在處理第 {chunk_count} 批資料 (每批 {CHUNK_SIZE:,} 筆)...")
            
            # 排除無效資料
            df = chunk.dropna(subset=['ShopId', 'CategorySegment']).copy()
            
            if df.empty:
                continue

            # 向量化字串處理 (擷取標籤)
            df['full_cat'] = df['CategorySegment'].str.extract(r'\]\s*(.*?):')[0]
            df = df.dropna(subset=['full_cat']).copy()
            
            # 切割為主類別與子類別
            split_cats = df['full_cat'].str.split('-', n=1, expand=True)
            df['main_cat'] = split_cats[0].str.strip()
            
            if len(split_cats.columns) > 1:
                df['sub_cat'] = split_cats[1].str.strip()
            else:
                df['sub_cat'] = None
                
            # 分組統計 (累加到我們全域的字典中)
            for shop_id, group in df.groupby('ShopId'):
                shop_stats[shop_id]['total_count'] += len(group)
                
                main_counts = group['main_cat'].value_counts()
                for m_cat, m_count in main_counts.items():
                    shop_stats[shop_id]['main_categories'][m_cat]['count'] += m_count
                
                if 'sub_cat' in group.columns:
                    has_sub = group.dropna(subset=['sub_cat'])
                    if not has_sub.empty:
                        sub_counts = has_sub.groupby(['main_cat', 'sub_cat']).size()
                        for (m_cat, s_cat), s_count in sub_counts.items():
                            s_cat_name = s_cat if s_cat else "其他未分類" 
                            shop_stats[shop_id]['main_categories'][m_cat]['sub_categories'][s_cat_name] += s_count

    except Exception as e:
        print(f"處理時發生錯誤: {e}")
        return

    # --- 寫入結果 ---
    print("\n資料處理完成！正在產出最終結果報告...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Data: {TARGET_FILE}\n")
        f.write(f"共計處理商店數: {len(shop_stats)} 間\n\n")
        
        for shop_id, stats in shop_stats.items():
            total = stats['total_count']
            f.write(f"ShopId: {shop_id}\n")
            f.write(f"數量: {total:,}\n")
            f.write("標籤內容:\n")
            
            sorted_mains = sorted(stats['main_categories'].items(), key=lambda x: x[1]['count'], reverse=True)
            top_12_mains = sorted_mains[:12]
            
            for m_cat, m_data in top_12_mains:
                m_count = m_data['count']
                m_pct = (m_count / total) * 100 if total > 0 else 0
                f.write(f"{m_cat} 有 {m_count:,} 個 (佔總數 {m_pct:.2f}%)\n")
                
                if m_data['sub_categories']:
                    for s_cat, s_count in m_data['sub_categories'].most_common():
                        s_pct = (s_count / m_count) * 100 if m_count > 0 else 0
                        f.write(f"  - {s_cat} 有 {s_count:,} 個 (佔該類別 {s_pct:.2f}%)\n")
            
            f.write("\n" + "="*40 + "\n\n") # 用等號分隔不同的商店，讓畫面更清楚
            
    print(f"分析成功！請查看 '{OUTPUT_FILE}' 檔案。")

if __name__ == "__main__":
    main()