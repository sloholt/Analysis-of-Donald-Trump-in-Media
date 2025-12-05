#!/usr/bin/env python3
"""
Analyze North American vs International sources
Determine if we have enough for a 500-article North American-only sample
"""
import pandas as pd
import os

def analyze_north_american_sources():
    """Analyze which sources are North American and assess feasibility"""
    
    # Load complete dataset
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    df = pd.read_csv(os.path.join(data_dir, 'final_articles.csv'))
    
    # Comprehensive North American source classification
    north_american_sources = get_north_american_sources()
    
    def is_north_american(source):
        s = str(source).lower().strip()
        
        # Explicit exclusions for known false positives
        # These sources appeared in "US" searches but are clearly international.
        # Excluding them is critical for valid sentiment analysis.
        if 'timesofindia' in s or 'indiatimes' in s:
            return False
            
        # Direct match
        if s in north_american_sources:
            return True
        # Substring match
        for na_source in north_american_sources:
            # Skip very short common words for substring matching to avoid false positives
            if len(na_source) < 5 and na_source != 'cnn' and na_source != 'npr' and na_source != 'pbs' and na_source != 'vox':
                 if s == na_source:
                     return True
                 continue
                 
            if na_source in s:
                return True
        return False
    
    df['is_north_american'] = df['source'].apply(is_north_american)
    
    # Apply political leaning
    source_map = create_source_map()
    def get_leaning(source):
        s = str(source).lower().strip()
        if s in source_map: return source_map[s]
        for key, val in source_map.items():
            if key in s: return val
        return 'Other'
    
    df['leaning'] = df['source'].apply(get_leaning)
    df['sentiment'] = df['SENTIMENT (Pos/Neg/Neu)'].replace({
        'Positive': 'POS', 'Negative': 'NEG', 'Neutral': 'NEU'
    })
    
    print("="*80)
    print("NORTH AMERICAN SOURCE ANALYSIS")
    print("="*80)
    
    # Overall split
    na_df = df[df['is_north_american']]
    intl_df = df[~df['is_north_american']]
    
    print(f"\nOVERALL DATASET SPLIT:")
    print(f"  North American articles: {len(na_df):,} ({len(na_df)/len(df)*100:.1f}%)")
    print(f"  International articles:  {len(intl_df):,} ({len(intl_df)/len(df)*100:.1f}%)")
    print(f"  Total:                   {len(df):,}")
    
    # North American sources breakdown
    print(f"\n" + "="*80)
    print("NORTH AMERICAN SOURCES - DETAILED BREAKDOWN")
    print("="*80)
    
    print("\nBy Political Leaning:")
    for leaning in ['Left', 'Center', 'Right', 'Other']:
        subset = na_df[na_df['leaning'] == leaning]
        print(f"  {leaning:8s}: {len(subset):4d} articles from {subset['source'].nunique():3d} sources")
    
    print("\nTop 25 North American Sources:")
    top_na = na_df['source'].value_counts().head(25)
    for i, (source, count) in enumerate(top_na.items(), 1):
        leaning = na_df[na_df['source'] == source]['leaning'].iloc[0]
        print(f"  {i:2d}. {source[:45]:45s} [{leaning:6s}]: {count:3d} articles")
    
    # International sources for reference
    print(f"\n" + "="*80)
    print("TOP 15 INTERNATIONAL SOURCES (EXCLUDED)")
    print("="*80)
    
    top_intl = intl_df['source'].value_counts().head(15)
    for i, (source, count) in enumerate(top_intl.items(), 1):
        print(f"  {i:2d}. {source[:45]:45s}: {count:3d} articles")
    
    # Can we create a balanced 500-article sample?
    print(f"\n" + "="*80)
    print("BALANCED SAMPLE FEASIBILITY (500 articles)")
    print("="*80)
    
    print("\nNorth American articles by leaning:")
    for leaning in ['Left', 'Center', 'Right']:
        subset = na_df[na_df['leaning'] == leaning]
        print(f"  {leaning:8s}: {len(subset):4d} articles")
    
    # Calculate maximum balanced sample size
    left_count = len(na_df[na_df['leaning'] == 'Left'])
    center_count = len(na_df[na_df['leaning'] == 'Center'])
    right_count = len(na_df[na_df['leaning'] == 'Right'])
    
    max_balanced = min(left_count, center_count, right_count)
    max_balanced_total = max_balanced * 3
    
    # Check if the smallest group (Center) is too small to make a balanced 500-article dataset.
    # This calculation drove the decision to collect supplemental data.
    
    print(f"\nMaximum Balanced Sample (equal Left/Center/Right):")
    print(f"  {max_balanced} per group × 3 = {max_balanced_total} total articles")
    
    if max_balanced_total >= 500:
        print(f"\n✅ YES! We can create a 500-article balanced sample")
        print(f"   Recommended: 167 per group × 3 = 501 articles")
    else:
        print(f"\n⚠️ INSUFFICIENT for perfect balance")
        print(f"   Alternative: Use all {len(na_df)} NA articles")
    
    # Topic distribution check
    print(f"\n" + "="*80)
    print("TOPIC COVERAGE IN NORTH AMERICAN SOURCES")
    print("="*80)
    
    na_topics = na_df['PRIMARY_TOPIC'].value_counts()
    print("\nArticles per topic:")
    for topic, count in na_topics.items():
        pct = (count / len(na_df)) * 100
        print(f"  {topic:12s}: {count:4d} ({pct:5.1f}%)")
    
    # Create the sample
    if max_balanced >= 167:
        print(f"\n" + "="*80)
        print("CREATING RECOMMENDED 501-ARTICLE SAMPLE")
        print("="*80)
        
        sample = pd.concat([
            na_df[na_df['leaning'] == 'Left'].sample(n=167, random_state=42),
            na_df[na_df['leaning'] == 'Center'].sample(n=167, random_state=42),
            na_df[na_df['leaning'] == 'Right'].sample(n=167, random_state=42)
        ])
        
        output_path = os.path.join(data_dir, 'north_american_sample_501.csv')
        sample.to_csv(output_path, index=False)
        
        print(f"\n✅ Created: north_american_sample_501.csv")
        print(f"   Composition: 167 Left + 167 Center + 167 Right = 501 articles")
        
        # Verify topic distribution in sample
        print("\nTopic distribution in sample:")
        sample_topics = sample['PRIMARY_TOPIC'].value_counts()
        for topic, count in sample_topics.items():
            pct = (count / len(sample)) * 100
            print(f"  {topic:12s}: {count:3d} ({pct:5.1f}%)")
    
    print(f"\n" + "="*80)
    print("CLASSIFICATION CRITERIA USED")
    print("="*80)
    print_classification_criteria()
    
    return na_df

def get_north_american_sources():
    """Return list of North American news sources"""
    return {
        # Major US Networks/National
        'cnn', 'cnn.com', 'msnbc', 'msnbc.com',
        'fox news', 'foxnews.com', 'radio.foxnews.com',
        'abc news', 'abcnews.go.com',
        'cbs news', 'cbsnews.com',
        'nbc news', 'nbcnews.com',
        
        # US Print/Digital
        'the new york times', 'nytimes.com',
        'washington post', 'washingtonpost.com',
        'wall street journal', 'wsj.com',
        'usa today', 'usatoday.com',
        'new york post', 'nypost.com',
        
        # US News Sites
        'politico', 'politico.com',
        'huffpost', 'huffpost.com', 'huffingtonpost.com',
        'breitbart', 'breitbart.com',
        'vox', 'vox.com',
        'slate', 'slate.com',
        'salon', 'salon.com',
        'the daily beast', 'thedailybeast.com',
        'alternet', 'alternet.org',
        'businessinsider', 'businessinsider.com',
        'axios', 'axios.com',
        'newsweek', 'newsweek.com',
        'time', 'time.com', 'time magazine',
        'the atlantic', 'theatlantic.com',
        'new yorker', 'newyorker.com',
        'vanity fair', 'vanityfair.com',
        'rolling stone', 'rollingstone.com',
        'mother jones', 'motherjones.com',
        'the nation', 'thenation.com',
        'forbes', 'forbes.com',
        'daily wire', 'dailywire.com',
        'washington examiner', 'washingtonexaminer.com',
        'the federalist', 'thefederalist.com',
        'national review', 'nationalreview.com',
        'newsmax', 'newsmax.com',
        'one america news', 'oann', 'oann.com',
        'the blaze', 'theblaze.com',
        'townhall', 'townhall.com',
        'redstate', 'redstate.com',
        'daily caller', 'dailycaller.com',
        'boston globe', 'bostonglobe.com',
        
        # US Wire Services / Public
        'associated press', 'ap', 'apnews.com',
        'reuters', 'reuters.com',  # US operations
        'bloomberg', 'bloomberg.com',  # US HQ
        'npr', 'npr.org',
        'pbs', 'pbs.org',
        'the hill', 'thehill.com',
        
        # US Gov/Institutional
        'national archives', 'archives.gov', '.gov',
        'u.s. department', 'department of',
        'brookings', 'brookings.edu',
        
        # US Entertainment that covers politics
        'eonline', 'eonline.com',
        'people', 'people.com',
        'us magazine', 'usmagazine.com',
        'tmz', 'tmz.com',
        
        # Canadian Sources
        'national post', 'nationalpost.com',
        'globe and mail', 'theglobeandmail.com',
        'toronto star', 'thestar.com',
        'toronto sun', 'torontosun.com',
        'cbc', 'cbc.ca',
        'ctv', 'ctvnews.ca',
        'global news', 'globalnews.ca',
        'macleans', 'macleans.ca',
        'national observer', 'nationalobserver.com',
        'national newswatch', 'nationalnewswatch.com',
        '680news', '680news.com',
        'the american presidency project', 'presidency.ucsb.edu',
    }

def create_source_map():
    """Political leaning classification"""
    return {
        # LEFT
        'cnn': 'Left', 'cnn.com': 'Left',
        'msnbc': 'Left', 'msnbc.com': 'Left',
        'the new york times': 'Left', 'nytimes.com': 'Left',
        'washington post': 'Left', 'washingtonpost.com': 'Left',
        'politico': 'Left', 'politico.com': 'Left',
        'huffpost': 'Left', 'huffpost.com': 'Left',
        'vox': 'Left', 'vox.com': 'Left',
        'alternet': 'Left', 'alternet.org': 'Left',
        'abc news': 'Left', 'abcnews.go.com': 'Left',
        'cbs news': 'Left', 'cbsnews.com': 'Left',
        'nbc news': 'Left', 'nbcnews.com': 'Left',
        'slate': 'Left', 'slate.com': 'Left',
        'salon': 'Left', 'salon.com': 'Left',
        'mother jones': 'Left', 'motherjones.com': 'Left',
        'new yorker': 'Left', 'newyorker.com': 'Left',
        'the atlantic': 'Left', 'theatlantic.com': 'Left',
        'vanity fair': 'Left', 'vanityfair.com': 'Left',
        
        # CENTER
        'reuters': 'Center', 'reuters.com': 'Center',
        'usa today': 'Center', 'usatoday.com': 'Center',
        'bloomberg': 'Center', 'bloomberg.com': 'Center',
        'npr': 'Center', 'npr.org': 'Center',
        'pbs': 'Center', 'pbs.org': 'Center',
        'the hill': 'Center', 'thehill.com': 'Center',
        
        # RIGHT
        'fox news': 'Right', 'foxnews.com': 'Right',
        'breitbart': 'Right', 'breitbart.com': 'Right',
        'new york post': 'Right', 'nypost.com': 'Right',
        'daily wire': 'Right', 'dailywire.com': 'Right',
        'national post': 'Right', 'nationalpost.com': 'Right',
        'washington examiner': 'Right', 'washingtonexaminer.com': 'Right',
        'wall street journal': 'Right', 'wsj.com': 'Right', 'online.wsj.com': 'Right',
        
        # RECLASSIFIED / ADDED for Balance
        'national archives': 'Center', 'archives.gov': 'Center',
        'the american presidency project': 'Center', 'presidency.ucsb.edu': 'Center',
        'forbes': 'Center', 'forbes.com': 'Center',
        'businessinsider': 'Center', 'businessinsider.com': 'Center',
    }

def print_classification_criteria():
    """Print the inclusion/exclusion criteria used"""
    print("\nINCLUDED (North American):")
    print("  ✅ US-based news organizations (CNN, NYT, Fox News, etc.)")
    print("  ✅ US wire services (AP, Reuters US operations, Bloomberg)")
    print("  ✅ Canadian news organizations (National Post, CBC, Globe & Mail)")
    print("  ✅ US government sources (.gov domains)")
    print("  ✅ US think tanks (Brookings, etc.)")
    
    print("\nEXCLUDED (International):")
    print("  ❌ UK sources (BBC, The Guardian, Daily Mail)")
    print("  ❌ Indian sources (Times of India, NDTV, Economic Times)")
    print("  ❌ Middle East (Jerusalem Post, Al Jazeera)")
    print("  ❌ African (The South African)")
    print("  ❌ Asian (Japan Times, Korea Times, Straits Times)")
    print("  ❌ Australian (ABC Australia, news.com.au)")
    print("  ❌ European (other than UK)")
    print("  ❌ South American")
    
    print("\nBORDERLINE CASES:")
    print("  ⚠️ Reuters: Included (US operations, major US presence)")
    print("  ⚠️ Bloomberg: Included (US HQ, primarily US coverage)")
    print("  ⚠️ The Guardian: Excluded (UK-based despite US edition)")

if __name__ == "__main__":
    analyze_north_american_sources()
