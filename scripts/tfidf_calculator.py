import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import sys
import seaborn as sns
import matplotlib.pyplot as plt

INPUT_PATH = "../data/ANNOTATED_trump_dataset_500.csv"
TEXT_COLS = ["title", "description"]
TOPIC_COLS = "PRIMARY_TOPIC"
OUTPUT_PATH = "tf-idf.csv"
EXPECTED_CATEGORIES = [
    "LEGAL",
    "ELECTION",
    "POLICY",
    "JAN6",
    "PERSONAL",
    "MEDIA",
    "GOP",
    "OTHER",
]
# Exclude from word counts
CUSTOM_STOP_WORDS = ["donald", "trump", "jan", "republicans", "6th"]
TOP_10 = 10


def load_and_prepare_data(input_path, text_cols, topic_cols, expected_cats):
    try:
        # Load Data:
        df = pd.read_csv(INPUT_PATH)
        # Fill missing values with empty strings
        for col in text_cols:
            df[col] = df[col].fillna("")

        df["combined_text"] = df[text_cols].agg(" ".join, axis=1)

        initial_row_count = len(df)
        df = df[df[topic_cols].isin(expected_cats)]
        if len(df) < initial_row_count:
            print(
                f"Note: Filtered ot {initial_row_count - len(df)} rows that did not match the defined categories"
            )
        # Group by topic and combine all text into 1 string per topic
        topic_text_agg = (
            df.groupby(topic_cols)["combined_text"].apply(" ".join).to_dict()
        )
        if not topic_text_agg:
            raise ValueError(
                "No data found for the defined topics after loading and filtering the CSV."
            )
        print(
            f"Successfully loaded and aggregated text for {len(topic_text_agg)} categories."
        )

        return topic_text_agg
    except FileNotFoundError:
        print(f"Error: File {input_path} not found")
    except Exception as e:
        print(f"An unexpected error occurred during data loading: {e}")
    return {}


def calc_tfidf(topic_text, top_n, int=10):
    if not topic_text:
        return pd.DataFrame()
    corpus = list(topic_text.values())
    categories = list(topic_text.keys())
    # Initializing & Fitting FT-IDF Vectorizer:
    """
    Use Tfidvectorizer to calculate the scores and set stop_words = 'english' to remove common words like 'the', 'a', 'is', etc
    mid_df = 2 ensures a word appears at least twice in the categories to be considered. 
    """
    vectorizer = TfidfVectorizer(
        stop_words=list(TfidfVectorizer(stop_words="english").get_stop_words())
        + CUSTOM_STOP_WORDS
    )
    # Checks if vectorizer is empty
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError as e:
        print(
            f"Error fitting TF-IDF model: {e}. This usually means the input text is too sparse or empty."
        )
        print("Please check your input data for content.")
        return pd.DataFrame()

    feature_names = vectorizer.get_feature_names_out()
    df_tfidf = pd.DataFrame(
        tfidf_matrix.toarray(), columns=feature_names, index=categories
    )
    df_to_concat = []
    for category in categories:
        num_words = min(top_n, len(df_tfidf.columns))
        top_words = df_tfidf.loc[category].sort_values(ascending=False).head(num_words)

        top_keywords = top_words[top_words > 0]
        print(f"\n Category: {category}")
        if top_keywords.empty:
            print("Not enough unique key words to calculate TF-IDF for this category")
        else:
            df_result = top_keywords.reset_index()
            df_result.columns = ["Keyword", "TFIDF_Score"]
            df_result["Category"] = category
            df_to_concat.append(df_result)

            for _, row in df_result.iterrows():
                print(f"{row['Keyword']}: {row['TFIDF_Score']:.4f}")
    if df_to_concat:
        final_df = pd.concat(df_to_concat, ignore_index=True)
        final_df["TFIDF_Score"] = final_df["TFIDF_Score"].round(3)
        final_df["TFIDF_Score"] = final_df["TFIDF_Score"].apply(lambda x: f"{x:.3f}")
        return final_df[["Category", "Keyword", "TFIDF_Score"]]
    return pd.DataFrame()


def main():
    topic_texts = load_and_prepare_data(
        input_path=INPUT_PATH,
        text_cols=TEXT_COLS,
        topic_cols=TOPIC_COLS,
        expected_cats=EXPECTED_CATEGORIES,
    )
    if not topic_texts:
        print("Analysis stopped because of loading error")
        sys.exit()

    final_df = calc_tfidf(topic_texts, top_n=10)
    # visualize_tfidf_scores(final_df)

    if not final_df.empty:
        try:
            final_df.to_csv(OUTPUT_PATH, index=False)
            print(f"Output successfull saved")
            print(f"Successfully calculated and saved results to: {OUTPUT_PATH}")
        except Exception as e:
            print(f"\n Error saving file to csv: {e}")
    else:
        print("\n Output Skipped: No results to save")


def visualize_tfidf_scores(df):
    if df is None or df.empty:
        print("No data to process or visualize")
        return
    # Display the full table
    print("--- TF-IDF Score Table (All Results) ---")
    print(df.to_markdown(index=False, floatfmt=".3f"))
    print("\n" + "=" * 50 + "\n")

    top_keywords_df = df.groupby("Category").head(TOP_10).reset_index(drop=True)
    top_keywords_df = top_keywords_df.sort_values(
        by=["Category", "TFIDF_Score"], ascending=[True, False]
    )
    plt.style.use("fivethirtyeight")
    g = sns.catplot(
        data=top_keywords_df,
        y="Keyword",
        x="TFIDF_Score",
        col="Category",
        kind="bar",
        col_wrap=2,
        sharex=False,
        palette="viridis",
        height=5,
        aspect=1.5,
    )
    g.fig.suptitle(
        f"Top {TOP_10} Keywords by TF-IDF Score Across Topics",
        y=1.02,
        fontsize=16,
        fontweight="bold",
    )
    for ax in g.axes.flat:
        if ax.get_title():
            title = ax.get_title().replace("Category = ", "")
            ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_xlabel("TF-IDF Score", fontsize=10)
        ax.set_ylabel("Keyword", fontsize=10)
        ax.invert_yaxis()

        plt.tight_layout(rect=[0, 0, 1, 0.98])
        plt.show()


if __name__ == "__main__":
    main()
