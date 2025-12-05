import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from . import config

class Analyzer:
    def __init__(self):
        # Try to load coded articles first, as it has the annotations
        if os.path.exists(config.DATA_DIR / 'coded_articles.csv'):
            print(f"Loading annotated data from {config.DATA_DIR / 'coded_articles.csv'}...")
            self.df = pd.read_csv(config.DATA_DIR / 'coded_articles.csv')
        elif os.path.exists(config.FINAL_ARTICLES_FILE):
            print(f"Loading raw data from {config.FINAL_ARTICLES_FILE} (no annotations)...")
            self.df = pd.read_csv(config.FINAL_ARTICLES_FILE)
        else:
            print(f"Error: No data found.")
            self.df = None
            return

        # Preprocessing
        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
        self.df['year'] = self.df['date'].dt.year
        
        # Ensure annotation columns exist even if empty
        if 'PRIMARY_TOPIC' not in self.df.columns:
            self.df['PRIMARY_TOPIC'] = None
        if 'SENTIMENT (Pos/Neg/Neu)' not in self.df.columns:
            self.df['SENTIMENT (Pos/Neg/Neu)'] = None
            
        # Rename sentiment column for easier access if needed
        self.df.rename(columns={'SENTIMENT (Pos/Neg/Neu)': 'sentiment'}, inplace=True)
        
        # Standardize Sentiment Values
        self.df['sentiment'] = self.df['sentiment'].replace({
            'Positive': 'POS', 'Negative': 'NEG', 'Neutral': 'NEU'
        })

    def generate_summary(self):
        if self.df is None: return
        
        print("=" * 70)
        print("TRUMP MEDIA COVERAGE DATASET - COMPREHENSIVE SUMMARY")
        print("=" * 70)
        
        print(f"Total Articles: {len(self.df):,}")
        print(f"Date Range: {self.df['date'].min()} to {self.df['date'].max()}")
        print(f"Unique Sources: {self.df['source'].nunique()}")
        
        print("\nTop Sources:")
        print(self.df['source'].value_counts().head(10))
        
        self.analyze_sources()
        self.analyze_topics_text()
        self.analyze_sentiment_text()
        self.analyze_statistics() # Added statistical analysis
        self.analyze_tfidf()

    def analyze_sources(self):
        if self.df is None: return
        
        source_leanings = {
            'cnn.com': 'Left', 'msnbc.com': 'Left', 'washingtonpost.com': 'Left', 'nytimes.com': 'Left',
            'foxnews.com': 'Right', 'breitbart.com': 'Right', 'nypost.com': 'Right',
            'reuters.com': 'Center', 'apnews.com': 'Center', 'usatoday.com': 'Center'
        }
        
        def get_leaning(source):
            return source_leanings.get(str(source).lower(), 'Other')
            
        self.df['leaning'] = self.df['source'].apply(get_leaning)
        
        print("\nLeaning Distribution:")
        print(self.df['leaning'].value_counts())
        
        # Save source analysis
        source_counts = self.df['source'].value_counts().reset_index()
        source_counts.columns = ['source', 'article_count']
        source_counts['leaning'] = source_counts['source'].apply(get_leaning)
        source_counts.to_csv(config.SOURCE_ANALYSIS_FILE, index=False)
        print(f"\nSaved source analysis to {config.SOURCE_ANALYSIS_FILE}")

    def analyze_topics_text(self):
        if self.df['PRIMARY_TOPIC'].isnull().all():
            print("\nTopic Analysis: No topic annotations found.")
            return

        print("\nTopic Distribution:")
        print(self.df['PRIMARY_TOPIC'].value_counts())

    def analyze_sentiment_text(self):
        if self.df['sentiment'].isnull().all():
            print("\nSentiment Analysis: No sentiment annotations found.")
            return

        print("\nSentiment Distribution:")
        print(self.df['sentiment'].value_counts())

    def analyze_tfidf(self):
        if self.df['PRIMARY_TOPIC'].isnull().all(): return
        
        print("\nTop Keywords per Topic (TF-IDF):")
        
        # Filter for valid topics
        valid_df = self.df.dropna(subset=['PRIMARY_TOPIC', 'title'])
        topics = valid_df['PRIMARY_TOPIC'].unique()
        
        keywords_list = []
        for topic in topics:
            topic_docs = valid_df[valid_df['PRIMARY_TOPIC'] == topic]['title']
            if len(topic_docs) < 5: continue
            
            vectorizer = TfidfVectorizer(stop_words='english', max_features=10)
            try:
                tfidf_matrix = vectorizer.fit_transform(topic_docs)
                feature_names = vectorizer.get_feature_names_out()
                print(f"  {topic}: {', '.join(feature_names)}")
                keywords_list.append({'topic': topic, 'keywords': ', '.join(feature_names)})
            except ValueError:
                print(f"  {topic}: (Not enough data for TF-IDF)")
                
        # Save to CSV
        if keywords_list:
            pd.DataFrame(keywords_list).to_csv(config.DATA_DIR / 'topic_keywords.csv', index=False)
            print(f"\nSaved TF-IDF keywords to {config.DATA_DIR / 'topic_keywords.csv'}")

    def analyze_statistics(self):
        """Perform statistical tests for analytical depth"""
        if self.df is None: return
        
        print("\n" + "="*60)
        print("STATISTICAL ANALYSIS RESULTS")
        print("="*60)
        
        # 1. Chi-square: Topic vs Source Leaning
        if 'leaning' not in self.df.columns:
            self.analyze_sources() # Ensure leaning is populated
            
        print("\n1. Chi-Square Test: Topic Distribution by Political Leaning")
        contingency = pd.crosstab(self.df['leaning'], self.df['PRIMARY_TOPIC'])
        chi2, p, dof, expected = stats.chi2_contingency(contingency)
        print(f"Chi2 Statistic: {chi2:.2f}, p-value: {p:.4e}")
        if p < 0.05:
            print("-> SIGNIFICANT difference in topic coverage across political leanings.")
        else:
            print("-> No significant difference in topic coverage.")

        # 2. Correlation: Sentiment vs Topic
        print("\n2. Sentiment Analysis by Topic")
        # Convert sentiment to numeric for analysis
        sent_map = {'POS': 1, 'NEU': 0, 'NEG': -1}
        self.df['sentiment_score'] = self.df['sentiment'].map(sent_map)
        
        topic_sent = self.df.groupby('PRIMARY_TOPIC')['sentiment_score'].agg(['mean', 'count', 'std'])
        topic_sent['se'] = topic_sent['std'] / np.sqrt(topic_sent['count']) # Standard Error
        print(topic_sent.sort_values('mean'))
        
        # ANOVA to test if sentiment differs by topic
        topics_list = [group['sentiment_score'].dropna().values for name, group in self.df.groupby('PRIMARY_TOPIC')]
        f_stat, p_val = stats.f_oneway(*topics_list)
        print(f"\nANOVA (Sentiment by Topic): F={f_stat:.2f}, p={p_val:.4e}")
        
        # 3. Time Series Trend (Mann-Kendall or simple regression)
        print("\n3. Temporal Trends (Linear Regression on Sentiment)")
        # Convert date to ordinal for regression
        valid_dates = self.df.dropna(subset=['date', 'sentiment_score'])
        valid_dates['date_ordinal'] = valid_dates['date'].map(pd.Timestamp.toordinal)
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            valid_dates['date_ordinal'], valid_dates['sentiment_score']
        )
        print(f"Slope: {slope:.2e} (sentiment change per day)")
        print(f"R-squared: {r_value**2:.4f}")
        print(f"P-value: {p_value:.4e}")
        if p_value < 0.05:
            trend = "improving" if slope > 0 else "declining"
            print(f"-> Significant {trend} trend in sentiment over time.")
        else:
            print("-> No significant linear trend in sentiment over time.")

    def visualize(self):
        if self.df is None: return
        
        config.ANALYSIS_RESULTS_DIR.mkdir(exist_ok=True)
        sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
        
        # Professional Color Palette (ColorBrewer-like)
        # POS=Green, NEG=Red, NEU=Gray
        sentiment_colors = {'POS': '#2ca02c', 'NEG': '#d62728', 'NEU': '#7f7f7f'} 
        topic_palette = sns.color_palette("Paired", n_colors=len(self.df['PRIMARY_TOPIC'].unique()))
        
        # 1. Articles by Year
        plt.figure(figsize=(10, 6))
        year_counts = self.df['year'].value_counts().sort_index()
        ax = sns.barplot(x=year_counts.index, y=year_counts.values, color="#1f77b4")
        plt.title(f'Temporal Distribution of Articles (n={len(self.df)})', fontsize=14, pad=15)
        plt.ylabel('Number of Articles')
        plt.xlabel('Year')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(config.ANALYSIS_RESULTS_DIR / 'articles_by_year.png', dpi=300)
        plt.close()
        print(f"Saved articles_by_year.png")
        
        # 2. Top Sources
        plt.figure(figsize=(10, 8))
        top_sources = self.df['source'].value_counts().head(15)
        sns.barplot(y=top_sources.index, x=top_sources.values, palette="viridis")
        plt.title(f'Top 15 News Sources (Total Sources={self.df["source"].nunique()})', fontsize=14)
        plt.xlabel('Number of Articles')
        plt.tight_layout()
        plt.savefig(config.ANALYSIS_RESULTS_DIR / 'top_sources.png', dpi=300)
        plt.close()
        print(f"Saved top_sources.png")

        # 3. Topic Distribution
        if not self.df['PRIMARY_TOPIC'].isnull().all():
            plt.figure(figsize=(12, 6))
            topic_counts = self.df['PRIMARY_TOPIC'].value_counts()
            ax = sns.barplot(x=topic_counts.index, y=topic_counts.values, palette=topic_palette)
            plt.title(f'Distribution of Topics (n={len(self.df.dropna(subset=["PRIMARY_TOPIC"]))})', fontsize=14)
            plt.xticks(rotation=45, ha='right')
            plt.ylabel('Number of Articles')
            
            # Add counts on top
            for i, v in enumerate(topic_counts.values):
                ax.text(i, v + 5, str(v), ha='center', fontsize=10)
                
            plt.tight_layout()
            plt.savefig(config.ANALYSIS_RESULTS_DIR / 'topic_distribution.png', dpi=300)
            plt.close()
            print(f"Saved topic_distribution.png")

        # 4. Sentiment Distribution
        if not self.df['sentiment'].isnull().all():
            plt.figure(figsize=(8, 6))
            sentiment_counts = self.df['sentiment'].value_counts()
            order = ['POS', 'NEU', 'NEG']
            ax = sns.barplot(x=sentiment_counts.index, y=sentiment_counts.values, order=order, palette=sentiment_colors)
            plt.title(f'Overall Sentiment Distribution (n={len(self.df.dropna(subset=["sentiment"]))})', fontsize=14)
            plt.ylabel('Number of Articles')
            
            # Add percentages
            total = sum(sentiment_counts.values)
            for i, cat in enumerate(order):
                count = sentiment_counts.get(cat, 0)
                pct = (count/total)*100
                ax.text(i, count + 10, f"{pct:.1f}%", ha='center', fontsize=11, fontweight='bold')
                
            plt.savefig(config.ANALYSIS_RESULTS_DIR / 'sentiment_distribution.png', dpi=300)
            plt.close()
            print(f"Saved sentiment_distribution.png")

            # 5. Sentiment by Topic (Normalized Stacked Bar)
            plt.figure(figsize=(12, 7))
            ct = pd.crosstab(self.df['PRIMARY_TOPIC'], self.df['sentiment'], normalize='index')
            cols = [c for c in ['NEG', 'NEU', 'POS'] if c in ct.columns]
            ct = ct[cols] # Reorder
            
            ct.plot(kind='bar', stacked=True, color=[sentiment_colors.get(c, '#333') for c in cols], 
                    figsize=(12, 7), width=0.8)
            
            plt.title('Sentiment Proportion by Topic', fontsize=14)
            plt.xlabel('Topic')
            plt.ylabel('Proportion of Articles')
            plt.legend(title='Sentiment', bbox_to_anchor=(1.02, 1), loc='upper left')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(config.ANALYSIS_RESULTS_DIR / 'sentiment_by_topic.png', dpi=300)
            plt.close()
            print(f"Saved sentiment_by_topic.png")
            
            # 5b. Sentiment Score by Topic with Error Bars (NEW)
            if 'sentiment_score' in self.df.columns:
                plt.figure(figsize=(12, 6))
                sns.barplot(x='PRIMARY_TOPIC', y='sentiment_score', data=self.df, 
                            palette=topic_palette, capsize=.1, errorbar=('ci', 95))
                plt.title('Mean Sentiment Score by Topic (with 95% CI)', fontsize=14)
                plt.ylabel('Sentiment Score (-1=Neg, 0=Neu, 1=Pos)')
                plt.axhline(0, color='black', linestyle='-', linewidth=0.8)
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(config.ANALYSIS_RESULTS_DIR / 'sentiment_score_by_topic.png', dpi=300)
                plt.close()
                print(f"Saved sentiment_score_by_topic.png")

        # 6. Topics over Time (Line Chart)
        if not self.df['PRIMARY_TOPIC'].isnull().all():
            plt.figure(figsize=(12, 7))
            ct_year = pd.crosstab(self.df['year'], self.df['PRIMARY_TOPIC'])
            
            # Plot
            ct_year.plot(kind='line', marker='o', linewidth=2.5, figsize=(12, 7), colormap='tab10')
            
            plt.title('Evolution of Topics over Time (2015-2025)', fontsize=14)
            plt.xlabel('Year')
            plt.ylabel('Article Count')
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.legend(title='Topic', bbox_to_anchor=(1.02, 1), loc='upper left')
            plt.tight_layout()
            plt.savefig(config.ANALYSIS_RESULTS_DIR / 'topics_over_time.png', dpi=300)
            plt.close()
            print(f"Saved topics_over_time.png")
            
        # 7. Sentiment over Time (Line Chart with Trend)
        if not self.df['sentiment'].isnull().all():
            plt.figure(figsize=(12, 7))
            
            # Aggregate sentiment score by year
            sent_trend = self.df.groupby('year')['sentiment_score'].mean()
            
            # Plot mean sentiment
            plt.plot(sent_trend.index, sent_trend.values, marker='o', linewidth=3, color='#2c3e50', label='Mean Sentiment')
            
            # Add trendline
            z = np.polyfit(sent_trend.index, sent_trend.values, 1)
            p = np.poly1d(z)
            plt.plot(sent_trend.index, p(sent_trend.index), "r--", alpha=0.8, label=f'Trend (slope={z[0]:.3f})')
            
            plt.title('Evolution of Mean Sentiment (2015-2025)', fontsize=14)
            plt.xlabel('Year')
            plt.ylabel('Mean Sentiment Score (-1 to +1)')
            plt.axhline(0, color='gray', linestyle=':', alpha=0.5)
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.legend()
            plt.tight_layout()
            plt.savefig(config.ANALYSIS_RESULTS_DIR / 'sentiment_over_time.png', dpi=300)
            plt.close()
            print(f"Saved sentiment_over_time.png")
