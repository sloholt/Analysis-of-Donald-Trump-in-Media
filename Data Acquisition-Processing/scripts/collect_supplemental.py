#!/usr/bin/env python3
"""
Targeted re-collection to supplement North American Center and Right sources
Avoids duplicates from existing dataset
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from src import config

class TargetedCollector:
    """Collect more Center and Right North American sources"""
    
    def __init__(self):
        self.api_key = config.THENEWSAPI_KEY
        self.base_url = config.THENEWSAPI_BASE_URL
        
        # Load existing articles to avoid duplicates
        self.existing_urls = self.load_existing_urls()
        
        # Target sources for supplemental collection
        # We are missing "Center" and "Right" perspectives after the NA filter,
        # so we manually selected these high-quality sources to fill the gap.
        self.target_sources = {
            'center': [
                # Wire services
                'reuters.com', 'apnews.com', 'usatoday.com',
                # Public media
                'npr.org', 'pbs.org',
                # Neutral news
                'thehill.com', 'axios.com', 'bloomberg.com',
                # Wall St
                'wsj.com', 'marketwatch.com',
                # Newsweek
                'newsweek.com'
            ],
            'right': [
                # Major right outlets
                'foxnews.com', 'nypost.com', 'breitbart.com',
                # Conservative digital
                'dailywire.com', 'washingtonexaminer.com',
                'nationalreview.com', 'thefederalist.com',
                # Other conservative
                'newsmax.com', 'washingtontimes.com',
                'dailycaller.com', 'redstate.com'
            ]
        }
    
    def load_existing_urls(self):
        """Load existing article URLs to avoid duplicates"""
        try:
            df = pd.read_csv(config.DATA_DIR / 'final_articles.csv')
            existing = set(df['url'].dropna().unique())
            print(f"Loaded {len(existing)} existing URLs to avoid duplicates")
            return existing
        except:
            print("No existing dataset found, starting fresh")
            return set()
    
    def collect_from_source(self, source, target_count=50):
        """Collect articles from a specific source"""
        print(f"\n{'='*70}")
        print(f"Collecting from: {source}")
        print(f"{'='*70}")
        
        articles = []
        
        # Try multiple time periods to get enough articles
        # Force the API to look back to ensure we cover the full 2015-2025 timeline,
        # avoiding the default recency bias.
        periods = [
            ('2023-01-01', '2023-12-31'),
            ('2024-01-01', '2024-12-31'),
            ('2022-01-01', '2022-12-31'),
            ('2021-06-01', '2021-12-31')
        ]
        
        for start, end in periods:
            if len(articles) >= target_count:
                break
            
            print(f"  Period: {start} to {end}...", end=' ')
            
            params = {
                'api_token': self.api_key,
                'search': 'Donald Trump',
                'language': 'en',
                'domains': source,
                'published_after': start,
                'published_before': end,
                'limit': 100
            }
            
            try:
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json().get('data', [])
                
                # Filter out duplicates
                new_articles = [
                    a for a in data 
                    if a.get('url') not in self.existing_urls
                ]
                
                articles.extend(new_articles)
                print(f"{len(new_articles)} new articles (de-duped from {len(data)})")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        # Limit to target count
        articles = articles[:target_count]
        
        # Add to existing URLs to prevent duplicates in same session
        for article in articles:
            if article.get('url'):
                self.existing_urls.add(article['url'])
        
        print(f"✓ Collected {len(articles)} new articles from {source}")
        return articles
    
    def collect_targeted(self, targets_per_source=30):
        """Main collection function"""
        
        print("="*70)
        print("TARGETED COLLECTION: CENTER & RIGHT NORTH AMERICAN SOURCES")
        print("="*70)
        print(f"\nGoal: Collect ~{targets_per_source} articles per source")
        print(f"Deduplication: Active ({len(self.existing_urls)} existing URLs)")
        
        all_articles = []
        collection_stats = {'center': 0, 'right': 0}
        
        # Collect Center sources
        print("\n" + "="*70)
        print("PHASE 1: CENTER SOURCES")
        print("="*70)
        
        for source in self.target_sources['center']:
            articles = self.collect_from_source(source, targets_per_source)
            
            # Tag with leaning
            for article in articles:
                article['collected_leaning'] = 'Center'
                article['collected_source'] = source
            
            all_articles.extend(articles)
            collection_stats['center'] += len(articles)
            
            time.sleep(2)  # Be nice to API
        
        # Collect Right sources
        print("\n" + "="*70)
        print("PHASE 2: RIGHT SOURCES")
        print("="*70)
        
        for source in self.target_sources['right']:
            articles = self.collect_from_source(source, targets_per_source)
            
            # Tag with leaning
            for article in articles:
                article['collected_leaning'] = 'Right'
                article['collected_source'] = source
            
            all_articles.extend(articles)
            collection_stats['right'] += len(articles)
            
            time.sleep(2)
        
        # Save results
        self.save_results(all_articles, collection_stats)
        
        return all_articles
    
    def save_results(self, articles, stats):
        """Save collected articles"""
        
        print("\n" + "="*70)
        print("COLLECTION SUMMARY")
        print("="*70)
        print(f"Total new articles collected: {len(articles)}")
        print(f"  Center sources: {stats['center']}")
        print(f"  Right sources:  {stats['right']}")
        
        if len(articles) == 0:
            print("\n⚠️ No new articles collected!")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'article_id': f"SUPP_{i}",
            'source': a.get('collected_source', a.get('source', '')),
            'source_leaning': a.get('collected_leaning', ''),
            'date': a.get('published_at', '')[:10],
            'title': a.get('title', ''),
            'description': a.get('description', ''),
            'url': a.get('url', ''),
            'snippet': a.get('snippet', '')
        } for i, a in enumerate(articles, 1)])
        
        # Save to CSV
        output_file = config.DATA_DIR / 'supplemental_articles.csv'
        df.to_csv(output_file, index=False)
        
        print(f"\n✓ Saved to: {output_file}")
        print("\nNext steps:")
        print("  1. Annotate these articles (run annotate_data.py)")
        print("  2. Merge with existing dataset")
        print("  3. Create balanced 500-article sample")
        
        # Show breakdown by source
        print("\n" + "="*70)
        print("BREAKDOWN BY SOURCE")
        print("="*70)
        source_counts = df['source'].value_counts()
        for source, count in source_counts.items():
            leaning = df[df['source'] == source]['source_leaning'].iloc[0]
            print(f"  {source:30s} [{leaning:6s}]: {count:3d} articles")

def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Targeted collection of Center and Right NA sources"
    )
    parser.add_argument(
        '--per-source',
        type=int,
        default=30,
        help='Target articles per source (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Check for API key
    if not config.THENEWSAPI_KEY:
        print("❌ ERROR: THENEWSAPI_KEY not found in environment")
        print("Please add your API key to .env file")
        return
    
    # Run collection
    collector = TargetedCollector()
    collector.collect_targeted(targets_per_source=args.per_source)

if __name__ == "__main__":
    main()
