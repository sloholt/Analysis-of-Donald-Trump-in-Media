import pandas as pd
import os
import random

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import config

def generate_balanced_sample():
    # Load data
    print(f"Loading data from: {config.INITIAL_DATASET}")
    df = pd.read_csv(config.INITIAL_DATASET)
    
    # --- Source Classification Logic ---
    # Refined list to exclude international sources (e.g., Times of India)
    # to ensure valid sentiment analysis for North American context.
    north_american_sources = {
        'cnn', 'cnn.com', 'msnbc', 'msnbc.com', 'fox news', 'foxnews.com', 'radio.foxnews.com',
        'abc news', 'abcnews.go.com', 'cbs news', 'cbsnews.com', 'nbc news', 'nbcnews.com',
        'the new york times', 'nytimes.com', 'washington post', 'washingtonpost.com',
        'wall street journal', 'wsj.com', 'usa today', 'usatoday.com', 'new york post', 'nypost.com',
        'politico', 'politico.com', 'huffpost', 'huffpost.com', 'huffingtonpost.com',
        'breitbart', 'breitbart.com', 'vox', 'vox.com', 'slate', 'slate.com', 'salon', 'salon.com',
        'the daily beast', 'thedailybeast.com', 'alternet', 'alternet.org', 'businessinsider', 'businessinsider.com',
        'axios', 'axios.com', 'newsweek', 'newsweek.com', 'time', 'time.com', 'time magazine',
        'the atlantic', 'theatlantic.com', 'new yorker', 'newyorker.com', 'vanity fair', 'vanityfair.com',
        'rolling stone', 'rollingstone.com', 'mother jones', 'motherjones.com', 'the nation', 'thenation.com',
        'forbes', 'forbes.com', 'daily wire', 'dailywire.com', 'washington examiner', 'washingtonexaminer.com',
        'the federalist', 'thefederalist.com', 'national review', 'nationalreview.com', 'newsmax', 'newsmax.com',
        'one america news', 'oann', 'oann.com', 'the blaze', 'theblaze.com', 'townhall', 'townhall.com',
        'redstate', 'redstate.com', 'daily caller', 'dailycaller.com', 'boston globe', 'bostonglobe.com',
        'associated press', 'ap', 'apnews.com', 'reuters', 'reuters.com', 'bloomberg', 'bloomberg.com',
        'npr', 'npr.org', 'pbs', 'pbs.org', 'the hill', 'thehill.com',
        'national archives', 'archives.gov', '.gov', 'u.s. department', 'department of', 'brookings', 'brookings.edu',
        'eonline', 'eonline.com', 'people', 'people.com', 'us magazine', 'usmagazine.com', 'tmz', 'tmz.com',
        'national post', 'nationalpost.com', 'globe and mail', 'theglobeandmail.com', 'toronto star', 'thestar.com',
        'toronto sun', 'torontosun.com', 'cbc', 'cbc.ca', 'ctv', 'ctvnews.ca', 'global news', 'globalnews.ca',
        'macleans', 'macleans.ca', 'national observer', 'nationalobserver.com', 'national newswatch', 'nationalnewswatch.com',
        '680news', '680news.com', 'the american presidency project', 'presidency.ucsb.edu'
    }

    source_map = {
        'cnn': 'Left', 'cnn.com': 'Left', 'msnbc': 'Left', 'msnbc.com': 'Left',
        'the new york times': 'Left', 'nytimes.com': 'Left', 'washington post': 'Left', 'washingtonpost.com': 'Left',
        'politico': 'Left', 'politico.com': 'Left', 'huffpost': 'Left', 'huffpost.com': 'Left',
        'vox': 'Left', 'vox.com': 'Left', 'alternet': 'Left', 'alternet.org': 'Left',
        'abc news': 'Left', 'abcnews.go.com': 'Left', 'cbs news': 'Left', 'cbsnews.com': 'Left',
        'nbc news': 'Left', 'nbcnews.com': 'Left', 'slate': 'Left', 'slate.com': 'Left',
        'salon': 'Left', 'salon.com': 'Left', 'mother jones': 'Left', 'motherjones.com': 'Left',
        'new yorker': 'Left', 'newyorker.com': 'Left', 'the atlantic': 'Left', 'theatlantic.com': 'Left',
        'vanity fair': 'Left', 'vanityfair.com': 'Left',
        
        'reuters': 'Center', 'reuters.com': 'Center', 'usa today': 'Center', 'usatoday.com': 'Center',
        'bloomberg': 'Center', 'bloomberg.com': 'Center', 'npr': 'Center', 'npr.org': 'Center',
        'pbs': 'Center', 'pbs.org': 'Center', 'the hill': 'Center', 'thehill.com': 'Center',
        'national archives': 'Center', 'archives.gov': 'Center',
        'the american presidency project': 'Center', 'presidency.ucsb.edu': 'Center',
        'forbes': 'Center', 'forbes.com': 'Center',
        'businessinsider': 'Center', 'businessinsider.com': 'Center',
        
        'fox news': 'Right', 'foxnews.com': 'Right', 'breitbart': 'Right', 'breitbart.com': 'Right',
        'new york post': 'Right', 'nypost.com': 'Right', 'daily wire': 'Right', 'dailywire.com': 'Right',
        'national post': 'Right', 'nationalpost.com': 'Right',
        'washington examiner': 'Right', 'washingtonexaminer.com': 'Right',
        'wall street journal': 'Right', 'wsj.com': 'Right', 'online.wsj.com': 'Right'
    }

    def is_north_american(source):
        s = str(source).lower().strip()
        if 'timesofindia' in s or 'indiatimes' in s: return False
        if 'forbesafrica' in s or 'bloombergquint' in s: return False
        if s in north_american_sources: return True
        for na_source in north_american_sources:
            if len(na_source) < 5 and na_source not in ['cnn', 'npr', 'pbs', 'vox']:
                 if s == na_source: return True
                 continue
            if na_source in s: return True
        return False

    def get_leaning(source):
        s = str(source).lower().strip()
        if s in source_map: return source_map[s]
        for key, val in source_map.items():
            if key in s: return val
        return 'Other'

    # Apply filters
    df['is_north_american'] = df['source'].apply(is_north_american)
    na_df = df[df['is_north_american']].copy()
    na_df['leaning'] = na_df['source'].apply(get_leaning)

    print(f"Total North American Articles: {len(na_df)}")
    print(na_df['leaning'].value_counts())

    # --- Sampling Logic (Maximize Center Strategy) ---
    # Since we only have ~130 Center articles after filtering, we take ALL of them.
    # Then we match Left/Right at a higher number (199) to keep the dataset robust (~528 total).
    
    left_pool = na_df[na_df['leaning'] == 'Left']
    right_pool = na_df[na_df['leaning'] == 'Right']
    center_pool = na_df[na_df['leaning'] == 'Center']
    other_pool = na_df[na_df['leaning'] == 'Other']

    # Sample sizes
    n_left = 199
    n_right = 199
    n_center = len(center_pool) # Take all available Center
    
    # Calculate remainder for Other
    # We accept this slight overage to maximize statistical power.
    total_target = 500
    n_other = total_target - (n_left + n_right + n_center)
    if n_other < 0: n_other = 0 # Expected behavior with current counts

    print(f"\nSampling Targets:")
    print(f"  Left:   {n_left}")
    print(f"  Right:  {n_right}")
    print(f"  Center: {n_center}")
    print(f"  Other:  {n_other}")
    print(f"  Total:  {n_left + n_right + n_center + n_other}")

    # Create samples
    sample_left = left_pool.sample(n=n_left, random_state=42)
    sample_right = right_pool.sample(n=n_right, random_state=42)
    sample_center = center_pool # Take all
    
    if n_other > 0:
        sample_other = other_pool.sample(n=n_other, random_state=42)
    else:
        sample_other = pd.DataFrame()

    # Combine
    final_sample = pd.concat([sample_left, sample_right, sample_center, sample_other])
    
    # Shuffle
    final_sample = final_sample.sample(frac=1, random_state=42).reset_index(drop=True)

    # Save
    # Save
    output_path = config.FINAL_DATASET
    final_sample.to_csv(output_path, index=False)
    print(f"\n✅ Created: {output_path}")
    print(f"Total articles: {len(final_sample)}")
    print(final_sample['leaning'].value_counts())

if __name__ == "__main__":
    generate_balanced_sample()
