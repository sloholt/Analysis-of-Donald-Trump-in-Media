# COMP 370 Final Project: Trump Media Coverage Analysis (2015-2025)

## Project Overview

This project analyzes media coverage of Donald Trump from 2015 to 2025, focusing on:
- **Primary Topics** discussed in news articles
- **Sentiment** (Positive, Negative, Neutral) of coverage
- **Temporal trends** in coverage over 10 years
- **Source diversity** across political leanings

**Current Status**: Data collected, annotated, and analyzed. Ready for report writing.

---

## Project Statistics

- **Total Articles**: 1,778 (exceeds 500 requirement by 3.5x)
- **Annotated Articles**: 1,765 (99.3% success rate)
- **Time Period**: January 2015 - November 2025
- **Unique Sources**: 329 news outlets
- **Topics Identified**: 8 distinct categories
- **Visualizations**: 7 high-quality plots generated

---

## Project Structure

```
├── data/                          # All data files
│   ├── final_articles.csv         # Main dataset (1,778 articles)
│   ├── coded_articles.csv         # Annotated dataset (topics + sentiment)
│   ├── topic_summaries.csv        # LLM-generated topic descriptions
│   ├── topic_keywords.csv         # TF-IDF keywords for each topic
│   ├── source_analysis.csv        # Source distribution by leaning
│   └── analysis_results/          # All visualization plots
│
├── scripts/                       # Executable CLI scripts
│   ├── collect_data.py            # Collect articles from APIs
│   ├── process_data.py            # Merge and clean data
│   ├── analyze_data.py            # Generate statistics and plots
│   ├── annotate_data.py           # Run LLM annotation
│   └── prepare_coding_sample.py  # Create manual coding sample
│
├── src/                           # Source code (modules)
│   ├── config.py                  # Configuration and paths
│   ├── collection.py              # API collectors
│   ├── processing.py              # Data processing logic
│   ├── analysis.py                # Analysis and visualization
│   └── annotation.py              # LLM annotation logic
│
├── coding/                        # Codebook and manual coding
│   └── CODEBOOK_DRAFT.md          # Topic definitions
│
├── requirements.txt               # Python dependencies
├── .env.example                   # Example environment variables
└── README.md                      # This file
```

---

## Quick Start for Teammates

### 1. Setup Environment

```bash
# Clone/navigate to project
cd "COMP 370/Final Project"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```bash
NEWS_API_KEY=your_key_here
THENEWSAPI_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

> **Note**: You don't need API keys if you're only analyzing existing data.

### 3. Explore the Data

```bash
# View summary statistics
python scripts/analyze_data.py --summary

# Generate all visualizations
python scripts/analyze_data.py --all
```

---

## Available Data Files

### Primary Datasets

| File | Description | Size |
|------|-------------|------|
| `data/final_articles.csv` | Merged dataset of all collected articles | 1,778 articles |
| `data/coded_articles.csv` | **Main annotated dataset** with topics & sentiment | 1,765 articles |

### Analysis Outputs

| File | Description | Use in Report |
|------|-------------|---------------|
| `data/topic_summaries.csv` | LLM-generated descriptions of each topic | Results section |
| `data/topic_keywords.csv` | Top 10 TF-IDF keywords per topic | Topic characterization |
| `data/source_analysis.csv` | Article counts by source and leaning | Data section |

### Visualizations (`data/analysis_results/`)

1. **articles_by_year.png** - Temporal distribution of articles
2. **top_sources.png** - Most frequent news outlets
3. **topic_distribution.png** - Breakdown of 8 topics
4. **sentiment_distribution.png** - Overall sentiment (Pos/Neg/Neu)
5. **sentiment_by_topic.png** - Sentiment variance across topics
6. **topics_over_time.png** - Topic evolution (2015-2025)
7. **sentiment_over_time.png** - Sentiment trends over time

---

## Topic Categories

Our codebook defines 8 topics:

1. **LEGAL** - Investigations, trials, fraud cases, indictments
2. **ELECTION** - Campaigns, rallies, polls, election results
3. **POLICY** - Government policies, executive actions, legislation
4. **JAN6** - January 6th Capitol riot and aftermath
5. **PERSONAL** - Family, lifestyle, personal ventures
6. **MEDIA** - Social media, press interactions, bans
7. **GOP** - Republican Party dynamics and endorsements
8. **OTHER** - Miscellaneous topics not fitting above categories

See `coding/CODEBOOK_DRAFT.md` for detailed definitions.

---

## Scripts Usage

### Data Collection (Optional - Data already collected)

```bash
# Collect from all sources
python scripts/collect_data.py --source all

# Collect from specific source
python scripts/collect_data.py --source newsapi
```

### Data Processing

```bash
# Merge raw datasets
python scripts/process_data.py
```

### Analysis

```bash
# Generate summary statistics
python scripts/analyze_data.py --summary

# Generate visualizations only
python scripts/analyze_data.py --visualize

# Run everything
python scripts/analyze_data.py --all
```

### Annotation (Already completed)

```bash
# Annotate remaining articles
python scripts/annotate_data.py
```

---

## For Report Writing

### Required Elements Checklist

- [x] **Data Collection** (10 pts)
  - 1,778 articles collected
  - Balanced sources (Left/Right/Center)
  - See: `data/source_analysis.csv`

- [x] **Topic Design** (15 pts)  
  - 8 well-defined topics
  - See: `coding/CODEBOOK_DRAFT.md`

- [x] **Annotation** (10 pts)
  - 99.3% success rate using LLM
  - See: `data/coded_articles.csv`

- [x] **Results** (20 pts)
  - Topic Distribution: `data/analysis_results/topic_distribution.png`
  - TF-IDF Keywords: `data/topic_keywords.csv`
  - Topic Summaries: `data/topic_summaries.csv`

- [ ] **Findings** (20 pts) - **TO DO**: Write Discussion section
- [ ] **Style** (10 pts) - **TO DO**: Format in AAAI template

### Key Files to Reference

1. **Introduction/Data Section**:
   - `data/source_analysis.csv` - Source distribution
   - `data/analysis_results/articles_by_year.png` - Temporal coverage

2. **Methods Section**:
   - `coding/CODEBOOK_DRAFT.md` - Topic definitions
   - Describe LLM annotation process

3. **Results Section**:
   - `data/topic_distribution.png` - Topic breakdown
   - `data/topic_keywords.csv` - TF-IDF characterization
   - `data/topic_summaries.csv` - Topic descriptions
   - `data/sentiment_by_topic.png` - Sentiment analysis

4. **Discussion Section**:
   - `data/topics_over_time.png` - Temporal trends
   - `data/sentiment_over_time.png` - Sentiment evolution

---

## Next Steps

1. **Write the Report** using AAAI template
2. **Copy visualizations** from `data/analysis_results/` into report
3. **Reference data files** when writing Data/Methods/Results sections
4. **Cite key findings** from the analysis outputs

---

## Questions?

- **Data issues**: Check `src/config.py` for file paths
- **Visualization issues**: Run `python scripts/analyze_data.py --all`
- **Missing dependencies**: Run `pip install -r requirements.txt`

---

## Additional Documentation

- `GETTING_STARTED.md` - Quick onboarding guide for new team members
- `data_sources.md` - Detailed source information
- `research_design.md` - Initial research questions and design
- `THENEWSAPI_SETUP.md` - API setup instructions
