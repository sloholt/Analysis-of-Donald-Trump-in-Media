import requests
from bs4 import BeautifulSoup
import time
import csv
from urllib.parse import urlparse
import os

URLS = []  # Left blank for space


def scrape_article(url):
    # Fetch HTML content
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

    # Extract Source
    source_name = "source not found"  # default value
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        clean_domain = domain.replace("www.", "")
        source_name = clean_domain.split(".")[0].capitalize()
    except Exception as e:
        print(f"Could not parse the source from URL: {e}")

    # Parse HTML content
    soup = BeautifulSoup(html_content, "html.parser")
    headline = "Headline Not Found"  # Default value
    h1_tag = soup.find("h1")
    if h1_tag:
        headline = h1_tag.get_text(strip=True)
    else:
        title_tag = soup.find("title")
        if title_tag:
            headline = title_tag.get_text(strip=True).split(" | ")[0]

    # Find the summary (or first paragraph)
    summary = "summary not found"  # default value
    paragraphs = soup.find_all("p")
    for p in paragraphs:
        text = p.get_text(strip=True)
        if len(text) > 75 and "." in text:
            summary = text
            break
    return {"URL": url, "Source": source_name, "Headline": headline, "Summary": summary}


def main(urls):
    all_results = []
    print(f"Starting to scrape {len(urls)} articles")

    output_file = "scraped_articles.tsv"
    file_exists = os.path.exists(output_file)
    fieldnames = ["URL", "Source", "Headline", "Summary"]

    with open(output_file, "a", newline="", encoding="utf-8") as tsvfile:
        writer = csv.DictWriter(
            tsvfile,
            fieldnames=fieldnames,
            delimiter="\t",
            quoting=csv.QUOTE_MINIMAL,
        )
        if not file_exists:
            print(f"File '{output_file}' created. Writing header...")
            writer.writeheader()
        else:
            print(f"File '{output_file}' found. Appending rows...")

        print(f"Starting to scrape {len(urls)} articles")
        for i, url in enumerate(urls):
            print(f"Processing article {i+1}/{len(urls)}: {url}")
            result = scrape_article(url)
            if result:
                try:
                    writer.writerow(result)
                except ValueError as e:
                    print(f"Error writing row for {url}: {e}")
            else:
                print(f"Skipping failed URL: {url}")
            time.sleep(5)
    print(
        f"Successfully processed files. New rows successfully appended to {output_file}"
    )


if __name__ == "__main__":
    main(URLS)
