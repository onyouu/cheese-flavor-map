import json
import numpy as np
from sentence_transformers import SentenceTransformer
import os

ATTRIBUTES_FILE = "cheese_attributes.json"
TASTE_V2_FILE = "cheese_dataset_v2.json"

def main():
    if not os.path.exists(ATTRIBUTES_FILE) or not os.path.exists(TASTE_V2_FILE):
        print("필요한 데이터 파일이 없습니다.")
        print(f"1. {ATTRIBUTES_FILE} (scrape_attributes.py 결과물)")
        print(f"2. {TASTE_V2_FILE} (taste_v2.py 결과물)")
        return

    print("데이터를 불러옵니다...")
    with open(ATTRIBUTES_FILE, "r", encoding="utf-8") as f:
        attributes_data = json.load(f)
        
    with open(TASTE_V2_FILE, "r", encoding="utf-8") as f:
        taste_data = json.load(f)

    texts = []
    names = []

    print("임베딩용 하이브리드 문장 생성 중...")
    for name, t_data in taste_data.items():
        if name not in attributes_data:
            continue
            
        attrs = attributes_data[name].get("attributes", {})
        taste = t_data.get("taste", {})

        # 공식 속성 (뼈대 역할)
        t_type = attrs.get("type", "")
        t_texture = attrs.get("texture", "")
        t_flavor = attrs.get("flavour", "")
        t_aroma = attrs.get("aroma", "")

        # AI 추출 상세 관능 (풍부함 역할)
        dairy = ", ".join(taste.get("dairy", []))
        earthy = ", ".join(taste.get("earthy_animal", []))
        fruity = ", ".join(taste.get("fruity_floral", []))
        nutty = ", ".join(taste.get("nutty_roasted", []))
        spicy = ", ".join(taste.get("spicy_herbaceous", []))
        ai_texture = ", ".join(taste.get("texture", []))
        infusions = ", ".join(taste.get("infusions", []))

        # 맛, 향, 식감 정보가 아예 없으면 제외
        if not (t_flavor or t_aroma or dairy or earthy or fruity or nutty or spicy):
            continue

        text = f"""
[Base Characteristics]
Type: {t_type}
Texture: {t_texture}
Flavor: {t_flavor}
Aroma: {t_aroma}

[Detailed Sensory Nuances]
Dairy: {dairy}
Earthy/Animal: {earthy}
Fruity/Floral: {fruity}
Nutty/Roasted: {nutty}
Spicy/Herbaceous: {spicy}
AI Texture: {ai_texture}
Infusions: {infusions}
"""
        texts.append(text.strip())
        names.append(name)

    print(f"사용 치즈 수: {len(texts)}")

    print("모델 로드 중...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("임베딩 생성 중...")
    embeddings = model.encode(texts, show_progress_bar=True)

    print(f"embedding shape: {embeddings.shape}")

    np.save("embeddings_v2.npy", embeddings)

    with open("metadata_v2.json", "w", encoding="utf-8") as f:
        json.dump(names, f, ensure_ascii=False, indent=2)

    print("완료! embeddings_v2.npy 와 metadata_v2.json 이 저장되었습니다.")

if __name__ == "__main__":
    main()
