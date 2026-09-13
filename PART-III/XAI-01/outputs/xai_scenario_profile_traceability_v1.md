# XAI 시나리오 입력 추적성 감사

## 목적
- MODEL-03의 27개 시나리오가 실제로 어떤 모델 입력값으로 예측되었는지 확인한다.
- `MISSING_TRACE` 특성은 기여도 계산 전에 시나리오별 수치를 복원해야 한다.

## 시나리오 프로필 관련 열
- `scenario_id, scenario_profile, size_scenario, brand_scenario_rank_by_predicted_sales, brand_scenario_rank_by_efficiency`

## 특성별 추적 결과
```text
                               field_name availability model_use       trace_status                   interpretation manifest_candidate_paths
                                 brand_id         개점 전     입력 허용             DIRECT          시나리오 파일에 실제 입력값이 직접 저장됨                         
                    area_id 및 개점 당시 상권 변수         개점 전     입력 허용      MISSING_TRACE  현재 파일만으로 시나리오별 실제 입력값을 추적할 수 없음                         
                            store_area_m2         개점 전     입력 허용             DIRECT          시나리오 파일에 실제 입력값이 직접 저장됨                         
monthly_rent_won 및 initial_investment_won         개점 전     입력 허용      MISSING_TRACE  현재 파일만으로 시나리오별 실제 입력값을 추적할 수 없음                         
        same_brand_store_count_at_opening         개점 전     입력 허용 MANIFEST_CANDIDATE 시나리오 매니페스트에 입력값 또는 생성 규칙 후보가 존재함           scenario_count
                        monthly_sales_won         개점 후    정답만 허용      MISSING_TRACE  현재 파일만으로 시나리오별 실제 입력값을 추적할 수 없음                         
                  closing_date 및 폐점 이후 상태         개점 후     입력 금지      MISSING_TRACE  현재 파일만으로 시나리오별 실제 입력값을 추적할 수 없음                         
```

## 매니페스트에서 profile·demand·traffic·competition 관련 항목