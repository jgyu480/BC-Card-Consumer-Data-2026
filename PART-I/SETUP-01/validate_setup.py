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
    root / "PART-I/SETUP-01/SERVICE_USER_CHECK.md",
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
    str(file.relative_to(root))
    for file in required_files
    if not file.is_file()
]

if missing:
    raise SystemExit(f"필수 파일 누락: {missing}")

for relative_path in [
    "PART-II/DATA-01/DATA_SCHEMA.csv",
    "PART-II/DATA-02/DATA_SCHEMA.csv",
]:
    with (root / relative_path).open(
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    names = [row["column_name"] for row in rows]

    if not rows:
        raise SystemExit(f"빈 스키마: {relative_path}")

    if len(names) != len(set(names)):
        raise SystemExit(f"중복 열: {relative_path}")

with (root / "PART-II/APP-01/mock_recommendations.json").open(
    encoding="utf-8"
) as file:
    mock = json.load(file)

if mock.get("schema_version") != "1.1.0":
    raise SystemExit("mock schema_version은 1.1.0이어야 합니다.")

if mock.get("is_mock") is not True:
    raise SystemExit("is_mock 값은 true여야 합니다.")

if "service_context" not in mock or "ui_copy" not in mock:
    raise SystemExit("서비스 사용자 정보가 없습니다.")

if mock["service_context"]["target_user"] != "베이커리 프랜차이즈 본사 사업개발팀":
    raise SystemExit("서비스 사용자가 잘못 정의되었습니다.")

brands = mock.get("brands", [])

if len(brands) != 3:
    raise SystemExit("mock 브랜드는 정확히 3개여야 합니다.")

for brand in brands:
    recommendations = brand["recommendations"]
    portfolios = brand["portfolios"]

    if len(recommendations) != 5:
        raise SystemExit(f"{brand['brand_id']}: 추천 상권은 5개여야 합니다.")

    area_ids = {area["area_id"] for area in recommendations}

    for area in recommendations:
        components = area["score_components"]

        if "competition_score" in components:
            raise SystemExit(
                f"{area['area_id']}: 이전 competition_score가 남아 있습니다."
            )

        required_components = {
            "dna_match_score",
            "market_score",
            "competition_attractiveness_score",
            "proximity_risk_score",
        }

        if not required_components.issubset(components):
            raise SystemExit(
                f"{area['area_id']}: 점수 구성요소 누락"
            )

        if "consumer_profile" not in area:
            raise SystemExit(
                f"{area['area_id']}: 소비자 프로필 누락"
            )

        if "data_quality" not in area:
            raise SystemExit(
                f"{area['area_id']}: 데이터 품질 누락"
            )

        if not area.get("next_checks"):
            raise SystemExit(
                f"{area['area_id']}: 추가 검토사항 누락"
            )

    by_distance = sorted(
        recommendations,
        key=lambda item: item["facts"]["min_distance_to_existing_store_m"],
    )

    risks = [
        item["score_components"]["proximity_risk_score"]
        for item in by_distance
    ]

    if any(
        earlier < later
        for earlier, later in zip(risks, risks[1:])
    ):
        raise SystemExit(
            f"{brand['brand_id']}: 거리가 멀어지는데 근접 위험이 증가합니다."
        )

    desired_counts = {
        portfolio["desired_store_count"]
        for portfolio in portfolios
    }

    if desired_counts != {1, 2, 3}:
        raise SystemExit(
            f"{brand['brand_id']}: 1·2·3개 조합이 모두 필요합니다."
        )

    for desired_count in [1, 2, 3]:
        selected = [
            item
            for item in portfolios
            if item["desired_store_count"] == desired_count
        ]

        if len(selected) != 3:
            raise SystemExit(
                f"{brand['brand_id']}: {desired_count}개 조합 Top 3 누락"
            )

        ranks = {item["portfolio_rank"] for item in selected}

        if ranks != {1, 2, 3}:
            raise SystemExit(
                f"{brand['brand_id']}: 포트폴리오 순위 오류"
            )

        for portfolio in selected:
            if len(portfolio["area_ids"]) != desired_count:
                raise SystemExit(
                    f"{brand['brand_id']}: 출점 수와 상권 수 불일치"
                )

            if not set(portfolio["area_ids"]).issubset(area_ids):
                raise SystemExit(
                    f"{brand['brand_id']}: 존재하지 않는 상권 사용"
                )

            if "score_components" not in portfolio:
                raise SystemExit(
                    f"{brand['brand_id']}: 포트폴리오 점수 구성 누락"
                )

print("SETUP-01 v1.1 validation passed")
print(f"필수 파일: {len(required_files)}개")
print(f"브랜드: {len(brands)}개")
print("경쟁점수 방향: 통과")
print("기존 점포 거리-위험 일관성: 통과")
print("서비스 사용자 관점: 통과")
