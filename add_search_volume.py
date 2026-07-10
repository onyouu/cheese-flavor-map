import json
import time
import re
import google.generativeai as genai
from tqdm import tqdm


INPUT = "all_cheeses.json"
OUTPUT = "all_cheeses_with_search.json"


# 여기만 수정
START_CHEESE = "Goat Curd"


genai.configure(
    api_key="YOUR_API_KEY_HERE"
)


model = genai.GenerativeModel(
    "gemini-3.1-flash-lite"
)

# =====================
# 데이터 로드
# =====================

with open(
    INPUT,
    "r",
    encoding="utf-8"
) as f:

    cheeses = json.load(f)
# =====================
# 기존 잘못된 search_volume 제거
# =====================

reset_count = 0

for cheese in cheeses:

    if cheese.get("search_volume") == 0:

        del cheese["search_volume"]

        reset_count += 1


print(
    "초기화된 search_volume:",
    reset_count
)


# 기존 결과 이어받기

try:

    with open(
        OUTPUT,
        "r",
        encoding="utf-8"
    ) as f:

        cheeses = json.load(f)

except:

    pass



print(
    "치즈 개수:",
    len(cheeses)
)



# =====================
# 시작 위치
# =====================

start_index = 0


for i, cheese in enumerate(cheeses):

    if cheese["name"] == START_CHEESE:

        start_index = i
        break

else:

    raise Exception(
        f"{START_CHEESE} 없음"
    )



print(
    "시작:",
    cheeses[start_index]["name"]
)



batch_size = 50



def save():

    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            cheeses,
            f,
            ensure_ascii=False,
            indent=2
        )




# =====================
# 처리
# =====================

for start in tqdm(
    range(
        start_index,
        len(cheeses),
        batch_size
    )
):


    batch = cheeses[
        start:start+batch_size
    ]


    if not batch:
        continue



    names = [
        c["name"]
        for c in batch
    ]



    prompt = f"""

You are an expert in cheese culture.

Estimate popularity score for each cheese.

Score should be your own judgement.

Consider:
- worldwide recognition
- cultural importance
- availability
- media exposure
- expected search interest


Do not use a fixed scoring table.
Different cheeses should naturally receive different scores.


Return ONLY JSON.

Required format:

[
 {{
  "name":"Cheddar",
  "score":95
 }}
]


The name MUST be exactly identical.


Cheeses:

{json.dumps(names, ensure_ascii=False)}

"""



    try:


        response = model.generate_content(
            prompt
        )


        text = response.text.strip()



        print("\n===== Gemini Raw =====")
        print(text[:1000])



        text = (
            text
            .replace("```json","")
            .replace("```","")
            .strip()
        )



        match = re.search(
            r"\[.*\]",
            text,
            re.DOTALL
        )


        if not match:

            raise Exception(
                "JSON 배열 없음"
            )



        scores = json.loads(
            match.group()
        )



        score_map = {}

        for item in scores:

            name = (
                item["name"]
                .strip()
                .lower()
            )

            score_map[name] = int(
                item["score"]
            )



        print(
            "매칭 개수:",
            len(score_map),
            "/",
            len(names)
        )



        for cheese in batch:


            key = (
                cheese["name"]
                .strip()
                .lower()
            )


            if key in score_map:

                cheese["search_volume"] = (
                    score_map[key]
                )

            else:

                print(
                    "매칭 실패:",
                    cheese["name"]
                )

                cheese["search_volume"] = None



    except Exception as e:


        print(
            "\n오류 발생:",
            e
        )


        for cheese in batch:

            cheese["search_volume"] = None



    # 매 배치 저장

    save()


    time.sleep(1)



print(
    "완료!"
)