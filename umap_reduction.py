import numpy as np
import json
import os

try:
    import umap
except ImportError:
    print("umap-learn 라이브러리가 설치되어 있지 않습니다. pip install umap-learn 을 실행해주세요.")
    exit(1)

def main():
    if not os.path.exists("embeddings_v2.npy") or not os.path.exists("metadata_v2.json"):
        print("embeddings_v2.npy 와 metadata_v2.json 파일이 필요합니다.")
        print("embedding_v2.py 를 먼저 실행해주세요.")
        return

    print("임베딩 로드 중...")
    embeddings = np.load("embeddings_v2.npy")
    with open("metadata_v2.json", "r", encoding="utf-8") as f:
        names = json.load(f)

    print(f"UMAP을 사용하여 {embeddings.shape[0]}개의 데이터를 2차원으로 축소합니다...")
    # 파라미터는 ENaO 철학에 맞게 약간 넓게 퍼지도록 조정 (min_dist 등)
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.3, n_components=2, random_state=42)
    embedding_2d = reducer.fit_transform(embeddings)

    print("UMAP 완료! 좌표 정규화 진행 중...")
    # 브라우저 시각화를 위해 0~100 (또는 -100~100) 스케일로 정규화
    x_coords = embedding_2d[:, 0]
    y_coords = embedding_2d[:, 1]
    
    # 0 ~ 1 사이로 Min-Max 스케일링 후, 화면 좌표계(예: 0~1000)로 변환해도 되지만, 
    # D3.js에서 자체 scaleLinear를 쓰기 편하게 원본 스케일 유지 또는 -1 ~ 1 스케일 유지
    x_min, x_max = x_coords.min(), x_coords.max()
    y_min, y_max = y_coords.min(), y_coords.max()
    
    normalized_x = (x_coords - x_min) / (x_max - x_min) * 100
    normalized_y = (y_coords - y_min) / (y_max - y_min) * 100

    results = {}
    for i, name in enumerate(names):
        results[name] = {
            "x": float(normalized_x[i]),
            "y": float(normalized_y[i])
        }

    with open("umap_coordinates.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        
    print("완료! umap_coordinates.json 파일이 생성되었습니다.")

if __name__ == "__main__":
    main()
