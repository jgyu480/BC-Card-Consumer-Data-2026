from __future__ import annotations

import json
import re
import unicodedata
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path.cwd().resolve()
BASE = ROOT / "PART-II/DATA-02"
CONFIG_PATH = BASE / "config/data02_config.json"
INTERMEDIATE = BASE / "intermediate"
OUTPUTS = BASE / "outputs"
REPORTS = BASE / "reports"

INTERMEDIATE.mkdir(parents=True, exist_ok=True)
OUTPUTS.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise SystemExit(f"설정 파일이 없습니다: {CONFIG_PATH}")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


CONFIG = load_config()


def persist_confirmed_codebook() -> None:
    CONFIG["bc_codebook"] = {
        "gender": {"1": "남성", "2": "여성", "3": "외국인", "x": "법인"},
        "age": {
            "1": "20대 이하", "2": "20대", "3": "30대", "4": "40대",
            "5": "50대", "6": "60대 이상", "x": "법인 및 외국인",
        },
        "bakery_industry_code": "8301",
    }
    CONFIG["seoul_codebook"] = {
        "bakery_service_code": "CS100005",
        "coffee_service_code": "CS100010",
    }
    CONFIG["small_business_codebook"] = {
        "bakery_subcategory_name": "빵/도넛"
    }
    CONFIG_PATH.write_text(
        json.dumps(CONFIG, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def input_path(key: str, fallback: str) -> Path:
    rel = CONFIG.get("input_paths", {}).get(key, fallback)
    path = ROOT / rel
    if not path.exists():
        raise SystemExit(f"입력 파일이 없습니다: {path}")
    return path


BC_PATH = input_path(
    "bc", "Datasets/a. BC Provided Data/ABP_CONTEST_DATA.csv"
)
STORE_PATH = input_path(
    "seoul_store",
    "Datasets/b. External Public Data/04_seoul_store_by_area/store_by_area_20262.jsonl",
)
SALES_PATH = input_path(
    "seoul_sales",
    "Datasets/b. External Public Data/05_seoul_sales_by_area/sales_by_area_20262.jsonl",
)
SMALL_ZIP_PATH = input_path(
    "small_business_zip",
    "Datasets/b. External Public Data/02_small_business_stores/소상공인시장진흥공단_상가(상권)정보_20260630.zip",
)
AREA_PATH = input_path(
    "area_reference",
    "Datasets/b. External Public Data/06_seoul_area_reference/area_reference.jsonl",
)


def canonical_text(value) -> str:
    if pd.isna(value):
        return ""
    return unicodedata.normalize("NFC", str(value)).strip()


def key_text(value) -> str:
    text = canonical_text(value)
    return re.sub(r"[\s·ㆍ.\-()]", "", text).lower()


SIDO_ALIASES = {
    "서울": "서울특별시",
    "부산": "부산광역시",
    "대구": "대구광역시",
    "인천": "인천광역시",
    "광주": "전남광주통합특별시",
    "광주광역시": "전남광주통합특별시",
    "대전": "대전광역시",
    "울산": "울산광역시",
    "세종": "세종특별자치시",
    "경기": "경기도",
    "강원": "강원특별자치도",
    "충북": "충청북도",
    "충남": "충청남도",
    "전북": "전북특별자치도",
    "전라북도": "전북특별자치도",
    "전남": "전남광주통합특별시",
    "전라남도": "전남광주통합특별시",
    "경북": "경상북도",
    "경남": "경상남도",
    "제주": "제주특별자치도",
}


SIDO_BY_CCG_PREFIX = {
    "12": "전남광주통합특별시",
    "11": "서울특별시",
    "26": "부산광역시",
    "27": "대구광역시",
    "28": "인천광역시",
    "29": "광주광역시",
    "30": "대전광역시",
    "31": "울산광역시",
    "36": "세종특별자치시",
    "41": "경기도",
    "43": "충청북도",
    "44": "충청남도",
    "46": "전라남도",
    "47": "경상북도",
    "48": "경상남도",
    "50": "제주특별자치도",
    "51": "강원특별자치도",
    "52": "전북특별자치도",
}

def normalize_sido(value) -> str:
    text = canonical_text(value)
    return SIDO_ALIASES.get(text, text)


def safe_divide(num: pd.Series, den: pd.Series) -> pd.Series:
    n = pd.to_numeric(num, errors="coerce").astype(float)
    d = pd.to_numeric(den, errors="coerce").astype(float)
    return pd.Series(np.where(d > 0, n / d, np.nan), index=num.index)


def read_jsonl(path: Path) -> pd.DataFrame:
    return pd.read_json(path, lines=True, dtype=False)


def build_ccg_reference() -> tuple[pd.DataFrame, list[tuple[str, str]]]:
    usecols = ["시도명", "시군구명", "시군구코드"]
    frames = []
    with zipfile.ZipFile(SMALL_ZIP_PATH) as archive:
        members = [n for n in archive.namelist() if n.lower().endswith(".csv")]
        for member in members:
            with archive.open(member) as stream:
                frame = pd.read_csv(
                    stream,
                    encoding="utf-8-sig",
                    dtype=str,
                    usecols=usecols,
                    low_memory=False,
                )
            frames.append(frame.drop_duplicates())

    ref = pd.concat(frames, ignore_index=True).drop_duplicates()
    ref = ref.rename(columns={
        "시도명": "sido_nm",
        "시군구명": "ccg_nm",
        "시군구코드": "ccg_id",
    })[["sido_nm", "ccg_nm", "ccg_id"]]
    for col in ["sido_nm", "ccg_nm", "ccg_id"]:
        ref[col] = ref[col].map(canonical_text)
    ref["sido_nm"] = ref["sido_nm"].map(normalize_sido)
    ref["ccg_id"] = ref["ccg_id"].str.replace(r"\.0$", "", regex=True).str.zfill(5)
    sido_from_code = ref["ccg_id"].str[:2].map(SIDO_BY_CCG_PREFIX)
    ref["sido_nm"] = sido_from_code.fillna(ref["sido_nm"])
    ref["sido_key"] = ref["sido_nm"].map(key_text)
    ref["ccg_key"] = ref["ccg_nm"].map(key_text)
    ref = ref.loc[(ref.ccg_id != "") & (ref.ccg_nm != "")].drop_duplicates()

    ambiguous = (
        ref.groupby(["sido_key", "ccg_key"])["ccg_id"]
        .nunique()
        .loc[lambda s: s > 1]
    )
    ambiguous_keys = list(ambiguous.index)
    if ambiguous_keys:
        bad = pd.MultiIndex.from_frame(ref[["sido_key", "ccg_key"]]).isin(ambiguous_keys)
        ref = ref.loc[~bad].copy()

    ref = ref.sort_values(["sido_nm", "ccg_nm", "ccg_id"]).drop_duplicates(
        ["sido_key", "ccg_key"]
    )
    ref.to_parquet(INTERMEDIATE / "ccg_reference.parquet", index=False)
    return ref, ambiguous_keys


BC_RENAME = {
    "TP_BUZ_NO": "TPBUZ_NO",
    "TP_BUZ_NM": "TPBUZ_NM",
    "amt": "AMT",
    "cnt": "CNT",
}


def prepare_bc(ccg_ref: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    bc = pd.read_csv(BC_PATH, encoding="utf-8-sig", dtype=str, low_memory=False)
    bc = bc.rename(columns=BC_RENAME)
    required = [
        "STRD_YYMM", "SIDO_NM", "CCG_NM", "GENDER_CD", "AGE_CD",
        "TPBUZ_NO", "TPBUZ_NM", "AMT", "CNT",
    ]
    missing = [c for c in required if c not in bc.columns]
    if missing:
        raise SystemExit(f"BC 필수 컬럼 누락: {missing}")
    bc = bc[required].copy()
    for col in required[:-2]:
        bc[col] = bc[col].map(canonical_text)
    bc["GENDER_CD"] = bc["GENDER_CD"].str.lower()
    bc["AGE_CD"] = bc["AGE_CD"].str.lower()
    bc["SIDO_NM"] = bc["SIDO_NM"].map(normalize_sido)
    bc["sido_key"] = bc["SIDO_NM"].map(key_text)
    bc["ccg_key"] = bc["CCG_NM"].map(key_text)
    bc["AMT"] = pd.to_numeric(bc["AMT"].str.replace(",", "", regex=False), errors="coerce").fillna(0)
    bc["CNT"] = pd.to_numeric(bc["CNT"].str.replace(",", "", regex=False), errors="coerce").fillna(0)

    ref_cols = ["sido_key", "ccg_key", "ccg_id"]
    bc = bc.merge(ccg_ref[ref_cols], how="left", on=["sido_key", "ccg_key"], validate="m:1")
    unmatched = bc.loc[bc.ccg_id.isna(), ["SIDO_NM", "CCG_NM"]].drop_duplicates()

    def amount(mask: pd.Series) -> pd.Series:
        return bc["AMT"].where(mask, 0.0)

    def count(mask: pd.Series) -> pd.Series:
        return bc["CNT"].where(mask, 0.0)

    personal = bc.GENDER_CD.isin(["1", "2"]) & bc.AGE_CD.isin(list("123456"))
    bc["total_amt"] = bc.AMT
    bc["total_cnt"] = bc.CNT
    bc["personal_amt"] = amount(personal)
    bc["personal_cnt"] = count(personal)
    bc["male_amt"] = amount(bc.GENDER_CD.eq("1") & personal)
    bc["female_amt"] = amount(bc.GENDER_CD.eq("2") & personal)
    bc["foreign_amt"] = amount(bc.GENDER_CD.eq("3"))
    bc["corporate_amt"] = amount(bc.GENDER_CD.eq("x"))
    for age in "123456":
        age_mask = personal & bc.AGE_CD.eq(age)
        bc[f"age_cd_{age}_amt"] = amount(age_mask)

    keys = ["STRD_YYMM", "ccg_id", "SIDO_NM", "CCG_NM", "TPBUZ_NO", "TPBUZ_NM"]
    value_cols = [
        "total_amt", "total_cnt", "personal_amt", "personal_cnt", "male_amt",
        "female_amt", "foreign_amt", "corporate_amt",
        *[f"age_cd_{age}_amt" for age in "123456"],
    ]
    matched = bc.loc[bc.ccg_id.notna()].copy()
    monthly = matched.groupby(keys, as_index=False, dropna=False)[value_cols].sum()
    monthly = monthly.rename(columns={
        "STRD_YYMM": "period_month", "SIDO_NM": "sido_nm", "CCG_NM": "ccg_nm",
        "TPBUZ_NO": "industry_code", "TPBUZ_NM": "industry_name",
    })
    monthly["female_share_personal_amt"] = safe_divide(monthly.female_amt, monthly.male_amt + monthly.female_amt)
    monthly["foreign_share_total_amt"] = safe_divide(monthly.foreign_amt, monthly.total_amt)
    monthly["corporate_share_total_amt"] = safe_divide(monthly.corporate_amt, monthly.total_amt)
    monthly["avg_ticket"] = safe_divide(monthly.total_amt, monthly.total_cnt)
    for age in "123456":
        monthly[f"age_cd_{age}_share_personal_amt"] = safe_divide(
            monthly[f"age_cd_{age}_amt"], monthly.personal_amt
        )
    monthly["model_eligible"] = True
    monthly = monthly.sort_values(["period_month", "ccg_id", "industry_code"])

    unique_key = ["period_month", "ccg_id", "industry_code"]
    if monthly.duplicated(unique_key).any():
        raise SystemExit(f"BC 월별 결과 키 중복: {unique_key}")
    monthly.to_parquet(OUTPUTS / "bc_ccg_month_features.parquet", index=False)

    sum_cols = value_cols
    profile_keys = ["ccg_id", "sido_nm", "ccg_nm", "industry_code", "industry_name"]
    profile = monthly.groupby(profile_keys, as_index=False)[sum_cols].sum()
    profile["period_start"] = monthly.period_month.min()
    profile["period_end"] = monthly.period_month.max()
    month_counts = (
        monthly.groupby(profile_keys, as_index=False)["period_month"]
        .nunique()
        .rename(columns={"period_month": "n_months"})
    )
    profile = profile.merge(month_counts, on=profile_keys, how="left", validate="1:1")
    profile["female_share_personal_amt"] = safe_divide(profile.female_amt, profile.male_amt + profile.female_amt)
    profile["foreign_share_total_amt"] = safe_divide(profile.foreign_amt, profile.total_amt)
    profile["corporate_share_total_amt"] = safe_divide(profile.corporate_amt, profile.total_amt)
    profile["avg_ticket"] = safe_divide(profile.total_amt, profile.total_cnt)
    for age in "123456":
        profile[f"age_cd_{age}_share_personal_amt"] = safe_divide(
            profile[f"age_cd_{age}_amt"], profile.personal_amt
        )

    monthly_totals = monthly[profile_keys + ["period_month", "total_amt", "total_cnt"]].copy()
    ordered_months = sorted(monthly_totals.period_month.unique())
    early, recent = set(ordered_months[:3]), set(ordered_months[-3:])
    early_stats = (
        monthly_totals.loc[monthly_totals.period_month.isin(early)]
        .groupby(profile_keys, as_index=False)[["total_amt", "total_cnt"]]
        .mean()
        .rename(columns={
            "total_amt": "total_amt_early_3m_mean",
            "total_cnt": "total_cnt_early_3m_mean",
        })
    )
    recent_stats = (
        monthly_totals.loc[monthly_totals.period_month.isin(recent)]
        .groupby(profile_keys, as_index=False)[["total_amt", "total_cnt"]]
        .mean()
        .rename(columns={
            "total_amt": "total_amt_recent_3m_mean",
            "total_cnt": "total_cnt_recent_3m_mean",
        })
    )
    profile = profile.merge(
        early_stats, on=profile_keys, how="left", validate="1:1"
    )
    profile = profile.merge(
        recent_stats, on=profile_keys, how="left", validate="1:1"
    )
    profile["amt_recent_vs_early_growth"] = safe_divide(
        profile["total_amt_recent_3m_mean"], profile["total_amt_early_3m_mean"]
    ) - 1
    profile["cnt_recent_vs_early_growth"] = safe_divide(
        profile["total_cnt_recent_3m_mean"], profile["total_cnt_early_3m_mean"]
    ) - 1
    profile["model_eligible"] = profile.n_months.eq(len(ordered_months))
    profile = profile.sort_values(["ccg_id", "industry_code"])
    if profile.duplicated(["ccg_id", "industry_code"]).any():
        raise SystemExit("BC 반기 프로필 키 중복")
    profile.to_parquet(OUTPUTS / "bc_ccg_profile_2026h1.parquet", index=False)
    profile.loc[profile.industry_code.eq("8301")].to_parquet(
        OUTPUTS / "bc_bakery_ccg_profile_2026h1.parquet", index=False
    )
    return monthly, unmatched


def one_service(frame: pd.DataFrame, code: str, prefix: str, columns: list[str]) -> pd.DataFrame:
    part = frame.loc[frame.SVC_INDUTY_CD.astype(str).eq(code), ["TRDAR_CD", *columns]].copy()
    part["TRDAR_CD"] = part["TRDAR_CD"].astype(str)
    part = part.rename(columns={c: f"{prefix}_{c.lower()}" for c in columns})
    if part.duplicated("TRDAR_CD").any():
        raise SystemExit(f"서울시 {prefix} 상권코드 중복")
    return part


def build_area_base() -> pd.DataFrame:
    area = read_jsonl(AREA_PATH)
    store = read_jsonl(STORE_PATH)
    sales = read_jsonl(SALES_PATH)
    for frame in [area, store, sales]:
        frame["TRDAR_CD"] = frame["TRDAR_CD"].astype(str)
    store["SVC_INDUTY_CD"] = store["SVC_INDUTY_CD"].astype(str)
    sales["SVC_INDUTY_CD"] = sales["SVC_INDUTY_CD"].astype(str)

    store_cols = [
        "SIMILR_INDUTY_STOR_CO", "STOR_CO", "FRC_STOR_CO", "OPBIZ_RT",
        "OPBIZ_STOR_CO", "CLSBIZ_RT", "CLSBIZ_STOR_CO",
    ]
    sales_cols = [c for c in sales.columns if c.endswith("_AMT") or c.endswith("_CO")]
    bakery_store = one_service(store, "CS100005", "bakery", store_cols)
    coffee_store = one_service(store, "CS100010", "coffee", store_cols)
    bakery_sales = one_service(sales, "CS100005", "bakery", sales_cols)
    coffee_sales = one_service(sales, "CS100010", "coffee", sales_cols)

    out = area.rename(columns={
        "TRDAR_CD": "area_id", "TRDAR_CD_NM": "area_name",
        "TRDAR_SE_CD": "area_type_code", "TRDAR_SE_CD_NM": "area_type_name",
        "SIGNGU_CD": "ccg_id", "SIGNGU_CD_NM": "ccg_nm",
        "ADSTRD_CD": "admin_dong_id", "ADSTRD_CD_NM": "admin_dong_nm",
        "XCNTS_VALUE": "centroid_x_epsg5181", "YDNTS_VALUE": "centroid_y_epsg5181",
        "RELM_AR": "area_geometry_raw",
    }).copy()
    out["area_id"] = out.area_id.astype(str)
    out["ccg_id"] = (
        out.ccg_id.map(canonical_text)
        .str.replace(r"\.0$", "", regex=True)
        .map(lambda value: value.zfill(5) if value else "")
    )

    for feature in [bakery_store, coffee_store, bakery_sales, coffee_sales]:
        feature = feature.rename(columns={"TRDAR_CD": "area_id"})
        out = out.merge(feature, on="area_id", how="left", validate="1:1")

    bakery_sales_total = "bakery_thsmon_selng_amt"
    coffee_sales_total = "coffee_thsmon_selng_amt"
    out["bakery_store_observed"] = out["bakery_stor_co"].notna()
    out["bakery_sales_observed"] = out[bakery_sales_total].notna()
    out["coffee_store_observed"] = out["coffee_stor_co"].notna()
    out["coffee_sales_observed"] = out[coffee_sales_total].notna()

    numeric_prefixed = [c for c in out.columns if c.startswith("bakery_") or c.startswith("coffee_")]
    observed_cols = [c for c in numeric_prefixed if c.endswith("_observed")]
    for col in numeric_prefixed:
        if col not in observed_cols:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    out["bakery_avg_ticket"] = safe_divide(out["bakery_thsmon_selng_amt"], out["bakery_thsmon_selng_co"])
    out["bakery_sales_per_store"] = safe_divide(out["bakery_thsmon_selng_amt"], out["bakery_stor_co"])
    out["bakery_txn_per_store"] = safe_divide(out["bakery_thsmon_selng_co"], out["bakery_stor_co"])
    out["bakery_franchise_store_share"] = safe_divide(
        out["bakery_frc_stor_co"],
        out["bakery_similr_induty_stor_co"],
    )
    out["coffee_avg_ticket"] = safe_divide(out["coffee_thsmon_selng_amt"], out["coffee_thsmon_selng_co"])
    out["coffee_sales_per_store"] = safe_divide(out["coffee_thsmon_selng_amt"], out["coffee_stor_co"])
    out["bakery_to_coffee_sales_ratio"] = safe_divide(out["bakery_thsmon_selng_amt"], out["coffee_thsmon_selng_amt"])

    total_bakery_amt = out["bakery_thsmon_selng_amt"]
    total_bakery_cnt = out["bakery_thsmon_selng_co"]
    share_sources = {
        "female_share_amt": "bakery_fml_selng_amt",
        "male_share_amt": "bakery_ml_selng_amt",
        "weekend_share_amt": "bakery_wkend_selng_amt",
        **{f"age_{age}_share_amt": f"bakery_agrde_{age}_selng_amt" for age in [10, 20, 30, 40, 50]},
        "age_60_above_share_amt": "bakery_agrde_60_above_selng_amt",
    }
    for suffix, source in share_sources.items():
        if source in out.columns:
            out[f"bakery_{suffix}"] = safe_divide(out[source], total_bakery_amt)
    if "bakery_wkend_selng_co" in out.columns:
        out["bakery_weekend_share_cnt"] = safe_divide(out["bakery_wkend_selng_co"], total_bakery_cnt)

    out["period_q"] = "20262"
    out["model_eligible"] = out["ccg_id"].ne("")
    out = out.sort_values("area_id")
    if out.duplicated("area_id").any():
        raise SystemExit("서울 상권 기본 특성의 area_id 중복")
    out.to_parquet(INTERMEDIATE / "area_base_features_20262.parquet", index=False)
    return out


def ratio_check(frame: pd.DataFrame) -> list[str]:
    bad = []
    share_cols = [c for c in frame if "share" in c and pd.api.types.is_numeric_dtype(frame[c])]
    for col in share_cols:
        values = frame[col].dropna()
        if ((values < -1e-9) | (values > 1 + 1e-9)).any():
            bad.append(col)
    return bad


def write_report(
    ccg_ref: pd.DataFrame,
    ambiguous_keys: list[tuple[str, str]],
    monthly: pd.DataFrame,
    unmatched: pd.DataFrame,
    area: pd.DataFrame,
) -> None:
    match_pairs = monthly[["sido_nm", "ccg_nm"]].drop_duplicates().shape[0]
    unmatched_pairs = len(unmatched)
    denom = match_pairs + unmatched_pairs
    match_rate = match_pairs / denom if denom else 0
    bad_ratios = ratio_check(monthly) + ratio_check(area)
    unmatched_lines = (
        "\n".join(f"  - {r.SIDO_NM} / {r.CCG_NM}" for r in unmatched.itertuples())
        if unmatched_pairs else "  - 없음"
    )
    report = f"""# DATA-02 2단계 품질 보고서

- 생성시각(UTC): `{datetime.now(timezone.utc).isoformat()}`
- BC 코드북: 성별 `1=남성, 2=여성, 3=외국인, x=법인`; 연령 `1~6`, `x=법인 및 외국인`

## 1. 전국 시군구 코드 연결

- 소진공 기반 시군구 기준표: {len(ccg_ref):,}행
- 모호한 명칭 키: {len(ambiguous_keys):,}개
- BC 지역명 연결 성공: {match_pairs:,}개
- BC 지역명 연결 실패: {unmatched_pairs:,}개
- 지역명 연결률: {match_rate:.2%}

연결 실패 지역:
{unmatched_lines}

## 2. BC 특성

- 월별 시군구×업종: {len(monthly):,}행
- 기간: {monthly.period_month.min()}~{monthly.period_month.max()}
- 업종 수: {monthly.industry_code.nunique():,}개
- 제과점 코드 8301 행: {(monthly.industry_code == '8301').sum():,}행
- 여성 비중 분모: 남성+여성 개인 이용금액
- 연령 비중 분모: 성별 1·2이면서 연령 1~6인 개인 이용금액
- 외국인·법인 비중 분모: 전체 이용금액

## 3. 서울 상권 기본 특성

- 전체 후보 상권: {len(area):,}개
- 제과점 점포 관측 상권: {int(area.bakery_store_observed.sum()):,}개
- 제과점 매출 관측 상권: {int(area.bakery_sales_observed.sum()):,}개
- 커피 점포 관측 상권: {int(area.coffee_store_observed.sum()):,}개
- 커피 매출 관측 상권: {int(area.coffee_sales_observed.sum()):,}개
- 시군구 코드 결측: {int(area.ccg_id.eq('').sum()):,}개

## 4. 검증

- BC 월별 키 중복: {int(monthly.duplicated(['period_month', 'ccg_id', 'industry_code']).sum()):,}행
- 서울 상권 ID 중복: {int(area.duplicated('area_id').sum()):,}행
- 범위를 벗어난 비중 컬럼: {bad_ratios if bad_ratios else '없음'}

## 5. 해석 주의

- BC는 월×시군구, 서울시는 분기×상권 자료이므로 DATA-02에서 BC 값을 상권별로 임의 배분하지 않습니다.
- `AGE_CD=1`과 `AGE_CD=2`의 명칭은 제공 코드북을 그대로 보존하며, 모델에는 코드별 비중으로 전달합니다.
- 서울시 매출 미관측과 실제 0을 구분하기 위해 `*_sales_observed`를 함께 제공합니다.
- 브랜드 기존 입점 여부와 점포 거리는 DATA-01을 결합하는 MODEL-01에서 계산합니다.
"""
    (REPORTS / "stage2_quality_report.md").write_text(report, encoding="utf-8")
    if match_rate < 0.95:
        raise SystemExit(
            f"BC 시군구 코드 연결률이 {match_rate:.2%}로 낮습니다. 보고서를 확인하세요."
        )
    if bad_ratios:
        raise SystemExit(f"비중 범위 검증 실패: {bad_ratios}")


def update_readme() -> None:
    path = BASE / "README.md"
    old = path.read_text(encoding="utf-8") if path.exists() else "# DATA-02\n"
    start = "<!-- STAGE2_METHOD_START -->"
    end = "<!-- STAGE2_METHOD_END -->"
    section = f"""{start}
## 2단계 방법론 확정

BC 원본의 실제 컬럼명 `TP_BUZ_NO`, `TP_BUZ_NM`, `amt`, `cnt`는 공식 레이아웃의 `TPBUZ_NO`, `TPBUZ_NM`, `AMT`, `CNT`로 표준화합니다. 성별은 `1=남성`, `2=여성`, `3=외국인`, `x=법인`으로 처리하며, 여성 비중은 외국인과 법인이 섞이지 않도록 남녀 개인 이용금액만 분모로 사용합니다. 연령 비중 역시 개인 고객의 코드 1~6만 분모에 포함하고 `x`는 제외합니다.

BC의 11개 업종은 모두 보존하여 향후 다른 외식 업종으로 확장할 수 있게 하고, 현재 제과점 파일럿은 `TPBUZ_NO=8301`로 별도 출력합니다. 서울시 제과점은 `CS100005`, 소진공의 공간 경쟁점은 3단계에서 `빵/도넛`으로 정의합니다. `카페`와 `떡/한과`는 동일 업종으로 합치지 않으며, 커피·음료(`CS100010`)만 보완 수요 지표로 분리합니다.

BC 자료는 월별 시군구 단위이고 서울시 자료는 분기별 상권 단위이므로, 시군구 소비액을 상권에 비례 배분하지 않습니다. 이 임의 배분은 가짜 정밀도를 만들기 때문입니다. 대신 전국 시군구 소비 프로필과 서울 상권 기본 특성을 각각 유지하고 MODEL-01이 계층적으로 결합합니다. 전국 시군구 코드는 DATA-01과 같은 소진공 `시군구코드`에서 생성하여 결합 기준을 통일합니다.

원시 합계·관측 여부·비율을 함께 남깁니다. 로그 변환, 표준화, 결측치 대체는 학습·평가 분할 이후 MODEL-01에서 수행하여 데이터 누수를 막습니다. 서울시 매출 행이 없는 경우도 실제 0과 구별하도록 `*_sales_observed`를 유지합니다.
{end}
"""
    if start in old and end in old:
        old = old.split(start)[0] + section + old.split(end, 1)[1]
    else:
        old = old.rstrip() + "\n\n" + section
    path.write_text(old.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    persist_confirmed_codebook()
    print("[2/4-1] 소진공 전국 시군구 코드 기준표 생성")
    ccg_ref, ambiguous = build_ccg_reference()
    print("[2/4-2] BC 월별·반기 시군구 소비 특성 생성")
    monthly, unmatched = prepare_bc(ccg_ref)
    print("[2/4-3] 서울 제과점·커피 상권 기본 특성 생성")
    area = build_area_base()
    print("[2/4-4] 품질 검증과 README 방법론 기록")
    write_report(ccg_ref, ambiguous, monthly, unmatched, area)
    update_readme()
    print("[DATA-02 2/4 완료]")
    print(f"보고서: {REPORTS / 'stage2_quality_report.md'}")


if __name__ == "__main__":
    main()
