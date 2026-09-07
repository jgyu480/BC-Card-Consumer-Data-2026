"""
DATA-01 : 1단계(브랜드 표준화) + 2단계(점포 후보 매칭) - v2

v1 대비 변경사항 (실제 데이터 검토 중 발견된 문제 반영):
1. "포함관계(contains)"를 "접두어(prefix)"로 좁힘
   -> 브랜드명이 상호명 맨 앞에 오는 경우만 medium으로 인정
   -> "오복호두"(브랜드 아님), "아더베이크샵", "언더베이크" 같이
      브랜드명 앞에 다른 글자가 붙어 의미가 달라지는 오탐을 자동 차단
2. 브랜드명이 상호명 중간/뒤에 있는 경우는 별도 신뢰도(low/review_needed)로 분리
   -> "대명브레댄코고속터미널역점", "파리크라상파리바게뜨~" 처럼 실제 매장일 수도 있어
      완전히 버리지 않되, 사람이 검토하도록 남김
3. 브랜드명이 2글자 이하로 너무 짧으면 이 영역(비-접두어 포함관계) 매칭에서 제외
   -> "라미"가 "동그라미", "쉐라미", "그라미" 등에 우연히 걸리는 문제 원천 차단
4. 명시적 제외/검토 규칙 추가
   -> "배송비" 키워드 포함 상호명은 실제 매장이 아닌 것으로 보고 자동 제외
   -> 사용자가 직접 확인한 존재하지 않는 매장("심봉사도로케통닭")은 확정 제외
   -> 슬로건/문구로 의심되나 존재 여부가 확정되지 않은 것들은 review_needed로 표시만

실행 전 확인:
- Datasets/b. External Public Data/03_ftc_franchise_brands/ftc_brand_list.jsonl
- Datasets/b. External Public Data/02_small_business_stores/소상공인시장진흥공단_상가(상권)정보_20260630/
    소상공인시장진흥공단_상가(상권)정보_*.csv  (전국 17개 시도 파일)

출력:
- brand_name_mapping.csv          (브랜드 표준화 대응표)
- store_match_candidates.parquet  (점포 매칭 결과, 신뢰도 + 제외사유 포함)
- store_match_review_needed.csv   (사람이 직접 검토해야 할 목록만 따로 추출)
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

# 브랜드명 변형(variant)이 이 길이 미만이면, 비-접두어(포함관계) 매칭에는 아예 사용하지 않음
# (예: "라미"(2자)가 "동그라미","쉐라미" 등에 우연히 걸리는 문제 방지)
MIN_VARIANT_LEN_FOR_NONPREFIX = 4

# 브랜드명 변형이 이 길이 미만이면, 접두어 일치(medium)라 해도 "짧은 브랜드명" 전용 등급으로 낮춤
# -> 브랜드명이 짧으면(예: "라미") 접두어가 맞아도 완전 무관한 개인 상호("라미제과")와
#    우연히 같은 음절로 시작할 뿐인 경우를 구분할 수 없기 때문. 별도 등급으로 모아서 사람이 검토.
MIN_BRAND_LEN_FOR_CONFIDENT_MEDIUM = 4

# 실제 매장이 아닌 것으로 보고 자동 제외할 키워드
AUTO_EXCLUDE_KEYWORDS = ["배송비"]

# 사용자가 직접 확인하여 "실제로 존재하지 않는 매장"으로 판명된 상호명 (원본 그대로, 정규화 전)
CONFIRMED_NONEXISTENT_STORES = [
    "심봉사도로케통닭",
]

# 슬로건/문구로 의심되나 존재 여부가 확정되지 않은 것들 -> 자동 제외하지 않고 검토 표시만
SUSPECTED_SLOGAN_STORES = [
    "심봉사도로케흥부가기가막혀",
    "포르피노여섯번째이야기",
    "포르피노세번째이야기",
    "심봉사도로케카페베트남",
]

# 브랜드명이 짧아(4자 미만) medium_short_brand로 분류됐지만,
# 실제로 검토해보니 흔한 일반 단어가 아니라 고유한 조어라 오탐 위험이 낮다고 확인된 브랜드
# -> medium으로 승격 (검토 대상에서 제외)
CONFIRMED_SAFE_SHORT_BRANDS = [
    "던킨/던킨도너츠",
    "복호두",
]


# ---------------------------------------------------------
# 이름 정규화 함수
# ---------------------------------------------------------
def normalize_name(name: str) -> str:
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return ""
    s = str(name).strip()
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[^0-9A-Za-z가-힣]", "", s)
    return s.lower()


def normalize_name_with_alias(name: str):
    """
    괄호 제거 전/후 두 버전을 모두 반환 (예: "티엠티피자(TMT피자)" -> ["티엠티피자", "tmt피자"])
    "/"로 여러 이름이 나열된 경우(예: "던킨/던킨도너츠") 각각을 별도 variant로 분리.
      -> 정규화 과정에서 "/"가 그냥 제거되면 "던킨던킨도너츠"라는 실존하지 않는 문자열이 되어
         실제 매장(상호명 "던킨" 또는 "던킨도너츠")과 전혀 매칭이 안 되는 문제를 방지.
    """
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return []
    raw = str(name).strip()
    variants = set()

    no_paren = re.sub(r"\(.*?\)", "", raw)
    variants.add(normalize_name(no_paren))

    paren_content = re.findall(r"\((.*?)\)", raw)
    for p in paren_content:
        variants.add(normalize_name(p))

    if "/" in raw:
        for part in raw.split("/"):
            part_no_paren = re.sub(r"\(.*?\)", "", part)
            variants.add(normalize_name(part_no_paren))

    return sorted(v for v in variants if v)


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
    df = df[df["indutyMlsfcNm"] == FTC_BAKERY_CATEGORY].copy()

    df["brand_id"] = df["brandMnno"]
    df["brand_name_raw"] = df["brandNm"]
    df["brand_name_variants"] = df["brand_name_raw"].apply(normalize_name_with_alias)

    return df[["brand_id", "brand_name_raw", "brand_name_variants", "indutyMlsfcNm"]]


# ---------------------------------------------------------
# 2단계: 소상공인 상가정보에서 점포 후보 매칭
# ---------------------------------------------------------
def load_sbiz_stores(sbiz_dir: str) -> pd.DataFrame:
    csv_files = glob.glob(f"{sbiz_dir}/*.csv")
    if not csv_files:
        raise FileNotFoundError(f"csv 파일을 찾을 수 없습니다: {sbiz_dir}")

    dfs = []
    for fp in csv_files:
        usecols = [
            "상가업소번호", "상호명", "지점명",
            "상권업종대분류명", "상권업종중분류명", "상권업종소분류명",
            "시도명", "시군구코드", "시군구명", "행정동명", "법정동명",
            "지번주소", "도로명주소",
            "경도", "위도",
        ]
        df = pd.read_csv(fp, usecols=usecols, encoding="utf-8", dtype=str)
        dfs.append(df)

    full_df = pd.concat(dfs, ignore_index=True)
    full_df = full_df[full_df["상권업종소분류명"] == SBIZ_BAKERY_CATEGORY].copy()
    full_df["store_name_normalized"] = full_df["상호명"].apply(normalize_name)

    return full_df


# ---------------------------------------------------------
# 매칭 로직
#   1) 완전일치 -> high
#   2) 접두어 일치(브랜드명으로 시작) -> medium
#   3) 비-접두어 포함관계(브랜드명이 중간/뒤에 위치) -> low (review_needed)
#      단, 브랜드명 변형 길이가 MIN_VARIANT_LEN_FOR_NONPREFIX 미만이면 아예 매칭 대상에서 제외
# ---------------------------------------------------------
def match_stores_to_brands(brands_df: pd.DataFrame, stores_df: pd.DataFrame) -> pd.DataFrame:
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

    remaining = stores_df[~stores_df["상가업소번호"].isin(matched_store_ids)].copy()

    # --- 접두어 일치 (medium) + 비-접두어 포함관계 (low) ---
    prefix_rows = []
    nonprefix_rows = []

    for _, brand_row in brand_variants_df.iterrows():
        variant = brand_row["variant"]
        if len(variant) < 2:
            continue  # 1글자짜리는 너무 위험해서 아예 제외

        hits = remaining[remaining["store_name_normalized"].str.contains(
            re.escape(variant), na=False
        )]

        for _, store_row in hits.iterrows():
            store_name_norm = store_row["store_name_normalized"]
            base = {
                **store_row.to_dict(),
                "brand_id": brand_row["brand_id"],
                "brand_name_raw": brand_row["brand_name_raw"],
                "variant": variant,
            }

            if store_name_norm.startswith(variant):
                # 브랜드명으로 시작 -> 접두어 일치
                # 단, 브랜드명 자체가 너무 짧으면(예: "라미") 완전 무관한 개인 상호와
                # 우연히 같은 음절로 시작할 뿐인지 구분이 안 되므로 별도 등급으로 분리
                if len(variant) < MIN_BRAND_LEN_FOR_CONFIDENT_MEDIUM:
                    prefix_rows.append({
                        **base,
                        "match_method": "prefix_short_brand",
                        "match_confidence": "medium_short_brand",
                    })
                else:
                    prefix_rows.append({
                        **base,
                        "match_method": "prefix",
                        "match_confidence": "medium",
                    })
            else:
                # 브랜드명이 중간/뒤에 위치 -> 비-접두어 포함관계
                # 브랜드명 변형이 너무 짧으면(2~3자) 오탐 위험이 커서 아예 후보에서 제외
                if len(variant) < MIN_VARIANT_LEN_FOR_NONPREFIX:
                    continue
                nonprefix_rows.append({
                    **base,
                    "match_method": "contains_nonprefix",
                    "match_confidence": "low",
                })

    if prefix_rows:
        prefix_df = pd.DataFrame(prefix_rows)
        matches.append(prefix_df)
        matched_store_ids |= set(prefix_df["상가업소번호"])

    if nonprefix_rows:
        nonprefix_df = pd.DataFrame(nonprefix_rows)
        matches.append(nonprefix_df)
        matched_store_ids |= set(nonprefix_df["상가업소번호"])

    result = pd.concat(matches, ignore_index=True)

    # 한 점포가 여러 variant(예: 괄호 안팎 버전)로 동시에 매칭될 경우,
    # 신뢰도가 가장 높은 매칭만 남기고 나머지는 제거한다.
    # (신뢰도 순서를 명시적으로 고정하지 않으면, pandas 내부 정렬 상태에 따라
    #  어떤 매칭이 남을지 실행마다 달라질 위험이 있어 재현성 문제가 생긴다)
    confidence_priority = {"high": 0, "medium": 1, "medium_short_brand": 2, "low": 3}
    result["_priority"] = result["match_confidence"].map(confidence_priority)
    result = result.sort_values(["상가업소번호", "brand_id", "_priority"])
    result = result.drop_duplicates(subset=["상가업소번호", "brand_id"], keep="first")
    result = result.drop(columns=["_priority"]).reset_index(drop=True)

    return result


# ---------------------------------------------------------
# 제외/검토 플래그 부여
# ---------------------------------------------------------
def apply_exclusion_flags(result_df: pd.DataFrame) -> pd.DataFrame:
    result_df = result_df.copy()
    result_df["excluded"] = False
    result_df["exclusion_reason"] = None
    result_df["review_needed"] = False
    result_df["review_reason"] = None

    # 1) 배송비 등 자동 제외 키워드
    for kw in AUTO_EXCLUDE_KEYWORDS:
        mask = result_df["상호명"].str.contains(kw, na=False)
        result_df.loc[mask, "excluded"] = True
        result_df.loc[mask, "exclusion_reason"] = f"실제 매장이 아닌 것으로 추정 (상호명에 '{kw}' 포함)"

    # 2) 사용자가 직접 확인한 실존하지 않는 매장 -> 확정 제외
    mask = result_df["상호명"].isin(CONFIRMED_NONEXISTENT_STORES)
    result_df.loc[mask, "excluded"] = True
    result_df.loc[mask, "exclusion_reason"] = "실제 매장 확인 불가 (수동 검증 결과 비실존)"

    # 3) 슬로건/문구 의심 -> 자동 제외하지 않고 검토 표시만
    mask = result_df["상호명"].isin(SUSPECTED_SLOGAN_STORES)
    result_df.loc[mask, "review_needed"] = True
    result_df.loc[mask, "review_reason"] = "상호명이 슬로건/문구 또는 지명이 아닌 단어를 포함, 실존 여부 미확정"

    # 4) match_confidence가 low(비-접두어 포함관계)인 것은 전부 검토 대상
    mask = result_df["match_confidence"] == "low"
    result_df.loc[mask & ~result_df["review_needed"], "review_needed"] = True
    result_df.loc[mask & (result_df["review_reason"].isna()), "review_reason"] = \
        "브랜드명이 상호명 맨 앞이 아닌 중간/뒤에 위치 (접두어 불일치)"

    # 5) match_confidence가 medium_short_brand(짧은 브랜드명의 접두어 일치)도 검토 대상
    #    -> 접두어는 맞지만 브랜드명 자체가 짧아 완전 무관한 개인 상호와 우연히
    #       같은 글자로 시작할 뿐인 케이스를 배제하지 못하므로, 사람이 실제 프랜차이즈
    #       매장이 맞는지 확인 필요
    mask = result_df["match_confidence"] == "medium_short_brand"
    result_df.loc[mask & ~result_df["review_needed"], "review_needed"] = True
    result_df.loc[mask & (result_df["review_reason"].isna()), "review_reason"] = \
        "브랜드명이 짧아(4자 미만) 접두어가 일치해도 동명의 무관한 개인 상호일 가능성 있음"

    # 6) 검토 결과 "흔한 단어가 아니라 고유 조어라 오탐 위험이 낮다"고 확인된 짧은 브랜드는
    #    medium으로 승격하고 검토 플래그 해제
    mask = result_df["brand_name_raw"].isin(CONFIRMED_SAFE_SHORT_BRANDS) & \
           (result_df["match_confidence"] == "medium_short_brand")
    result_df.loc[mask, "match_confidence"] = "medium"
    result_df.loc[mask, "match_method"] = "prefix_short_brand_confirmed_safe"
    result_df.loc[mask, "review_needed"] = False
    result_df.loc[mask, "review_reason"] = None

    return result_df


# ---------------------------------------------------------
# 상호명 + 지점명 통일
#   - store_name_raw : 사람이 읽기 좋은 원본 형태 (상호명 + 지점명, 지점명 있을 때만 결합)
#   - store_name_std : store_name_raw를 정규화한 버전 (공백/특수문자 제거, 소문자 통일)
#     -> 상호명 자체에 이미 지점 정보가 포함된 경우("파리바게뜨수지구청역점", 지점명 없음)와
#        상호명/지점명이 분리된 경우("쥬씨&고망고" + "서울숲점")를 모두 하나의 형태로 통일한다.
# ---------------------------------------------------------
def finalize_store_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    def combine(row):
        name = str(row["상호명"]).strip() if pd.notna(row["상호명"]) else ""
        branch = str(row["지점명"]).strip() if pd.notna(row["지점명"]) else ""
        if branch and branch not in name:
            return f"{name} {branch}"
        return name

    df["store_name_raw"] = df.apply(combine, axis=1)
    df["store_name_std"] = df["store_name_raw"].apply(normalize_name)
    return df


# ---------------------------------------------------------
# 메인 실행
# ---------------------------------------------------------
if __name__ == "__main__":
    print("1단계: 공정위 브랜드 목록 로딩 및 표준화...")
    brands_df = load_ftc_brands(FTC_PATH)
    print(f"  -> 베이커리 브랜드 {len(brands_df)}개 확인")

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
    print(f"  -> 매칭 결과(제외/검토 반영 전) {len(result_df)}건")
    print(result_df["match_confidence"].value_counts())

    print("\n제외/검토 플래그 적용...")
    result_df = apply_exclusion_flags(result_df)
    print(f"  -> 자동 제외: {result_df['excluded'].sum()}건")
    print(f"  -> 검토 필요: {result_df['review_needed'].sum()}건")

    result_df.to_parquet("store_match_candidates.parquet", index=False)
    print("\n-> store_match_candidates.parquet 저장 완료")

    review_df = result_df[result_df["review_needed"]].sort_values("brand_name_raw")
    review_df[[
        "brand_name_raw", "상호명", "지점명", "시도명", "시군구명",
        "match_method", "match_confidence", "review_reason"
    ]].to_csv("store_match_review_needed.csv", index=False, encoding="utf-8-sig")
    print(f"-> store_match_review_needed.csv 저장 완료 ({len(review_df)}건)")

    print("\n상호명/지점명 통일...")
    result_df = finalize_store_names(result_df)
    result_df.to_parquet("store_match_candidates.parquet", index=False)
    print("  -> store_name_raw, store_name_std 컬럼 추가 완료 (store_match_candidates.parquet 갱신)")

    print("\n최종 요약")
    print(f"  전체 매칭: {len(result_df)}건")
    print(f"  - high(완전일치): {(result_df['match_confidence']=='high').sum()}건")
    print(f"  - medium(접두어일치): {(result_df['match_confidence']=='medium').sum()}건")
    print(f"  - medium_short_brand(짧은 브랜드명 접두어, 검토필요): {(result_df['match_confidence']=='medium_short_brand').sum()}건")
    print(f"  - low(비접두어, 검토필요): {(result_df['match_confidence']=='low').sum()}건")
    print(f"  자동 제외: {result_df['excluded'].sum()}건")
