#!/usr/bin/env python3
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collection import NewsAPICollector, TheNewsAPICollector, GNewsCollector
import argparse

def main():
    parser = argparse.ArgumentParser(description="Collect Trump media coverage data")
    parser.add_argument('--source', choices=['newsapi', 'thenewsapi', 'gnews', 'all'], default='all', help='Source to collect from')
    args = parser.parse_args()

    if args.source in ['newsapi', 'all']:
        NewsAPICollector().collect()
        
    if args.source in ['thenewsapi', 'all']:
        TheNewsAPICollector().collect()
        
    if args.source in ['gnews', 'all']:
        GNewsCollector().collect()

if __name__ == "__main__":
    main()
