# APP-01

브랜드 맞춤형 서울 출점 포트폴리오 대시보드의 화면 골격을 제작한다.

## 서비스 사용자

이 서비스의 직접 사용자는 카드 소비자가 아니라 베이커리 프랜차이즈 본사 사업개발팀이다.

- 서비스 사용자: 본사 사업개발팀
- 분석 대상: BC카드 소비자 집계
- 사용 목적: 이번 분기에 함께 검토할 서울 출점 후보 조합 선정
- 제공하지 않는 것: 예상 매출, 성공 확률, 최종 출점 결정

## 사용 파일

- `result_schema.json`: 모델 결과의 필수 JSON 구조
- `mock_recommendations.json`: APP-01 개발용 가짜 결과

두 파일은 최종 경로에 있으므로 이동하지 않는다.

## 사용자 입력

1. 브랜드
2. 희망 출점 수 1·2·3개

v1에서는 복잡한 가중치 입력을 받지 않는다.

## 권장 화면 순서

1. 브랜드와 희망 출점 수 선택
2. 브랜드 입점 DNA 요약
3. 해당 출점 수의 추천 포트폴리오 Top 3
4. 조합을 구성하는 개별 상권
5. 추천 점수의 구성
6. 긍정 요인과 위험 요인
7. 데이터 신뢰도
8. 실제 출점 전 추가 검토사항

개별 상권 전체 순위보다 추천 포트폴리오를 먼저 보여준다.

## 점수 방향

높을수록 좋은 점수:

- `suitability_score`
- `dna_match_score`
- `market_score`
- `competition_attractiveness_score`
- `portfolio_score`
- `geographic_diversification_score`
- `consumer_diversification_score`
- `coverage_score`

높을수록 위험한 점수:

- `proximity_risk_score`
- `overlap_risk_score`

위험점수는 좋은 점수와 같은 색으로 표시하지 않는다.

## 주요 피처

### 개별 상권

- `rank`: 브랜드 내 추천 순위
- `recommendation_label`: 최우선 검토·우선 검토·비교 후보
- `suitability_score`: 브랜드와 상권의 최종 적합도
- `dna_match_score`: 브랜드 기존 입점환경과의 유사성
- `market_score`: 소비와 시장 규모
- `competition_attractiveness_score`: 경쟁 부담을 고려한 상권 매력도
- `proximity_risk_score`: 기존 점포와 가까울수록 높아지는 위험
- `consumer_profile`: 주요 고객과 소비 상황
- `data_quality`: 데이터 포괄성과 신뢰도
- `next_checks`: 실제 출점 전 추가 확인사항

### 복수 출점 조합

- `portfolio_score`: 조합 전체 점수
- `average_area_score`: 구성 상권의 평균 적합도
- `geographic_diversification_score`: 지역 분산 정도
- `consumer_diversification_score`: 소비 수요 유형 분산 정도
- `overlap_risk_score`: 상권 간 고객시장 중복 위험
- `rationale_facts`: 조합을 추천한 수치 근거
- `risk_factors`: 조합 차원의 위험
- `next_checks`: 임대료·공실·운영인력 등 추가 확인사항

## 필수 동작

- 브랜드 변경 시 DNA·추천 상권·조합이 함께 달라져야 한다.
- 희망 출점 수와 같은 `desired_store_count`만 표시한다.
- 포트폴리오 Top 3를 서로 비교할 수 있어야 한다.
- 지도와 목록에서 같은 상권을 선택할 수 있어야 한다.
- 긍정 요인과 위험 요인을 동시에 표시한다.
- 데이터 신뢰도와 추가 검토사항을 숨기지 않는다.
- 화면 상단에 mock 데이터 안내문을 표시한다.
- 예상 매출 또는 성공 확률처럼 보이는 표현을 사용하지 않는다.

## mock 데이터 주의

현재 수치는 화면 개발을 위한 가짜 값이다.

실제 MODEL-01 결과가 나오면 JSON 구조는 유지하고 값만 교체한다. C는 모델에 없는 수치나 설명을 새로 생성하지 않는다.
