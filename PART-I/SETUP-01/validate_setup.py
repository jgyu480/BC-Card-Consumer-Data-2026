from __future__ import annotations

import csv
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]

required_files = [
    root / "PART-I/SETUP-01/README.md",
    root / "PART-I/SETUP-01/PROJECT_SPEC.md",
    root / "PART-I/SETUP-01/DATA_INVENTORY.md",
    root / "PART-I/SETUP-01/HANDOFF.md",
    root / "PART-I/SETUP-01/setup_manifest.json",
    root / "PART-II/DATA-01/README.md",
    root / "PART-II/DATA-01/DATA_SCHEMA.csv",
    root / "PART-II/DATA-02/README.md",
    root / "PART-II/DATA-02/DATA_SCHEMA.csv",
    root / "PART-II/APP-01/README.md",
    root / "PART-II/APP-01/result_schema.json",
    root / "PART-II/APP-01/mock_recommendations.json",
]

missing = [
    str(path.relative_to(root))
    for path in required_files
    if not path.is_file()
]
if missing:
    raise SystemExit(f"필수 파일 누락: {missing}")

for relative_path in [
    "PART-II/DATA-01/DATA_SCHEMA.csv",
    "PART-II/DATA-02/DATA_SCHEMA.csv",
]:
    path = root / relative_path
    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise SystemExit(f"빈 스키마: {relative_path}")

    names = [row["column_name"] for row in rows]
    if len(names) != len(set(names)):
        raise SystemExit(f"중복 열: {relative_path}")

with (root / "PART-II/APP-01/mock_recommendations.json").open(
    encoding="utf-8"
) as file:
    mock = json.load(file)

if mock.get("is_mock") is not True:
    raise SystemExit("is_mock 값이 true가 아닙니다.")

brands = mock.get("brands", [])
if len(brands) != 3:
    raise SystemExit("mock 브랜드는 정확히 3개여야 합니다.")

brand_ids = [brand["brand_id"] for brand in brands]
if len(brand_ids) != len(set(brand_ids)):
    raise SystemExit("브랜드 ID가 중복되었습니다.")

for brand in brands:
    recommendations = brand["recommendations"]
    portfolios = brand["portfolios"]

    if len(recommendations) != 5:
        raise SystemExit(f"{brand['brand_id']}: 추천 상권이 5개가 아닙니다.")

    area_ids = {area["area_id"] for area in recommendations}
    desired_counts = {item["desired_store_count"] for item in portfolios}

    if desired_counts != {1, 2, 3}:
        raise SystemExit(f"{brand['brand_id']}: 1·2·3개 조합이 모두 필요합니다.")

    for portfolio in portfolios:
        if len(portfolio["area_ids"]) != portfolio["desired_store_count"]:
            raise SystemExit(f"{brand['brand_id']}: 출점 수와 상권 수 불일치")

        if not set(portfolio["area_ids"]).issubset(area_ids):
            raise SystemExit(f"{brand['brand_id']}: 존재하지 않는 상권 사용")

with (root / "PART-I/SETUP-01/setup_manifest.json").open(
    encoding="utf-8"
) as file:
    manifest = json.load(file)

if manifest.get("setup_status") != "completed":
    raise SystemExit("setup_manifest 상태 오류")

print("SETUP-01 validation passed")
print(f"필수 파일: {len(required_files)}개")
print(f"가짜 브랜드: {len(brands)}개")
