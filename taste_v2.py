import json
import os
import time
import ollama
from tqdm import tqdm

INPUT_FILE = "cheese_dataset_fixed.json"
OUTPUT_FILE = "cheese_dataset_v2.json"

# 친구분 GPU 사양에 맞춰 더 똑똑한 모델로 변경하세요. (예: llama3:8b, llama3.1:8b 등)
# 기존 qwen2.5:3b 보다 파라미터가 많은 모델을 추천합니다.
OLLAMA_MODEL = "llama3.1" 

def extract_taste_v2(name, description):
    if not description or not description.strip():
        return {
            "dairy": [], "earthy_animal": [], "fruity_floral": [], 
            "nutty_roasted": [], "spicy_herbaceous": [], "texture": [], 
            "infusions": [], "other": []
        }

    prompt = f"""
You are an expert cheese sensory evaluator.
Analyze the following cheese description.
Extract sensory information ONLY. 
CRITICAL RULE 1: Focus STRICTLY on the mature/peak stage of the cheese. Ignore characteristics described for the young/unripened stage.
CRITICAL RULE 2: NEVER include country, region, or historical information.

Categorize the sensory information into the following JSON arrays exactly as shown. 

Categories:
"dairy": Milky, Buttery, Creamy, Whey, Lactic, etc.
"earthy_animal": Mushroom, Earthy, Barnyard, Animal, Moldy, etc.
"fruity_floral": Fruity, Citrus, Floral, Sweet, etc.
"nutty_roasted": Nutty, Caramel, Roasted, Brown butter, etc.
"spicy_herbaceous": Grassy, Herbaceous, Spicy, Peppery, Garlic, etc.
"texture": Soft, Creamy, Crumbly, Firm, Hard, Elastic, Gooey, etc.
"infusions": Non-cheese ingredients explicitly added (e.g., Cranberries, Truffles, Walnuts, Wine wash, Pepper, Ash). Do not put these in other flavor categories!
"other": Milk type, aging time (but NO origin/country info).

Cheese:
{name}

Description:
{description}

Return ONLY valid JSON in this exact format:
{{
  "dairy": [],
  "earthy_animal": [],
  "fruity_floral": [],
  "nutty_roasted": [],
  "spicy_herbaceous": [],
  "texture": [],
  "infusions": [],
  "other": []
}}
"""
    
    try:
        result = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            format="json"
        )
        return json.loads(result["message"]["content"])
    except Exception as e:
        print(f"[Ollama Error] {name}: {e}")
        return {
            "dairy": [], "earthy_animal": [], "fruity_floral": [], 
            "nutty_roasted": [], "spicy_herbaceous": [], "texture": [], 
            "infusions": [], "other": []
        }

def save_data(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"{INPUT_FILE} 파일이 없습니다.")
        return

    # 원본 파일에는 크롤링된 raw_description이 모두 들어있습니다.
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        cheeses = json.load(f)
    
    # 이전에 작업하던 파일이 있으면 이어서 진행
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                dataset_v2 = json.load(f)
        except json.JSONDecodeError:
            print(f"[{OUTPUT_FILE}] 파일이 손상되어 새로 시작합니다.")
            dataset_v2 = {}
    else:
        dataset_v2 = {}

    total = len(cheeses)
    print(f"총 {total}개의 치즈 데이터를 처리합니다. (크롤링 없음 - GPU 순수 추론)")
    
    # tqdm으로 진행률 표시
    for name, data in tqdm(cheeses.items(), total=total):
        if name in dataset_v2:
            continue
            
        description = data.get("raw_description", "")
        url = data.get("url", "")
        
        taste = extract_taste_v2(name, description)
        
        dataset_v2[name] = {
            "url": url,
            "raw_description": description,
            "taste": taste
        }
        
        # 중간 저장 (혹시라도 꺼질 때를 대비해 매번 저장)
        save_data(dataset_v2)

if __name__ == "__main__":
    main()
