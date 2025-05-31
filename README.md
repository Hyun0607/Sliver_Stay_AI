# 🏡 SilverStay: 
고령자·장애인을 위한 자연어 기반 숙소 추천 시스템

> 자연어로 숙소를 검색하고, 고령층 및 장애인을 위한 조건에 맞춰 AI가 직접 숙소를 추천해주는 RAG 기반 AI 시스템

---

## 📌 프로젝트 개요

현대 사회는 고령화가 급속히 진행되고 있으며, 국내 등록 장애인은 전체 인구의 5% 이상입니다. 하지만 기존 숙소 플랫폼은 단순 키워드 필터 기반으로 구성되어 있어 **"휠체어 가능", "엘리베이터 있음", "○○역 근처"** 등의 조건을 **정확히 반영하지 못하는 한계**가 존재합니다.

**SilverStay**는 이러한 한계를 해결하기 위해, 사용자의 자연어 질의를 이해하고, 조건에 부합하는 숙소를 AI가 직접 추천하는 **LLM 기반 숙소 추천 시스템**입니다. 숙소 설명문 기반 벡터 검색(RAG)과 정형 정보(RDB)를 결합하여 실제 조건과 문맥에 맞는 숙소를 추천합니다.

---

## 🧠 RAG 기술 구조

![Image](https://github.com/user-attachments/assets/9bbcff9f-1f87-423f-b3bf-38bbb63d1a74)

## ⚙️ 질의 → 추천 흐름 요약

```
사용자 질의
↓
OpenAI Embedding
↓
VectorDB(예상질의 기반)
↓
Top-K 숙소 검색
↓
PostgreSQL 정형 정보 조회
↓
LLM (GPT-4o)이 Top-3 숙소 추천
```

---

## 🧩 프로젝트 전체 기술 스택

| 영역 | 도구 |
|------|------|
| LLM | OpenAI API(GPT-4o) (예상질의 생성, 고유명사 리스트 생성, 평가질의 생성, 추천 응답 생성) |
| Embedding | OpenAI Embedding model |
| Vector DB | Chroma (LangChain 기반 VectorStore) |
| RDB | PostgreSQL (GCP Cloud SQL 연동) |
| Backend | FastAPI |
| Frontend | React (음성 검색 인터페이스) |
| 평가/분석 | pandas, KoNLPy, TF-IDF 기반 정답 키워드 추출 |

---

## 🔍 평가 파이프라인

### 1️⃣ 고유명사 추출 (OpenAI API(GPT-4o) 기반)
- 숙소 설명문에서 숙소명을 제외한 관광지·지명 등 고유명사를 추출
- 예: `"설악산"`, `"강릉역"`, `"경포대"` 등
- 📄 `고유명사_리스트_capstone.py`

### 2️⃣ 핵심어 레이블 구축 (TF-IDF)
- 고유명사와 설명문 명사를 비교하여, TF-IDF 기반 핵심어 추출
- 📄 `핵심어_추출capstone.py`

### 3️⃣ 평가 질의 생성 (OpenAI API(GPT-4o) 기반)
- 고유명사 및 장애인 편의시설을 조합하여 자연어 질의 자동 생성 (총 300개)
- 조합 규칙:
  - 1개: 편의시설 1개
  - 2개: 고유명사 1 + 편의시설 1
  - 3개: 고유명사 2 + 편의시설 1 또는 고유명사 1 + 편의시설 2
- 📄 `평가_질의_만들기_capstone_ver2.py`

### 4️⃣ 평가용 RAG 추천 실행
- 사용자가 평가 질의 입력 → 벡터 검색 (Chroma) + 정형 정보 조회 (PostgreSQL)
- GPT-4o가 상위 3개 숙소 추천
- 📄 `capstone_rag(예상질의)_평가용.py`

### 5️⃣ 모델 성능 평가
- 정답 키워드(고유명사+편의시설)와 추천 숙소 비교
- 포함 키워드 개수 및 완전 일치 여부 평가
- 📄 `모델_평가_capstone.py`

---

## 🧪 성능 평가 결과

| 지역 | 정확도(Accuracy) | 정밀도(Precision@3) | 평가 질의 수 |
|------|------------------|----------------------|---------------|
| 춘천시 | 0.73 | 0.61 | 100 |
| 강릉시 | 0.69 | 0.59 | 100 |
| 속초시 | 0.71 | 0.60 | 100 |

✅ *● 평가 결과, 모든 지역에서 정확도(Accuracy)가 약 0.6 이상으로 나타났으며, 특히 강릉시는 0.7/0.58(Accuracy/Precision)로 우수한 성능을 보였음*

✅ *● 전반적으로, 서비스 초기 버전으로 충분한 신뢰도를 확보한 결과라 판단.*

---

## 📁 발표영상

<table>
  <tbody>
    <tr>
      <td>
        <p align="center"> 25.06.01 발표 </p>
        <a href="https://youtube.com/shorts/zrDNK5mdWFA?feature=share" title="SilverStay 발표 영상">
          <img align="center" src="https://github.com/user-attachments/assets/defc25e0-b497-4147-9676-417dd817745d" width="300" >
        </a>
      </td>
      <td>
        <ul>
          <li> 자연어 질의에 기반한 숙소 추천 흐름 시연 </li>
          <li> 음성 검색 → LLM 기반 Top-3 숙소 응답 과정 시각화 </li>
          <li> 예상질의 기반 벡터 검색 성능 데모 포함 </li>
        </ul>
      </td>
    </tr>
  </tbody>
</table>
