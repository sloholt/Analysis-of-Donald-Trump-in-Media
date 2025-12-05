import requests
import time
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from gnews import GNews
from . import config

class NewsAPICollector:
    def __init__(self):
        self.api_key = config.NEWS_API_KEY
        self.base_url = config.NEWS_API_BASE_URL

    def get_date_ranges(self, start_date: str, end_date: str, interval_days: int = 30) -> List[tuple]:
        ranges = []
        current = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current < end:
            next_date = current + timedelta(days=interval_days)
            if next_date > end:
                next_date = end
            ranges.append((
                current.strftime('%Y-%m-%d'),
                next_date.strftime('%Y-%m-%d')
            ))
            current = next_date
        return ranges

    def fetch_articles(self, query: str, from_date: str, to_date: str, sources: Optional[str] = None) -> List[Dict]:
        params = {
            'q': query,
            'from': from_date,
            'to': to_date,
            'language': 'en',
            'sortBy': 'relevancy',
            'pageSize': 100,
            'apiKey': self.api_key
        }
        if sources:
            params['sources'] = sources
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get('status') == 'ok':
                return data.get('articles', [])
            else:
                print(f"API Error: {data.get('message', 'Unknown error')}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return []

    def collect(self):
        if not self.api_key:
            print("⚠ WARNING: NEWS_API_KEY not set.")
            return

        print("Collecting from NewsAPI...")
        all_articles = []
        date_ranges = self.get_date_ranges(config.START_DATE, config.END_DATE)
        
        all_source_ids = []
        for sources in config.SOURCES.values():
            all_source_ids.extend(sources)
        source_string = ','.join(all_source_ids)

        for idx, (from_date, to_date) in enumerate(date_ranges, 1):
            print(f"[{idx}/{len(date_ranges)}] Fetching: {from_date} to {to_date}")
            articles = self.fetch_articles(config.SEARCH_QUERY, from_date, to_date, source_string)
            print(f"  → Retrieved {len(articles)} articles")
            all_articles.extend(articles)
            time.sleep(1)

        # Filter and Deduplicate
        relevant = [a for a in all_articles if 'Trump' in a.get('title', '') or 'Trump' in a.get('description', '')]
        unique = {a.get('title'): a for a in relevant}.values()
        
        self.save_to_csv(list(unique), config.RAW_ARTICLES_FILE)

    def save_to_csv(self, articles: List[Dict], filename):
        fieldnames = ['article_id', 'source', 'source_leaning', 'date', 'title', 
                      'description', 'url', 'author', 'content']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for idx, article in enumerate(articles, 1):
                source_name = article.get('source', {}).get('id', '')
                leaning = 'unknown'
                for category, sources in config.SOURCES.items():
                    if source_name in sources:
                        leaning = category
                        break
                
                writer.writerow({
                    'article_id': idx,
                    'source': article.get('source', {}).get('name', ''),
                    'source_leaning': leaning,
                    'date': article.get('publishedAt', '')[:10],
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'author': article.get('author', ''),
                    'content': article.get('content', '')
                })
        print(f"✓ Saved {len(articles)} articles to {filename}")


class TheNewsAPICollector:
    def __init__(self):
        self.api_key = config.THENEWSAPI_KEY
        self.base_url = config.THENEWSAPI_BASE_URL

    def get_month_ranges(self, start_date: str, end_date: str) -> List[tuple]:
        ranges = []
        current = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        while current < end:
            month_start = current.replace(day=1)
            next_month = (month_start + timedelta(days=32)).replace(day=1)
            month_end = next_month - timedelta(days=1)
            if month_end > end: month_end = end
            ranges.append((month_start.strftime('%Y-%m-%d'), month_end.strftime('%Y-%m-%d')))
            current = next_month
        return ranges

    def fetch_articles(self, query: str, from_date: str, to_date: str) -> List[Dict]:
        params = {
            'api_token': self.api_key,
            'search': query,
            'language': 'en',
            'countries': config.THENEWSAPI_COUNTRIES,
            'published_after': from_date,
            'published_before': to_date,
            'limit': 100
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return []

    def collect(self):
        if not self.api_key:
            print("⚠ WARNING: THENEWSAPI_KEY not set.")
            return

        print("Collecting from TheNewsAPI...")
        all_articles = []
        month_ranges = self.get_month_ranges(config.START_DATE, config.END_DATE)

        for idx, (from_date, to_date) in enumerate(month_ranges, 1):
            print(f"[{idx}/{len(month_ranges)}] {from_date[:7]} ...", end=' ')
            articles = self.fetch_articles(config.SEARCH_QUERY, from_date, to_date)
            print(f"{len(articles)} articles")
            all_articles.extend(articles)
            time.sleep(0.5)

        self.save_to_csv(all_articles, config.RAW_ARTICLES_THENEWSAPI_FILE)

    def save_to_csv(self, articles: List[Dict], filename):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['article_id', 'source', 'date', 'title', 'description', 'url', 'snippet'])
            writer.writeheader()
            for idx, article in enumerate(articles, 1):
                writer.writerow({
                    'article_id': idx,
                    'source': article.get('source', ''),
                    'date': article.get('published_at', '')[:10],
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'snippet': article.get('snippet', '')
                })
        print(f"✓ Saved {len(articles)} articles to {filename}")


class GNewsCollector:
    def collect(self):
        print("Collecting from GNews...")
        all_articles = []
        google_news = GNews(language='en', country='US', max_results=100)

        for year in config.GNEWS_YEARS:
            print(f"Processing {year}...")
            year_articles = []
            for month in range(1, 13):
                google_news.start_date = (year, month, 1)
                google_news.end_date = (year, month, 28)
                try:
                    articles = google_news.get_news(config.SEARCH_QUERY)
                    count = 0
                    for art in articles:
                        if count >= 5: break
                        if not any(a['url'] == art['url'] for a in year_articles):
                            year_articles.append(art)
                            count += 1
                    time.sleep(1)
                except Exception as e:
                    print(f"Error {year}-{month:02d}: {e}")
            all_articles.extend(year_articles)

        self.save_to_csv(all_articles, config.RAW_ARTICLES_GNEWS_FILE)

    def save_to_csv(self, articles: List[Dict], filename):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['article_id', 'source', 'date', 'title', 'description', 'url', 'snippet'])
            writer.writeheader()
            for idx, article in enumerate(articles, 1):
                pub_date = article.get('published date', '')
                try:
                    dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                    date_str = dt.strftime('%Y-%m-%d')
                except:
                    date_str = pub_date
                
                writer.writerow({
                    'article_id': f"G{idx}",
                    'source': article.get('publisher', {}).get('title', ''),
                    'date': date_str,
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'snippet': ''
                })
        print(f"✓ Saved {len(articles)} articles to {filename}")
