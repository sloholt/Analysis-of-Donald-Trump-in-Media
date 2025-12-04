import pandas as pd
import os

INPUT_FILE = "ANNOTATED_trump_dataset_500.csv"
POS_OUTPUT_TXT = "pos_descriptions.txt"
NEG_OUTPUT_TXT = "neg_descriptions.txt"
NEUTRAL_OUTPUT_TXT = "neu_descriptions.txt"


SENTIMENT_COL = "SENTIMENT (Pos/Neg/Neu)"
DESCRIPTION = "description"
TOPIC_COL = "PRIMARY_TOPIC"


def extract_descriptions(filter_col, description_col, target_value):
    if not os.path.exists(INPUT_FILE):
        print("Error: No input file found")
        return
    sentiment_upper = target_value.strip().upper()
    safe_name = target_value.strip().lower().replace(" ", "_")
    output_txt = f"{safe_name}_descriptions.txt"
    try:
        df = pd.read_csv(INPUT_FILE, low_memory=False)
        filtered_df = df[
            df[filter_col].astype(str).str.strip().str.upper() == sentiment_upper
        ]
        # Extract descriptions
        descriptions = filtered_df[description_col].astype(str).tolist()
        # Combine descriptions
        combined_text = "\n\n".join(descriptions)

        # Write to output file
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write(combined_text)
        print(f"Successfully combined all {target_value} and saved to {output_txt}!")

    except KeyError as e:
        print(f"Error: Column name missing: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def main():
    """
    SENTIMENTS_TO_PROCESS = ["NEG", "POS", "NEU"]

    for s in SENTIMENTS_TO_PROCESS:
        print(f"Processing sentiment: {s}")
        if s == "NEG":
            extract_descriptions(
                sentiment_col=SENTIMENT_COL,
                description_col=DESCRIPTION,
                target_sentiment=s,
                output_txt=NEG_OUTPUT_TXT,
            )
        elif s == "POS":
            extract_descriptions(
                sentiment_col=SENTIMENT_COL,
                description_col=DESCRIPTION,
                target_sentiment=s,
                output_txt=POS_OUTPUT_TXT,
            )
        elif s == "NEU":
            extract_descriptions(
                sentiment_col=SENTIMENT_COL,
                description_col=DESCRIPTION,
                target_sentiment=s,
                output_txt=NEUTRAL_OUTPUT_TXT,
            )
    """
    TOPICS_TO_PROCESS = [
        "LEGAL",
        "ELECTION",
        "POLICY",
        "JAN6",
        "PERSONAL",
        "MEDIA",
        "GOP",
    ]
    for t in TOPICS_TO_PROCESS:
        print(f"Processing topic: {t}")
        extract_descriptions(
            filter_col=TOPIC_COL, description_col=DESCRIPTION, target_value=t
        )


if __name__ == "__main__":
    main()
