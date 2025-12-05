#!/usr/bin/env python3
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processing import DataProcessor
import argparse

def main():
    parser = argparse.ArgumentParser(description="Merge and process data from different sources")
    args = parser.parse_args()
    
    DataProcessor().merge_datasets()

if __name__ == "__main__":
    main()
