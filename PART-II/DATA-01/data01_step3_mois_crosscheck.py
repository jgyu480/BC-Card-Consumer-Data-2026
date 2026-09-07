"""
DATA-01 : 3단계 (행안부 식품·휴게음식점 데이터로 주소/영업상태 교차검증)

주의: 행안부 데이터(rest_cafes_seoul_address.jsonl)는 서울 소재 업소만 포함되어 있음.
      -> 서울 외 지역 매장은 이 단계의 교차검증 대상이 아니며, mois_matched=False,
         mois_note="행안부 데이터가 서울만 포함 -> 교차검증 대상 아님" 으로 표시한다.

매칭 전략:
1) 주소 정규화 (쉼표 이후 건물명/층수 정보 절단, 공백/특수문자 제거)
2) 정규화된 주소가 정확히 일치하거나, 서로 포함관계면 주소 매칭 성공으로 간주
3) 주소만으로는 같은 건물 내 여러 점포를 구분 못할 위험이 있으므로,
   상호명(store_name_std)과 행안부 상호명(BPLC_NM)도 함께 대조하여
   "주소 일치 + 이름 일치(또는 포함)"인 경우만 최종 매칭으로 인정
4) 매칭 성공 시 행안부의 영업상태(SALS_STTS_NM)를 가져와 폐업 여부 확인

입력:
- store_match_candidates.parquet (1~2단계 + 상호/지점명 통일 결과)
- Datasets/b. External Public Data/01_mois_rest_cafes/rest_cafes_seoul_address.jsonl

출력:
- store_match_with_status.parquet (mois_matched, business_status, mois_note 컬럼 추가)
"""

import re
import json
import pandas as pd

MOIS_PATH = "Datasets/b. External Public Data/01_mois_rest_cafes/rest_cafes_seoul_address.jsonl"
INPUT_PATH = "store_match_candidates.parquet"
OUTPUT_PATH = "store_match_with_status.parquet"


def normalize_name(name: str) -> str:
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return ""
    s = str(name).strip()
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[^0-9A-Za-z가-힣]", "", s)
    return s.lower()


def normalize_address(addr: str) -> str:
    """쉼표 이후(건물명/층/호수 등 상세정보)는 잘라내고, 공백/특수문자 제거."""
    if addr is None or (isinstance(addr, float) and pd.isna(addr)):
        return ""
    s = str(addr).strip()
    s = s.split(",")[0]  # 쉼표 이전까지만 사용
    s = re.sub(r"[^0-9A-Za-z가-힣]", "", s)
    return s


def load_mois_data(path: str) -> pd.DataFrame:
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    df = pd.DataFrame(records)

    df["mois_name_std"] = df["BPLC_NM"].apply(normalize_name)
    df["mois_lotno_addr_std"] = df["LOTNO_ADDR"].apply(normalize_address)
    df["mois_road_addr_std"] = df["ROAD_NM_ADDR"].apply(normalize_address)

    return df[[
        "BPLC_NM", "mois_name_std",
        "LOTNO_ADDR", "ROAD_NM_ADDR", "mois_lotno_addr_std", "mois_road_addr_std",
        "SALS_STTS_NM", "DTL_SALS_STTS_NM", "MNG_NO",
    ]]


def addresses_match(a: str, b: str) -> bool:
    if not a or not b:
        return False
    return a == b or a in b or b in a


def names_match(a: str, b: str) -> bool:
    if not a or not b:
        return False
    return a == b or a in b or b in a


def cross_check_with_mois(stores_df: pd.DataFrame, mois_df: pd.DataFrame) -> pd.DataFrame:
    stores_df = stores_df.copy()
    stores_df["store_lotno_addr_std"] = stores_df["지번주소"].apply(normalize_address)
    stores_df["store_road_addr_std"] = stores_df["도로명주소"].apply(normalize_address) \
        if "도로명주소" in stores_df.columns else ""

    stores_df["mois_matched"] = False
    stores_df["business_status"] = None
    stores_df["mois_note"] = None

    seoul_mask = stores_df["시도명"] == "서울특별시"
    non_seoul_idx = stores_df[~seoul_mask].index
    stores_df.loc[non_seoul_idx, "mois_note"] = "행안부 데이터가 서울만 포함 -> 교차검증 대상 아님"

    seoul_idx = stores_df[seoul_mask].index
    matched_count = 0

    for idx in seoul_idx:
        row = stores_df.loc[idx]
        store_name = row.get("store_name_std", "")
        store_lot = row.get("store_lotno_addr_std", "")
        store_road = row.get("store_road_addr_std", "")

        candidates = mois_df[
            mois_df["mois_lotno_addr_std"].apply(lambda x: addresses_match(store_lot, x)) |
            mois_df["mois_road_addr_std"].apply(lambda x: addresses_match(store_road, x))
        ]

        if candidates.empty:
            stores_df.at[idx, "mois_note"] = "주소 일치하는 행안부 레코드 없음"
            continue

        name_matched = candidates[
            candidates["mois_name_std"].apply(lambda x: names_match(store_name, x))
        ]

        if not name_matched.empty:
            best = name_matched.iloc[0]
            stores_df.at[idx, "mois_matched"] = True
            stores_df.at[idx, "business_status"] = best["SALS_STTS_NM"]
            stores_df.at[idx, "mois_note"] = "주소+상호명 일치"
            matched_count += 1
        else:
            stores_df.at[idx, "mois_note"] = "주소는 일치하나 상호명 불일치 (같은 건물 내 다른 업소로 추정)"

    print(f"  -> 서울 소재 매장 {len(seoul_idx)}건 중 {matched_count}건 행안부 교차검증 성공")

    return stores_df


if __name__ == "__main__":
    print("store_match_candidates.parquet 로딩...")
    stores_df = pd.read_parquet(INPUT_PATH)
    print(f"  -> {len(stores_df)}건 로딩 완료")

    print("\n행안부 식품·휴게음식점 데이터 로딩 (서울)...")
    mois_df = load_mois_data(MOIS_PATH)
    print(f"  -> {len(mois_df)}건 로딩 완료")

    print("\n주소/상호명 교차검증 수행...")
    result_df = cross_check_with_mois(stores_df, mois_df)

    print("\n영업상태 분포 (매칭 성공 건만):")
    print(result_df[result_df["mois_matched"]]["business_status"].value_counts())

    # 행안부 교차검증으로 "폐업"이 확인된 건은 최종 제외 처리
    # (기존 excluded/exclusion_reason 컬럼이 1~2단계에서 이미 있으므로 이어서 갱신)
    closed_mask = result_df["business_status"] == "폐업"
    result_df.loc[closed_mask, "excluded"] = True
    result_df.loc[closed_mask, "exclusion_reason"] = "행안부 교차검증 결과 폐업 확인됨"
    print(f"\n행안부 교차검증으로 폐업 확인되어 추가 제외: {closed_mask.sum()}건")
    print(f"누적 제외 건수(1~3단계 전체): {result_df['excluded'].sum()}건")

    result_df.to_parquet(OUTPUT_PATH, index=False)
    print(f"\n-> {OUTPUT_PATH} 저장 완료")
