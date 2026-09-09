import json
from pathlib import Path

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


def load_recommendations():
    return load_json("mock_recommendations.json")


def load_schema():
    return load_json("result_schema.json")


def get_brand_options(data):
    """브랜드 선택 드롭다운에 넣을 [{label, value}, ...] 형태로 변환"""
    return [
        {"label": b["brand_name"], "value": b["brand_id"]}
        for b in data.get("brands", [])
    ]


def get_brand_by_id(data, brand_id):
    """brand_id로 특정 브랜드의 전체 데이터를 찾는다"""
    for b in data.get("brands", []):
        if b["brand_id"] == brand_id:
            return b
    return None
