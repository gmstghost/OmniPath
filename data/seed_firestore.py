"""
seed_firestore.py
data/nodes.csv, data/edges.csv를 Firestore의 nodes / edges 컬렉션으로 업로드한다.

사전 준비:
1. Firebase 콘솔 > 프로젝트 설정 > 서비스 계정에서 비공개 키(JSON)를 발급받아
   이 파일과 같은 폴더에 serviceAccountKey.json 이름으로 저장한다.
   (이 키는 절대 git에 커밋하지 말 것 — .gitignore에 반드시 추가)
2. pip install firebase-admin

실행:
    python seed_firestore.py
"""

import csv
import os

import firebase_admin
from firebase_admin import credentials, firestore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")

cred = credentials.Certificate(KEY_PATH)
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
    print(f"[nodes] {count}개 업로드 완료")


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
    print(f"[edges] {count}개 업로드 완료")


if __name__ == "__main__":
    seed_nodes()
    seed_edges()
    print("Firestore 시드 완료. Firebase 콘솔의 Firestore Database에서 확인하세요.")
