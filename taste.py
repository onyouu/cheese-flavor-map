import requests
from bs4 import BeautifulSoup
import ollama
import json
import os
import time


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


INPUT_FILE = "all_cheeses.json"
OUTPUT_FILE = "cheese_dataset.json"



# =====================================
# cheese.com 전체 description 가져오기
# =====================================

def get_description(url):

    r = requests.get(
        url,
        headers=HEADERS,
        timeout=15
    )

    r.raise_for_status()

    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )


    description = soup.find(
        "div",
        class_="description"
    )


    if not description:
        return ""


    texts = []


    # h2 + p만 추출
    for tag in description.find_all(
        ["h2", "p"]
    ):

        text = tag.get_text(
            " ",
            strip=True
        )

        if text:
            texts.append(text)


    return "\n".join(texts)




# =====================================
# Ollama taste 추출
# =====================================

def extract_taste(name, description):


    if not description:

        return {

            "flavor": [],
            "aroma": [],
            "texture": [],
            "other": []

        }



    prompt = f"""

You are a cheese expert.

Analyze the following cheese description.

Extract sensory information only.

Return JSON only.


Categories:

flavor:
taste such as sweet, salty, nutty, spicy, buttery

aroma:
smell such as smoky, earthy, fruity

texture:
mouthfeel such as creamy, soft, hard

other:
aging, milk type, special characteristics


Cheese:
{name}


Description:
{description}


JSON format:

{{
 "flavor": [],
 "aroma": [],
 "texture": [],
 "other": []
}}

"""


    result = ollama.chat(

        model="qwen2.5:3b",

        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ],

        format="json"

    )


    return json.loads(
        result["message"]["content"]
    )




# =====================================
# 저장
# =====================================

def save(data):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )





# =====================================
# main
# =====================================


# 기존 데이터 불러오기

if os.path.exists(
    OUTPUT_FILE
):

    with open(
        OUTPUT_FILE,
        encoding="utf-8"
    ) as f:

        dataset = json.load(f)


else:

    dataset = {}



# 전체 치즈

with open(
    INPUT_FILE,
    encoding="utf-8"
) as f:

    cheeses = json.load(f)



total = len(cheeses)

# =========================
# 재시작 지점
# =========================

START_FROM = "Yarra Valley Saffy"
started = False

for i, cheese in enumerate(cheeses):

    name = cheese["name"]
    url = cheese["url"]


    # 시작 치즈를 만날 때까지 건너뛰기
    if not started:

        if name == START_FROM:
            started = True
        else:
            continue


    if (not started) and (name in dataset):

        print("[SKIP]", name)
        continue

    print(
        f"\n[{i+1}/{total}] {name}"
    )


    try:


        description = get_description(
            url
        )


        if description:

            print(
                "description:",
                description[:100],
                "..."
            )

        else:

            print(
                "description 없음"
            )



        taste = extract_taste(
            name,
            description
        )



        dataset[name] = {

            "url": url,

            "raw_description":
                description,

            "taste":
                taste

        }



        save(dataset)



        print(
            "taste:",
            taste
        )


        time.sleep(1)



    except Exception as e:


        print(
            "ERROR:",
            name,
            e
        )


        # 실패해도 노드는 남김

        dataset[name] = {

            "url":url,

            "raw_description":"",

            "taste":{

                "flavor":[],
                "aroma":[],
                "texture":[],
                "other":[]

            }

        }


        save(dataset)



print("====================")
print(
    "완료:",
    len(dataset)
)
print("====================")