import requests
from bs4 import BeautifulSoup
import json
import time
from tqdm import tqdm

INPUT_FILE = "all_cheeses.json"
OUTPUT_FILE = "cheese_attributes.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_cheese_attributes(url):
    """치즈 페이지에서 사진 옆의 요약 속성(Summary Points)들을 가져옵니다."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Network error on {url}: {e}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    
    # cheese.com의 요약 정보는 보통 summary-points 클래스를 가진 ul 태그에 있습니다.
    summary_ul = soup.find("ul", class_="summary-points")
    
    attributes = {}
    
    if summary_ul:
        for li in summary_ul.find_all("li"):
            text = li.get_text(strip=True)
            # "Texture: smooth" 형태를 분리
            if ":" in text:
                key, value = text.split(":", 1)
                attributes[key.strip().lower()] = value.strip()
                
    return attributes

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        cheeses = json.load(f)

    attributes_data = {}
    
    total = len(cheeses)
    print("치즈 사진 옆의 요약 정보(Attributes) 크롤링을 시작합니다...")
    
    for cheese in tqdm(cheeses, total=total):
        name = cheese["name"]
        url = cheese["url"]
        
        attrs = get_cheese_attributes(url)
        
        attributes_data[name] = {
            "url": url,
            "attributes": attrs
        }
        
        # 서버 과부하 및 차단 방지를 위한 딜레이 (0.5초 ~ 1초 권장)
        time.sleep(0.5)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(attributes_data, f, indent=4, ensure_ascii=False)
        
    print(f"총 {len(attributes_data)}개의 치즈 속성 저장 완료!")

if __name__ == "__main__":
    main()
