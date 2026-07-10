import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.cheese.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_substitutes(url):
    """치즈 페이지에서 이름과 대체 치즈 목록 가져오기"""

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    name = soup.find("h1").get_text(strip=True)

    substitutes = []

    panel = soup.find(id="collapse-substitutes")

    if panel:
        for h3 in panel.find_all("h3"):
            a = h3.find("a")

            if a:
                substitutes.append(a.get_text(strip=True))

    return name, substitutes


# ------------------------
# 전체 치즈 목록 불러오기
# ------------------------

with open("all_cheeses.json", "r", encoding="utf-8") as f:
    cheeses = json.load(f)

graph = {}

total = len(cheeses)

for i, cheese in enumerate(cheeses):

    print(f"[{i+1}/{total}] {cheese['name']}")

    try:

        name, substitutes = get_substitutes(cheese["url"])

        graph[name] = substitutes

        time.sleep(0.3)

    except Exception as e:

        print("오류 :", cheese["url"])
        print(e)


# ------------------------
# 저장
# ------------------------

with open("graph.json", "w", encoding="utf-8") as f:
    json.dump(graph, f, indent=4, ensure_ascii=False)

print()
print("=" * 40)
print(f"총 {len(graph)}개의 치즈 저장 완료!")
print("=" * 40)