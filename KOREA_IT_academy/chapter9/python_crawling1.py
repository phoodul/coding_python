import time
import random
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://quotes.toscrape.com/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PracticeCrawler/1.0)"
}

def scrape_all_quotes():
    url = BASE
    rows = []

    while True:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "lxml")

        for block in soup.select(".quote"):
            text = block.select_one(".text").get_text(strip=True)
            author = block.select_one(".author").get_text(strip=True)
            tags = [t.get_text(strip=True) for t in block.select(".tags .tag")]
            rows.append({"text": text, "author": author, "tags": ",".join(tags)})

        next_a = soup.select_one("li.next a")
        if not next_a:
            break

        url = urljoin(BASE, next_a["href"])
        time.sleep(random.uniform(0.8, 2.0))  # 예의상 딜레이

    return rows

def save_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["text", "author", "tags"])
        w.writeheader()
        w.writerows(rows)

if __name__ == "__main__":
    data = scrape_all_quotes()
    print("rows:", len(data))
    save_csv(data, "quotes_static.csv")
    print("saved: quotes_static.csv")
