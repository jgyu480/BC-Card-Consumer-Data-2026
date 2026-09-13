# MODEL-03 XAI 재현 결과

- 충실도 상태: `TRANSPARENT_XAI_REPLICA_ONLY`
- 기존 예측 대비 중앙 절대백분율오차: `18.91%`
- 기존 예측과의 상관계수: `0.8375`
- 선택된 Ridge alpha: `0.07498942093324558`

## 전역 중요도
```text
                             feature feature_korean  mean_absolute_log_contribution  mean_multiplicative_effect_pct
                            brand_id      브랜드 기본 수준                        0.230359                       -0.994997
        area_demand_index_at_opening          상권 수요                        0.164323                      -12.108256
   same_brand_store_count_at_opening   동일 브랜드 기존점 수                        0.146126                       15.734230
competition_density_index_at_opening          경쟁 밀도                        0.025800                       -0.068537
                       store_area_m2          점포 면적                        0.010684                        0.579657
                    monthly_rent_won          월 임대료                        0.007134                       -0.209407
              initial_investment_won         초기 투자비                        0.002003                        0.092863
       foot_traffic_index_at_opening           유동인구                        0.000061                        0.003928
```

## 시나리오별 상위 5개 기여 요인 예시
```text
       scenario_id                              feature feature_korean direction  log_sales_contribution  multiplicative_effect_pct
BRAND_ALPHA_HIGH_L                             brand_id      브랜드 기본 수준     상승 요인                0.385777                  44.064527
BRAND_ALPHA_HIGH_L    same_brand_store_count_at_opening   동일 브랜드 기존점 수     상승 요인                0.146126                  15.734230
BRAND_ALPHA_HIGH_L competition_density_index_at_opening          경쟁 밀도     하락 요인               -0.040302                  -3.950023
BRAND_ALPHA_HIGH_L         area_demand_index_at_opening          상권 수요     상승 요인                0.039379                   4.016479
BRAND_ALPHA_HIGH_L                     monthly_rent_won          월 임대료     하락 요인               -0.019752                  -1.955804
BRAND_ALPHA_HIGH_M                             brand_id      브랜드 기본 수준     상승 요인                0.385777                  44.064527
BRAND_ALPHA_HIGH_M    same_brand_store_count_at_opening   동일 브랜드 기존점 수     상승 요인                0.146126                  15.734230
BRAND_ALPHA_HIGH_M competition_density_index_at_opening          경쟁 밀도     하락 요인               -0.040302                  -3.950023
BRAND_ALPHA_HIGH_M         area_demand_index_at_opening          상권 수요     상승 요인                0.039379                   4.016479
BRAND_ALPHA_HIGH_M                     monthly_rent_won          월 임대료     하락 요인               -0.008922                  -0.888233
BRAND_ALPHA_HIGH_S                             brand_id      브랜드 기본 수준     상승 요인                0.385777                  44.064527
BRAND_ALPHA_HIGH_S    same_brand_store_count_at_opening   동일 브랜드 기존점 수     상승 요인                0.146126                  15.734230
BRAND_ALPHA_HIGH_S competition_density_index_at_opening          경쟁 밀도     하락 요인               -0.040302                  -3.950023
BRAND_ALPHA_HIGH_S         area_demand_index_at_opening          상권 수요     상승 요인                0.039379                   4.016479
BRAND_ALPHA_HIGH_S                        store_area_m2          점포 면적     하락 요인               -0.012795                  -1.271311
```