# 데이터 현황

## BC카드 제공 데이터

경로: `Datasets/a. BC Provided Data/ABP_CONTEST_DATA.csv`

- 약 15.66MB
- 242,574행
- 기간: 202601~202606
- 용도: 시군구별 제과 소비금액·건수와 고객 구성
- Git 업로드: 금지

주요 원본 열:

- `STRD_YYMM`
- `SIDO_NM`
- `CCG_NM`
- `GENDER_CD`
- `AGE_CD`
- `TP_BUZ_NO`
- `TP_BUZ_NM`
- `amt`
- `cnt`

## 행정안전부 식품·휴게음식점

경로: `Datasets/b. External Public Data/01_mois_rest_cafes/`

- 서울 주소 기준 105,305행
- 용도: 점포명·주소·영업상태 확인
- 단순 키워드 일치는 브랜드 확정 결과로 사용하지 않음
- Git 업로드: 원본 금지

## 소상공인시장진흥공단 상가정보

경로: `Datasets/b. External Public Data/02_small_business_stores/`

- 2026-06-30 전국 ZIP
- 약 336.36MB
- 용도: 점포명·주소·좌표 및 브랜드 점포 후보
- Git 업로드: 원본 금지

## 공정거래위원회 가맹 브랜드

경로: `Datasets/b. External Public Data/03_ftc_franchise_brands/`

- 2026년 브랜드 7,458행
- 용도: 공식 브랜드명 확인과 표준화
- Git 업로드: 원본 금지

## 서울시 점포-상권

경로: `Datasets/b. External Public Data/04_seoul_store_by_area/`

- `store_by_area_20261.jsonl`
- `store_by_area_20262.jsonl`
- 용도: 점포 수, 프랜차이즈 비중, 개폐업, 경쟁 환경
- Git 업로드: 원본 금지

## 서울시 추정매출-상권

경로: `Datasets/b. External Public Data/05_seoul_sales_by_area/`

- `sales_by_area_20261.jsonl`
- `sales_by_area_20262.jsonl`
- 용도: 추정매출, 거래건수, 시장 규모
- Git 업로드: 원본 금지

## Git에 올리는 항목

- 수집·전처리 코드
- 데이터 사전과 열 규격
- 수집 manifest
- 가짜 앱 데이터
- 공개 가능한 비식별 집계 결과
- 분석 보고서

## Git에 올리지 않는 항목

- BC카드 원본
- 외부 원본 ZIP·JSONL·CSV
- `.env`
- API 키
- 배포에 불필요한 원본 주소·좌표
