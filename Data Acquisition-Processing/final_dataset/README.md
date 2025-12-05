# Trump Media Coverage Dataset (2015-2025)

## Overview
This dataset contains **528 annotated news articles** about Donald Trump from North American sources, spanning January 2015 to November 2025. The dataset is balanced by political leaning and includes topic and sentiment classifications.

## Dataset Composition

### Political Balance
- **Left-leaning sources:** 199 articles (37.7%)
- **Right-leaning sources:** 199 articles (37.7%)
- **Center/Neutral sources:** 130 articles (24.6%)

### Topic Distribution
| Topic | Count | Description |
|-------|-------|-------------|
| ELECTION | 123 (23.3%) | Campaigns, rallies, polls, debates |
| POLICY | 86 (16.3%) | Immigration, trade, taxes, foreign policy |
| LEGAL | 83 (15.7%) | Investigations, lawsuits, trials |
| PERSONAL | 70 (13.3%) | Family, business, health, wealth |
| MEDIA | 60 (11.4%) | Press feuds, Truth Social |
| GOP | 58 (11.0%) | Republican party politics |
| JAN6 | 27 (5.1%) | January 6th, election denial |
| OTHER | 17 (3.2%) | Miscellaneous |

### Sentiment Distribution
| Sentiment | Count |
|-----------|-------|
| Neutral | 261 (49.4%) |
| Negative | 173 (32.8%) |
| Positive | 91 (17.2%) |

## File Structure
```
final_dataset/
├── trump_media_dataset_528.csv    # Main dataset
├── CODEBOOK.md                     # Annotation codebook
├── DATASET_SUMMARY.md              # Detailed statistics
└── README.md                       # This file
```

## Dataset Schema

### Columns
- `article_id`: Unique identifier for each article
- `source`: News source domain or name
- `date`: Publication date (YYYY-MM-DD)
- `title`: Article headline
- `description`: Article description/snippet
- `url`: Article URL
- `snippet`: Additional text snippet
- `PRIMARY_TOPIC`: Primary topic classification (see CODEBOOK.md)
- `SENTIMENT (Pos/Neg/Neu)`: Sentiment classification
- `is_north_american`: Boolean flag for North American source
- `leaning`: Political leaning (Left/Right/Center/Other)

## Data Collection

### Sources
**Left Sources:**
- CNN, MSNBC, The New York Times, Washington Post, Politico, HuffPost, Vox, Alternet, ABC News, CBS News, NBC News, Slate, Salon, The Atlantic, New Yorker

**Center Sources:**
- USA Today, Reuters, Bloomberg, NPR, PBS, The Hill, Forbes, Business Insider, National Archives, American Presidency Project

**Right Sources:**
- Fox News, Breitbart, New York Post, National Post, Washington Examiner, Wall Street Journal

### Collection Method
- Articles collected via TheNewsAPI and GNews API
- Date range: 2015-01-06 to 2025-11-26
- Query: "Donald Trump" OR "Trump"
- North American sources only (US and Canada)

## Annotation Method

### Automated Annotation
- **Tool:** Google Gemini API (gemini-flash-latest)
- **Input:** Article title and description
- **Output:** Topic and sentiment classification
- **Codebook:** See CODEBOOK.md for detailed category definitions

### Validation
- 100% annotation coverage (528/528 articles)
- Low "OTHER" category usage (3.2%) indicates good codebook fit
- Consistent with established political science frameworks

## Usage

### Loading the Dataset
```python
import pandas as pd

df = pd.read_csv('trump_media_dataset_528.csv')
print(df.head())
```

### Example Analysis
```python
# Topic distribution by political leaning
topic_by_leaning = pd.crosstab(df['PRIMARY_TOPIC'], df['leaning'])
print(topic_by_leaning)

# Sentiment distribution by political leaning
sentiment_by_leaning = pd.crosstab(df['leaning'], df['SENTIMENT (Pos/Neg/Neu)'])
print(sentiment_by_leaning)
```

## Citation
If you use this dataset, please cite:

```
Trump Media Coverage Dataset (2015-2025)
Balanced North American News Sources
Collected: November-December 2024
Source: TheNewsAPI, GNews API
Annotation: Google Gemini API
```

## License
This dataset is provided for educational and research purposes. News article content is subject to original publisher copyright. URLs and metadata are provided for reference only.

## Contact
For questions or issues with this dataset, please open an issue in the repository.

## Changelog
- **v1.0** (December 2024): Initial release with 528 balanced and annotated articles
