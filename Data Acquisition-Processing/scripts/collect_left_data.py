#!/usr/bin/env python3
"""
Targeted Data Collection
Collects articles specifically from Left-leaning sources to balance the dataset.
"""
import os
import sys
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import config

from gnews import GNews

# Target Left-leaning domains (GNews format)
LEFT_SOURCES = [
    'cnn.com',
    'nytimes.com',
    'msnbc.com',
    'huffpost.com',
    'motherjones.com',
    'vox.com',
    'theguardian.com',
    'washingtonpost.com',
    'politico.com',
    'newyorker.com'
]

def collect_left_articles(target_count=150):
    print(f"Attempting to collect {target_count} articles from Left-leaning sources (2015-2025)...")
    print(f"Targets: {', '.join(LEFT_SOURCES)}")
    
    all_articles = []
    google_news = GNews(language='en', country='US', max_results=100) # Max 100 per query
    
    # Iterate through years to get historical coverage
    for year in range(2015, 2026):
        start_date = (datetime(year, 1, 1)).strftime('%Y-%m-%d')
        end_date = (datetime(year, 12, 31)).strftime('%Y-%m-%d')
        
        google_news.start_date = (datetime(year, 1, 1))
        google_news.end_date = (datetime(year, 12, 31))
        
        print(f"  Querying {year}...")
        
        for domain in LEFT_SOURCES:
            # Search for Trump in specific site
            query = f'Trump site:{domain}'
            try:
                articles = google_news.get_news(query)
                print(f"    {domain}: found {len(articles)} articles")
                
                for art in articles:
                    all_articles.append({
                        'title': art.get('title'),
                        'description': art.get('description'),
                        'source': domain, # Explicitly set source
                        'date': art.get('published date'),
                        'url': art.get('url')
                    })
            except Exception as e:
                print(f"    Error querying {domain}: {e}")
                
    # Save to new CSV
    if all_articles:
        new_df = pd.DataFrame(all_articles)
        
        # Clean dates
        # GNews returns diverse date formats, try to standardize
        # For simplicity in this targeted script, we'll try basic parsing
        # In production, use the robust cleaning from src/processing.py
        try:
            new_df['date'] = pd.to_datetime(new_df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
        except:
            pass
            
        new_df = new_df.dropna(subset=['title'])
        
        output_file = config.DATA_DIR / 'left_articles_raw.csv'
        new_df.to_csv(output_file, index=False)
        print(f"\nSaved {len(new_df)} raw articles to {output_file}")
        
        # Check against existing to avoid duplicates
        existing_df = pd.read_csv(config.DATA_DIR / 'final_articles.csv')
        
        # Normalize titles for comparison
        new_df['title_norm'] = new_df['title'].str.lower().str.strip()
        existing_df['title_norm'] = existing_df['title'].str.lower().str.strip()
        
        is_new = ~new_df['title_norm'].isin(existing_df['title_norm'])
        unique_new = new_df[is_new].drop(columns=['title_norm'])
        
        print(f"After removing duplicates: {len(unique_new)} new unique articles found")
        
        if len(unique_new) > 0:
            # Sample to target count if we have too many
            if len(unique_new) > target_count:
                unique_new = unique_new.sample(n=target_count, random_state=42)
                print(f"Subsampled to {target_count} articles")
                
            unique_file = config.DATA_DIR / 'left_articles_unique.csv'
            unique_new.to_csv(unique_file, index=False)
            print(f"Saved unique articles to {unique_file}")
            print("\nNext steps:")
            print("1. Run annotation on 'data/left_articles_unique.csv'")
            print("2. Merge with main dataset")
    else:
        print("No articles found.")

if __name__ == "__main__":
    collect_left_articles()
