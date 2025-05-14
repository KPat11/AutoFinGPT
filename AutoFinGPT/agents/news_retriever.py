# file for scraping financial headlines and storing them for our model to parse throuugh
# ran into js rendering issues and blocks with traditional web scrapes so elected to pull RSS feeds
import schedule
import time
import requests
import feedparser
import csv
import os
from datetime import datetime

def scrape_rss():

    #News sites we will pulling financial news from
    feeds = {
        "MarketWatch": "https://www.marketwatch.com/rss/topstories",
        "The Economist": "https://www.economist.com/latest/rss.xml",
        "FT": "https://www.ft.com/?format=rss",
        "CNN Business": "http://rss.cnn.com/rss/money_latest.rss",
        "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "Money Morning": "https://moneymorning.com/feed/",
        "TheStreet": "https://www.thestreet.com/.rss/full/",
        "Kiplinger": "https://www.kiplinger.com/rss/kiplinger.rss",
        "Investing.com": "https://www.investing.com/rss/news_25.rss",
        "WSJ": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        "Forbes": "https://www.forbes.com/business/feed/",
        "Reuters": "http://feeds.reuters.com/reuters/businessNews",
        "Bloomberg (ETFs)": "https://www.bloomberg.com/feed/podcast/etf-report.xml",
    }

    #creates raw data csv if it does not already exist
    csv_path = "data/raw/news.csv"
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)


    #Since we will run the job every 30 mins I will handle duplicate content using seen_links and a set()
    seen_links = set()
    if os.path.exists(csv_path):
        with open(csv_path, newline='', encoding='utf-8') as f:
            seen_links = {row['link'] for row in csv.DictReader(f)}

    #creating a more defined header due connection issues
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    
    #defining which fields in the xml we want to extract
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "source", "title", "description", "link"])
        #if file is empty, create the headers specified by checking file size
        if os.stat(csv_path).st_size == 0:
            writer.writeheader()
    #pointing to each hash map key and parsing feed
        for source, url in feeds.items():
            print(f"\n[{datetime.now()}] Fetching from {source}")
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                resp.raise_for_status()

                feed = feedparser.parse(resp.content)
                total = len(feed.entries)
                added = 0
                skipped = 0

                for entry in feed.entries:
                    title = entry.get('title', '').strip()
                    description = entry.get('description', '').strip()
                    link = entry.get('link', '').strip()
                    pub_date = entry.get('published', datetime.now().isoformat())

                    if not link:
                        skipped += 1
                        continue

                    if link not in seen_links:
                        writer.writerow({
                            "timestamp": pub_date,
                            "source": source,
                            "title": title,
                            "description": description,
                            "link": link
                        })
                        seen_links.add(link)
                        added += 1
                        print(f"Added: {title[:80]}")
                    else:
                        skipped += 1

                print(f"{total} total | {added} new | ⏭ {skipped} skipped for {source}")
            except Exception as e:
                print(f"Error fetching {source}: {e}")
                
#scheduler to extract data every 30 mins
#     schedule.every(30).minutes.do(scrape_rss)

#     print("\n RSS News Retriever started...\n")
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
