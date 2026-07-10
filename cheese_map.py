import umap
import numpy as np
import json


# =========================
# embedding 불러오기
# =========================

embeddings = np.load(
    "embeddings.npy"
)



# =========================
# UMAP
# =========================

reducer = umap.UMAP(
    n_components=2,
    n_neighbors=50,
    min_dist=0.3,
    metric="cosine",
    random_state=42
)


coords = reducer.fit_transform(
    embeddings
)



# =========================
# 시각화용 공간 확대
# =========================

spread = 20

coords = coords * spread



print(
    "좌표 범위:"
)

print(
    coords.min(axis=0),
    coords.max(axis=0)
)



# =========================
# metadata
# =========================

with open(
    "metadata.json",
    "r",
    encoding="utf-8"
) as f:

    names = json.load(f)



result = []


for name, xy in zip(
    names,
    coords
):

    result.append({

        "name": name,

        "x": float(xy[0]),

        "y": float(xy[1])

    })



with open(
    "cheese_coordinates.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        result,
        f,
        ensure_ascii=False,
        indent=2
    )



print(
    "완료:",
    len(result)
)