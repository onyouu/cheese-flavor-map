import json
import math
import os

print("=" * 60)
print("치즈 맵 데이터 품질 검사 (Audit)")
print("=" * 60)

# 1. umap_coordinates.json 검사
print("\n[1] umap_coordinates.json 검사")
with open("umap_coordinates.json", "r", encoding="utf-8") as f:
    umap_data = json.load(f)
print(f"  총 치즈 수: {len(umap_data)}")
xs = [v["x"] for v in umap_data.values()]
ys = [v["y"] for v in umap_data.values()]
nan_count = sum(1 for x, y in zip(xs, ys) if math.isnan(x) or math.isnan(y))
print(f"  X 범위: {min(xs):.2f} ~ {max(xs):.2f}")
print(f"  Y 범위: {min(ys):.2f} ~ {max(ys):.2f}")
print(f"  NaN 값 개수: {nan_count}")
# 좌표가 완전히 같은 점(겹침) 체크
coords = [(round(v["x"], 4), round(v["y"], 4)) for v in umap_data.values()]
duplicates = len(coords) - len(set(coords))
print(f"  완전히 겹치는 좌표 쌍: {duplicates}")

# 2. cheese_dataset_v2.json 검사
print("\n[2] cheese_dataset_v2.json 검사")
with open("cheese_dataset_v2.json", "r", encoding="utf-8") as f:
    v2_data = json.load(f)
print(f"  총 치즈 수: {len(v2_data)}")
empty_taste = 0
sample_keys = set()
for name, data in v2_data.items():
    taste = data.get("taste", {})
    if isinstance(taste, dict):
        sample_keys.update(taste.keys())
        all_empty = all(not v for v in taste.values() if isinstance(v, list))
        if all_empty:
            empty_taste += 1
print(f"  taste 카테고리 키: {sorted(sample_keys)}")
print(f"  taste 데이터가 모두 비어있는 치즈: {empty_taste}")

# 샘플: 까망베르 계열 확인
print("\n  [까망베르 계열 샘플 확인]")
for name in v2_data:
    if "camembert" in name.lower():
        taste = v2_data[name].get("taste", {})
        dairy = taste.get("dairy", [])
        earthy = taste.get("earthy_animal", [])
        texture = taste.get("texture", [])
        print(f"    {name}: dairy={dairy}, earthy={earthy}, texture={texture}")

# 샘플: 브리 계열 확인
print("\n  [브리(Brie) 계열 샘플 확인]")
for name in v2_data:
    if "brie" in name.lower() and "brie" in name.lower().split():
        taste = v2_data[name].get("taste", {})
        dairy = taste.get("dairy", [])
        earthy = taste.get("earthy_animal", [])
        texture = taste.get("texture", [])
        print(f"    {name}: dairy={dairy}, earthy={earthy}, texture={texture}")

# 3. cheese_attributes.json 검사
print("\n[3] cheese_attributes.json 검사")
with open("cheese_attributes.json", "r", encoding="utf-8") as f:
    attrs_data = json.load(f)
print(f"  총 치즈 수: {len(attrs_data)}")
empty_attrs = sum(1 for v in attrs_data.values() if not v.get("attributes"))
print(f"  속성이 비어있는 치즈: {empty_attrs}")
# 어떤 속성 키들이 있는지
all_attr_keys = set()
for v in attrs_data.values():
    all_attr_keys.update(v.get("attributes", {}).keys())
print(f"  발견된 속성 키들: {sorted(all_attr_keys)}")

# 4. metadata_v2.json과 umap_coordinates.json 정합성 확인
print("\n[4] metadata_v2.json ↔ umap_coordinates.json 정합성")
with open("metadata_v2.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)
print(f"  metadata_v2 치즈 수: {len(metadata)}")
print(f"  umap_coordinates 치즈 수: {len(umap_data)}")
meta_set = set(metadata)
umap_set = set(umap_data.keys())
print(f"  일치 여부: {'✅ 완벽 일치' if meta_set == umap_set else '❌ 불일치 발견!'}")
if meta_set != umap_set:
    print(f"  metadata에만 있는 치즈: {meta_set - umap_set}")
    print(f"  umap에만 있는 치즈: {umap_set - meta_set}")

print("\n" + "=" * 60)
print("검사 완료!")
print("=" * 60)
