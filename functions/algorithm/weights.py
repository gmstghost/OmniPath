"""
weights.py
6가지 이동성 프로필(휠체어, 유모차, 시각장애인, 고령자, 캐리어 소지자, 일시적 부상자)에 대해
간선(도로 구간)의 보행 환경 속성(경사도, 계단, 엘리베이터, 점자블록 유무)을
경로 탐색 비용(가중치)으로 환산한다.

Firestore의 edges 컬렉션 문서 형태 (예시):
{
  "from": "N01",
  "to": "N02",
  "distance": 42.0,          # 미터
  "slope": 3.5,               # 경사도(%). 완만한 구간은 0에 가깝다
  "has_stairs": false,
  "has_elevator": false,
  "has_braille_block": true
}
"""

from typing import Optional

# 프로필별 파라미터.
# - avoid_stairs: True면 계단 구간은 아예 통행 불가로 처리(엘리베이터 대체 경로가 없는 한)
# - stairs_penalty: 계단이 있지만 통행 자체는 가능한 프로필에 추가되는 비용
# - slope_penalty: 경사도 1%당 추가되는 비용 계수
# - elevator_factor: 엘리베이터가 있는 구간에 곱해지는 비용 배수(1.0 미만이면 우대)
# - missing_braille_penalty: 점자블록이 없는 구간에 추가되는 비용(시각장애인 전용)
PROFILES = {
    "wheelchair": {
        "label": "휠체어 이용자",
        "avoid_stairs": True,
        "stairs_penalty": 0.0,
        "slope_penalty": 4.0,
        "elevator_factor": 0.6,
        "missing_braille_penalty": 0.0,
    },
    "stroller": {
        "label": "유모차 이용자",
        "avoid_stairs": True,
        "stairs_penalty": 0.0,
        "slope_penalty": 3.0,
        "elevator_factor": 0.6,
        "missing_braille_penalty": 0.0,
    },
    "visually_impaired": {
        "label": "시각장애인",
        "avoid_stairs": False,
        "stairs_penalty": 2.0,
        "slope_penalty": 1.0,
        "elevator_factor": 0.9,
        "missing_braille_penalty": 6.0,
    },
    "elderly": {
        "label": "고령자",
        "avoid_stairs": False,
        "stairs_penalty": 5.0,
        "slope_penalty": 2.5,
        "elevator_factor": 0.7,
        "missing_braille_penalty": 0.0,
    },
    "carrier": {
        "label": "캐리어 소지자",
        "avoid_stairs": False,
        "stairs_penalty": 4.0,
        "slope_penalty": 1.5,
        "elevator_factor": 0.7,
        "missing_braille_penalty": 0.0,
    },
    "temporary_injury": {
        "label": "일시적 부상자(목발 등)",
        "avoid_stairs": False,
        "stairs_penalty": 6.0,
        "slope_penalty": 3.0,
        "elevator_factor": 0.6,
        "missing_braille_penalty": 0.0,
    },
}

DEFAULT_PROFILE = "wheelchair"


def calculate_weight(edge_data: dict, profile_name: str) -> Optional[float]:
    """
    간선 하나에 대해 주어진 프로필 기준의 비용을 계산한다.
    통행 자체가 불가능한 구간이면 None을 반환한다.
    (networkx는 가중치 함수가 None을 반환하면 해당 간선을 탐색에서 제외한다.)
    """
    profile = PROFILES.get(profile_name, PROFILES[DEFAULT_PROFILE])

    distance = float(edge_data.get("distance", 1.0))
    slope = float(edge_data.get("slope", 0.0))
    has_stairs = bool(edge_data.get("has_stairs", False))
    has_elevator = bool(edge_data.get("has_elevator", False))
    has_braille = bool(edge_data.get("has_braille_block", False))

    # 계단 구간인데 엘리베이터 대체가 없고, 이 프로필이 계단을 회피해야 한다면 통행 불가
    if has_stairs and not has_elevator and profile["avoid_stairs"]:
        return None

    weight = distance
    weight += slope * profile["slope_penalty"]

    if has_stairs:
        weight += profile["stairs_penalty"]

    if has_elevator:
        weight *= profile["elevator_factor"]

    if profile["missing_braille_penalty"] and not has_braille:
        weight += profile["missing_braille_penalty"]

    # 비용은 항상 양수여야 데이크스트라 알고리즘이 정상 동작한다
    return max(weight, 0.01)


def list_profiles() -> dict:
    """프론트엔드에서 프로필 선택 UI를 그릴 때 쓸 수 있는 {id: 표시이름} 매핑"""
    return {key: value["label"] for key, value in PROFILES.items()}
