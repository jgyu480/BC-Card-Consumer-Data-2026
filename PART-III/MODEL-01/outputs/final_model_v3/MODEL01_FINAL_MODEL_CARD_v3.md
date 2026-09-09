# MODEL-01 Final v3: Contrastive Area DNA

## 점수 정의

이 모델은 예상 매출, 생존 확률, 출점 인과효과를 예측하지 않는다.
점수는 다음 네 요소를 투명하게 결합한 의사결정용 적합도다.

1. 상권 단위 절대 환경 적합도
2. 동일 상권에서 다른 베이커리 브랜드 대비 상대적 환경 우위
3. 관측된 제과점 시장 기회
4. 브랜드 제외 경쟁 위험과 동일 브랜드 근접 제약

## 기본 시나리오

- high_profile_stability: balanced_default
- moderate_profile_stability: conservative_fit
- 동일 브랜드 750m 미만, 경쟁위험 0.80 이상 후보는 기본 추천에서 제외

## 외부 브랜드 문맥

DATA-04 메뉴·텍스트 정보는 브랜드 설명 보조용이다.
가격 관측이 불충분하므로 저가·고가·매장 규모 점수에는 사용하지 않는다.

## 규모 추천

점포 면적, 좌석 수, 임대료, 점포별 매출·생존 결과가 없으므로
f(brand, area, store_size) 및 argmax store_size는 이번 버전에서 제공하지 않는다.
