import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://www.cheese.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    BASE_URL + "/all-cheeses/",
    headers=HEADERS
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

cheeses = []

for section in soup.select("div.cheese-letter"):

    for a in section.select("li a"):

        cheeses.append({
            "name": a.get_text(strip=True),
            "url": BASE_URL + a["href"]
        })

print(f"총 {len(cheeses)}개의 치즈 발견")

with open("all_cheeses.json", "w", encoding="utf-8") as f:
    json.dump(cheeses, f, ensure_ascii=False, indent=4)

print("all_cheeses.json 저장 완료")