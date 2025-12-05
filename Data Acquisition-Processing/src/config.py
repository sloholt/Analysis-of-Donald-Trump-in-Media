import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
DATA_DIR = PROJECT_ROOT / 'data'

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# API Keys
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
THENEWSAPI_KEY = os.getenv('THENEWSAPI_KEY')

# NewsAPI Configuration
NEWS_API_BASE_URL = 'https://newsapi.org/v2/everything'
SEARCH_QUERY = 'Donald Trump'
START_DATE = '2015-01-01'
END_DATE = '2025-12-31'

# TheNewsAPI Configuration
THENEWSAPI_BASE_URL = 'https://api.thenewsapi.com/v1/news/all'
THENEWSAPI_COUNTRIES = 'us,ca'

# GNews Configuration
GNEWS_YEARS = range(2015, 2021)
GNEWS_ARTICLES_PER_YEAR = 60

# Sources by political leaning (for NewsAPI)
SOURCES = {
    'left': ['the-new-york-times', 'cnn', 'the-washington-post', 'msnbc'],
    'right': ['fox-news', 'breitbart-news'],
    'center': ['reuters', 'associated-press', 'usa-today'],
    'canadian': ['cbc-news']
}

# Output Files
RAW_DIR = DATA_DIR / 'raw'
INTERMEDIATE_DIR = DATA_DIR / 'intermediate'
FINAL_DIR = PROJECT_ROOT / 'final_dataset'

# Ensure directories exist
RAW_DIR.mkdir(exist_ok=True)
INTERMEDIATE_DIR.mkdir(exist_ok=True)
FINAL_DIR.mkdir(exist_ok=True)

# File Paths
INITIAL_DATASET = RAW_DIR / 'initial_dataset_1928.csv'
CLEANED_DATASET = INTERMEDIATE_DIR / 'cleaned_dataset_528.csv'
FINAL_DATASET = FINAL_DIR / 'final_500_dataset.csv'

# Legacy paths (kept for compatibility if needed, but pointing to new structure where possible)
RAW_ARTICLES_FILE = RAW_DIR / 'raw_articles.csv'
RAW_ARTICLES_THENEWSAPI_FILE = RAW_DIR / 'raw_articles_thenewsapi.csv'
RAW_ARTICLES_GNEWS_FILE = RAW_DIR / 'raw_articles_gnews.csv'
FINAL_ARTICLES_FILE = INITIAL_DATASET # The "final" output of collection is the input for analysis
SOURCE_ANALYSIS_FILE = DATA_DIR / 'source_analysis.csv'
ANALYSIS_RESULTS_DIR = DATA_DIR / 'analysis_results'
