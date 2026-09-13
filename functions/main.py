"""
main.py
OmniPath 백엔드를 Firebase Cloud Functions(Python) 위에서 구동하기 위한 진입점.

로컬 실행:
    firebase emulators:start --only functions,firestore,hosting

배포:
    firebase deploy --only functions,firestore,hosting

엔드포인트:
    GET/POST /get_route            ?start=N01&end=N09&profile=wheelchair
    GET      /list_profiles
    GET/POST /curb_cut_effect      ?start=N01&end=N09
"""

import json

from firebase_admin import firestore, initialize_app
from firebase_functions import https_fn, options

from algorithm.graph_builder import build_graph
from algorithm.routing import find_baseline_route, find_route
from algorithm.weights import DEFAULT_PROFILE, PROFILES, list_profiles

initialize_app()

_db = None
_graph_cache = None

_CORS = options.CorsOptions(cors_origins="*", cors_methods=["GET", "POST", "OPTIONS"])


def _get_db():
    global _db
    if _db is None:
        _db = firestore.client()
    return _db


def _get_graph(force_refresh: bool = False):
    # Cloud Functions 인스턴스는 웜 스타트 시 재사용되므로,
    # 그래프를 전역 캐시에 담아 매 요청마다 Firestore를 다시 읽지 않게 한다.
    global _graph_cache
    if _graph_cache is None or force_refresh:
        _graph_cache = build_graph(_get_db())
    return _graph_cache


def _json_response(payload: dict, status: int = 200) -> https_fn.Response:
    response = https_fn.Response(
        json.dumps(payload, ensure_ascii=False),
        status=status,
        mimetype="application/json",
    )
    return response


def _read_params(req: https_fn.Request) -> dict:
    body = req.get_json(silent=True) or {}
    return {
        "start": req.args.get("start") or body.get("start"),
        "end": req.args.get("end") or body.get("end"),
        "profile": req.args.get("profile") or body.get("profile") or DEFAULT_PROFILE,
    }


@https_fn.on_request(cors=_CORS)
def get_route(req: https_fn.Request) -> https_fn.Response:
    # Preflight 요청 조기 종료
    if req.method == "OPTIONS":
        return _json_response({}, 204)

    params = _read_params(req)
    start, end, profile = params["start"], params["end"], params["profile"]

    if not start or not end:
        return _json_response({"error": "start, end 파라미터가 필요합니다."}, 400)
    if profile not in PROFILES:
        return _json_response(
            {"error": f"알 수 없는 프로필입니다: {profile}", "valid_profiles": list(PROFILES)},
            400,
        )

    graph = _get_graph()
    path, cost = find_route(graph, start, end, profile)

    if path is None:
        return _json_response(
            {"error": "해당 프로필로 이동 가능한 경로를 찾지 못했습니다.", "profile": profile},
            404,
        )

    return _json_response(
        {
            "profile": profile,
            "profile_label": PROFILES[profile]["label"],
            "start": start,
            "end": end,
            "cost": round(cost, 2),
            "path": [
                {"id": n, "lat": graph.nodes[n]["lat"], "lng": graph.nodes[n]["lng"]}
                for n in path
            ],
        }
    )


@https_fn.on_request(cors=_CORS)
def list_profiles_endpoint(req: https_fn.Request) -> https_fn.Response:
    return _json_response({"profiles": list_profiles()})


@https_fn.on_request(cors=_CORS)
def curb_cut_effect(req: https_fn.Request) -> https_fn.Response:
    """
    같은 출발지-도착지에 대해 6개 프로필 각각의 최적 경로를 계산하고,
    동일한 간선이 몇 개의 프로필에서 공통으로 선택되는지를 집계해
    '연석 효과'를 데이터로 보여준다.
    """
    params = _read_params(req)
    start, end = params["start"], params["end"]

    if not start or not end:
        return _json_response({"error": "start, end 파라미터가 필요합니다."}, 400)

    graph = _get_graph()

    baseline_path, baseline_cost = find_baseline_route(graph, start, end)

    def _with_coords(path):
        if not path:
            return None
        return [
            {"id": n, "lat": graph.nodes[n]["lat"], "lng": graph.nodes[n]["lng"]}
            for n in path
        ]

    per_profile = {}
    edge_usage_count = {}

    for profile_id in PROFILES:
        path, cost = find_route(graph, start, end, profile_id)
        per_profile[profile_id] = {
            "label": PROFILES[profile_id]["label"],
            "path": _with_coords(path),
            "cost": round(cost, 2) if cost is not None else None,
        }
        if path:
            for a, b in zip(path, path[1:]):
                edge_key = "-".join(sorted([a, b]))
                edge_usage_count[edge_key] = edge_usage_count.get(edge_key, 0) + 1

    # 2개 이상 프로필에서 공통으로 쓰인 구간만 '연석 효과' 구간으로 추린다
    shared_edges = [
        {"edge": key, "profile_count": count}
        for key, count in sorted(edge_usage_count.items(), key=lambda x: -x[1])
        if count >= 2
    ]

    return _json_response(
        {
            "start": start,
            "end": end,
            "baseline_distance_only": {
                "path": _with_coords(baseline_path),
                "cost": round(baseline_cost, 2) if baseline_cost is not None else None,
            },
            "per_profile": per_profile,
            "shared_edges": shared_edges,
        }
    )
