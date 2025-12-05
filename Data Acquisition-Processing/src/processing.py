import pandas as pd
import os
from . import config

class DataProcessor:
    def merge_datasets(self):
        print("=" * 60)
        print("Merging Datasets")
        print("=" * 60)
        
        dfs = []
        
        if os.path.exists(config.RAW_ARTICLES_THENEWSAPI_FILE):
            df1 = pd.read_csv(config.RAW_ARTICLES_THENEWSAPI_FILE)
            print(f"Loaded {len(df1)} articles from TheNewsAPI")
            dfs.append(df1)
        else:
            print(f"Warning: {config.RAW_ARTICLES_THENEWSAPI_FILE} not found")
            
        if os.path.exists(config.RAW_ARTICLES_GNEWS_FILE):
            df2 = pd.read_csv(config.RAW_ARTICLES_GNEWS_FILE)
            print(f"Loaded {len(df2)} articles from GNews")
            dfs.append(df2)
        else:
            print(f"Warning: {config.RAW_ARTICLES_GNEWS_FILE} not found")
            
        if not dfs:
            print("No data to merge!")
            return
            
        final_df = pd.concat(dfs, ignore_index=True)
        
        # Standardize date
        final_df['date'] = pd.to_datetime(final_df['date'], errors='coerce')
        final_df = final_df.sort_values('date')
        
        # Deduplicate
        before_dedup = len(final_df)
        final_df = final_df.drop_duplicates(subset=['title'], keep='first')
        deduped = before_dedup - len(final_df)
        
        if deduped > 0:
            print(f"Removed {deduped} duplicates")
            
        final_df.to_csv(config.FINAL_ARTICLES_FILE, index=False)
        print(f"\n✓ Saved {len(final_df)} unique articles to {config.FINAL_ARTICLES_FILE}")
