# XAI 입력 감사

- 실행 위치: `/Users/jgyu480/3_personal/26-2/BC공모전/BC-Card-Consumer-Data-2026`
- 탐색 파일 수: 129

## 모델·예측 관련 파일

### `PART-III/MODEL-02/intermediate/bakery_area_quarter_panel_2021q1_2026q2.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 25,964 | 열 수: 64
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, SIMILR_INDUTY_STOR_CO, STOR_CO, FRC_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO, sales_observed, model_eligible_t0`

### `PART-III/MODEL-02/intermediate/bakery_area_quarter_panel_coverage.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 4
- 열: `period_q, rows, sales_observed_rows, model_eligible_t0_rows`

### `PART-III/MODEL-02/intermediate/baseline_metrics_by_origin.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 7
- 열: `prediction, n, wape_pct, mae_won, spearman, top10_lift, origin_period_q`

### `PART-III/MODEL-02/intermediate/baseline_metrics_by_origin_v2.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 8
- 열: `prediction, n, wape_pct, mae_won, spearman, top10_vs_median_lift, top10_vs_mean_lift, origin_period_q`

### `PART-III/MODEL-02/intermediate/baseline_metrics_common_support.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 7
- 열: `prediction, n, wape_pct, mae_won, spearman, top10_vs_median_lift, top10_vs_mean_lift`

### `PART-III/MODEL-02/intermediate/baseline_metrics_overall.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 7
- 열: `prediction, n, wape_pct, mae_won, spearman, top10_lift, relative_mae_vs_trailing_12m`

### `PART-III/MODEL-02/intermediate/baseline_metrics_overall_v2.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 7
- 열: `prediction, n, wape_pct, mae_won, spearman, top10_vs_median_lift, top10_vs_mean_lift`

### `PART-III/MODEL-02/intermediate/baseline_wins_by_origin.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 4
- 열: `origin_period_q, best_wape_baseline, best_wape_pct, common_n`

### `PART-III/MODEL-02/intermediate/evaluation_dataset_v1.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 7,116 | 열 수: 62
- 열: `TRDAR_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD_NM, SVC_INDUTY_CD, origin_period_q, target_start_period_q, target_end_period_q, t0_sales_amt, t0_sales_count, t0_store_count, y_12m_sales_potential_per_store, road_tot_flpop_co, road_ml_flpop_co, road_fml_flpop_co, road_agrde_10_flpop_co, road_agrde_20_flpop_co, road_agrde_30_flpop_co, road_agrde_40_flpop_co, road_agrde_50_flpop_co, road_agrde_60_above_flpop_co, road_tmzon_00_06_flpop_co, road_tmzon_06_11_flpop_co, road_tmzon_11_14_flpop_co, road_tmzon_14_17_flpop_co, road_tmzon_17_21_flpop_co, road_tmzon_21_24_flpop_co, road_mon_flpop_co, road_tues_flpop_co, road_wed_flpop_co, road_thur_flpop_co, road_fri_flpop_co, road_sat_flpop_co, road_sun_flpop_co, road_observed, facility_viatr_fclty_co, facility_pblofc_co, facility_bank_co, facility_gehspt_co, facility_gnrl_hsptl_co, facility_parmacy_co, facility_kndrgr_co, facility_elesch_co, facility_mskul_co, facility_hgschl_co, facility_univ_co, facility_drts_co, facility_supmk_co, facility_theat_co, facility_stayng_fclty_co, facility_arprt_co, facility_rlroad_statn_co, facility_bus_trminl_co, facility_subway_statn_co, facility_bus_sttn_co, facility_observed, baseline_current_q_annualized, baseline_trailing_12m_per_store, XCNTS_VALUE, YDNTS_VALUE, SIGNGU_CD, ADSTRD_CD`

### `PART-III/MODEL-02/intermediate/evaluation_dataset_v2.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 7,116 | 열 수: 63
- 열: `TRDAR_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD_NM, SVC_INDUTY_CD, origin_period_q, target_start_period_q, target_end_period_q, t0_sales_amt, t0_sales_count, t0_store_count, y_12m_sales_potential_per_store, road_tot_flpop_co, road_ml_flpop_co, road_fml_flpop_co, road_agrde_10_flpop_co, road_agrde_20_flpop_co, road_agrde_30_flpop_co, road_agrde_40_flpop_co, road_agrde_50_flpop_co, road_agrde_60_above_flpop_co, road_tmzon_00_06_flpop_co, road_tmzon_06_11_flpop_co, road_tmzon_11_14_flpop_co, road_tmzon_14_17_flpop_co, road_tmzon_17_21_flpop_co, road_tmzon_21_24_flpop_co, road_mon_flpop_co, road_tues_flpop_co, road_wed_flpop_co, road_thur_flpop_co, road_fri_flpop_co, road_sat_flpop_co, road_sun_flpop_co, road_observed, facility_viatr_fclty_co, facility_pblofc_co, facility_bank_co, facility_gehspt_co, facility_gnrl_hsptl_co, facility_parmacy_co, facility_kndrgr_co, facility_elesch_co, facility_mskul_co, facility_hgschl_co, facility_univ_co, facility_drts_co, facility_supmk_co, facility_theat_co, facility_stayng_fclty_co, facility_arprt_co, facility_rlroad_statn_co, facility_bus_trminl_co, facility_subway_statn_co, facility_bus_sttn_co, facility_observed, baseline_current_q_annualized, baseline_trailing_12m_per_store, XCNTS_VALUE, YDNTS_VALUE, SIGNGU_CD, ADSTRD_CD, baseline_same_quarter_last_year_annualized`

### `PART-III/MODEL-02/intermediate/future_12m_label_coverage.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 5
- 열: `origin_period_q, target_window, t0_eligible_rows, future_4q_complete_rows, future_4q_complete_coverage_pct`

### `PART-III/MODEL-02/intermediate/future_12m_sales_potential_labels.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 7,813 | 열 수: 80
- 열: `TRDAR_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD_NM, SVC_INDUTY_CD, t0_sales_amt, t0_sales_count, t0_store_count, sales_amt_20212, store_count_20212, sales_observed_20212, sales_amt_20213, store_count_20213, sales_observed_20213, sales_amt_20214, store_count_20214, sales_observed_20214, sales_amt_20221, store_count_20221, sales_observed_20221, origin_period_q, target_start_period_q, target_end_period_q, future_4q_sales_observed_all, future_4q_store_positive_all, future_4q_sales_sum, future_4q_avg_store_count, target_eligible, y_12m_sales_potential_per_store, sales_amt_20222, store_count_20222, sales_observed_20222, sales_amt_20223, store_count_20223, sales_observed_20223, sales_amt_20224, store_count_20224, sales_observed_20224, sales_amt_20231, store_count_20231, sales_observed_20231, sales_amt_20232, store_count_20232, sales_observed_20232, sales_amt_20233, store_count_20233, sales_observed_20233, sales_amt_20234, store_count_20234, sales_observed_20234, sales_amt_20241, store_count_20241, sales_observed_20241, sales_amt_20242, store_count_20242, sales_observed_20242, sales_amt_20243, store_count_20243, sales_observed_20243, sales_amt_20244, store_count_20244, sales_observed_20244, sales_amt_20251, store_count_20251, sales_observed_20251, sales_amt_20252, store_count_20252, sales_observed_20252, sales_amt_20253, store_count_20253, sales_observed_20253, sales_amt_20254, store_count_20254, sales_observed_20254, sales_amt_20261, store_count_20261, sales_observed_20261, sales_amt_20262, store_count_20262, sales_observed_20262`

### `PART-III/MODEL-02/intermediate/model_candidate_bootstrap_qualification_v1.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 8
- 열: `prediction, overall_wape_pct, wape_difference_vs_baseline_pct_point, bootstrap_diff_95pct_lower, bootstrap_diff_95pct_upper, bootstrap_probability_beats_baseline_pct, winning_folds_out_of_10, qualified_as_sales_potential_model`

### `PART-III/MODEL-02/intermediate/model_candidate_common_outer_predictions_v1.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 3,863 | 열 수: 10
- 열: `TRDAR_CD, origin_period_q, y_12m_sales_potential_per_store, baseline_current_q_annualized, ridge_log_v1, elasticnet_log_v1, ridge_baseline_corrected_v1, elasticnet_baseline_corrected_v1, hist_gradient_boosting_corrected_v1, random_forest_corrected_v1`

### `PART-III/MODEL-02/intermediate/model_candidate_qualification_decision_v1.json`
- 형식: JSON | 이름 관련성: 높음

### `PART-III/MODEL-02/intermediate/modeling_dataset_v1.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 7,116 | 열 수: 56
- 열: `TRDAR_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD_NM, SVC_INDUTY_CD, origin_period_q, target_start_period_q, target_end_period_q, t0_sales_amt, t0_sales_count, t0_store_count, y_12m_sales_potential_per_store, road_tot_flpop_co, road_ml_flpop_co, road_fml_flpop_co, road_agrde_10_flpop_co, road_agrde_20_flpop_co, road_agrde_30_flpop_co, road_agrde_40_flpop_co, road_agrde_50_flpop_co, road_agrde_60_above_flpop_co, road_tmzon_00_06_flpop_co, road_tmzon_06_11_flpop_co, road_tmzon_11_14_flpop_co, road_tmzon_14_17_flpop_co, road_tmzon_17_21_flpop_co, road_tmzon_21_24_flpop_co, road_mon_flpop_co, road_tues_flpop_co, road_wed_flpop_co, road_thur_flpop_co, road_fri_flpop_co, road_sat_flpop_co, road_sun_flpop_co, road_observed, facility_viatr_fclty_co, facility_pblofc_co, facility_bank_co, facility_gehspt_co, facility_gnrl_hsptl_co, facility_parmacy_co, facility_kndrgr_co, facility_elesch_co, facility_mskul_co, facility_hgschl_co, facility_univ_co, facility_drts_co, facility_supmk_co, facility_theat_co, facility_stayng_fclty_co, facility_arprt_co, facility_rlroad_statn_co, facility_bus_trminl_co, facility_subway_statn_co, facility_bus_sttn_co, facility_observed`

### `PART-III/MODEL-02/intermediate/modeling_dataset_v1_feature_coverage.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 5
- 열: `origin_period_q, total_rows, observed_rows, dataset, coverage_pct`

### `PART-III/MODEL-02/intermediate/nonlinear_baseline_corrected_metrics_by_fold_v1.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 10
- 열: `prediction, n, wape_pct, mae_won, spearman, top10_vs_mean_lift, fold_no, test_origin_period_q, train_origin_end, relative_mae_vs_primary_baseline`

### `PART-III/MODEL-02/intermediate/nonlinear_baseline_corrected_metrics_overall_v1.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 7
- 열: `prediction, n, wape_pct, mae_won, spearman, top10_vs_mean_lift, relative_mae_vs_primary_baseline`

### `PART-III/MODEL-02/intermediate/nonlinear_baseline_corrected_predictions_v1.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 3,863 | 열 수: 6
- 열: `TRDAR_CD, origin_period_q, y_12m_sales_potential_per_store, baseline_current_q_annualized, hist_gradient_boosting_corrected_v1, random_forest_corrected_v1`

### `PART-III/MODEL-02/intermediate/nonlinear_baseline_corrected_win_summary_v1.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 4
- 열: `prediction, winning_folds, total_folds, winning_fold_pct`

### `PART-III/MODEL-02/intermediate/ridge_elasticnet_baseline_corrected_metrics_by_fold_v1.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 10
- 열: `prediction, n, wape_pct, mae_won, spearman, top10_vs_mean_lift, fold_no, test_origin_period_q, train_origin_end, relative_mae_vs_primary_baseline`

### `PART-III/MODEL-02/intermediate/ridge_elasticnet_baseline_corrected_metrics_overall_v1.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 7
- 열: `prediction, n, wape_pct, mae_won, spearman, top10_vs_mean_lift, relative_mae_vs_primary_baseline`

### `PART-III/MODEL-02/intermediate/ridge_elasticnet_baseline_corrected_predictions_v1.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 3,863 | 열 수: 6
- 열: `TRDAR_CD, origin_period_q, y_12m_sales_potential_per_store, baseline_current_q_annualized, ridge_baseline_corrected_v1, elasticnet_baseline_corrected_v1`

### `PART-III/MODEL-02/intermediate/ridge_elasticnet_baseline_corrected_win_summary_v1.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 4
- 열: `prediction, winning_folds, total_folds, winning_fold_pct`

### `PART-III/MODEL-02/intermediate/ridge_elasticnet_feature_contract_v1.json`
- 형식: JSON | 이름 관련성: 높음

### `PART-III/MODEL-02/intermediate/ridge_elasticnet_outer_metrics_by_fold_v1.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 10
- 열: `prediction, n, wape_pct, mae_won, spearman, top10_vs_mean_lift, fold_no, test_origin_period_q, train_origin_end, relative_mae_vs_primary_baseline`

### `PART-III/MODEL-02/intermediate/ridge_elasticnet_outer_metrics_overall_v1.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 7
- 열: `prediction, n, wape_pct, mae_won, spearman, top10_vs_mean_lift, relative_mae_vs_primary_baseline`

### `PART-III/MODEL-02/intermediate/ridge_elasticnet_outer_predictions_v1.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 3,863 | 열 수: 6
- 열: `TRDAR_CD, origin_period_q, y_12m_sales_potential_per_store, baseline_current_q_annualized, ridge_log_v1, elasticnet_log_v1`

### `PART-III/MODEL-02/intermediate/temporal_embargo_folds_v1.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 9
- 열: `fold_no, test_origin_period_q, train_origin_start, train_origin_end, train_origin_count, train_rows, test_rows, test_rows_with_primary_baseline, outcome_embargo_quarters`

### `PART-III/MODEL-02/outputs/latest_observed_4q_bakery_sales_environment_2026q2.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 29
- 열: `TRDAR_CD, TRDAR_CD_NM, TRDAR_SE_CD, TRDAR_SE_CD_NM, recent_4q_period_rows, recent_4q_sales_observed_q, recent_4q_positive_store_q, recent_4q_total_sales_won, recent_4q_total_transactions, recent_4q_avg_store_count, recent_4q_complete_observation, recent_4q_sales_per_store_won, recent_4q_average_ticket_won, prior_year_4q_period_rows, prior_year_4q_sales_observed_q, prior_year_4q_positive_store_q, prior_year_4q_total_sales_won, prior_year_4q_total_transactions, prior_year_4q_avg_store_count, prior_year_4q_complete_observation, prior_year_4q_sales_per_store_won, prior_year_4q_average_ticket_won, recent_4q_vs_prior_year_pct, seoul_observed_percentile, top_10pct_by_recent_actual, display_metric_name, display_period, forecast_available, forecast_status`

### `PART-III/MODEL-02/outputs/latest_observed_4q_bakery_sales_environment_2026q2.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 1,186 | 열 수: 29
- 열: `TRDAR_CD, TRDAR_CD_NM, TRDAR_SE_CD, TRDAR_SE_CD_NM, recent_4q_period_rows, recent_4q_sales_observed_q, recent_4q_positive_store_q, recent_4q_total_sales_won, recent_4q_total_transactions, recent_4q_avg_store_count, recent_4q_complete_observation, recent_4q_sales_per_store_won, recent_4q_average_ticket_won, prior_year_4q_period_rows, prior_year_4q_sales_observed_q, prior_year_4q_positive_store_q, prior_year_4q_total_sales_won, prior_year_4q_total_transactions, prior_year_4q_avg_store_count, prior_year_4q_complete_observation, prior_year_4q_sales_per_store_won, prior_year_4q_average_ticket_won, recent_4q_vs_prior_year_pct, seoul_observed_percentile, top_10pct_by_recent_actual, display_metric_name, display_period, forecast_available, forecast_status`

### `PART-III/MODEL-02/outputs/latest_observed_4q_bakery_sales_environment_top20_2026q2.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 29
- 열: `TRDAR_CD, TRDAR_CD_NM, TRDAR_SE_CD, TRDAR_SE_CD_NM, recent_4q_period_rows, recent_4q_sales_observed_q, recent_4q_positive_store_q, recent_4q_total_sales_won, recent_4q_total_transactions, recent_4q_avg_store_count, recent_4q_complete_observation, recent_4q_sales_per_store_won, recent_4q_average_ticket_won, prior_year_4q_period_rows, prior_year_4q_sales_observed_q, prior_year_4q_positive_store_q, prior_year_4q_total_sales_won, prior_year_4q_total_transactions, prior_year_4q_avg_store_count, prior_year_4q_complete_observation, prior_year_4q_sales_per_store_won, prior_year_4q_average_ticket_won, recent_4q_vs_prior_year_pct, seoul_observed_percentile, top_10pct_by_recent_actual, display_metric_name, display_period, forecast_available, forecast_status`

### `PART-III/MODEL-02/outputs/model02_allowed_and_prohibited_outputs.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 3
- 열: `output, status, reason`

### `PART-III/MODEL-02/outputs/model02_data_limit_facts_2026q2.json`
- 형식: JSON | 이름 관련성: 높음

### `PART-III/MODEL-02/outputs/model02_executive_observed_market_screen_2026q2.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 18
- 열: `TRDAR_CD, TRDAR_CD_NM, TRDAR_SE_CD_NM, display_as_of, display_window, recent_4q_sales_per_store_won, seoul_observed_percentile, actual_market_level, recent_4q_vs_prior_year_pct, year_over_year_trend, recent_4q_avg_store_count, recent_4q_quarterly_variation_pct, quarterly_variation_flag, observation_scope, metric_interpretation, permitted_decision_use, prohibited_interpretation, forecast_status`

### `PART-III/MODEL-02/outputs/model02_executive_observed_market_screen_dictionary.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 3
- 열: `column, meaning, interpretation`

### `PART-III/MODEL-02/outputs/model02_executive_observed_market_screen_final_2026q2.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 24
- 열: `TRDAR_CD, TRDAR_CD_NM, TRDAR_SE_CD_NM, display_as_of, display_window, recent_4q_sales_per_store_won, seoul_observed_percentile, actual_market_level, recent_4q_vs_prior_year_pct, year_over_year_trend, recent_4q_avg_store_count, recent_4q_quarterly_variation_pct, quarterly_variation_flag, observation_scope, metric_interpretation, permitted_decision_use, prohibited_interpretation, forecast_status, recent_4q_total_sales_won, recent_4q_total_sales_percentile, store_count_interpretation, field_check_risks, field_check_priority, priority_interpretation`

### `PART-III/MODEL-02/outputs/model02_executive_observed_market_screen_top20_2026q2.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 18
- 열: `TRDAR_CD, TRDAR_CD_NM, TRDAR_SE_CD_NM, display_as_of, display_window, recent_4q_sales_per_store_won, seoul_observed_percentile, actual_market_level, recent_4q_vs_prior_year_pct, year_over_year_trend, recent_4q_avg_store_count, recent_4q_quarterly_variation_pct, quarterly_variation_flag, observation_scope, metric_interpretation, permitted_decision_use, prohibited_interpretation, forecast_status`

### `PART-III/MODEL-02/outputs/model02_failure_protocol_summary.json`
- 형식: JSON | 이름 관련성: 높음

### `PART-III/MODEL-02/outputs/model02_field_check_priority_2026q2.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 24
- 열: `TRDAR_CD, TRDAR_CD_NM, TRDAR_SE_CD_NM, display_as_of, display_window, recent_4q_sales_per_store_won, seoul_observed_percentile, actual_market_level, recent_4q_vs_prior_year_pct, year_over_year_trend, recent_4q_avg_store_count, recent_4q_quarterly_variation_pct, quarterly_variation_flag, observation_scope, metric_interpretation, permitted_decision_use, prohibited_interpretation, forecast_status, recent_4q_total_sales_won, recent_4q_total_sales_percentile, store_count_interpretation, field_check_risks, field_check_priority, priority_interpretation`

### `PART-III/MODEL-02/outputs/model02_final_qa_checks_2026q2.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 3
- 열: `check, passed, detail`

### `PART-III/MODEL-02/outputs/model02_final_release_decision_2026q2.json`
- 형식: JSON | 이름 관련성: 높음

### `PART-III/MODEL-02/outputs/model02_observed_market_screen_qa_2026q2.json`
- 형식: JSON | 이름 관련성: 높음

### `PART-III/MODEL-02/outputs/model02_retraining_data_requirements.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 8
- 열: `priority, data_needed, minimum_granularity, why_needed, what_it_enables, availability_status, can_restart_future_forecast, can_claim_without_it`

### `PART-III/MODEL-02/outputs/panel_coverage_audit.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 12
- 열: `period_q, sales_rows, store_rows, sales_area_count, store_area_count, matched_sales_store_rows, sales_observed_rows, future_sales_label_eligible_rows, store_rows_without_sales_observation, sales_observation_coverage_pct, nonpositive_sales_rows, nonpositive_store_rows`

### `PART-III/MODEL-02/raw/api_probes/model02_service_availability_probe.json`
- 형식: JSON | 이름 관련성: 높음

### `PART-III/MODEL-02/raw/api_probes/sales_by_area_api_probe.json`
- 형식: JSON | 이름 관련성: 높음

### `PART-III/MODEL-02/raw/api_probes/store_by_area_api_probe.json`
- 형식: JSON | 이름 관련성: 일반

### `PART-III/MODEL-02/raw/archive_metadata/historical_archive_availability_probe.json`
- 형식: JSON | 이름 관련성: 일반

### `PART-III/MODEL-02/raw/archive_metadata/official_download_sequence_context.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 5
- 열: `dataset, download_seq, years_found_near_call, korean_year_labels_near_call, context_preview`

### `PART-III/MODEL-02/raw/archive_metadata/official_download_sequence_context.json`
- 형식: JSON | 이름 관련성: 일반

### `PART-III/MODEL-02/raw/area_reference/seoul_area_reference.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,650 | 열 수: 11
- 열: `TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, XCNTS_VALUE, YDNTS_VALUE, SIGNGU_CD, SIGNGU_CD_NM, ADSTRD_CD, ADSTRD_CD_NM, RELM_AR`

### `PART-III/MODEL-02/raw/historical_bakery_panel/collection_manifest.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 6
- 열: `period, dataset, status, api_total_rows, bakery_rows, path`

### `PART-III/MODEL-02/raw/historical_bakery_panel/collection_manifest_2021_2022.json`
- 형식: JSON | 이름 관련성: 일반

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20211.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 438 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20212.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 445 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20213.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 452 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20214.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 453 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20221.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 452 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20222.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 455 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20223.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 448 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20224.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 447 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20231.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 445 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20232.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 441 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20233.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 442 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20234.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 436 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20241.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 434 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20242.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 431 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20243.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 430 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20244.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 424 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20251.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 419 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20252.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 418 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20253.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 423 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20254.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 430 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20261.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 430 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_sales_20262.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 433 | 열 수: 55
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, THSMON_SELNG_AMT, THSMON_SELNG_CO, MDWK_SELNG_AMT, WKEND_SELNG_AMT, MON_SELNG_AMT, TUES_SELNG_AMT, WED_SELNG_AMT, THUR_SELNG_AMT, FRI_SELNG_AMT, SAT_SELNG_AMT, SUN_SELNG_AMT, TMZON_00_06_SELNG_AMT, TMZON_06_11_SELNG_AMT, TMZON_11_14_SELNG_AMT, TMZON_14_17_SELNG_AMT, TMZON_17_21_SELNG_AMT, TMZON_21_24_SELNG_AMT, ML_SELNG_AMT, FML_SELNG_AMT, AGRDE_10_SELNG_AMT, AGRDE_20_SELNG_AMT, AGRDE_30_SELNG_AMT, AGRDE_40_SELNG_AMT, AGRDE_50_SELNG_AMT, AGRDE_60_ABOVE_SELNG_AMT, MDWK_SELNG_CO, WKEND_SELNG_CO, MON_SELNG_CO, TUES_SELNG_CO, WED_SELNG_CO, THUR_SELNG_CO, FRI_SELNG_CO, SAT_SELNG_CO, SUN_SELNG_CO, TMZON_00_06_SELNG_CO, TMZON_06_11_SELNG_CO, TMZON_11_14_SELNG_CO, TMZON_14_17_SELNG_CO, TMZON_17_21_SELNG_CO, TMZON_21_24_SELNG_CO, ML_SELNG_CO, FML_SELNG_CO, AGRDE_10_SELNG_CO, AGRDE_20_SELNG_CO, AGRDE_30_SELNG_CO, AGRDE_40_SELNG_CO, AGRDE_50_SELNG_CO, AGRDE_60_ABOVE_SELNG_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20211.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,128 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, STOR_CO, SIMILR_INDUTY_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO, FRC_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20212.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,139 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, STOR_CO, SIMILR_INDUTY_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO, FRC_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20213.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,149 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, STOR_CO, SIMILR_INDUTY_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO, FRC_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20214.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,156 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, STOR_CO, SIMILR_INDUTY_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO, FRC_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20221.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,163 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, STOR_CO, SIMILR_INDUTY_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO, FRC_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20222.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,160 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, STOR_CO, SIMILR_INDUTY_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO, FRC_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20223.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,171 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, STOR_CO, SIMILR_INDUTY_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO, FRC_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20224.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,174 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, STOR_CO, SIMILR_INDUTY_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO, FRC_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20231.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,190 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, SIMILR_INDUTY_STOR_CO, STOR_CO, FRC_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20232.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,196 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, SIMILR_INDUTY_STOR_CO, STOR_CO, FRC_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20233.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,198 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, SIMILR_INDUTY_STOR_CO, STOR_CO, FRC_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20234.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,199 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, SIMILR_INDUTY_STOR_CO, STOR_CO, FRC_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20241.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,200 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, SIMILR_INDUTY_STOR_CO, STOR_CO, FRC_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20242.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,196 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, SIMILR_INDUTY_STOR_CO, STOR_CO, FRC_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20243.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,192 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, SIMILR_INDUTY_STOR_CO, STOR_CO, FRC_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20244.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,191 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, SIMILR_INDUTY_STOR_CO, STOR_CO, FRC_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20251.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,193 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, SIMILR_INDUTY_STOR_CO, STOR_CO, FRC_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20252.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,193 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, SIMILR_INDUTY_STOR_CO, STOR_CO, FRC_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20253.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,202 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, SIMILR_INDUTY_STOR_CO, STOR_CO, FRC_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20254.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,196 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, SIMILR_INDUTY_STOR_CO, STOR_CO, FRC_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20261.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,192 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, SIMILR_INDUTY_STOR_CO, STOR_CO, FRC_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO`

### `PART-III/MODEL-02/raw/historical_bakery_panel/seoul_bakery_store_20262.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 1,186 | 열 수: 14
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, SVC_INDUTY_CD, SVC_INDUTY_CD_NM, SIMILR_INDUTY_STOR_CO, STOR_CO, FRC_STOR_CO, OPBIZ_RT, OPBIZ_STOR_CO, CLSBIZ_RT, CLSBIZ_STOR_CO`

### `PART-III/MODEL-02/raw/supplementary_panels/attracting_facilities_2021q1_2026q2.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 34,716 | 열 수: 25
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, VIATR_FCLTY_CO, PBLOFC_CO, BANK_CO, GEHSPT_CO, GNRL_HSPTL_CO, PARMACY_CO, KNDRGR_CO, ELESCH_CO, MSKUL_CO, HGSCHL_CO, UNIV_CO, DRTS_CO, SUPMK_CO, THEAT_CO, STAYNG_FCLTY_CO, ARPRT_CO, RLROAD_STATN_CO, BUS_TRMINL_CO, SUBWAY_STATN_CO, BUS_STTN_CO`

### `PART-III/MODEL-02/raw/supplementary_panels/road_population_2021q1_2026q2.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 36,281 | 열 수: 27
- 열: `STDR_YYQU_CD, TRDAR_SE_CD, TRDAR_SE_CD_NM, TRDAR_CD, TRDAR_CD_NM, TOT_FLPOP_CO, ML_FLPOP_CO, FML_FLPOP_CO, AGRDE_10_FLPOP_CO, AGRDE_20_FLPOP_CO, AGRDE_30_FLPOP_CO, AGRDE_40_FLPOP_CO, AGRDE_50_FLPOP_CO, AGRDE_60_ABOVE_FLPOP_CO, TMZON_00_06_FLPOP_CO, TMZON_06_11_FLPOP_CO, TMZON_11_14_FLPOP_CO, TMZON_14_17_FLPOP_CO, TMZON_17_21_FLPOP_CO, TMZON_21_24_FLPOP_CO, MON_FLPOP_CO, TUES_FLPOP_CO, WED_FLPOP_CO, THUR_FLPOP_CO, FRI_FLPOP_CO, SAT_FLPOP_CO, SUN_FLPOP_CO`

### `PART-III/MODEL-02/raw/supplementary_panels/supplementary_collection_manifest.json`
- 형식: JSON | 이름 관련성: 일반

### `PART-III/MODEL-03/intermediate/synthetic_baseline_metrics_by_fold_v1.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 8
- 열: `n, wape_pct, mae_won, spearman, top10_vs_mean_lift, fold_no, test_cohort, prediction`

### `PART-III/MODEL-03/intermediate/synthetic_baseline_metrics_overall_v1.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 6
- 열: `n, wape_pct, mae_won, spearman, top10_vs_mean_lift, prediction`

### `PART-III/MODEL-03/intermediate/synthetic_baseline_predictions_v1.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 191 | 열 수: 12
- 열: `brand_id, store_id, opening_month, area_demand_band, y_first_12m_sales_won, baseline_brand_prior_mean, baseline_brand_demand_band_mean, brand_demand_band_train_n, baseline_brand_demand_band_prior_mean, fold_no, test_cohort, train_target_available_before`

### `PART-III/MODEL-03/intermediate/synthetic_brand_aware_model_metrics_by_fold_v1.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 9
- 열: `n, wape_pct, mae_won, spearman, top10_vs_mean_lift, fold_no, test_cohort, prediction, relative_mae_vs_primary_baseline`

### `PART-III/MODEL-03/intermediate/synthetic_brand_aware_model_metrics_overall_v1.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 7
- 열: `n, wape_pct, mae_won, spearman, top10_vs_mean_lift, prediction, relative_mae_vs_primary_baseline`

### `PART-III/MODEL-03/intermediate/synthetic_brand_aware_model_predictions_v1.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 191 | 열 수: 10
- 열: `brand_id, store_id, opening_month, y_first_12m_sales_won, baseline_brand_prior_mean, baseline_brand_demand_band_prior_mean, ridge_brand_aware_v1, hist_gradient_boosting_brand_aware_v1, fold_no, test_cohort`

### `PART-III/MODEL-03/intermediate/synthetic_model_candidate_qualification_v1.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 10
- 열: `prediction, overall_wape_pct, wape_difference_vs_baseline_pct_point, mae_won, spearman, winning_cohorts_out_of_5, bootstrap_diff_95pct_lower, bootstrap_diff_95pct_upper, bootstrap_probability_beats_baseline_pct, qualified_for_partner_model_pipeline`

### `PART-III/MODEL-03/intermediate/synthetic_model_selection_decision_v1.json`
- 형식: JSON | 이름 관련성: 높음

### `PART-III/MODEL-03/intermediate/synthetic_modeling_dataset_v1.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 360 | 열 수: 24
- 열: `data_origin, brand_id, store_id, opening_date, opening_month, area_id, area_name, latitude, longitude, store_area_m2, monthly_rent_won, initial_investment_won, area_demand_index_at_opening, foot_traffic_index_at_opening, competition_density_index_at_opening, same_brand_store_count_at_opening, brand_area_fit_score_at_opening, target_window, target_available_as_of, future_12m_sales_month_count, future_12m_sales_complete, y_first_12m_sales_won, y_first_12m_average_monthly_sales_won, model_eligible`

### `PART-III/MODEL-03/intermediate/synthetic_new_store_12m_labels_v1.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 360 | 열 수: 11
- 열: `data_origin, brand_id, store_id, area_id, opening_month, target_window, target_available_as_of, future_12m_sales_month_count, future_12m_sales_complete, y_first_12m_sales_won, y_first_12m_average_monthly_sales_won`

### `PART-III/MODEL-03/intermediate/synthetic_new_store_label_coverage_v1.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 5
- 열: `brand_id, opening_month, opened_store_count, eligible_store_count, eligible_pct`

### `PART-III/MODEL-03/intermediate/synthetic_new_store_label_manifest_v1.json`
- 형식: JSON | 이름 관련성: 일반

### `PART-III/MODEL-03/intermediate/synthetic_opening_cohort_folds_v1.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 5
- 열: `fold_no, test_cohort, train_store_count, test_store_count, outcome_embargo_months`

### `PART-III/MODEL-03/intermediate/synthetic_ridge_conformal_calibration_v1.json`
- 형식: JSON | 이름 관련성: 높음

### `PART-III/MODEL-03/intermediate/synthetic_ridge_conformal_coverage_by_cohort_v1.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 8
- 열: `fold_no, test_cohort, calibration_residual_count, q80_log_residual, q90_log_residual, test_store_count, interval_80_coverage_pct, interval_90_coverage_pct`

### `PART-III/MODEL-03/intermediate/synthetic_ridge_conformal_intervals_oof_v1.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 191 | 열 수: 17
- 열: `brand_id, store_id, opening_month, y_first_12m_sales_won, baseline_brand_prior_mean, baseline_brand_demand_band_prior_mean, ridge_brand_aware_v1, hist_gradient_boosting_brand_aware_v1, fold_no, test_cohort, log_abs_residual, calibration_residual_count, interval_80_lower_won, interval_80_upper_won, interval_90_lower_won, interval_90_upper_won, interval_available`

### `PART-III/MODEL-03/outputs/model03_feature_availability_contract_v1.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 4
- 열: `field_name, availability, model_use, reason`

### `PART-III/MODEL-03/outputs/synthetic_brand_area_size_revenue_scenarios_v1.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 17
- 열: `scenario_id, brand_id, scenario_profile, size_scenario, store_area_m2, monthly_rent_won, initial_investment_won, predicted_first_12m_sales_won, interval_80_lower_won, interval_80_upper_won, interval_90_lower_won, interval_90_upper_won, sales_investment_efficiency, brand_scenario_rank_by_predicted_sales, brand_scenario_rank_by_efficiency, synthetic_only_notice, interpretation_limit`

### `PART-III/MODEL-03/outputs/synthetic_brand_area_size_scenario_manifest_v1.json`
- 형식: JSON | 이름 관련성: 높음

### `PART-III/MODEL-03/outputs/synthetic_brand_area_size_scenario_summary_v1.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 5
- 열: `brand_id, scenario_count, best_predicted_sales_won, best_sales_investment_efficiency, synthetic_only_notice`

### `PART-III/MODEL-03/outputs/synthetic_partner_input_quality_report_v1.json`
- 형식: JSON | 이름 관련성: 일반

### `PART-III/MODEL-03/outputs/synthetic_partner_store_input_quality_flags_v1.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 8
- 열: `brand_id, store_id, opening_month, expected_sales_month_count, actual_sales_month_count, missing_sales_month_count, extra_sales_month_count, training_input_status`

### `PART-III/MODEL-03/raw/partner_input_template/partner_store_monthly_sales_schema.csv`
- 형식: CSV | 이름 관련성: 높음
- 열 수: 6
- 열: `field_name, required, data_type, description, known_before_opening, example`

### `PART-III/MODEL-03/raw/synthetic/synthetic_area_context_v1.csv`
- 형식: CSV | 이름 관련성: 일반
- 열 수: 7
- 열: `area_id, area_name, area_demand_index, foot_traffic_index, competition_density_index, latitude, longitude`

### `PART-III/MODEL-03/raw/synthetic/synthetic_data_manifest_v1.json`
- 형식: JSON | 이름 관련성: 일반

### `PART-III/MODEL-03/raw/synthetic/synthetic_partner_monthly_sales_v1.parquet`
- 형식: Parquet | 이름 관련성: 높음
- 행 수: 14,255 | 열 수: 10
- 열: `data_origin, brand_id, store_id, sales_month, monthly_sales_won, months_since_opening, store_area_m2, monthly_rent_won, initial_investment_won, area_id`

### `PART-III/MODEL-03/raw/synthetic/synthetic_partner_store_master_v1.parquet`
- 형식: Parquet | 이름 관련성: 일반
- 행 수: 360 | 열 수: 19
- 열: `data_origin, brand_id, store_id, opening_date, opening_month, closing_date, operating_status_as_of_2026q2, area_id, area_name, latitude, longitude, store_area_m2, monthly_rent_won, initial_investment_won, area_demand_index_at_opening, foot_traffic_index_at_opening, competition_density_index_at_opening, same_brand_store_count_at_opening, brand_area_fit_score_at_opening`
