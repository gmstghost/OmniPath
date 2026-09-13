"""
seed_firestore.py (에뮬레이터용 수정본)
data/nodes.csv, data/edges.csv를 로컬 로컬 에뮬레이터의 Firestore로 업로드한다.
"""

import csv
import os

import firebase_admin
from firebase_admin import credentials, firestore

# 1. 로컬 에뮬레이터 강제 연결 (운영 DB 접근 차단 및 에뮬레이터로 라우팅)
os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8080"
os.environ["GCLOUD_PROJECT"] = "omnipath-27168"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")

# 2. 기존 서비스 키 파일로 인증 통과 (실제 데이터는 에뮬레이터에만 저장됨)
cred = credentials.Certificate(KEY_PATH)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

def _to_bool(value: str) -> bool:
    return str(value).strip().lower() in ("true", "1", "yes")

def seed_nodes(path: str = os.path.join(BASE_DIR, "nodes.csv")) -> None:
    batch = db.batch()
    count = 0
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ref = db.collection("nodes").document(row["node_id"])
            batch.set(
                ref,
                {
                    "lat": float(row["lat"]),
                    "lng": float(row["lng"]),
                    "name": row.get("name", row["node_id"]),
                },
            )
            count += 1
            if count % 400 == 0:
                batch.commit()
                batch = db.batch()
    batch.commit()
    print(f"[nodes] {count}개 에뮬레이터 업로드 완료")

def seed_edges(path: str = os.path.join(BASE_DIR, "edges.csv")) -> None:
    batch = db.batch()
    count = 0
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            edge_id = f"{row['from']}_{row['to']}"
            ref = db.collection("edges").document(edge_id)
            batch.set(
                ref,
                {
                    "from": row["from"],
                    "to": row["to"],
                    "distance": float(row["distance"]),
                    "slope": float(row.get("slope", 0)),
                    "has_stairs": _to_bool(row.get("has_stairs", False)),
                    "has_elevator": _to_bool(row.get("has_elevator", False)),
                    "has_braille_block": _to_bool(row.get("has_braille_block", False)),
                },
            )
            count += 1
            if count % 400 == 0:
                batch.commit()
                batch = db.batch()
    batch.commit()
    print(f"[edges] {count}개 에뮬레이터 업로드 완료")

if __name__ == "__main__":
    seed_nodes()
    seed_edges()
    print("로컬 Firestore 에뮬레이터 시드 완료. http://127.0.0.1:4000/firestore 에서 확인하세요.")