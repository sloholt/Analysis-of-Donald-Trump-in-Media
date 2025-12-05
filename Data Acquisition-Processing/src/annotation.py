import os
import google.generativeai as genai
import pandas as pd
import time
import json
from typing import Dict, Optional
from . import config

class Annotator:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            print("⚠ WARNING: GEMINI_API_KEY not set.")
            self.model = None
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')

    def classify_article(self, title: str, description: str) -> Optional[Dict]:
        if not self.model: return None
        
        prompt = f"""
        You are a political media analyst. Classify the following news article about Donald Trump.
        
        Title: {title}
        Description: {description}
        
        Topics:
        - LEGAL: Investigations, lawsuits, trials, indictments, fraud, hush money.
        - ELECTION: Campaigning, rallies, polls, debates, voting, primaries, VP picks.
        - JAN6: Capitol riot, election denial, "Stop the Steal", democracy threats.
        - POLICY: Immigration (border wall), trade (tariffs), taxes, healthcare, foreign policy.
        - PERSONAL: Family (Melania, Ivanka), business (Trump Org), health, wealth, golf.
        - MEDIA: Feuds with press, Truth Social, celebrity feuds, pop culture.
        - GOP: Republican party politics, endorsements, infighting, McCarthy/McConnell.
        - OTHER: Anything not fitting the above categories.
        
        Task:
        1. Identify the PRIMARY_TOPIC (must be one of the codes above).
        2. Identify the SENTIMENT (POS, NEG, NEU).
           - POS: Favorable/Praise/Achievement
           - NEG: Critical/Scandal/Failure
           - NEU: Factual/Balanced
        
        Return ONLY a JSON object with this format:
        {{
            "PRIMARY_TOPIC": "CODE",
            "SENTIMENT": "CODE"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:-3]
            elif text.startswith('```'):
                text = text[3:-3]
            return json.loads(text)
        except Exception as e:
            if "429" in str(e):
                print("  ⚠ Rate limit hit. Waiting 30 seconds...")
                time.sleep(30)
                try:
                    response = self.model.generate_content(prompt)
                    text = response.text.strip()
                    if text.startswith('```json'):
                        text = text[7:-3]
                    elif text.startswith('```'):
                        text = text[3:-3]
                    return json.loads(text)
                except Exception as e2:
                    print(f"  Error after retry: {e2}")
                    return None
            else:
                print(f"  Error classifying: {e}")
                return None

    def annotate_dataset(self, input_file=None, output_file=None):
        if not self.model: return

        input_path = input_file or config.FINAL_ARTICLES_FILE
        output_path = output_file or config.DATA_DIR / 'coded_articles.csv'
        
        print(f"Annotating {input_path} -> {output_path}")
        
        if os.path.exists(output_path):
            df = pd.read_csv(output_path)
            print(f"Resuming... {len(df)} articles already in output.")
            
            # Load original input to get the full list
            df_input = pd.read_csv(input_path)
            
            # Identify missing
            if 'article_id' in df.columns and 'article_id' in df_input.columns:
                processed_ids = set(df['article_id'].astype(str))
                to_process_indices = df_input[~df_input['article_id'].astype(str).isin(processed_ids)].index.tolist()
                # We need to append these to df
                to_append = df_input.loc[to_process_indices].copy()
                to_append['PRIMARY_TOPIC'] = ''
                to_append['SENTIMENT (Pos/Neg/Neu)'] = ''
                df = pd.concat([df, to_append], ignore_index=True)
            else:
                 # Fallback if IDs missing
                 if len(df) < len(df_input):
                    to_append = df_input.iloc[len(df):].copy()
                    to_append['PRIMARY_TOPIC'] = ''
                    to_append['SENTIMENT (Pos/Neg/Neu)'] = ''
                    df = pd.concat([df, to_append], ignore_index=True)
        else:
            print(f"Starting fresh from {input_path}")
            df = pd.read_csv(input_path)
            df['PRIMARY_TOPIC'] = ''
            df['SENTIMENT (Pos/Neg/Neu)'] = ''
            df.to_csv(output_path, index=False)

        # Process rows with empty topic
        to_process_indices = df.index[df['PRIMARY_TOPIC'].isna() | (df['PRIMARY_TOPIC'] == '')].tolist()
        total_to_process = len(to_process_indices)
        
        print(f"Articles remaining to annotate: {total_to_process}")
        if total_to_process == 0:
            print("All articles are already annotated!")
            return

        success_count = 0
        for i, idx in enumerate(to_process_indices):
            row = df.loc[idx]
            print(f"[{i+1}/{total_to_process}] Processing ID {row.get('article_id', idx)}: {str(row['title'])[:50]}...")
            
            result = self.classify_article(str(row['title']), str(row['description']))
            
            if result:
                df.at[idx, 'PRIMARY_TOPIC'] = result.get('PRIMARY_TOPIC', '')
                df.at[idx, 'SENTIMENT (Pos/Neg/Neu)'] = result.get('SENTIMENT', '')
                success_count += 1
            
            time.sleep(0.5) # Rate limit (Paid tier: ~60-100 RPM)
            
            if success_count % 5 == 0:
                df.to_csv(output_path, index=False)
                print(f"  Saved progress ({success_count} session total)...")
        
        df.to_csv(output_path, index=False)
        print(f"✓ Completed! Annotated {success_count} articles.")
