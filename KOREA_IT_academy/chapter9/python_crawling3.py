import json
import csv
import requests

BASE = "https://jsonplaceholder.typicode.com"

def fetch_posts(limit=20):
    r = requests.get(f"{BASE}/posts", timeout=10)
    r.raise_for_status()
    posts = r.json()
    return posts[:limit]

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_csv(posts, path):
    # posts는 dict 리스트: userId, id, title, body
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["userId", "id", "title", "body"])
        w.writeheader()
        w.writerows(posts)

if __name__ == "__main__":
    posts = fetch_posts(limit=20)
    print("posts:", len(posts))
    print("first title:", posts[0]["title"])

    save_json(posts, "posts.json")
    save_csv(posts, "posts.csv")
    print("saved: posts.json, posts.csv")
