# MODEL-01 입력 결합 규격 (DATA-01 x DATA-02)

작성일: 2026-09-07

## 1. 원칙

DATA-01과 DATA-02는 하나의 파일로 미리 합치지 않는다. MODEL-01이 필요한 시점에
`area_id`, `ccg_id`, 점포 좌표를 이용해 결합한다 (DATA-02 README 6절 원칙과 동일).

## 2. 결합 대상 파일

| DATA-01 | DATA-02 | 결합키 | 용도 |
|---|---|---|---|
| `brand_ccg_presence.parquet` | `bc_bakery_ccg_profile_2026h1.parquet` | `ccg_id` | 브랜드 입점 DNA (전국 소비 프로필) |
| `brand_area_presence.parquet` | `area_feature_master.parquet` | `area_id` | 기존 입점 상권 확인/제외 |
| `brand_store_master.parquet`의 `longitude`/`latitude` | `area_feature_master.parquet`의 `centroid_x_epsg5181`/`centroid_y_epsg5181` | 좌표 거리 계산 (조인 아님) | 기존 점포-후보 상권 거리 |

## 3. 결합키 검증 결과 (2026-09-07 기준)

- **`ccg_id`**: DATA-01 253개 중 249개(98.4%) DATA-02와 연결됨. 미연결 4개
  (제물포구/영종구/서해구/검단구, 전체 매장의 1.7%)는 DATA-02 README에 명시된
  인천 행정구역 개편(2026년 7월 신설) 이슈로, 양쪽 모두 알려진 한계로 처리한다.
  이 4개 지역이 걸리는 브랜드-시군구 조합(36건)은 `bc_bakery_ccg_profile` 특성 없이
  점포 존재만 알 수 있는 상태로 남는다.
- **`area_id`**: DATA-01 584개 전량(100%) DATA-02 1,650개 상권 목록과 연결됨. 문제 없음.
- **자료형**: 양쪽 모두 문자열(object), 원본 소진공/서울시 공식 코드를 그대로 사용해
  형 변환이 필요 없음.
- **결합키 중복(fan-out) 여부**: DATA-02 쪽 `ccg_id`, `area_id` 모두 1행당 1개 값으로
  유일하여, 좌측(DATA-01) 기준 left join 시 행 수가 부풀지 않음을 확인함
  (`brand_ccg_presence` 2,019행, `brand_area_presence` 950행 모두 결합 전후 동일).

## 4. 좌표 기반 계산 검증

- `brand_store_master.parquet`의 좌표는 결측 0건, 대한민국 영역(경도 124~132,
  위도 33~43) 이탈 0건으로 전량 유효함.
- 좌표계 변환(WGS84 -> EPSG:5181) 후 상권 중심점과의 거리 계산이 정상 작동함을
  샘플로 확인함 (예: "파리바게뜨평창점" -> 최근접 상권 "평창동서측" 372m).
- 기존 입점 상권 제외 로직도 정상 작동함을 확인함 (예: 특정 브랜드의 서울 기존
  입점 상권 384개를 전체 1,650개에서 제외하면 후보 1,266개가 남음).

## 5. MODEL-01 사용 권장 사항

1. `match_confidence`가 `low` 또는 `medium_short_brand`인 레코드는 검증이 완료되지
   않았으므로, 브랜드 입점 DNA 계산 시 가중치를 낮추거나 제외하는 것을 권장한다.
2. `store_status`가 "미확인"인 레코드는 폐업 여부가 확인되지 않았을 뿐 존재를
   부정하는 것이 아니므로, 그대로 활성 매장으로 취급해도 무방하다.
3. 인천 4개 신설 자치구(1.7%)는 `bc_bakery_ccg_profile` 결합 시 특성값이 없을 수
   있으므로, 결측을 0이 아닌 NULL로 유지하고 모델 학습 시 별도 처리를 권장한다
   (DATA-02 품질 원칙과 동일).
4. 거리 계산은 반드시 EPSG:5181(또는 동일 평면좌표계)로 변환 후 수행해야 하며,
   WGS84(경위도) 상태로 유클리드 거리를 계산하면 오차가 크다.
