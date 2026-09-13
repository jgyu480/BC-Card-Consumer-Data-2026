# XAI 범위 고정

## 주 설명 대상
- MODEL-03의 Ridge 기반 브랜드×입지환경×규모 매출 시나리오
- 설명 단위: 브랜드 1개 × 입지환경 1개 × 매장규모 1개
- 주의: 합성 학습자료 기반 시나리오이며 실제 신규 점포 매출 보증값이 아님

## MODEL-02 처리
- MODEL-02 최종 결과는 미래 예측이 아닌 관측 시장 스크리닝임.
- SHAP을 적용하지 않고 최근 매출·백분위·추세·점포수 근거를 제시함.

## 금지
- MODEL-02 관측 시장 화면을 미래 매출 예측으로 해석하지 않음
- MODEL-03 시나리오를 실제 출점 후 확정 매출로 표현하지 않음
- 타깃값·미래 기간 정보·사후 관측값을 설명 변수로 사용하지 않음
- SHAP 기여도를 인과효과로 표현하지 않음

## 연결 파일
- `model03_training_data`: `PART-III/MODEL-03/intermediate/synthetic_modeling_dataset_v1.parquet`
- `model03_selection`: `PART-III/MODEL-03/intermediate/synthetic_model_selection_decision_v1.json`
- `model03_feature_contract`: `PART-III/MODEL-03/outputs/model03_feature_availability_contract_v1.csv`
- `model03_scenarios`: `PART-III/MODEL-03/outputs/synthetic_brand_area_size_revenue_scenarios_v1.csv`
- `model03_scenario_manifest`: `PART-III/MODEL-03/outputs/synthetic_brand_area_size_scenario_manifest_v1.json`
- `model02_observed_screen`: `PART-III/MODEL-02/outputs/model02_executive_observed_market_screen_final_2026q2.csv`

## 선택 모델 메타데이터
```json
{
  "data_origin": "SYNTHETIC_DO_NOT_USE_FOR_BUSINESS",
  "validation_method": "개점 코호트 시간차단 검증 + 코호트 블록 부트스트랩 10,000회",
  "qualification_rule": "기준선보다 낮은 WAPE, 부트스트랩 차이 95% 구간 전체 0 미만, 5개 중 4개 이상 코호트 승리, 양의 순위상관",
  "qualified_models": [
    "ridge_brand_aware_v1",
    "hist_gradient_boosting_brand_aware_v1"
  ],
  "selected_model_for_synthetic_prototype": "ridge_brand_aware_v1",
  "production_status": "NOT_DEPLOYABLE_UNTIL_REAL_PARTNER_DATA_VALIDATION",
  "warning": "합성 데이터에서 통과한 모델은 실제 본사 데이터에서 동일 검증을 통과하기 전까지 배포할 수 없음"
}
```