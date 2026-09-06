# 담당자별 인수인계

## B

작업 위치:

- `PART-II/DATA-01`
- `PART-II/DATA-02`

B에게 전달하는 `For_B/Datasets` 내부의 두 폴더를 본인 레포의 기존 `Datasets` 안에 병합한다.

최종 경로:

- `Datasets/a. BC Provided Data/`
- `Datasets/b. External Public Data/`

`Datasets/Datasets/`처럼 중복된 경로가 생기면 안 된다.

B가 Git에서 바로 확인할 파일:

- `PART-II/DATA-01/README.md`
- `PART-II/DATA-01/DATA_SCHEMA.csv`
- `PART-II/DATA-02/README.md`
- `PART-II/DATA-02/DATA_SCHEMA.csv`

## C

작업 위치:

- `PART-II/APP-01`

C는 원본 데이터와 API 키가 필요하지 않다. 저장소를 clone하면 아래 파일이 최종 위치에 이미 존재한다.

- `PART-II/APP-01/README.md`
- `PART-II/APP-01/result_schema.json`
- `PART-II/APP-01/mock_recommendations.json`

파일을 이동하지 않고 해당 위치에서 바로 앱을 개발한다.

## A

B에게 받을 파일:

- `PART-II/DATA-01/brand_store_area_map.parquet`
- `PART-II/DATA-01/data01_quality_report.csv`
- `PART-II/DATA-01/brand_name_mapping.csv`
- `PART-II/DATA-02/area_feature_master.parquet`
- `PART-II/DATA-02/data02_quality_report.csv`
- `PART-II/DATA-02/bc_bakery_industry_mapping.csv`

다음 작업 위치:

- `PART-III/MODEL-01`
