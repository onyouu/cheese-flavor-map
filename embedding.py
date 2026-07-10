import json
import numpy as np
from sentence_transformers import SentenceTransformer


# =========================
# 데이터 불러오기
# =========================

with open(
    "cheese_dataset_fixed.json",
    "r",
    encoding="utf-8"
) as f:
    cheeses = json.load(f)



texts = []
names = []



# =========================
# 임베딩용 문장 생성
# =========================

for name, data in cheeses.items():

    description = data.get(
        "raw_description",
        ""
    )


    taste = data.get(
        "taste",
        {}
    )


    flavor = ", ".join(
        taste.get("flavor", [])
    )


    aroma = ", ".join(
        taste.get("aroma", [])
    )


    texture = ", ".join(
        taste.get("texture", [])
    )



    # 맛, 향, 식감 정보가 하나도 없으면 제외
    if not flavor and not aroma and not texture:
        continue

    text = f"""
Flavor:
{flavor}

Aroma:
{aroma}

Texture:
{texture}
"""

    texts.append(text)

    names.append(name)




print(
    "사용 치즈 수:",
    len(texts)
)



# =========================
# 모델 로드
# =========================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)



# =========================
# embedding 생성
# =========================

embeddings = model.encode(
    texts,
    show_progress_bar=True
)



print(
    "embedding shape:",
    embeddings.shape
)



# =========================
# 저장
# =========================

np.save(
    "embeddings.npy",
    embeddings
)



with open(
    "metadata.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        names,
        f,
        ensure_ascii=False,
        indent=2
    )


print("완료!")