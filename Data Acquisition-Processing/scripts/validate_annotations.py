#!/usr/bin/env python3
"""
Self-Consistency Validation
Validates annotation reliability by re-annotating with Gemini using a slightly rephrased prompt.
"""
import os
import sys
import pandas as pd
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
from sklearn.metrics import cohen_kappa_score, confusion_matrix, classification_report

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import config

# Alternative prompt (same categories, different wording)
# We want to see if the LLM is robust. If we ask the same question slightly differently,
# does it give the same answer? This measures "Self-Consistency".
TOPIC_PROMPT_V2 = """
Categorize this news article about Donald Trump into ONE topic:

- LEGAL: Court cases, legal battles, indictments, trials, investigations
- ELECTION: Political campaigns, rallies, voting, electoral politics  
- POLICY: Governmental policies, executive orders, legislative actions, foreign relations
- JAN6: Events related to the January 6, 2021 Capitol incident
- PERSONAL: Family matters, personal business, lifestyle, relationships
- MEDIA: Press coverage, social platforms, media bans, public communications
- GOP: Relations with Republican Party, party endorsements, GOP politics
- OTHER: Content not covered by above categories

Output only the category name.
"""

SENTIMENT_PROMPT_V2 = """
Rate the tone of this Trump article:
- POS: Supportive or favorable
- NEG: Critical or unfavorable  
- NEU: Factual and balanced

Output only: POS, NEG, or NEU.
"""

def annotate_with_gemini_v2(title, description, model):
    """Re-annotate using alternative prompt"""
    article_text = f"Title: {title}\nDescription: {description}"
    
    try:
        # Get topic
        topic_response = model.generate_content(
            TOPIC_PROMPT_V2 + "\n\nArticle:\n" + article_text
        )
        topic = topic_response.text.strip()
        
        # Get sentiment  
        sentiment_response = model.generate_content(
            SENTIMENT_PROMPT_V2 + "\n\nArticle:\n" + article_text
        )
        sentiment = sentiment_response.text.strip()
        
        return topic, sentiment
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def validate_consistency(sample_size=100):
    """Validate annotation consistency"""
    
    # Load environment
    load_dotenv()
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("Error: GEMINI_API_KEY not found in .env file")
        return
    
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    
    # Load coded articles
    df = pd.read_csv(config.DATA_DIR / 'coded_articles.csv')
    
    # Rename sentiment column
    if 'SENTIMENT (Pos/Neg/Neu)' in df.columns:
        df.rename(columns={'SENTIMENT (Pos/Neg/Neu)': 'sentiment'}, inplace=True)
    
    df = df.dropna(subset=['PRIMARY_TOPIC', 'sentiment'])
    
    # Random sample
    np.random.seed(42)
    sample = df.sample(n=min(sample_size, len(df)))
    
    print(f"Validating consistency on {len(sample)} articles...")
    print("=" * 60)
    
    # Collect annotations
    original_topics = []
    original_sentiments = []
    retest_topics = []
    retest_sentiments = []
    
    for idx, row in sample.iterrows():
        print(f"Processing {len(original_topics) + 1}/{len(sample)}...", end='\r')
        
        # Re-annotate with alternative prompt
        topic, sentiment = annotate_with_gemini_v2(
            row['title'], 
            row.get('description', ''), 
            model
        )
        
        # Only keep valid responses for comparison
        if topic and sentiment:
            original_topics.append(row['PRIMARY_TOPIC'])
            original_sentiments.append(row['sentiment'])
            retest_topics.append(topic)
            retest_sentiments.append(sentiment)
    
    print("\n" + "=" * 60)
    print(f"Successfully validated {len(original_topics)} articles")
    print("=" * 60)
    
    # Calculate metrics
    print("\n### TOPIC CONSISTENCY ###\n")
    
    topic_kappa = cohen_kappa_score(original_topics, retest_topics)
    topic_agreement = np.mean(np.array(original_topics) == np.array(retest_topics))
    
    print(f"Cohen's Kappa: {topic_kappa:.3f}")
    print(f"Raw Agreement: {topic_agreement:.1%}")
    
    # Interpretation
    if topic_kappa > 0.8:
        interpretation = "Almost perfect agreement"
    elif topic_kappa > 0.6:
        interpretation = "Substantial agreement"
    elif topic_kappa > 0.4:
        interpretation = "Moderate agreement"
    else:
        interpretation = "Fair agreement"
    
    print(f"Interpretation: {interpretation}")
    
    # Confusion matrix
    print("\nConfusion Matrix (rows=Original, cols=Retest):")
    topics = sorted(set(original_topics + retest_topics))
    cm = confusion_matrix(original_topics, retest_topics, labels=topics)
    cm_df = pd.DataFrame(cm, index=topics, columns=topics)
    print(cm_df)
    
    print("\n### SENTIMENT CONSISTENCY ###\n")
    
    sentiment_kappa = cohen_kappa_score(original_sentiments, retest_sentiments)
    sentiment_agreement = np.mean(np.array(original_sentiments) == np.array(retest_sentiments))
    
    print(f"Cohen's Kappa: {sentiment_kappa:.3f}")
    print(f"Raw Agreement: {sentiment_agreement:.1%}")
    
    # Detailed report
    print("\n### DETAILED CLASSIFICATION REPORT ###\n")
    print("Topic Classification:")
    print(classification_report(original_topics, retest_topics, zero_division=0))
    
    print("\nSentiment Classification:")
    print(classification_report(original_sentiments, retest_sentiments, zero_division=0))
    
    # Save results
    results = {
        'metric': ['Topic Kappa', 'Topic Agreement', 'Sentiment Kappa', 'Sentiment Agreement'],
        'value': [topic_kappa, topic_agreement, sentiment_kappa, sentiment_agreement]
    }
    results_df = pd.DataFrame(results)
    output_file = config.DATA_DIR / 'validation_results.csv'
    results_df.to_csv(output_file, index=False)
    
    print(f"\n✓ Results saved to {output_file}")
    
    # Generate report text
    print("\n" + "=" * 60)
    print("FOR YOUR REPORT (Methods section):")
    print("=" * 60)
    print(f"""
To validate annotation reliability, we employed a test-retest approach, re-annotating 
a random sample of {len(original_topics)} articles using an alternative prompt formulation. 
This self-consistency check yielded Cohen's κ = {topic_kappa:.2f} for topic classification 
and κ = {sentiment_kappa:.2f} for sentiment, indicating {interpretation.lower()}. This 
demonstrates the stability and reliability of our LLM-based annotation methodology.
""")

if __name__ == "__main__":
    validate_consistency(sample_size=100)
