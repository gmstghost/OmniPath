"""
routing.py
프로필별 가중치를 반영한 데익스트라 최단 경로 탐색.
networkx의 dijkstra_path에 커스텀 weight 함수를 꽂아 넣는 방식으로,
'물리적 거리만 최소화'하던 기존 알고리즘을 '이동성 프로필 비용 최소화'로 대체한다.
"""

from typing import List, Optional, Tuple

import networkx as nx

from .weights import calculate_weight


def find_route(
    graph: nx.Graph, start: str, end: str, profile: str
) -> Tuple[Optional[List[str]], Optional[float]]:
    if start not in graph or end not in graph:
        return None, None

    def weight_func(u, v, edge_data):
        return calculate_weight(edge_data, profile)

    try:
        path = nx.dijkstra_path(graph, start, end, weight=weight_func)
        cost = nx.dijkstra_path_length(graph, start, end, weight=weight_func)
        return path, cost
    except nx.NetworkXNoPath:
        return None, None


def find_baseline_route(
    graph: nx.Graph, start: str, end: str
) -> Tuple[Optional[List[str]], Optional[float]]:
    """비교용: 프로필을 무시하고 물리적 거리만으로 계산하는 기존 방식의 경로"""
    if start not in graph or end not in graph:
        return None, None
    try:
        path = nx.dijkstra_path(graph, start, end, weight="distance")
        cost = nx.dijkstra_path_length(graph, start, end, weight="distance")
        return path, cost
    except nx.NetworkXNoPath:
        return None, None
