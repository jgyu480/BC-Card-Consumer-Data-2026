#!/usr/bin/env python3
"""
서울시 상권분석 Open API 수집기

- 점포-상권: VwsmTrdarStorQq
- 추정매출-상권: VwsmTrdarSelngQq
- 대상 시점: 2026Q1(20261), 2026Q2(20262)

실행:
  python3 "3. Source Code/ingestion/fetch_seoul_commercial.py" --check
  python3 "3. Source Code/ingestion/fetch_seoul_commercial.py" --fetch
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"
BASE_URL = "http://openapi.seoul.go.kr:8088"
PAGE_SIZE = 1000
QUARTERS = ["20261", "20262"]

DATASETS = {
    "store_by_area": {
        "service": "VwsmTrdarStorQq",
        "output_dir": ROOT
        / "1. Datasets/b. External Public Data/04_seoul_store_by_area",
    },
    "sales_by_area": {
        "service": "VwsmTrdarSelngQq",
        "output_dir": ROOT
        / "1. Datasets/b. External Public Data/05_seoul_sales_by_area",
    },
}


def read_env_value(path: Path, key: str) -> str:
    if not path.exists():
        raise FileNotFoundError(
            f".env 파일이 없습니다: {path}\n"
            "cp .env.example .env 후 API 키를 입력하세요."
        )

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() == key:
            return value.strip().strip('"').strip("'")

    raise KeyError(f"{key} 값이 .env에 없습니다.")


def request_page(api_key: str, service: str, start: int, end: int, quarter: str):
    url = (
        f"{BASE_URL}/{quote(api_key, safe='')}/json/"
        f"{service}/{start}/{end}/{quarter}"
    )

    request = Request(url, headers={"User-Agent": "bc-card-consumer-data/1.0"})

    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            break
        except Exception as error:
            if attempt == 2:
                raise RuntimeError(
                    f"API 호출 실패: {service}, {quarter}, {start}-{end}\n{error}"
                ) from error
            time.sleep(2 * (attempt + 1))

    if service not in payload:
        raise RuntimeError(
            "서울시 API가 정상 데이터 대신 오류를 반환했습니다.\n"
            f"응답: {json.dumps(payload, ensure_ascii=False)[:500]}"
        )

    body = payload[service]

    result = body.get("RESULT", {})
    if result.get("CODE") not in (None, "INFO-000"):
        raise RuntimeError(
            f"서울시 API 오류: {result.get('CODE')} - {result.get('MESSAGE')}"
        )

    rows = body.get("row", [])
    total = int(body.get("list_total_count", 0))
    return rows, total


def ensure_requested_quarter(rows: list[dict], quarter: str) -> None:
    returned_quarters = {
        str(row.get("STDR_YYQU_CD"))
        for row in rows
        if row.get("STDR_YYQU_CD") is not None
    }

    if returned_quarters and returned_quarters != {quarter}:
        raise RuntimeError(
            f"API가 요청한 {quarter} 외의 분기를 반환했습니다: "
            f"{sorted(returned_quarters)}\n"
            "전체 수집을 중단합니다. API 명세를 다시 확인해야 합니다."
        )


def check_dataset(api_key: str, dataset_name: str, config: dict, quarter: str) -> None:
    rows, total = request_page(
        api_key=api_key,
        service=config["service"],
        start=1,
        end=5,
        quarter=quarter,
    )
    ensure_requested_quarter(rows, quarter)

    print(f"\n[{dataset_name} | {quarter}]")
    print(f"  service: {config['service']}")
    print(f"  total rows: {total:,}")
    print(f"  preview rows: {len(rows)}")

    if rows:
        print(f"  columns: {', '.join(rows[0].keys())}")
        print(
            "  first row: "
            + json.dumps(rows[0], ensure_ascii=False)[:500]
        )
    else:
        print("  WARNING: 반환된 행이 없습니다.")


def fetch_dataset(api_key: str, dataset_name: str, config: dict, quarter: str) -> None:
    output_dir = config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    first_rows, total = request_page(
        api_key=api_key,
        service=config["service"],
        start=1,
        end=PAGE_SIZE,
        quarter=quarter,
    )
    ensure_requested_quarter(first_rows, quarter)

    if total == 0:
        print(f"[SKIP] {dataset_name} {quarter}: 0 rows")
        return

    output_path = output_dir / f"{dataset_name}_{quarter}.jsonl"
    temp_path = output_path.with_suffix(".jsonl.tmp")
    manifest_path = output_dir / f"{dataset_name}_{quarter}_manifest.json"

    print(f"\n[FETCH] {dataset_name} {quarter}: {total:,} rows")

    written = 0
    with temp_path.open("w", encoding="utf-8") as file:
        for start in range(1, total + 1, PAGE_SIZE):
            end = min(start + PAGE_SIZE - 1, total)

            if start == 1:
                rows = first_rows
            else:
                rows, _ = request_page(
                    api_key=api_key,
                    service=config["service"],
                    start=start,
                    end=end,
                    quarter=quarter,
                )
                ensure_requested_quarter(rows, quarter)

            for row in rows:
                file.write(json.dumps(row, ensure_ascii=False) + "\n")
                written += 1

            print(f"  saved {written:,}/{total:,} rows")
            time.sleep(0.15)

    temp_path.replace(output_path)

    manifest = {
        "dataset_name": dataset_name,
        "service_name": config["service"],
        "quarter": quarter,
        "requested_rows": total,
        "saved_rows": written,
        "format": "JSON Lines",
        "source": "서울 열린데이터광장 Open API",
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"  completed: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="각 API에서 5행만 받아 연결·컬럼·전체 행 수를 확인합니다.",
    )
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="2026Q1·Q2 전체 데이터를 JSONL 원본 파일로 저장합니다.",
    )
    args = parser.parse_args()

    if not args.check and not args.fetch:
        parser.error("--check 또는 --fetch 중 하나를 입력하세요.")

    api_key = read_env_value(ENV_PATH, "SEOUL_OPEN_API_KEY")
    if not api_key:
        raise ValueError("SEOUL_OPEN_API_KEY 값이 비어 있습니다.")

    for dataset_name, config in DATASETS.items():
        for quarter in QUARTERS:
            if args.check:
                check_dataset(api_key, dataset_name, config, quarter)
            if args.fetch:
                fetch_dataset(api_key, dataset_name, config, quarter)


if __name__ == "__main__":
    main()
