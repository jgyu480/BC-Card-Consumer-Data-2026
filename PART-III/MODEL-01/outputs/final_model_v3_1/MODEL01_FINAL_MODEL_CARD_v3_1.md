# MODEL-01 Final v3.1 — App/LLM 전달 기준

## 반드시 사용할 파일

- `model01_final_recommendations_v3_1.parquet`
- `model01_brand_availability_v3_1.csv`

기존 v3의 `structured_evidence`는 앱과 LLM에 사용하지 않는다.

## 설명 생성 규칙

LLM은 `llm_allowed_facts`, `positive_drivers`, `caution_flags`에 있는 사실만
문장으로 바꿀 수 있다. 예상 매출, 생존 확률, 인과효과, 권장 매장 규모를
새롭게 생성해서는 안 된다.

## 후보 수 규칙

`available_recommendation_count`보다 많은 후보를 화면에 표시하지 않는다.
후보가 20개 미만인 브랜드는 위험·근접 제약을 완화해 채우지 않는다.

## 모델 범위

이 결과는 브랜드의 기존 운영환경과 상권 소비·경쟁 환경에 기반한
의사결정용 적합도다. 예상 매출이나 출점 성공 확률이 아니다.
