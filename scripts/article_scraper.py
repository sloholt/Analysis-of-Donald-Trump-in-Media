import requests
from bs4 import BeautifulSoup
import time
import csv
from urllib.parse import urlparse
import os

URLS = [
    "https://www.cbsnews.com/news/trump-government-shutdown-democrats-fault-60-minutes/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/news/trumps-plans-to-restart-nuclear-testing-experts/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/news/venezuela-cartel-de-los-soles-us-designation-terrorist-organization-what-is-it/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/newyork/news/trump-cuomo-nyc-mayor-race/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/news/trump-mamdani-cuomo-nyc-mayor-60-minutes-interview/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/miami/news/trump-touts-economic-record-blasts-democrats-at-miami-business-forum/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/news/fbi-inquiry-six-democrats-illegal-orders-video/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/news/nobel-peace-prize-donald-trump-what-to-know/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/miami/news/president-donald-trump-miami-anniversary-election-win-economy-agenda/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/news/trump-bbc-lawsuit-threat-january-6-panorama-editing/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/chicago/news/treasurer-melissa-conyears-ervin-boycott-us-bonds-president-trump/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/atlanta/news/trump-says-rep-marjorie-taylor-greene-has-lost-her-way-after-criticism-over-foreign-policy-focus/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/news/jeffrey-epstein-donald-trump-emails-house-oversight/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/news/jeffrey-epstein-trump-emails-texts-inner-circle/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/news/trump-jeffrey-epstein-justice-department-democrats-banks/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/news/marjorie-taylor-greene-receiving-threats-amid-rift-with-trump/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/sacramento/news/judge-bars-trump-from-immediately-cutting-funding-to-the-university-of-california/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/news/corporate-trump-ballroom-donors-represented-by-3-lobbying-firms/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/news/trump-scotland-golf-course-neighbors-react-to-visit-protests/",
    "https://www.cbsnews.com/atlanta/news/georgia-rep-marjorie-taylor-greene-blames-trump-for-hoax-pizza-harassment-pipe-bomb-threats-i-am-not-a-traitor/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/detroit/news/trump-administration-extends-order-keeping-michigan-coal-plant-online-past-closure-date/?intcid=CNM-00-10abd1h",
    "https://www.cbsnews.com/news/donald-trump-business-empire/",
    "https://www.cbsnews.com/philadelphia/news/pennsylvania-shapiro-trump-truth-social-posts-seditious-behavior/?intcid=CNM-00-10abd1h",
    "https://fortune.com/longform/donald-trump-businessman/",
    "https://www.bbc.com/news/world-us-canada-35318432",
    "https://www.bbc.com/news/business-35836623",
    "https://www.newyorker.com/news/our-columnists/as-a-businessman-trump-was-the-biggest-loser-of-all",
    "https://www.newyorker.com/news/our-columnists/hundreds-of-former-federal-prosecutors-would-indict-donald-trump",
    "https://www.newyorker.com/news/our-columnists/attorney-general-william-barr-acts-as-trumps-human-shield-on-capitol-hill",
    "https://www.newyorker.com/magazine/2025/12/01/the-justice-department-hits-a-new-low-with-the-epstein-files#intcid=_the-new-yorker-article-bottom-recirc-bkt-a_1c779e44-6f72-4e58-90ed-4bc05b590433_closr",
    "https://www.newyorker.com/news/the-financial-page/socialism-but-make-it-trump#intcid=_the-new-yorker-article-bottom-recirc-bkt-a_1c779e44-6f72-4e58-90ed-4bc05b590433_closr",
    "https://www.newyorker.com/magazine/1997/05/19/trump-solo",
    "https://theweek.com/articles/644820/how-donald-trump-built-business-empire",
    "https://millercenter.org/president/trump/life-presidency",
    "https://www.theatlantic.com/business/archive/2017/04/product-placement-presidency/523797",
    "https://www.vanityfair.com/magazine/1987/12/trump_excerpt198712",
    "https://people.com/politics/poor-donald-trumps-money-woes-detailed-in-1990-people-cover",
    "https://nymag.com/nymetro/news/bizfinance/biz/features/2235",
    "https://nymag.com/intelligencer/2016/11/the-fake-donald-trump-quote-that-just-wont-die.html",
    "https://www.theguardian.com/us-news/2020/mar/14/teen-models-powerful-men-when-donald-trump-hosted-look-of-the-year",
    "https://digitalcommons.csbsju.edu/cgi/viewcontent.cgi?article=1130&context=psychology_pubs",
    "https://news.sky.com/story/trump-hits-back-over-reported-financial-losses-of-1bn-in-1980s-and-1990s-11714648",
    "https://www.thoughtco.com/donald-trump-business-bankruptcies-4152019#:~:text=Trump%20opened%20the%20%241.2%20billion,facility%2C%20particularly%20amid%20a%20recession",
    "https://www.thoughtco.com/donald-trump-business-bankruptcies-4152019",
    "https://www.nytimes.com/interactive/2019/05/07/us/politics/donald-trump-taxes.html",
    "https://www.vanityfair.com/news/2016/10/donald-trump-financial-troubles-taxes-1990s",
    "https://abcnews.go.com/Business/trumps-economic-legacy/story?id=74760051",
    "https://www.bloomberg.com/news/articles/2019-06-14/failed-trump-golf-course-turned-into-dilapidated-n-y-state-park?embedded-checkout=true",
    "https://news.temple.edu/news/2016-10-25/bankruptcy-expert-studies-trump-casinos#:~:text=A%20new%20study%20by%20a%20Temple%20University%20professor%20shows%20that,Jonathan%20Lipson%2C%20Harold%20E",
    "https://www.motherjones.com/politics/2016/10/how-donald-trump-destroyed-his-empire-and-dumped-ruins-others-timeline/#:~:text=By%20Trump's%20own%20admission%2C%20he,which%20he'd%20personally%20guaranteed",
    "https://www.lemonde.fr/international/article/2024/04/13/entre-donald-trump-et-new-york-une-histoire-d-amour-haine_6227561_3210.html",
    "https://www.politico.com/magazine/story/2016/03/1988-the-year-donald-lost-his-mind-213721/",
    "https://nouveau.eureka.cc/Search/ResultMobile/11",
    "https://www.timesunion.com/hudsonvalley/news/article/Trump-alleged-fraud-Dutchess-County-golf-club-17460501.php",
    "https://www.thestar.com/news/world/europe/trumps-trip-to-scotland-as-his-new-golf-course-opens-blurs-politics-and-the-familys/article_72d23013-8e62-50db-adcc-723b1de6ba44.html",
    "https://www.lse.ac.uk/granthaminstitute/news/green-claims-for-donald-trumps-new-golf-course-laughable/",
    "https://www.business-humanrights.org/en/latest-news/late-wages-for-migrant-workers-at-a-trump-golf-course-in-dubai/",
]


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
