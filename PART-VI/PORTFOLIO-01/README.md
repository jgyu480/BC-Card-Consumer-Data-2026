# PORTFOLIO-01 — 복수 출점 조합(포트폴리오) 스코어링


## 입력 파일

```
PART-III/MODEL-01/outputs/final_model_v3_1/model01_final_recommendations_v3_1.parquet
PART-II/DATA-02/outputs/area_feature_master.parquet
```

MODEL-01의 상위 후보(브랜드당 최대 15개, `TOP_N_CANDIDATES_PER_BRAND`)에서 `itertools.combinations`로 1~3개 조합을 생성해 스코어링한다.

## 스코어링 공식

```
portfolio_score = 0.65 × average_area_score              (평균상권적합도)
                 + 0.25 × geographic_diversification_score   (자치구분산 0.5 + 거리 0.5 를 합친 값)
                 - 0.10 × overlap_risk_score(정규화됨)        (소비자분산도의 반대 표현, 아래 4번 참고)
```

| 요인 | 실질 가중치 |
|---|---|
| 평균상권적합도 | 65% |
| 자치구 분산 | 12.5% |
| 상권 간 거리 | 12.5% |
| 소비자 구성 분산(중복위험의 반대) | 10% |

`consumer_diversification_score`와 `overlap_risk_score`는 합이 항상 100인 반대쌍이라 점수식엔 하나만 사용(`overlap_risk_score`를 감점 형태로).

**CONFIG 값**
- `TOP_N_CANDIDATES_PER_BRAND`: 15
- `MIN_DISTANCE_M` / `FULL_SCORE_DISTANCE_M`: 800m / 5000m (초기 3000m에서 상향)
- `desired_store_count=1`일 때 분산 관련 필드는 `null` 처리

## 4. 버그 발견 및 수정 히스토리

### 4-1. overlap_risk 절대값 문제
`overlap_risk_penalty`를 10%→20%로 올려보는 실험 중 발견: `overlap_risk_score`가 원래 절대값 자체가 평균 85점 근처로 항상 높은 지표라, 가중치를 올리니 "순위를 가르는" 게 아니라 "모든 조합을 일괄로 17점씩 깎는" 현상 발생(예: 못난이꽈배기 종합점수가 44.5까지 하락).

**수정**: `overlap_risk`를 절대값이 아니라 "같은 브랜드·같은 조합크기 후보군 안에서의 상대적 위치"로 min-max 정규화해서 점수 계산에만 사용(화면에 보여주는 절대값은 안 건드림). 결과: 2개조합 1~3위 평균 격차 0.76점 → 3.21점으로 약 4배 개선.

### 4-2. 그룹 간 점수 비교 불가 (알려진 한계, 안내 문구로 대응)
1개/2개/3개 조합 그룹은 overlap_risk를 각자 독립적으로 정규화하기 때문에, `desired_store_count`가 다른 그룹끼리는 `portfolio_score`를 직접 비교하면 안 됨(3개조합 1위가 2개조합 1위보다 점수가 높게 나올 수 있는데, 이게 "3개가 더 낫다"는 뜻이 아님).

**대응**: 정규화 방식(코드)은 그대로 두고, `assemble_result_v3.py`의 `UI_COPY.portfolio_score_note`에 안내 문구 추가 — *"점수는 선택하신 출점 수 안에서의 순위입니다. 출점 수가 다른 옵션끼리 점수를 직접 비교하지 마세요."* 

## 5. 동점 처리 (`is_top_recommendation`, `gap_tier`)

### 5-1. is_top_recommendation
1~2위 점수차가 임계값 이내면 둘 다 "최우선 추천"으로 표시. **사이즈별로 임계값이 다름**:

```python
TIE_GAP_THRESHOLD_BY_SIZE = {1: 1.0, 2: 0.5, 3: 0.2}
```

조합 개수가 많을수록(3개 > 2개 > 1개) 후보 풀(조합 가능한 경우의 수)이 촘촘해져서 1~2위 격차가 자연히 작아지기 때문. 처음에 고정 1점을 전부에 적용했더니 3개조합만 75%가 동점 처리되는 문제 발견(1개 21%, 2개 42%, 3개 75%) → 각 사이즈 그룹 1~2위 격차의 실측 25분위값 기준으로 재조정 → 세 사이즈 다 21~29%로 고르게 맞춤. 

### 5-2. gap_tier
동점이 아닌 대안들도 "1위와 근소한 차이인지"를 알려주는 범주형 필드. 

```python
gap_tier: "top" | "close" | "alternative"
# close: 1위와의 격차가 해당 사이즈 임계값의 2배 이내
```

## 6. rationale_facts / risk_factors — 규칙 기반 템플릿 유지 (의도적 결정)

포트폴리오 "왜 이 상권들을 함께 조합했는지"에 대한 설명은 LLM으로 만들지 않고 규칙 기반 템플릿을 그대로 유지하기로 결정했다. 

```python
def build_rationale_facts(areas_df, avg_area_score, overlap_risk_raw, desired_store_count, min_dist_m):
    # "선택 상권의 평균 적합도 XX.X점", "상권 간 최소 거리 X.Xkm",
    # "N개 자치구로 분산" 등 — 전부 구조화 데이터 기반 결정론적 문장
```

`risk_factors`는 항상 최소 1개("특별히 확인된 위험 요인 없음")를 채워서 내보낸다 — 빈 배열이면 화면 코드가 `risk_factors[0]`에 접근하다 `IndexError`가 나는 문제가 있었다(`build_recommendations_v3.py`의 동일 패턴과 같은 이유).

## 7. 실사업 타당성 검토

실측 데이터로 직접 돌려보고 결과가 타당하다고 판단해 완료 처리. (서울 상권 특성상 합리적인 조합이 나오는지, 1위·2위가 사실상 같은 지역 조합에서 순서만 바뀐 건 아닌지 등을 확인)

## 8. 알려진 데이터 한계


- 소비자 구성이 서울 상권 전반적으로 코사인 유사도가 높아 `overlap_risk_score` 절대값이 대부분 70~90대로 높게 나옴(4-1 정규화로 대응)
- `structured_evidence` 컬럼은 모델카드가 LLM/앱 사용을 금지한 필드 — 참조하지 않음