# XAI 특성 연결 감사

## 1. 학습표본
- 행 수: 360
- 열 수: 24
- 열: `data_origin, brand_id, store_id, opening_date, opening_month, area_id, area_name, latitude, longitude, store_area_m2, monthly_rent_won, initial_investment_won, area_demand_index_at_opening, foot_traffic_index_at_opening, competition_density_index_at_opening, same_brand_store_count_at_opening, brand_area_fit_score_at_opening, target_window, target_available_as_of, future_12m_sales_month_count, future_12m_sales_complete, y_first_12m_sales_won, y_first_12m_average_monthly_sales_won, model_eligible`

## 2. 특성 계약 파일
- 행 수: 7
- 열: `field_name, availability, model_use, reason`

## 3. MODEL-03 시나리오
- 행 수: 27
- 열 수: 17
- 열: `scenario_id, brand_id, scenario_profile, size_scenario, store_area_m2, monthly_rent_won, initial_investment_won, predicted_first_12m_sales_won, interval_80_lower_won, interval_80_upper_won, interval_90_lower_won, interval_90_upper_won, sales_investment_efficiency, brand_scenario_rank_by_predicted_sales, brand_scenario_rank_by_efficiency, synthetic_only_notice, interpretation_limit`

## 4. 학습표본과 시나리오에 공통으로 있는 열
- 공통 열 수: 4
- 공통 열: `brand_id, initial_investment_won, monthly_rent_won, store_area_m2`

## 5. 타깃 후보 — XAI 입력에서 제외
- `competition_density_index_at_opening, future_12m_sales_complete, future_12m_sales_month_count, monthly_rent_won, target_available_as_of, target_window, y_first_12m_average_monthly_sales_won, y_first_12m_sales_won`

## 6. 식별자·기간 후보 — XAI 입력 여부를 별도 판단
- `area_demand_index_at_opening, area_id, area_name, brand_area_fit_score_at_opening, brand_id, opening_date, same_brand_store_count_at_opening, store_area_m2, store_id`

## 7. 학습표본에만 있는 열
- `area_demand_index_at_opening, area_id, area_name, brand_area_fit_score_at_opening, competition_density_index_at_opening, data_origin, foot_traffic_index_at_opening, future_12m_sales_complete, future_12m_sales_month_count, latitude, longitude, model_eligible, opening_date, opening_month, same_brand_store_count_at_opening, store_id, target_available_as_of, target_window, y_first_12m_average_monthly_sales_won, y_first_12m_sales_won`

## 8. 시나리오에만 있는 열
- `brand_scenario_rank_by_efficiency, brand_scenario_rank_by_predicted_sales, interpretation_limit, interval_80_lower_won, interval_80_upper_won, interval_90_lower_won, interval_90_upper_won, predicted_first_12m_sales_won, sales_investment_efficiency, scenario_id, scenario_profile, size_scenario, synthetic_only_notice`