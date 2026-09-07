# DATA-02 | 서울 상권 소비·경쟁 특성

## 1. 역할

DATA-02는 브랜드와 무관한 서울 후보 상권의 소비·시장·경쟁 특성을 구축합니다. 브랜드 점포 식별, 영업 상태 확인, 점포 중복 제거와 서울 상권 연결은 DATA-01이 담당합니다. 기존 브랜드 점포와 후보 상권의 거리, 기존 입점 여부, 브랜드별 적합도는 MODEL-01이 DATA-01과 DATA-02를 결합해 계산합니다.

### DATA-01과의 결합 계약

| DATA-01 | DATA-02 | MODEL-01 사용 |
|---|---|---|
| `brand_ccg_presence.parquet` | 자치구별 BC 제과 소비 특성 | 브랜드 입점 DNA |
| `brand_area_presence.parquet` | 전체 서울 상권 목록 | 기존 입점 상권 제외·검증 |
| `brand_store_master.parquet`의 좌표 | 상권 기준정보·특성 | 기존 점포 근접 위험 |

DATA-02에는 `brand_id`, 브랜드별 기존 입점 여부, 브랜드별 거리를 넣지 않습니다.

## 2. 분석 단위와 업종

- 결과의 한 행: `area_id × period_q`
- 기준분기: `2026Q2`
- 서울시 업종: `CS100005 제과점`
- BC 업종: `8301 제 과 점`
- BC 특성은 자치구 단위이므로 변수명에 `_ccg`를 붙입니다.
- 자치구 BC 값을 상권 고유 소비값으로 해석하지 않습니다.

## 3. 방법론과 선정 이유

### 즉시 적용

1. **시장 수요와 경쟁 공급의 분리**  
   점포 수는 공급, 매출액·거래건수는 수요로 따로 저장합니다. 점포가 많은 지역은 포화일 수도 있지만 수요가 검증된 집적지일 수도 있으므로 경쟁으로만 해석하지 않습니다.

2. **점포당 매출·거래건수**  
   `상권 추정매출 / 상권 점포 수`로 수요 대비 공급의 설명 가능한 대리변수를 만듭니다. 개별 매장의 실제 평균매출이나 신규점포 예상매출로 해석하지 않습니다.

3. **프랜차이즈 비중과 개·폐업 지표**  
   서울시가 같은 상권·업종 단위로 직접 제공하므로 1차 경쟁구조 지표로 사용합니다. 폐업률은 실패 확률이 아니라 현재 상권의 변화·위험 신호입니다.

### 데이터 확인 후 적용

4. **250m·500m·1km 반경 점포 수**  
   단일 반경을 자의적으로 정하지 않고 세 반경의 민감도를 비교합니다. 소진공 점포 좌표는 상권 내 공식 점포 수를 대체하지 않고 주변 미시 경쟁을 보완합니다.

5. **거리감쇠 경쟁지수**  
   가까운 경쟁점에 더 큰 가중치를 주는 `sum(exp(-distance / bandwidth))`를 계산합니다. 반경 점포 수보다 거리 차이를 보존한다는 장점이 있습니다.

### 현재 제외

- **HHI**: 상권별 브랜드 매칭이 충분히 검증되기 전에는 계산하지 않습니다.
- **KDE**: 공식 상권 점포 집계와 정보가 크게 중복되고 해석이 어렵습니다.
- **Local Moran/Getis-Ord**: 탐색적 지도에는 유용하지만 브랜드별 추천 피처로 직접 해석하기 어렵습니다.
- **도로망 거리**: 구현비용에 비해 현재 상권 단위 추천에서 추가효과가 불확실합니다.
- **폐업·매출 예측**: DATA-02의 주장 범위를 벗어납니다.

## 4. 참고 연구·공개 구현

- Zhao, Zong & Wu (2023), *Site Selection Prediction for Coffee Shops Based on Multi-Source Space Data Using Machine Learning Techniques*: 다원 공간자료로 후보지 특성을 구성하는 방법을 참고합니다.  
  https://www.mdpi.com/2220-9964/12/8/329
- Ouyang et al. (2020), *Site Selection Improvement of Retailers Based on Spatial Competition Strategy*: 거리 기반 공간 경쟁지수의 근거로 참고합니다.  
  https://www.mdpi.com/2220-9964/9/6/357
- Wang et al. (2018), *Site Selection of Retail Shops Based on Spatial Accessibility and Hybrid Model*: 후보 필터 후 적합도를 평가하는 2단계 구조를 참고합니다.  
  https://www.mdpi.com/2220-9964/7/6/202
- Sánchez-Saiz et al. (2022), *Identification of Robust Retailing Location Patterns*: 동종·이종 점포 집적과 회피를 구분하는 관점을 참고합니다.  
  https://doi.org/10.1007/s40747-021-00335-8
- Databricks Site Selection Accelerator: 지역 유사도와 경쟁 패널티를 분리한 공개 구현을 참고합니다. Hex2Vec/H3 자체는 현재 범위에서 사용하지 않습니다.  
  https://github.com/databricks-industry-solutions/site-selection-accelerator
- GeoPandas 공식 문서: 좌표계 변환, 공간조인, 최근접 거리 구현의 기준입니다.  
  https://geopandas.org/en/stable/docs/user_guide.html

## 5. 최종 산출물

- `output/bc_bakery_ccg_features.parquet`
- `output/seoul_bakery_area_features.parquet`
- `output/area_feature_master.parquet`
- `output/area_feature_dictionary.csv`
- `reports/data02_quality_report.md`

## 6. 품질 원칙

- 모든 식별자는 문자열로 저장합니다.
- 원문 열과 표준화 열을 구분합니다.
- 조인 실패와 미관측은 0이 아니라 `NULL`로 둡니다.
- 실제 0과 미관측을 `*_observed`로 구분합니다.
- 비율의 분모가 0이면 `NULL`입니다.
- 모든 출력에 출처와 기준기간을 기록합니다.
- 원본 BC 데이터는 출력·저장소·앱에 포함하지 않습니다.

<!-- STAGE2_METHOD_START -->
## 2단계 방법론 확정

BC 원본의 실제 컬럼명 `TP_BUZ_NO`, `TP_BUZ_NM`, `amt`, `cnt`는 공식 레이아웃의 `TPBUZ_NO`, `TPBUZ_NM`, `AMT`, `CNT`로 표준화합니다. 성별은 `1=남성`, `2=여성`, `3=외국인`, `x=법인`으로 처리하며, 여성 비중은 외국인과 법인이 섞이지 않도록 남녀 개인 이용금액만 분모로 사용합니다. 연령 비중 역시 개인 고객의 코드 1~6만 분모에 포함하고 `x`는 제외합니다.

BC의 11개 업종은 모두 보존하여 향후 다른 외식 업종으로 확장할 수 있게 하고, 현재 제과점 파일럿은 `TPBUZ_NO=8301`로 별도 출력합니다. 서울시 제과점은 `CS100005`, 소진공의 공간 경쟁점은 3단계에서 `빵/도넛`으로 정의합니다. `카페`와 `떡/한과`는 동일 업종으로 합치지 않으며, 커피·음료(`CS100010`)만 보완 수요 지표로 분리합니다.

BC 자료는 월별 시군구 단위이고 서울시 자료는 분기별 상권 단위이므로, 시군구 소비액을 상권에 비례 배분하지 않습니다. 이 임의 배분은 가짜 정밀도를 만들기 때문입니다. 대신 전국 시군구 소비 프로필과 서울 상권 기본 특성을 각각 유지하고 MODEL-01이 계층적으로 결합합니다. 전국 시군구 코드는 DATA-01과 같은 소진공 `시군구코드`에서 생성하여 결합 기준을 통일합니다.

원시 합계·관측 여부·비율을 함께 남깁니다. 로그 변환, 표준화, 결측치 대체는 학습·평가 분할 이후 MODEL-01에서 수행하여 데이터 누수를 막습니다. 서울시 매출 행이 없는 경우도 실제 0과 구별하도록 `*_sales_observed`를 유지합니다.
<!-- STAGE2_METHOD_END -->

<!-- STAGE3_METHOD_START -->
## 3단계 공간 경쟁지표 방법론

행정구역 기준일 차이로 전남·광주의 기존 시도명은 경계가 유지된 시군구명을 기준으로 2026년 7월 신설 코드에 연결했습니다. 인천의 옛 중구·동구·서구는 새 제물포구·영종구·서해구·검단구와 일대일 대응하지 않으므로, BC 소비액을 임의 분할하지 않고 3개 지역을 전국 시군구 프로필에서 제외했습니다. 최종 연결률은 252/255(98.82%)입니다.

소진공 서울 점포의 WGS84 경위도를 서울 상권 중심점과 동일한 EPSG:5181로 변환합니다. 동일 업종은 `빵/도넛`, 인접 업종은 `카페`와 `떡/한과`로 분리하며, 동일 점포 ID는 한 번만 사용합니다.

경쟁 강도는 250m·500m·1,000m의 다중 반경 점포 수, 최근접 점포 거리, `exp(-거리/300m)` 지수 거리감쇠 합으로 표현합니다. 단일 반경만 사용하면 경계 바로 밖의 점포에 결과가 급변하므로 여러 반경과 연속형 거리감쇠를 함께 보존합니다. 최근접 거리는 주변 점포가 적은 후보 사이의 차이를 보완합니다.

상권 폴리곤 내부 점포 수만 다시 계산하는 방식은 채택하지 않습니다. 서울시 점포 자료가 이미 상권 내부 점포 수를 제공하고, 폴리곤 방식은 경계 바로 밖의 경쟁점을 놓치기 때문입니다. KDE의 대역폭 자동 최적화도 단일 시점 자료에서 과적합 위험이 있어 보류합니다. 대신 해석 가능한 원시 공간 특성을 만들고, 실제 선택할 반경과 변환은 MODEL-01 교차검증에서 결정합니다.

서울시 상권 내부 점포 수와 소진공 중심점 반경 점포 수의 상관을 교차검증으로 기록합니다. 두 값은 공간 정의가 달라 일치 여부가 아니라 전반적 방향의 일관성을 확인하는 용도입니다.
<!-- STAGE3_METHOD_END -->

<!-- DATA02_PROGRESS_START -->

## 7. 작업 진행 현황

### 1/4. 분석 구조 및 데이터 검증 — 완료

DATA-02의 역할, 분석 단위와 DATA-01 및 MODEL-01과의 결합 규격을 정의하였다.

- 분석 단위: `area_id × period_q`
- 기준 분기: `2026Q2`
- 서울시 제과점 업종코드: `CS100005`
- BC카드 제과점 업종코드: `8301`
- BC카드·서울시·소진공 원본 스키마 검증
- 기간, 식별자, 업종코드, 결측 및 중복 확인
- DATA-01 및 MODEL-01과의 역할 분리
- 분석 설정과 방법론 문서화

주요 결과물:

- `config/data02_config.json`
- `src/inspect_and_collect.py`
- `reports/stage1_schema_report.md`

### 2/4. BC카드 및 서울시 상권 기본 특성 생성 — 완료

BC카드 데이터를 월별·시군구별 소비 프로필로 가공하고, 서울시 상권분석서비스를 이용해 상권별 시장 및 경쟁 특성을 생성하였다.

생성 특성:

- 소비금액, 거래건수 및 객단가
- 성별·연령대별 소비 비중
- 제과점 점포 수와 프랜차이즈 비중
- 개업·폐업 수와 비율
- 추정매출액과 거래건수
- 점포당 매출 및 점포당 거래건수
- 커피 업종의 점포 및 매출 특성

BC카드 자료는 시군구 단위, 서울시 자료는 상권 단위로 유지하며 시군구 소비를 개별 상권에 임의 배분하지 않는다.

주요 결과물:

- `outputs/bc_ccg_month_features.parquet`
- `outputs/bc_ccg_profile_2026h1.parquet`
- `outputs/bc_bakery_ccg_profile_2026h1.parquet`
- `intermediate/ccg_reference.parquet`
- `intermediate/area_base_features_20262.parquet`
- `reports/stage2_quality_report.md`

현재 결과 규모:

- 전체 BC 시군구·업종 프로필: 2,352행
- 제과점 BC 시군구 프로필: 252행
- 서울 후보 상권: 1,650개

### 3/4. 좌표 기반 공간 경쟁 특성 생성 — 완료

소진공 서울 점포 좌표를 이용해 후보 상권 주변의 공간 경쟁 특성을 생성하였다.

입력 점포:

| 업종 | 점포 수 |
|---|---:|
| 빵·도넛 | 6,119개 |
| 카페 | 22,739개 |
| 떡·한과 | 1,063개 |
| 합계 | 29,921개 |

생성 특성:

- 250m·500m·1,000m 반경 내 점포 수
- 가장 가까운 제과점까지의 거리
- `exp(-거리/300m)` 기반 거리감쇠 경쟁압력
- 카페와 떡·한과 점포의 공간 밀도
- 제과점 대비 카페 점포 비율
- 서울시 공식 점포 수와 소진공 반경 지표의 교차검증

품질검증 결과:

- 최종 후보 상권: 1,650개
- 최종 특성 수: 165개
- `area_id` 중복: 0건
- 검증 오류: 없음
- 비교 가능 상권: 1,186개
- Pearson 상관계수: 0.4319
- Spearman 상관계수: 0.3887

주요 결과물:

- `intermediate/seoul_relevant_store_points_202606.parquet`
- `outputs/seoul_spatial_competition_features_202606.parquet`
- `outputs/area_feature_master.parquet`
- `reports/stage3_quality_report.md`
- `reports/stage3_manifest.json`

### 4/4. DATA-01 결합 계약 및 최종 품질검증 — DATA-01 완료 후 진행

DATA-01 담당자는 다음 결과물을 완성한 후 DATA-02의 4/4 작업까지 진행한다.

필요한 DATA-01 결과물:

- `brand_store_master.parquet`
- `brand_ccg_presence.parquet`
- `brand_area_presence.parquet`
- `brand_name_mapping.csv`
- `data01_quality_report.md`

4/4 작업 내용:

1. DATA-01과 DATA-02의 `area_id`, `ccg_id` 자료형을 통일한다.
2. `brand_ccg_presence.parquet`과 BC 시군구 프로필의 연결률을 확인한다.
3. `brand_area_presence.parquet`과 상권 특성 테이블의 연결률을 확인한다.
4. 결합키의 중복, 결측 및 미연결 행을 검증한다.
5. 브랜드 점포 좌표의 유효성을 확인한다.
6. 동일 브랜드가 이미 입점한 상권을 후보에서 제외할 수 있는지 확인한다.
7. 기존 점포와 후보 상권 사이의 거리 계산 가능 여부를 확인한다.
8. 결합 전후 행 수와 데이터 보존 여부를 확인한다.
9. MODEL-01 입력 규격과 결합 계약을 문서화한다.
10. 최종 품질보고서를 작성하고 README 상태를 갱신한다.

DATA-01과 DATA-02는 하나의 파일로 미리 합치지 않는다. 두 특성 테이블을 독립적으로 유지하고 MODEL-01에서 `area_id`, `ccg_id`와 점포 좌표를 이용해 결합한다.

<!-- DATA02_PROGRESS_END -->
