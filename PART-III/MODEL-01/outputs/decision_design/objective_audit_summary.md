# MODEL-01 의사결정 축 점검

## 데이터 역할
model_role
hold_for_ablation         61
A_customer_context        52
C_recompute_before_use    11
C_safe_competition         6
C_dynamics_diagnostic      4
D_market_core              2
D_market_support           1

## 시장 기회 D
- 핵심: bakery_thsmon_selng_amt, bakery_thsmon_selng_co
- 보조: bakery_avg_ticket

## 브랜드 환경 적합성 A
- 고객의 성별·연령·요일·시간대 소비 구성
- 이후 presence-only 공간선택모형의 입력으로 사용

## 위험·제약 C
- `C_safe_competition`: 커피 등 다른 업종 경쟁
- `C_recompute_before_use`: 해당 브랜드 점포를 제외하고 다시 계산한 뒤에만 사용
- `C_dynamics_diagnostic`: 방향을 단정할 수 없어 우선 진단용으로 보관

## 미래 성과 라벨 후보
- brand_store_master의 날짜 관련 열: ['source_date']
- 날짜 열이 없으면 원천 행안부 데이터에서 개업·폐업일을 별도 추출해야 함

## BC카드 결합 상태
- BC 제과 시군구 수치 열: 31개
- 상권 → BC 시군구 연결률: 100.00%
