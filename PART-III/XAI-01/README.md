# XAI-01 · MODEL-03 매출 시나리오 설명 가능성 검토

## 목적

MODEL-03의 브랜드×입지환경×규모별 첫 12개월 매출 시나리오가 어떤 입력 요인에 의해 달라지는지 설명하기 위한 XAI 분석이다.

## 분석 결과

원래 27개 시나리오를 생성한 코드와 프로필별 수치 입력값은 저장소에 보존되어 있지 않았다. 따라서 원천 합성 상권 환경 데이터와 학습 데이터를 사용해, 재현 가능한 Ridge 기반 XAI 보조모델을 구성하였다.

기존 시나리오 예측값과 보조모델 예측값의 비교 결과는 다음과 같다.

- 중앙 절대백분율오차: 18.91%
- 예측값 상관계수: 0.8375
- 판정: `TRANSPARENT_XAI_REPLICA_ONLY`

따라서 이 결과는 기존 27개 예측값의 정확한 사후 설명이 아니라, MODEL-03이 사용한 입력 구조를 재현해 해석한 보조 분석이다.

## 해석

재현모델에서는 브랜드 기본 수준과 상권 수요가 가장 큰 매출 기여 요인으로 나타났다. 동일 브랜드 기존점 수가 상승 요인으로 나타난 결과는 합성 데이터 내부의 상관 구조를 반영한 것으로, 실제 사업에서 기존점이 많을수록 신규 출점 성과가 높다는 인과적 결론으로 해석하지 않는다.

모든 결과는 합성 데이터 기반이며 실제 파트너 점포 데이터의 시간차단 검증을 통과하기 전에는 출점 추천·실제 매출예측·투자수익률 판단에 사용할 수 없다.

## 산출물

- `outputs/xai_scope_manifest_v1.md`: XAI 범위와 해석 제한
- `outputs/xai_feature_join_audit_v1.md`: 학습 특성과 시나리오 특성 연결 감사
- `outputs/xai_scenario_profile_traceability_v1.md`: 시나리오 프로필 입력 추적성 감사
- `outputs/xai_raw_context_recovery_audit_v1.md`: 원천 상권 환경 복원 감사
- `outputs/xai_replica_scenario_inputs_v1.csv`: 재현모델 시나리오 입력값
- `outputs/xai_global_feature_importance_v1.csv`: 전역 중요도
- `outputs/xai_top5_local_contributions_v1.csv`: 시나리오별 상위 기여 요인
- `outputs/xai_replica_prediction_comparison_v1.csv`: 기존 예측과 재현모델 예측 비교
- `outputs/xai_report_v1.md`: XAI 결과 요약
