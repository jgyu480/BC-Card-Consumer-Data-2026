from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    raise SystemExit("pandas가 필요합니다. 먼저 `python3 -m pip install pandas`를 실행하세요.")


def find_repo_root() -> Path:
    here = Path(__file__).resolve()
    candidates = [Path.cwd().resolve(), here.parent, *here.parents]

    for parent in candidates:
        if (parent / ".git").exists():
            return parent

    for parent in candidates:
        dataset_names = (
            "1. Datasets",
            "1.Datasets",
            "1. Dataset",
            "Datasets",
            "data",
        )
        if any((parent / name).exists() for name in dataset_names):
            return parent

    raise SystemExit("저장소 루트를 찾지 못했습니다.")


ROOT = find_repo_root()
BASE = ROOT / "PART-II" / "DATA-02"
CONFIG_PATH = BASE / "config" / "data02_config.json"
REPORT_PATH = BASE / "reports" / "stage1_schema_report.md"
CONFIG = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def norm(value: object) -> str:
    return re.sub(r"\s+", "", str(value)).upper()


def read_csv_flexible(path_or_buffer, nrows=None):
    errors = []
    for encoding in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            if hasattr(path_or_buffer, "seek"):
                path_or_buffer.seek(0)
            return pd.read_csv(path_or_buffer, encoding=encoding, nrows=nrows, low_memory=False), encoding
        except Exception as exc:
            errors.append(f"{encoding}: {exc}")
    raise RuntimeError("CSV 인코딩 판별 실패\n" + "\n".join(errors))


def read_text_flexible(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_api_key() -> str | None:
    env_file = load_env(ROOT / ".env")
    candidates = (
        "SEOUL_API_KEY",
        "SEOUL_OPEN_API_KEY",
        "SEOUL_OPEN_DATA_API_KEY",
        "SEOUL_DATA_API_KEY",
    )
    for key in candidates:
        value = os.environ.get(key) or env_file.get(key)
        if value:
            return value
    return None


def fetch_area_reference(report: list[str]) -> None:
    output = ROOT / CONFIG["input_paths"]["area_reference"]
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.stat().st_size > 0:
        count = sum(1 for _ in output.open(encoding="utf-8"))
        report.append(f"- 서울 상권 기준정보: 기존 파일 사용 `{rel(output)}` ({count:,}행)")
        return

    api_key = get_api_key()
    if not api_key:
        report.append("- 서울 상권 기준정보: 미수집(.env에서 서울시 API 키를 찾지 못함)")
        report.append("- 키 변수명 후보: `SEOUL_API_KEY`, `SEOUL_OPEN_API_KEY`, `SEOUL_OPEN_DATA_API_KEY`")
        return

    service = "TbgisTrdarRelm"
    rows: list[dict] = []
    start, batch, total = 1, 1000, None
    while total is None or start <= total:
        end = start + batch - 1
        encoded_key = urllib.parse.quote(api_key, safe="")
        url = f"http://openapi.seoul.go.kr:8088/{encoded_key}/json/{service}/{start}/{end}/"
        with urllib.request.urlopen(url, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        body = payload.get(service)
        if body is None:
            message = payload.get("RESULT") or payload
            raise RuntimeError(f"서울시 API 응답 오류: {message}")
        result = body.get("RESULT", {})
        if result.get("CODE") not in (None, "INFO-000"):
            raise RuntimeError(f"서울시 API 오류: {result}")
        total = int(body.get("list_total_count", 0))
        batch_rows = body.get("row", [])
        rows.extend(batch_rows)
        print(f"  상권 기준정보 수집: {len(rows):,}/{total:,}")
        if not batch_rows:
            break
        start += batch
        time.sleep(0.15)

    with output.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    manifest = {
        "source": "서울 열린데이터광장 TbgisTrdarRelm",
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "rows": len(rows),
        "service": service,
        "api_key_saved": False,
    }
    output.with_name("area_reference_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report.append(f"- 서울 상권 기준정보: `{rel(output)}` ({len(rows):,}행)")


def inspect_bc(report: list[str]) -> None:
    path = ROOT / CONFIG["input_paths"]["bc"]
    report.extend(["", "## 2. BC 데이터"])
    if not path.exists():
        report.append(f"- **파일 없음**: `{rel(path)}`")
        return
    df, encoding = read_csv_flexible(path)
    report.append(f"- 파일: `{rel(path)}`")
    report.append(f"- 인코딩: `{encoding}`")
    report.append(f"- 크기: {len(df):,}행 × {len(df.columns)}열")
    report.append(f"- 컬럼: `{list(df.columns)}`")
    expected = ["STRD_YYMM", "SIDO_NM", "CCG_NM", "GENDER_CD", "AGE_CD", "TP_BUZ_NO", "TP_BUZ_NM", "amt", "cnt"]
    missing = [c for c in expected if c not in df.columns]
    report.append(f"- 예상 컬럼 누락: `{missing}`")
    for col in ("STRD_YYMM", "GENDER_CD", "AGE_CD", "TP_BUZ_NO", "TP_BUZ_NM"):
        if col in df.columns:
            counts = df[col].astype(str).str.strip().value_counts(dropna=False).head(30).to_dict()
            report.append(f"- `{col}` 값: `{counts}`")
    if "TP_BUZ_NO" in df.columns:
        bakery = df[df["TP_BUZ_NO"].astype(str).str.strip().eq(CONFIG["bc_industry_code"])]
    elif "TP_BUZ_NM" in df.columns:
        bakery = df[df["TP_BUZ_NM"].map(norm).eq("제과점")]
    else:
        bakery = df.iloc[0:0]
    report.append(f"- 제과점 필터 결과: **{len(bakery):,}행**")
    duplicate_cols = [c for c in ["STRD_YYMM", "SIDO_NM", "CCG_NM", "GENDER_CD", "AGE_CD", "TP_BUZ_NO"] if c in df.columns]
    if duplicate_cols:
        report.append(f"- 차원키 완전중복 추가행: **{int(df.duplicated(duplicate_cols).sum()):,}행**")

    readme = ROOT / CONFIG["input_paths"]["bc_readme"]
    if readme.exists():
        text = read_text_flexible(readme)
        lines = [line.strip() for line in text.splitlines() if re.search(r"GENDER|AGE|성별|연령|법인|외국", line, re.I)]
        report.append("- BC README에서 찾은 코드 설명:")
        if lines:
            report.extend([f"  - `{line[:500]}`" for line in lines[:40]])
        else:
            report.append("  - 관련 문구를 자동으로 찾지 못함")
    else:
        report.append(f"- BC README 없음: `{rel(readme)}`")


def inspect_jsonl(label: str, path: Path, report: list[str]) -> None:
    report.extend(["", f"## {label}"])
    if not path.exists():
        report.append(f"- **파일 없음**: `{rel(path)}`")
        return
    df = pd.read_json(path, lines=True)
    report.append(f"- 파일: `{rel(path)}`")
    report.append(f"- 크기: {len(df):,}행 × {len(df.columns)}열")
    report.append(f"- 컬럼: `{list(df.columns)}`")
    for col in ("STDR_YYQU_CD", "TRDAR_SE_CD", "TRDAR_SE_CD_NM", "SVC_INDUTY_CD", "SVC_INDUTY_CD_NM"):
        if col in df.columns:
            counts = df[col].astype(str).str.strip().value_counts(dropna=False).head(20).to_dict()
            report.append(f"- `{col}` 값 상위: `{counts}`")
    if "SVC_INDUTY_CD" in df.columns:
        subset = df[df["SVC_INDUTY_CD"].astype(str).str.strip().eq(CONFIG["seoul_industry_code"])]
        report.append(f"- `{CONFIG['seoul_industry_code']}` 필터 결과: **{len(subset):,}행**")
        keys = [c for c in ["STDR_YYQU_CD", "TRDAR_CD", "SVC_INDUTY_CD"] if c in subset.columns]
        if keys:
            report.append(f"- 제과점 키 완전중복 추가행: **{int(subset.duplicated(keys).sum()):,}행**")


def decode_zip_name(name: str) -> str:
    try:
        return name.encode("cp437").decode("cp949")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return name


def inspect_small_business(report: list[str]) -> None:
    path = ROOT / CONFIG["input_paths"]["small_business_zip"]
    report.extend(["", "## 5. 소진공 상가정보"])
    if not path.exists():
        report.append(f"- **파일 없음**: `{rel(path)}`")
        return
    report.append(f"- 파일: `{rel(path)}`")
    with zipfile.ZipFile(path) as zf:
        csv_members = [m for m in zf.infolist() if m.filename.lower().endswith(".csv")]
        decoded = [(m, decode_zip_name(m.filename)) for m in csv_members]
        seoul = [(m, name) for m, name in decoded if "서울" in name]
        report.append(f"- ZIP CSV 수: {len(csv_members)}개")
        report.append(f"- 서울 파일 후보: `{[name for _, name in seoul]}`")
        if not seoul:
            report.append("- 서울 파일명을 자동 판별하지 못함")
            return
        member, decoded_name = seoul[0]
        with zf.open(member) as f:
            sample, encoding = read_csv_flexible(f, nrows=5000)
        report.append(f"- 선택 파일: `{decoded_name}`")
        report.append(f"- 표본 인코딩: `{encoding}`")
        report.append(f"- 컬럼: `{list(sample.columns)}`")
        category_cols = [c for c in sample.columns if "업종" in c and c.endswith("명")]
        for col in category_cols:
            values = sorted({str(v).strip() for v in sample[col].dropna().unique() if re.search(r"제과|제빵|빵|베이커|케이크|도넛|떡|카페|커피", str(v))})
            report.append(f"- `{col}` 베이커리 관련 후보: `{values}`")


def inspect_area_reference(report: list[str]) -> None:
    path = ROOT / CONFIG["input_paths"]["area_reference"]
    report.extend(["", "## 6. 서울 상권 기준정보"])
    try:
        fetch_area_reference(report)
    except Exception as exc:
        report.append(f"- 수집 실패: `{type(exc).__name__}: {exc}`")
    if path.exists() and path.stat().st_size > 0:
        df = pd.read_json(path, lines=True)
        report.append(f"- 크기: {len(df):,}행 × {len(df.columns)}열")
        report.append(f"- 컬럼: `{list(df.columns)}`")
        if "TRDAR_CD" in df.columns:
            report.append(f"- 상권코드 고유값: {df['TRDAR_CD'].astype(str).nunique():,}개")
            report.append(f"- 상권코드 중복 추가행: {int(df.duplicated(['TRDAR_CD']).sum()):,}행")


def update_config_from_verified_schema(report: list[str]) -> None:
    report.extend(["", "## 7. 2단계 전 확인할 항목"])
    report.append("- `GENDER_CD`의 개인 성별 코드 중 여성 코드")
    report.append("- `AGE_CD` 1~6의 실제 연령대 매핑")
    report.append("- 소진공에서 베이커리로 사용할 정확한 업종 소분류")
    report.append("- DATA-01과 DATA-02가 동일한 `area_id`와 시군구 코드 문자열을 사용하는지")


def main() -> None:
    report = [
        "# DATA-02 1단계 스키마 검증 보고서",
        "",
        f"- 생성시각(UTC): `{datetime.now(timezone.utc).isoformat()}`",
        f"- 저장소: `{ROOT}`",
        "",
        "## 1. 목적",
        "",
        "원시 데이터의 실제 컬럼·코드·기간을 확인하고 추측에 의한 전처리를 차단합니다.",
    ]
    inspect_bc(report)
    inspect_jsonl("3. 서울시 점포-상권", ROOT / CONFIG["input_paths"]["seoul_store"], report)
    inspect_jsonl("4. 서울시 추정매출-상권", ROOT / CONFIG["input_paths"]["seoul_sales"], report)
    inspect_small_business(report)
    inspect_area_reference(report)
    update_config_from_verified_schema(report)
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"\n[DATA-02 1/4 완료] {rel(REPORT_PATH)}")
    print("아래 명령으로 내용을 복사한 뒤 대화에 붙여 넣으세요.")
    print(f'pbcopy < "{rel(REPORT_PATH)}"')


if __name__ == "__main__":
    main()
