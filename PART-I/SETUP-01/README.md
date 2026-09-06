# SETUP-01

프로젝트의 분석 범위, 데이터 규격, 앱 입출력 구조와 담당자별 인수인계를 확정하는 단계이다.

## 완료 산출물

- `PROJECT_SPEC.md`: 프로젝트 공통 분석 규격
- `DATA_INVENTORY.md`: 확보된 데이터와 사용 목적
- `HANDOFF.md`: A·B·C 인수인계
- `setup_manifest.json`: 작업 일정과 의존성
- `validate_setup.py`: SETUP-01 자동 검사

## 담당별 시작 위치

- B: `PART-II/DATA-01`, `PART-II/DATA-02`
- C: `PART-II/APP-01`
- A: B의 결과를 받은 뒤 `PART-III/MODEL-01`

B와 C가 사용할 규격 파일은 각자의 최종 작업 폴더에 직접 배치되어 있다.
별도 파일 이동 없이 저장소를 clone한 뒤 바로 작업한다.
