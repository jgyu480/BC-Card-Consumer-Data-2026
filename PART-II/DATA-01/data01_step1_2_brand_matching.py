"""
DATA-01 : 1단계(브랜드 표준화) + 2단계(점포 후보 매칭)

실행 전 확인:
- Datasets/b. External Public Data/03_ftc_franchise_brands/ftc_brand_list.jsonl
- Datasets/b. External Public Data/02_small_business_stores/소상공인시장진흥공단_상가(상권)정보_20260630/
    소상공인시장진흥공단_상가(상권)정보_*.csv  (전국 17개 시도 파일)

출력:
- brand_name_mapping.csv   (브랜드 표준화 대응표)
- store_match_candidates.parquet  (점포 매칭 결과, 신뢰도 포함)
"""

import re
import glob
import json
import pandas as pd

# ---------------------------------------------------------
# 경로 설정 (본인 로컬 경로에 맞게 수정)
# ---------------------------------------------------------
BASE_DIR = "Datasets/b. External Public Data"
FTC_PATH = f"{BASE_DIR}/03_ftc_franchise_brands/ftc_brand_list.jsonl"
SBIZ_DIR = f"{BASE_DIR}/02_small_business_stores/소상공인시장진흥공단_상가(상권)정보_20260630"

# 업종 카테고리명 (데이터셋마다 다름 — 확인 완료된 값)
FTC_BAKERY_CATEGORY = "제과제빵"
SBIZ_BAKERY_CATEGORY = "빵/도넛"


# ---------------------------------------------------------
# 이름 정규화 함수
# ---------------------------------------------------------
def normalize_name(name: str) -> str:
    """
    브랜드명/상호명을 비교 가능한 형태로 표준화한다.
    - None/NaN -> 빈 문자열
    - 앞뒤 공백 제거
    - 괄호와 괄호 안 내용 제거 (예: "티엠티피자(TMT피자)" -> "티엠티피자")
      주의: 괄호 안에 실제 브랜드 별칭이 들어있는 경우도 있어
            제거 전/후 값을 모두 후보로 남기고 싶다면 별도 처리 필요.
            여기서는 우선 괄호 제거 버전을 기본 정규화 결과로 사용.
    - 특수문자/공백 제거
    - 소문자 변환 (영문 대비)
    """
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return ""
    s = str(name).strip()
    # 괄호와 그 안의 내용 제거
    s = re.sub(r"\(.*?\)", "", s)
    # 한글, 영문, 숫자만 남기고 나머지(공백, 특수문자) 제거
    s = re.sub(r"[^0-9A-Za-z가-힣]", "", s)
    return s.lower()


def normalize_name_with_alias(name: str):
    """
    괄호 제거 전/후 두 버전을 모두 반환한다.
    예: "티엠티피자(TMT피자)" -> ["티엠티피자", "tmt피자"]
    브랜드명 매칭 시 둘 다 후보로 사용해 재현율을 높인다.
    """
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return []
    raw = str(name).strip()
    variants = set()

    # 괄호 제거 버전
    no_paren = re.sub(r"\(.*?\)", "", raw)
    variants.add(normalize_name(no_paren))

    # 괄호 안 내용만 추출한 버전 (별칭으로 쓰이는 경우 대비)
    paren_content = re.findall(r"\((.*?)\)", raw)
    for p in paren_content:
        variants.add(normalize_name(p))

    return [v for v in variants if v]  # 빈 문자열 제거


# ---------------------------------------------------------
# 1단계: 공정위 브랜드 목록 표준화
# ---------------------------------------------------------
def load_ftc_brands(path: str) -> pd.DataFrame:
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

    df = pd.DataFrame(records)

    # 베이커리(제과제빵) 업종만 필터링
    df = df[df["indutyMlsfcNm"] == FTC_BAKERY_CATEGORY].copy()

    # brand_id는 공정위 브랜드 고유번호를 그대로 사용
    df["brand_id"] = df["brandMnno"]
    df["brand_name_raw"] = df["brandNm"]

    # 정규화 (괄호 제거 버전 + 별칭 버전 모두 생성)
    df["brand_name_variants"] = df["brand_name_raw"].apply(normalize_name_with_alias)

    return df[["brand_id", "brand_name_raw", "brand_name_variants", "indutyMlsfcNm"]]


# ---------------------------------------------------------
# 2단계: 소상공인 상가정보에서 점포 후보 매칭
# ---------------------------------------------------------
def load_sbiz_stores(sbiz_dir: str) -> pd.DataFrame:
    """전국 17개 시도 csv를 모두 읽어 하나로 합친다."""
    csv_files = glob.glob(f"{sbiz_dir}/*.csv")
    if not csv_files:
        raise FileNotFoundError(f"csv 파일을 찾을 수 없습니다: {sbiz_dir}")

    dfs = []
    for fp in csv_files:
        # 대용량이므로 필요한 컬럼만 선택해서 읽는다
        usecols = [
            "상가업소번호", "상호명", "지점명",
            "상권업종대분류명", "상권업종중분류명", "상권업종소분류명",
            "시도명", "시군구명", "행정동명", "법정동명",
            "지번주소", "도로명주소",
            "경도", "위도",
        ]
        df = pd.read_csv(fp, usecols=usecols, encoding="utf-8", dtype=str)
        dfs.append(df)

    full_df = pd.concat(dfs, ignore_index=True)

    # 베이커리 업종만 필터링 (1차 후보군 축소 — 매칭 속도 향상 목적)
    full_df = full_df[full_df["상권업종소분류명"] == SBIZ_BAKERY_CATEGORY].copy()

    # 상호명만 정규화 대상으로 사용 (지점명은 원본 보존용으로만 따로 둠)
    full_df["store_name_normalized"] = full_df["상호명"].apply(normalize_name)

    return full_df


# ---------------------------------------------------------
# 매칭 로직 (완전일치 -> 포함관계 -> 나머지는 검토 대상으로 표시)
# ---------------------------------------------------------
def match_stores_to_brands(brands_df: pd.DataFrame, stores_df: pd.DataFrame) -> pd.DataFrame:
    """
    브랜드 하나당 여러 정규화 변형(variants)을 가질 수 있으므로,
    variants를 explode해서 brand_id : normalized_variant 1:N 매핑 테이블을 만든다.
    """
    brand_variant_rows = []
    for _, row in brands_df.iterrows():
        for variant in row["brand_name_variants"]:
            brand_variant_rows.append({
                "brand_id": row["brand_id"],
                "brand_name_raw": row["brand_name_raw"],
                "variant": variant,
            })
    brand_variants_df = pd.DataFrame(brand_variant_rows)

    matches = []

    # --- 완전일치 (high) ---
    exact = stores_df.merge(
        brand_variants_df,
        left_on="store_name_normalized",
        right_on="variant",
        how="inner",
    )
    exact["match_method"] = "exact"
    exact["match_confidence"] = "high"
    matches.append(exact)

    matched_store_ids = set(exact["상가업소번호"])

    # --- 포함관계 (medium): 완전일치로 안 잡힌 점포 중, 상호명이 브랜드명을 포함하는 경우 ---
    remaining = stores_df[~stores_df["상가업소번호"].isin(matched_store_ids)].copy()

    partial_rows = []
    # 브랜드 수가 한정적(베이커리만)이므로 이중 루프 허용 가능한 규모
    for _, brand_row in brand_variants_df.iterrows():
        variant = brand_row["variant"]
        if len(variant) < 2:
            # 너무 짧은 문자열은 오탐 위험이 커서 포함관계 매칭에서 제외
            continue
        hits = remaining[remaining["store_name_normalized"].str.contains(
            re.escape(variant), na=False
        )]
        for _, store_row in hits.iterrows():
            partial_rows.append({
                **store_row.to_dict(),
                "brand_id": brand_row["brand_id"],
                "brand_name_raw": brand_row["brand_name_raw"],
                "variant": variant,
                "match_method": "partial_contains",
                "match_confidence": "medium",
            })

    if partial_rows:
        partial_df = pd.DataFrame(partial_rows)
        matches.append(partial_df)
        matched_store_ids |= set(partial_df["상가업소번호"])

    result = pd.concat(matches, ignore_index=True)

    # 완전일치가 여러 브랜드와 중복 매칭될 가능성은 낮지만, 방어적으로 중복 제거
    result = result.drop_duplicates(subset=["상가업소번호", "brand_id"])

    return result


# ---------------------------------------------------------
# 메인 실행
# ---------------------------------------------------------
if __name__ == "__main__":
    print("1단계: 공정위 브랜드 목록 로딩 및 표준화...")
    brands_df = load_ftc_brands(FTC_PATH)
    print(f"  -> 베이커리 브랜드 {len(brands_df)}개 확인")

    # 브랜드명 대응표 저장 (문서 요구사항: brand_name_mapping.csv)
    mapping_rows = []
    for _, row in brands_df.iterrows():
        for variant in row["brand_name_variants"]:
            mapping_rows.append({
                "brand_id": row["brand_id"],
                "brand_name_raw": row["brand_name_raw"],
                "brand_name_std_variant": variant,
            })
    pd.DataFrame(mapping_rows).to_csv(
        "brand_name_mapping.csv", index=False, encoding="utf-8-sig"
    )
    print("  -> brand_name_mapping.csv 저장 완료")

    print("\n2단계: 소상공인 상가정보 로딩 (전국, 베이커리 업종만 필터)...")
    stores_df = load_sbiz_stores(SBIZ_DIR)
    print(f"  -> 전국 베이커리 업종 점포 {len(stores_df)}개 확인")

    print("\n브랜드-점포 매칭 수행...")
    result_df = match_stores_to_brands(brands_df, stores_df)
    print(f"  -> 매칭 결과 {len(result_df)}건")
    print(result_df["match_confidence"].value_counts())

    result_df.to_parquet("store_match_candidates.parquet", index=False)
    print("\n-> store_match_candidates.parquet 저장 완료")
