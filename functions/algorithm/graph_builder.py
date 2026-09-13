"""
graph_builder.py
Firestore의 nodes / edges 컬렉션을 읽어 networkx 그래프 객체로 변환한다.
README의 3차원 보행 환경 데이터(경사도, 계단, 엘리베이터, 점자블록)를
간선(edge)의 속성으로 그대로 실어 둔 뒤, weights.py에서 프로필별 비용으로 환산한다.
"""

import networkx as nx


def build_graph(db) -> nx.Graph:
    """
    db: firebase_admin.firestore.client()로 얻은 Firestore 클라이언트

    nodes 문서: { lat: float, lng: float }
    edges 문서: { from: str, to: str, distance, slope, has_stairs, has_elevator,
                  has_braille_block, bidirectional(optional, 기본 True) }
    """
    graph = nx.Graph()

    for doc in db.collection("nodes").stream():
        data = doc.to_dict() or {}
        graph.add_node(
            doc.id,
            lat=data.get("lat"),
            lng=data.get("lng"),
            name=data.get("name", doc.id),
        )

    for doc in db.collection("edges").stream():
        data = doc.to_dict() or {}
        u, v = data.get("from"), data.get("to")
        if u is None or v is None:
            continue
        if u not in graph or v not in graph:
            # 노드 데이터가 아직 없는 간선은 건너뛴다 (데이터 정합성 문제 방지)
            continue
        graph.add_edge(u, v, **data)

    return graph
