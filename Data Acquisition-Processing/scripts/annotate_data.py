#!/usr/bin/env python3
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.annotation import Annotator
import argparse

def main():
    parser = argparse.ArgumentParser(description="Annotate dataset using Gemini")
    parser.add_argument('--input', help='Input CSV file')
    parser.add_argument('--output', help='Output CSV file')
    args = parser.parse_args()
    
    Annotator().annotate_dataset(args.input, args.output)

if __name__ == "__main__":
    main()
