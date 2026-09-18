# APP-03 — 설명 포함 최종 대시보드


## 1. APP-03의 역할

APP-03은 MODEL-01과 LLM-01의 실제 산출물을 mock 대시보드에 연결해 실서비스로 완성한다. 복수 출점 조합(포트폴리오) 로직을 구현했고(자세한 내용은 PORTFOLIO-01 참고), LLM-01의 자연어 설명을 4~20위까지 확장하였다.  추가적으로 실제 화면에서 발생한 버그들을 수정했고, 실제 MODEL-01 데이터 기반의 전체 대시보드(Brand Overview·추천 포트폴리오·상권 상세)를 완성하였다.


## 2. 사용한 입력 파일 (v3 기준)

```
PART-III/MODEL-01/outputs/final_model_v3_1/model01_final_recommendations_v3_1.parquet
PART-II/DATA-02/outputs/area_feature_master.parquet
PART-II/DATA-01/brand_area_presence.parquet
PART-II/DATA-01/brand_name_mapping.csv        (경쟁 브랜드 조회용, competitor_lookup.py)
PART-V/LLM-01/scripts/code_to_text_mapping.json
PART-V/LLM-01/scripts/glossary.json
PART-V/LLM-01/scripts/llm01_final_explanations.json        (B 원본, 1~3위)
PART-V/LLM-01/scripts/llm01_explanations_api_4to20.json    (C 확장분, 4~20위)
```



## 3. 데이터 파이프라인 구조

```
build_portfolios_v3.py       (PART-VI/PORTFOLIO-01/scripts/)
        ↓ portfolios_output_v3.json
build_recommendations_v3.py  (PART-VI/APP-03/data_pipeline/)
        ↓ recommendations_output_v3.json
assemble_result_v3.py        (PART-VI/APP-03/data_pipeline/)
        ↓ result_v3.json  ←  data_loader.py가 이 파일을 읽음
```

LLM-01 확장(4~20위)은 별도 1회성 스크립트로 앞단에서 실행:
```
PART-V/LLM-01/scripts/generate_with_llm_4to20.py   (DRY_RUN=False로 실제 API 호출)
```

**실행 순서**
```bash
# 1. 최초 1회만 (또는 LLM 결과를 다시 만들고 싶을 때만)
python PART-V/LLM-01/scripts/generate_with_llm_4to20.py

# 2. 데이터 갱신할 때마다
python PART-VI/PORTFOLIO-01/scripts/build_portfolios_v3.py
python PART-VI/APP-03/data_pipeline/build_recommendations_v3.py
python PART-VI/APP-03/data_pipeline/assemble_result_v3.py

# 3. 서버 재시작 (utils/data_loader.py가 lru_cache로 캐싱하므로 필수)
python app.py
```

## 4. 필드 매핑 (mock → 실제 데이터)

| mock 필드 | 실제 소스 |
|---|---|
| `suitability_score` | `final_suitability_score × 100` (재계산 금지) |
| `dna_match_score` | `absolute_fit_percentile × 100` |
| `market_score` | `market_opportunity_percentile × 100` |
| `competition_attractiveness_score` | `low_competition_risk_percentile × 100` |
| `proximity_risk_score` | 직접 계산 (500m 미만=100, 2000m 이상=0, 선형 보간) |
| `rank` | `final_rank` (동점 처리는 미적용 — 6-2 참고) |
| `district_nm` | `area_feature_master`의 `ccg_nm` |
| `centroid_latitude/longitude` | EPSG:5181 → WGS84 변환 (pyproj) |
| `positive_factors`/`risk_factors` | `positive_drivers`/`caution_flags` 코드를 `code_to_text_mapping.json`으로 문장 변환 |
| `area_explanation` (신규) | LLM-01 텍스트 (1~3위는 B 원본, 4~20위는 C 확장분) |
| `facts.monthly_sales_amt` 등 (신규) | 원본 매출·경쟁점 개수 (percentile 아닌 실수치) |
| `consumer_profile.demand_context` | 연령대 + 성비 + (법인/외국인 비중 상위 25%인 경우만 추가 표기) |
| `brand_type` | 기존 매장(`brand_area_presence.parquet`) 가중평균 연령대 기반, 표본 불충분 시 "복합형" |

## 5. 주요 설계 결정 사항

### 5-1. brand_type 분류
기존 매장을 `store_cnt` 가중평균한 연령대로 분류. **1위-2위 연령대 비중 차이가 2%p 미만이면 "복합형"으로 처리**(ex - 더베이크 사례: 기존 매장 6개뿐이라 1위 50대 12.0% vs 2위 30대 11.4%로 사실상 균등했는데 "중장년층 중심형"이라고 단정적으로 표시되던 문제 수정). `classify_brand_type_fallback`은 기존 매장 데이터 자체가 없는 브랜드용 폴백.

### 5-2. 법인/외국인 비중 반영
전체 82개 컬럼 재검토 중 `bc_corporate_share_amt`(법인 비중), `bc_foreign_share_amt`(외국인 비중)를 반영. 상위 25%(각각 0.6746, 0.5794 이상)인 경우만 "(법인 수요 비중 높음)"처럼 괄호로 추가 표기 

### 5-3. next_checks 다양화
`risk_review_flag` 컬럼을 활용해 상권마다 다르게 — 기존엔 고정 2개 문구만 반복되던 문제.

### 5-4. 브랜드 요약(Overview) 태그 설계 변경
초기엔 `positive_factors`/`risk_factors` 전체 문장을 pill 태그로 표시했으나 두 가지 문제 발견:
- percentile을 소수점 없이 반올림하면서 "상위 0%"처럼 오해 소지 있는 값 노출 (실제로는 0.46%처럼 좋은 값)
- 상위 5개 상권을 뭉뚱그려서 집계하다 보니 "경쟁 다소 높음"+"경쟁 보통"처럼 모순돼 보이는 태그가 동시 노출

**해결**: 태그 자체를 완전히 제거하고 "기존 매장 N곳 데이터 기반", "서울 N개 자치구에 후보 분포"(실측으로 검증: 6~15개로 실제 갈림, 등급별 후보 개수는 시도했으나 거의 모든 브랜드가 "3/7/10"으로 동일해서 철회) 같은 명확한 팩트로 교체.

### 5-5. 포트폴리오 동점 처리 (`is_top_recommendation`, `gap_tier`)
1~2위 포트폴리오 점수차가 근소하면 둘 다 "최우선 추천"으로 표시. **사이즈별로 임계값이 다름**(1개조합:1.0점, 2개조합:0.5점, 3개조합:0.2점) — 조합 개수가 많을수록(3개>2개>1개) 후보 풀이 촘촘해져서 1~2위 격차가 자연히 작아지기 때문. 고정 1점을 전부에 적용했더니 3개조합만 75%가 동점 처리되는 문제가 있어 실측 25분위 기준으로 사이즈별 값을 따로 잡음.

### 5-6. rank/recommendation_label 색상 로직
초기엔 `suitability_score` 절대값(80/65점 구간)으로 색을 정했으나, 브랜드마다 점수 분포가 달라(예: 파리바게뜨 1위 62.7점, 화이트리에 1위 86.8점) 대부분 "적합"에만 몰리는 문제. `recommendation_label`(브랜드 내 상대 순위 기반: 1~3위=최우선검토, 4~10위=우선검토, 11위~=비교후보) 기준으로 변경.


## 6. 알려진 한계  

### 6-1. DATA-01 기존 매장 데이터는 2026-06-30 기준 스냅샷
그 이후 신규 개점/폐점은 반영 안 될 수 있음. 실제로 뚜레쥬르 1위 추천 상권(까치산역)에 이미 뚜레쥬르 매장이 있다는 걸 발견함 — `brand_area_presence.parquet`엔 매칭이 없었음. 개점일이 6월 이전인지 이후인지는 미확인. 

### 6-2. "더보기" UI 미구현
상권 리스트는 항상 4~20위까지 전부 펼쳐서 보여줌 (11~20위를 접어두는 페이지네이션은 검토만 하고 구현하지 않았다— 기능상 문제는 없다고 판단).


## 7. 프론트엔드 파일 구조 (`PART-VI/APP-03/`)

```
app.py
layout.py                          - 전체 레이아웃, Modal 2개(포트폴리오 상세/상권 상세) 포함
callbacks.py                       - 전체 콜백 (탭 전환, 브랜드 선택, 스크롤 이동 등)
utils/
  data_loader.py                   - result_v3.json 로드 (lru_cache 적용, 브랜드 가나다순 정렬)
components/
  shared_ui.py                     - 색상 톤/거리 포맷 공용 헬퍼 (순환 import 방지용 독립 모듈)
  selector.py                      - 브랜드/출점수 선택 드롭다운
  tabbar.py                        - 탭 네비게이션
  tab1_overview.py                 - Brand Overview 탭
  tab2_portfolio.py                - 추천 포트폴리오 탭 (카드 목록)
  tab2_portfolio_modal.py          - 포트폴리오 상세 모달 (경쟁 브랜드 현황 포함)
  tab3_area_table.py               - 상권 상세 탭 (표 + 행 펼침)
  tab3_area_map.py                 - 지도 (Leaflet)
  competitor_lookup.py             - 상권별 경쟁 브랜드 조회 (DATA-01 직접 참조)
data_pipeline/
  build_recommendations_v3.py
  assemble_result_v3.py
```
