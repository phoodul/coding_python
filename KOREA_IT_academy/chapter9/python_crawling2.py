import asyncio
import csv
from urllib.parse import urljoin
from playwright.async_api import async_playwright

BASE = "https://quotes.toscrape.com/js/"

async def scrape_js_quotes():
    rows = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        url = BASE
        while True:
            await page.goto(url, wait_until="networkidle")

            blocks = page.locator(".quote")
            n = await blocks.count()

            for i in range(n):
                b = blocks.nth(i)
                text = (await b.locator(".text").inner_text()).strip()
                author = (await b.locator(".author").inner_text()).strip()
                tags = [t.strip() for t in await b.locator(".tags .tag").all_inner_texts()]
                rows.append({"text": text, "author": author, "tags": ",".join(tags)})

            next_link = page.locator("li.next a")
            if await next_link.count() == 0:
                break

            href = await next_link.get_attribute("href")
            url = urljoin(BASE, href)

        await browser.close()

    return rows

def save_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["text", "author", "tags"])
        w.writeheader()
        w.writerows(rows)

if __name__ == "__main__":
    data = asyncio.run(scrape_js_quotes())
    print("rows:", len(data))
    save_csv(data, "quotes_js.csv")
    print("saved: quotes_js.csv")
