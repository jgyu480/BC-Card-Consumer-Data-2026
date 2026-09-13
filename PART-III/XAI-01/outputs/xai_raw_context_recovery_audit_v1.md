# XAI 원천 상권환경 복원 감사

## 1. 합성 상권 환경 원천 데이터
- 행 수: 80
- 열 수: 7
- 전체 열: `area_id, area_name, area_demand_index, foot_traffic_index, competition_density_index, latitude, longitude`

## 2. XAI와 관련 있는 원천 열
- `area_id, area_name, area_demand_index, foot_traffic_index, competition_density_index`

## 3. 원천 수치 분포
```text
                           count   mean    std    min    10%    25%    50%    75%    90%    max
area_demand_index           80.0  1.113  0.499  0.358  0.631  0.754  0.997  1.427  1.682  2.671
foot_traffic_index          80.0  1.114  0.389  0.484  0.670  0.851  1.041  1.332  1.743  2.316
competition_density_index   80.0  1.633  1.340  0.064  0.388  0.772  1.286  2.154  3.324  7.101
```

## 4. 합성 데이터 생성 매니페스트
```json
{
  "created_at_utc": "2026-09-09T14:38:24.561718+00:00",
  "data_origin": "SYNTHETIC_DO_NOT_USE_FOR_BUSINESS",
  "random_seed": 20260910,
  "purpose": "MODEL-03 파트너 데이터 입력·학습·검증 파이프라인 시험용 합성 데이터. 실제 성능·사업성 주장에 사용 금지.",
  "brands": [
    "BRAND_ALPHA",
    "BRAND_BETA",
    "BRAND_GAMMA"
  ],
  "store_count": 360,
  "monthly_sales_row_count": 14255,
  "area_count": 80,
  "sales_period": "2021-01~2026-06",
  "known_data_generating_relationships": [
    "브랜드별 기본 매출 수준 차이",
    "상권 수요와 유동인구 효과",
    "브랜드-상권 적합도 효과",
    "점포 면적 적합도 효과",
    "경쟁 밀도 및 동일 브랜드 기존점 잠식 효과",
    "개점 초기 매출 램프업과 계절성"
  ]
}
```

## 5. 신규 점포 라벨 생성 매니페스트
```json
{
  "created_at_utc": "2026-09-09T14:42:53.901522+00:00",
  "data_origin": "SYNTHETIC_DO_NOT_USE_FOR_BUSINESS",
  "target_definition": "개점월부터 12개월 동안의 점포별 월매출 합계",
  "target_column": "y_first_12m_sales_won",
  "all_store_count": 360,
  "eligible_store_count": 360,
  "preopening_feature_columns": [
    "data_origin",
    "brand_id",
    "store_id",
    "opening_date",
    "opening_month",
    "area_id",
    "area_name",
    "latitude",
    "longitude",
    "store_area_m2",
    "monthly_rent_won",
    "initial_investment_won",
    "area_demand_index_at_opening",
    "foot_traffic_index_at_opening",
    "competition_density_index_at_opening",
    "same_brand_store_count_at_opening",
    "brand_area_fit_score_at_opening"
  ],
  "future_leakage_columns_in_inputs": [],
  "warning": "합성 데이터 파이프라인 시험 결과이며 실제 브랜드 매출 성능으로 해석할 수 없음"
}
```

## 6. 기존 27개 시나리오 매니페스트
```json
{
  "data_origin": "SYNTHETIC_DO_NOT_USE_FOR_BUSINESS",
  "selected_model": "ridge_brand_aware_v1",
  "prediction_target": "개점 후 첫 12개월 총매출",
  "scenario_count": 27,
  "interval_80_log_residual": 0.1283814972590136,
  "interval_90_log_residual": 0.15900619387732462,
  "business_use_restriction": "실제 파트너 데이터의 시간차단 검증 통과 전에는 출점 추천·실제 매출예측·투자수익률 판단에 사용할 수 없음"
}
```

## 7. 원천 상권 데이터 예시
```text
 area_id area_name  area_demand_index  foot_traffic_index  competition_density_index
AREA_001  합성상권_001           1.016929            1.335810                   0.137350
AREA_002  합성상권_002           0.819210            0.858641                   0.318132
AREA_003  합성상권_003           2.220712            1.796826                   0.063937
AREA_004  합성상권_004           0.851935            0.932299                   0.762723
AREA_005  합성상권_005           1.145911            0.885599                   0.464505
AREA_006  합성상권_006           0.759766            0.845388                   1.110608
AREA_007  합성상권_007           0.515175            1.622803                   1.447491
AREA_008  합성상권_008           1.180315            1.201155                   0.432009
AREA_009  합성상권_009           1.041269            1.923302                   0.715529
AREA_010  합성상권_010           1.224706            0.635158                   1.779332
```