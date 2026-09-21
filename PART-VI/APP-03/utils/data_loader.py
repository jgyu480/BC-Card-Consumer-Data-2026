import json
from pathlib import Path
from functools import lru_cache

# 이 파일(utils/data_loader.py) 기준 상위 폴더 = 프로젝트 루트(APP-01/)
BASE_DIR = Path(__file__).resolve().parent.parent


def load_json(filename):
    """프로젝트 루트에 있는 JSON 파일을 그대로 읽는다.
    (README 안내대로 result_schema.json, mock_recommendations.json은
    이동하지 않고 원래 위치에서 참조만 한다)
    """
    path = BASE_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_recommendations():
    """결과 JSON을 딱 한 번만 디스크에서 읽고 메모리에 캐싱한다.
    브랜드/탭 전환마다 여러 콜백에서 각각 이 함수를 호출하는데, 캐싱 전엔
    클릭 한 번에 같은(수 MB짜리) 파일을 3~4번씩 다시 읽고 파싱하고 있었음
    — 이게 체감 로딩 지연의 주요 원인이었을 가능성이 높음.

    주의: 서버를 켜둔 채로 result_v3.json을 다시 생성해도(파이프라인
    스크립트 재실행) 이 캐시 때문에 반영이 안 됨 — 데이터 갱신 후에는
    Dash 서버를 재시작해야 함.
    """
    return load_json("outputs/result_v3.json")


def load_schema():
    return load_json("result_schema.json")


def get_brand_options(data):
    """브랜드 선택 드롭다운에 넣을 [{label, value}, ...] 형태로 변환.
    brand_name 가나다순 정렬 (한글은 유니코드 순서가 자모 순서와 일치해서
    별도 로케일 설정 없이 sorted()만으로 정확히 가나다순이 됨)."""
    brands = sorted(data.get("brands", []), key=lambda b: b["brand_name"])
    return [
        {"label": b["brand_name"], "value": b["brand_id"]}
        for b in brands
    ]


def get_brand_by_id(data, brand_id):
    """brand_id로 특정 브랜드의 전체 데이터를 찾는다"""
    for b in data.get("brands", []):
        if b["brand_id"] == brand_id:
            return b
    return None