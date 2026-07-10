import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def crawl_cheese(item):
    name = item['name']
    url = item['url']
    
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        summary_data = {}
        ul = soup.find('ul', class_='summary-points')
        if ul:
            for li in ul.find_all('li'):
                cls = li.get('class', [''])[0]
                p = li.find('p')
                if p:
                    text = p.get_text(separator=' ', strip=True)
                    summary_data[cls] = text
                    
        return name, summary_data, None
    except Exception as e:
        return name, None, str(e)

def main():
    print("Loading all_cheeses_with_search.json...")
    with open('all_cheeses_with_search.json', 'r', encoding='utf-8') as f:
        cheeses = json.load(f)
        
    results = {}
    total = len(cheeses)
    print(f"Starting crawl for {total} cheeses...")
    
    start_time = time.time()
    
    # 20 workers is usually safe and fast enough without being blocked
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_cheese = {executor.submit(crawl_cheese, c): c for c in cheeses}
        
        count = 0
        for future in as_completed(future_to_cheese):
            name, data, err = future.result()
            count += 1
            if err:
                print(f"[{count}/{total}] Error crawling {name}: {err}")
            else:
                results[name] = data
                if count % 100 == 0:
                    print(f"[{count}/{total}] Successfully crawled {name}")
                    
    elapsed = time.time() - start_time
    print(f"Crawl completed in {elapsed:.1f} seconds.")
    
    with open('cheese_summary_crawled.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("Saved to cheese_summary_crawled.json")

if __name__ == '__main__':
    main()
