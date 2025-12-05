import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define the path to the uploaded file.
FILE_PATH = "../data/ANNOTATED_trump_dataset_500.csv"
# The column we want to analyze
TOPIC_COLUMN = "PRIMARY_TOPIC"


def plot_topic_distribution(file_path, column_name):
    """
    Loads the dataset, calculates the frequency distribution of a specified
    column, and plots the results as a horizontal bar chart.
    """
    try:
        # Load the CSV file into a pandas DataFrame
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    # Check if the required column exists
    if column_name not in df.columns:
        print(
            f"Error: Column '{column_name}' not found in the file. Available columns are: {list(df.columns)}"
        )
        return

    # 1. Calculate the value counts (frequency) of each unique topic
    topic_counts = df[column_name].value_counts()

    # 2. Check if there is data to plot
    if topic_counts.empty:
        print(f"No data found in the '{column_name}' column to plot.")
        return

    # 3. Create the plot
    plt.figure(
        figsize=(10, len(topic_counts) * 0.5 + 2)
    )  # Dynamic height based on number of topics
    sns.set_style("whitegrid")

    # Use a horizontal bar plot for better readability of topic labels
    # Use color palette for better visual distinction
    bar_plot = sns.barplot(
        x=topic_counts.values,
        y=topic_counts.index,
        palette="viridis",
        hue=topic_counts.index,
        dodge=False,
        legend=False,
    )

    # 4. Add labels, title, and formatting
    plt.title(
        f"Distribution of Topics in the Dataset (N={len(df)})",
        fontsize=16,
        fontweight="bold",
    )
    plt.xlabel("Number of Articles (Count)", fontsize=12)
    plt.ylabel(column_name.replace("_", " ").title(), fontsize=12)

    # Add the count labels on the bars
    for index, value in enumerate(topic_counts.values):
        bar_plot.text(value, index, f" {value}", va="center", ha="left")

    # Adjust layout to prevent labels from being cut off
    plt.tight_layout()

    # 5. Display the plot
    plt.show()


# Run the function with the defined file path and column name
plot_topic_distribution(FILE_PATH, TOPIC_COLUMN)

# The specific column name for sentiment
SENTIMENT_COLUMN = "SENTIMENT (Pos/Neg/Neu)"


def plot_sentiment_distribution(file_path, column_name):
    """
    Loads the dataset, cleans the sentiment column, and plots the distribution
    of positive, negative, and neutral sentiments.
    """
    try:
        # 1. Load the data
        df = pd.read_csv(file_path)
        print(f"Successfully loaded {file_path}. Total rows: {len(df)}")

        if column_name not in df.columns:
            print(f"\nError: Column '{column_name}' not found in the CSV file.")
            print(f"Available columns are: {df.columns.tolist()}")
            return

        # 2. Data Cleaning and Preparation

        # Convert all entries to uppercase strings, remove surrounding whitespace,
        # and replace NaN values with 'MISSING' or similar, though 'NEU' might be
        # a safer default if the data is expected to be clean. We'll use 'MISSING'
        # to explicitly track missing labels.
        df["cleaned_sentiment"] = df[column_name].astype(str).str.upper().str.strip()

        # Filter for the expected categories: POS, NEG, NEU
        valid_sentiments = ["POS", "NEG", "NEU"]
        sentiment_counts = df["cleaned_sentiment"].value_counts()

        # Filter the counts to only include the primary sentiment categories
        plot_data = sentiment_counts.loc[sentiment_counts.index.isin(valid_sentiments)]

        # Check if we have any data to plot
        if plot_data.empty:
            print(
                "\nError: No valid 'POS', 'NEG', or 'NEU' sentiment labels found after cleaning."
            )
            return

        print("\nSentiment Counts:")
        print(plot_data)

        # 3. Plotting the Distribution

        # Set a clean style
        sns.set_theme(style="whitegrid")

        # Define colors for clarity (e.g., Green for Pos, Red for Neg, Blue/Gray for Neu)
        color_map = {"POS": "#27AE60", "NEG": "#C0392B", "NEU": "#3498DB"}

        # Sort data by the defined order for consistent plotting
        plot_data = plot_data.reindex(valid_sentiments, fill_value=0)

        # Create the figure and axes
        plt.figure(figsize=(8, 6))

        # Create a bar plot
        ax = sns.barplot(
            x=plot_data.index,
            y=plot_data.values,
            palette=[color_map.get(x, "#7F8C8D") for x in plot_data.index],
            edgecolor="black",
            linewidth=1.2,
        )

        # 4. Add labels and title
        plt.title(
            "Distribution of News Sentiment towards Trump",
            fontsize=16,
            fontweight="bold",
        )
        plt.xlabel("Sentiment Category", fontsize=12)
        plt.ylabel("Count of Articles", fontsize=12)

        # Add the count labels on top of the bars
        for container in ax.containers:
            ax.bar_label(container, fmt="%d", padding=5, fontsize=10)

        # Adjust Y-axis limits to give space for labels
        max_y = plot_data.max()
        plt.ylim(0, max_y * 1.15)

        # Remove top and right spines for a cleaner look
        sns.despine(left=True, bottom=True)

        # Show the plot
        plt.tight_layout()
        plt.show()

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    plot_sentiment_distribution(FILE_PATH, SENTIMENT_COLUMN)
