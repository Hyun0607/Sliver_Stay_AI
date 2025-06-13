# -*- coding: utf-8 -*-
"""예상 질의 만들기_CapStone_ver2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12-_5ryPdSACyzzvWcrtPv5oCld2p9AQK
"""

#  필수 설치
!pip install openai pandas openpyxl tqdm
!pip install openai==0.28

#  라이브러리 불러오기
import openai
import pandas as pd
from tqdm import tqdm
import os
import time

# OpenAI API 키 설정
openai.api_key = "sk-..."

# API 연결 확인
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response["choices"][0]["message"]["content"])

# ✅ 데이터 불러오기
df = pd.read_csv("숙소_설명문.csv", encoding="utf-8")
df["숙소설명"] = df["숙소설명"].fillna("")
df["장애인편의시설"] = df["장애인편의시설"].fillna("")

df

# ✅ 3. 프롬프트 템플릿 함수
def build_prompt(overview, facilities):
    if facilities.strip() and facilities.strip() != "X":  # ✅ 장애인 편의시설이 있을 경우
        return f"""당신은 고령자 및 장애인을 위한 맞춤 숙소 추천 시스템의 질문 생성 전문가입니다.

아래 숙소에 대한 설명과 장애인 편의시설 정보를 참고하여, 사용자가 숙소를 추천받기 위해 할 수 있는 **현실적인 질문 5가지**를 만들어주세요.

[설명문]
{overview}

[장애인 편의시설 정보]
{facilities}

[지침]
- 반드시 위의 정보만을 바탕으로 질문을 작성해주세요.
- 질문은 **장소/지명 관련 질문 2개**, **고령자 및 장애인 편의시설 관련 질문 최대 3개**로 구성해주세요.
- 질문은 고령자나 장애인 당사자 또는 보호자의 시각에서 자연스럽고 구체적인 표현으로 작성해주세요.
- 숙소명은 질문에 절대 포함하지 마세요.

[예상 질문 리스트]
1. 휠체어를 사용하시는 아버지와 함께 여행하려고 하는데, 엘리베이터가 있는 숙소가 있을까요?
2. 할머니가 시각장애가 있어서 그러는데, 점자 안내판이 잘 되어 있는 숙소가 있을까요?
3. 부모님이 몸이 불편하셔서, 장애인 편의시설이 잘 되어있는 숙소가 있나요?
4. 오죽헌 근처에 숙소를 잡고 싶은데, 편의시설도 잘 갖춰져 있는 숙소가 있을까요?
5. 아침에 해변을 산책하고 싶은데, 정동진 해변 근처에 숙소가 있을까요?
"""
    else:
        # ❗편의시설 정보가 없을 경우: 설명문만 활용
        return f"""당신은 고령자 및 장애인을 위한 맞춤 숙소 추천 시스템의 질문 생성 전문가입니다.

아래 숙소 설명문을 읽고, 숙소 주변 환경이나 위치 등을 고려한 **현실적인 질문 5가지**를 만들어주세요.

[설명문]
{overview}

[지침]
- 장애인 편의시설 정보가 없으므로, **장소/지명 중심의 질문 위주로** 구성해주세요.
- 질문은 고령자나 보호자의 입장에서 자연스럽고 구체적인 표현으로 작성해주세요.
- 숙소명은 질문에 절대 포함하지 마세요.

[예시]
1. 일출을 보고싶은데, 바다 전망이 보이는 숙소가 있나요?
2. 차를 가져오지 않아서, 춘천역 근처에 호텔이 있나요?
3. 부모님이 산책을 좋아하셔서, 근처에 공원이 있는 숙소를 추천해줘
4. 아버지가 골프를 즐겨 하는데, 골프장이 잘 구축되어 있는 숙소가 있나요?
5. 아침 일찍 설악산을 올라가야해서, 근처에 숙소가 있을까요?
"""

# ✅ 4. LLM 질의 생성 함수 (재시도 포함)
def generate_questions(overview, facilities, retries=3, delay=5):
    prompt = build_prompt(overview, facilities)
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "당신은 고령자 및 장애인을 위한 숙소 추천 시스템의 질문 생성 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=512,
                timeout=60
            )
            content = response.choices[0].message['content']
            questions = [line.strip("12345. ").strip() for line in content.strip().split('\n') if line.strip()]
            return questions[:5] + [""] * (5 - len(questions))
        except Exception as e:
            print(f"[{attempt+1}회차 재시도] 에러 발생: {e}")
            time.sleep(delay)
    return None

# ✅ 5. 전체 숙소에 대해 질문 생성 실행
results = []
failed_hotels = []

for _, row in tqdm(df.iterrows(), total=len(df)):
    숙소명 = row["숙소명"]
    설명문 = row["숙소설명"]
    편의시설 = row["장애인편의시설"]

    질문들 = generate_questions(설명문, 편의시설)
    if 질문들 is None:
        failed_hotels.append(숙소명)
        질문들 = [""] * 5

    results.append({
        "숙소명": 숙소명,
        "설명문": 설명문,
        "장애인편의시설": 편의시설,
        "질문1": 질문들[0],
        "질문2": 질문들[1],
        "질문3": 질문들[2],
        "질문4": 질문들[3],
        "질문5": 질문들[4]
    })


    time.sleep(1.5)

# 결과 확인
df_result = pd.DataFrame(results)
df_result

# ✅ 6. 결과 저장
df_result.to_csv("VectorDB.csv", index=False, encoding="utf-8-sig")
print("✅ 결과 저장 완료: 생성된_질문_결과.csv")
