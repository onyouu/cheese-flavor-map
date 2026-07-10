import json

INPUT = "cheese_dataset.json"
OUTPUT = "cheese_dataset_fixed.json"


with open(INPUT, "r", encoding="utf-8") as f:
    cheeses = json.load(f)


def normalize_list(items, is_other=False):

    result = []

    for item in items:

        # 이미 문자열이면 그대로
        if isinstance(item, str):
            result.append(item)
            continue

        # dict 처리
        if isinstance(item, dict):

            # other 전용
            if is_other:

                if "category" in item and "information" in item:
                    result.append(
                        f'{item["category"]}: {item["information"]}'
                    )

                elif len(item) == 1:
                    k, v = next(iter(item.items()))
                    result.append(f"{k}: {v}")

                else:
                    result.append(
                        ", ".join(
                            f"{k}: {v}"
                            for k, v in item.items()
                        )
                    )

            # flavor/aroma/texture
            else:

                if len(item) == 1:
                    result.append(
                        next(iter(item.values()))
                    )

                else:
                    result.append(
                        ", ".join(
                            str(v)
                            for v in item.values()
                        )
                    )

            continue

        # 혹시 숫자 등 다른 타입
        result.append(str(item))

    return result


count = 0

for cheese in cheeses.values():

    taste = cheese.get("taste", {})

    taste["flavor"] = normalize_list(
        taste.get("flavor", [])
    )

    taste["aroma"] = normalize_list(
        taste.get("aroma", [])
    )

    taste["texture"] = normalize_list(
        taste.get("texture", [])
    )

    taste["other"] = normalize_list(
        taste.get("other", []),
        is_other=True
    )

    count += 1


with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        cheeses,
        f,
        ensure_ascii=False,
        indent=4
    )

print(f"완료! ({count}개 치즈 변환)")