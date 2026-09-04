from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "1. Datasets" / "b. External Public Data"

FTC_DIR = RAW / "03_ftc_franchise_brands"
FTC_FILE = FTC_DIR / "ftc_brand_list.jsonl"
FTC_META = FTC_DIR / "ftc_brand_list.manifest.json"

MOIS_URL = "https://apis.data.go.kr/1741000/rest_cafes/info"
MOIS_DIR = RAW / "01_mois_rest_cafes"
MOIS_FILE = MOIS_DIR / "rest_cafes_seoul_address.jsonl"
MOIS_META = MOIS_DIR / "rest_cafes_seoul_address.manifest.json"
CACHE_DIR = MOIS_DIR / "seoul_address_pages"
CHECKPOINT = CACHE_DIR / "checkpoint.json"

PAGE_SIZE = 100

# 이번 실행에서 추가로 호출할 최대 횟수.
# 포털의 실제 일일 한도 및 다른 스크립트의 사용량과는 별개이다.
MAX_CALLS_PER_RUN = 700

FILTERS = {
    "returnType": "json",
    "cond[ROAD_NM_ADDR::LIKE]": "서울특별시",
}

EXISTING_FILES = {
    "small_business_stores_zip": (
        RAW / "02_small_business_stores"
        / "소상공인시장진흥공단_상가(상권)정보_20260630.zip"
    ),
    "seoul_store_by_area_20261": (
        RAW / "04_seoul_store_by_area" / "store_by_area_20261.jsonl"
    ),
    "seoul_store_by_area_20262": (
        RAW / "04_seoul_store_by_area" / "store_by_area_20262.jsonl"
    ),
    "seoul_sales_by_area_20261": (
        RAW / "05_seoul_sales_by_area" / "sales_by_area_20261.jsonl"
    ),
    "seoul_sales_by_area_20262": (
        RAW / "05_seoul_sales_by_area" / "sales_by_area_20262.jsonl"
    ),
}


def now():
    return datetime.now(timezone.utc).isoformat()


def read_key():
    path = ROOT / ".env"
    if not path.is_file():
        raise RuntimeError("레포 루트에 .env 파일이 없습니다.")

    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        name, value = line.split("=", 1)
        if name.strip() == "DATA_GO_KR_SERVICE_KEY":
            value = value.strip()
            if (
                len(value) >= 2
                and value[0] == value[-1]
                and value[0] in "\"'"
            ):
                value = value[1:-1]
            if value:
                return unquote(value)

    raise RuntimeError(".env의 DATA_GO_KR_SERVICE_KEY가 비어 있습니다.")


def redact(text, key):
    for secret in (quote(key, safe=""), key):
        if secret:
            text = text.replace(secret, "[REDACTED]")
    return text


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def write_json(path, value):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary.replace(path)


def xml_object(element):
    children = list(element)
    if not children:
        return (element.text or "").strip()

    result = {}
    for child in children:
        name = child.tag.split("}")[-1]
        value = xml_object(child)
        if name not in result:
            result[name] = value
        elif isinstance(result[name], list):
            result[name].append(value)
        else:
            result[name] = [result[name], value]
    return result


def fetch_mois_page(key, page):
    params = {
        "serviceKey": key,
        "pageNo": page,
        "numOfRows": PAGE_SIZE,
        **FILTERS,
    }

    request = Request(
        MOIS_URL + "?" + urlencode(params),
        headers={
            "Accept": "application/json",
            "User-Agent": "bc-card-consumer-data/1.0",
        },
    )

    try:
        with urlopen(request, timeout=60) as response:
            text = response.read().decode("utf-8-sig", errors="replace")
    except HTTPError as error:
        text = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"행안부 HTTP {error.code}: {redact(text, key)[:600]}"
        ) from None
    except URLError as error:
        raise RuntimeError(
            "행안부 연결 실패: " + redact(str(error.reason), key)
        ) from None

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        try:
            payload = xml_object(ET.fromstring(text))
        except ET.ParseError:
            raise RuntimeError(
                "응답 해석 실패: " + redact(text, key)[:600]
            ) from None

    if not isinstance(payload, dict):
        raise RuntimeError("응답이 객체 형식이 아닙니다.")

    response = payload.get("response", payload)
    if not isinstance(response, dict):
        raise RuntimeError("response 형식이 예상과 다릅니다.")

    header = response.get("header", {})
    if not isinstance(header, dict):
        raise RuntimeError("header 형식이 예상과 다릅니다.")

    code = str(header.get("resultCode", "")).strip()
    message = str(header.get("resultMsg", ""))

    if code not in {"0", "00", "000", "0000", "INFO-000"}:
        raise RuntimeError(
            f"행안부 API 오류: {code or '결과 코드 없음'} | "
            + redact(message, key)
            + "\n이미 받은 페이지는 보존됩니다."
        )

    body = response.get("body")
    if not isinstance(body, dict):
        raise RuntimeError("응답에 body가 없습니다.")

    total = int(body["totalCount"])
    actual_page = int(body["pageNo"])
    size = int(body["numOfRows"])

    if actual_page != page or size != PAGE_SIZE:
        raise RuntimeError("응답의 페이지 번호 또는 크기가 요청과 다릅니다.")

    items = body.get("items") or {}
    rows = items.get("item", []) if isinstance(items, dict) else items
    rows = rows or []

    if isinstance(rows, dict):
        rows = [rows]

    if not isinstance(rows, list) or any(
        not isinstance(row, dict) for row in rows
    ):
        raise RuntimeError("행안부 item 목록 형식이 예상과 다릅니다.")

    return rows, total


def verify_completed(path, meta_path):
    if not path.exists():
        return None

    if not meta_path.is_file():
        raise RuntimeError(
            f"{path.name}: 검증 기록이 없습니다. 기존 파일은 유지합니다."
        )

    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    if not meta.get("complete") or digest(path) != meta.get("sha256"):
        raise RuntimeError(
            f"{path.name}: 파일 검증 실패. 기존 파일은 유지합니다."
        )

    return meta


def collect_mois():
    MOIS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    completed = verify_completed(MOIS_FILE, MOIS_META)
    if completed:
        print(
            f"[SKIP] 행안부 서울 주소 자료: "
            f"{completed['rows']:,}건, 파일 검증 통과"
        )
        return completed

    key = read_key()

    # 재실행 시 현재 전체 건수를 확인한 뒤 저장된 페이지를 이어 사용한다.
    first_rows, total = fetch_mois_page(key, 1)
    calls = 1

    if total <= 0:
        raise RuntimeError("서울특별시 주소 조건의 조회 결과가 0건입니다.")

    if CHECKPOINT.exists():
        checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        if (
            checkpoint.get("filters") != FILTERS
            or checkpoint.get("total_count") != total
            or checkpoint.get("page_size") != PAGE_SIZE
        ):
            raise RuntimeError(
                "이전 수집과 조건 또는 전체 건수가 달라졌습니다.\n"
                "페이지를 섞지 않도록 중단했습니다. 기존 캐시는 유지됩니다."
            )
    else:
        checkpoint = {
            "started_at_utc": now(),
            "total_count": total,
            "page_size": PAGE_SIZE,
            "filters": FILTERS,
        }
        write_json(CHECKPOINT, checkpoint)

    pages = math.ceil(total / PAGE_SIZE)
    print(
        f"[FETCH] 행안부 서울 주소 자료: {total:,}건 / {pages:,}페이지",
        flush=True,
    )

    for page in range(1, pages + 1):
        page_file = CACHE_DIR / f"page_{page:06d}.json"

        if page_file.exists():
            cached = json.loads(page_file.read_text(encoding="utf-8"))
            rows = cached["rows"]
            if cached["page"] != page or cached["total"] != total:
                raise RuntimeError(f"{page}페이지 캐시 정보가 다릅니다.")
        else:
            if page == 1:
                rows = first_rows
            else:
                if calls >= MAX_CALLS_PER_RUN:
                    raise RuntimeError(
                        f"이번 실행의 호출 상한 {MAX_CALLS_PER_RUN}회에 도달했습니다.\n"
                        f"{page - 1:,}/{pages:,}페이지를 보존했습니다.\n"
                        "남은 일일 한도를 확인한 뒤 같은 명령으로 이어받을 수 있습니다."
                    )

                time.sleep(0.2)
                rows, current_total = fetch_mois_page(key, page)
                calls += 1

                if current_total != total:
                    raise RuntimeError(
                        "수집 중 전체 건수가 변경되었습니다. 캐시는 보존합니다."
                    )

            expected = min(PAGE_SIZE, total - (page - 1) * PAGE_SIZE)
            if len(rows) != expected:
                raise RuntimeError(
                    f"{page}페이지 건수 불일치: "
                    f"기대 {expected}건, 응답 {len(rows)}건"
                )

            write_json(
                page_file,
                {
                    "page": page,
                    "total": total,
                    "fetched_at_utc": now(),
                    "rows": rows,
                },
            )

        expected = min(PAGE_SIZE, total - (page - 1) * PAGE_SIZE)
        if len(rows) != expected:
            raise RuntimeError(f"{page}페이지 캐시 건수가 맞지 않습니다.")

        if page == 1 or page % 10 == 0 or page == pages:
            print(
                f"  확보 {min(page * PAGE_SIZE, total):,}/{total:,}건",
                flush=True,
            )

    # 중복 행도 삭제하지 않고, API 원본을 페이지 순서대로 합친다.
    temporary = MOIS_FILE.with_name(MOIS_FILE.name + ".part")
    saved = 0
    with temporary.open("w", encoding="utf-8") as output:
        for page in range(1, pages + 1):
            page_file = CACHE_DIR / f"page_{page:06d}.json"
            cached = json.loads(page_file.read_text(encoding="utf-8"))
            for row in cached["rows"]:
                output.write(json.dumps(row, ensure_ascii=False) + "\n")
                saved += 1

    if saved != total:
        raise RuntimeError("최종 건수가 일치하지 않아 완료 처리하지 않았습니다.")

    meta = {
        "complete": True,
        "rows": saved,
        "source": MOIS_URL,
        "filters": FILTERS,
        "scope": "도로명주소에 서울특별시가 포함된 휴게음식점, 영업상태 제한 없음",
        "started_at_utc": checkpoint["started_at_utc"],
        "completed_at_utc": now(),
        "coordinate_crs": "EPSG:5174",
        "sha256": digest(temporary),
        "limitations": [
            "도로명주소가 비어 있거나 다른 표기로 기록된 서울 사업장은 누락될 수 있음",
            "휴게음식점에는 카페 외 업종도 포함됨",
            "현재조회 API의 수집 결과이며 단일 과거시점 스냅샷을 보장하지 않음",
            "중복 행은 삭제하지 않고 보존함",
        ],
    }

    temporary.replace(MOIS_FILE)
    write_json(MOIS_META, meta)
    print(f"[OK] 행안부 {saved:,}건 저장 및 건수 검증 완료")
    return meta


def main():
    for name, path in EXISTING_FILES.items():
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"기존 원본이 없거나 비어 있습니다: {name}")

    print("[SKIP] 소진공 ZIP·서울 점포·매출: 기존 파일 유지")

    ftc = verify_completed(FTC_FILE, FTC_META)
    if ftc is None:
        raise RuntimeError("앞서 수집한 공정위 완료 파일이 없습니다.")

    print(
        f"[SKIP] 공정위 {ftc['year']}년: "
        f"{ftc['rows']:,}행, 파일 검증 통과"
    )

    mois = collect_mois()

    targets = dict(EXISTING_FILES)
    targets["ftc_brand_list"] = FTC_FILE
    targets["mois_rest_cafes_seoul_address"] = MOIS_FILE

    manifest = {
        "updated_at_utc": now(),
        "datasets": {
            name: {
                "exists": path.is_file(),
                "path": str(path.relative_to(ROOT)),
                "size_mb": round(path.stat().st_size / 1024**2, 2),
            }
            for name, path in targets.items()
        },
        "ftc_fetch_result": ftc,
        "mois_fetch_result": mois,
    }
    write_json(RAW / "collection_manifest.json", manifest)

    print("\n[COMPLETE] 서울 파일럿용 5개 데이터 종류 확보")
    for name, info in manifest["datasets"].items():
        print(f"  [OK] {name}: {info['size_mb']} MB")

    print("\n행안부 범위: 서울특별시 도로명주소 조건, 모든 영업상태")
    print("행안부 과거시점 history 자료는 아직 수집하지 않았습니다.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[중단] 저장된 페이지와 기존 완료 파일은 유지됩니다.")
        sys.exit(130)
    except Exception as error:
        print(f"\n[중단] {error}", file=sys.stderr)
        sys.exit(1)