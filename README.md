# 🚶‍♂️ OmniPath (포용적 보행 경로 안내 시스템)

**OmniPath**는 기존 지도 서비스의 '물리적 최단 거리' 중심 경로 안내가 가진 한계를 극복하고, 사용자의 신체적 조건과 상황에 맞춘 '이동성 프로필'을 기반으로 최적의 보행 경로를 안내하는 포용적 내비게이션 시스템입니다.

이 프로젝트는 무장애(Barrier-Free) 설계가 소수만을 위한 배려가 아니라 모두를 위한 보편적 인프라임을 증명하는 '연석 효과(Curb-Cut Effect)'를 알고리즘과 데이터 시각화를 통해 실증하는 것을 목표로 합니다.

전체 스택은 **Firebase(Hosting + Cloud Functions + Firestore)** 기반의 서버리스 구조로 구현되어 있습니다.

---

## ✨ 핵심 기능 (Key Features)

* **6가지 맞춤형 이동성 프로필 제공**
  휠체어 이용자, 유모차 이용자, 시각장애인, 고령자, 캐리어 소지자, 일시적 부상자(목발 등) 중 하나를 선택해 맞춤형 경로를 탐색합니다.

* **보행 환경 기반 가중치 라우팅 알고리즘**
  NetworkX의 데익스트라 알고리즘에 커스텀 weight 함수를 주입하여, 물리적 거리뿐 아니라 **경사도, 계단 유무, 엘리베이터 유무, 점자블록 유무**를 프로필별 비용으로 환산해 경로를 탐색합니다.

* **교통 약자 보행 장벽 회피 시스템**
  계단처럼 특정 프로필이 통행 불가능한 구간(엘리베이터 대체가 없는 계단 등)은 그래프 탐색에서 아예 제외되며, 다소 우회하더라도 엘리베이터·완만한 경사로를 포함한 경로가 우선 제시됩니다.

* **연석 효과(Curb-Cut Effect) 시각화**
  동일한 출발지-도착지에 대해 6개 프로필의 최적 경로를 한 번에 계산하고, 2개 이상의 프로필이 공통으로 사용한 구간을 집계해 지도 위에 겹쳐 그려줍니다. (휠체어용 엘리베이터가 캐리어 소지자·고령자에게도 최적 경로로 선택되는 현상 등)

---

## 🛠 기술 스택 (Tech Stack)

* **Frontend:** HTML5, CSS3, Vanilla JavaScript (Fetch API), [Leaflet.js](https://leafletjs.com/) + OpenStreetMap 타일
* **Backend:** Firebase Cloud Functions (Python 3.11, `firebase-functions`, `firebase-admin`)
* **Database:** Cloud Firestore (`nodes`, `edges` 컬렉션)
* **Algorithm:** NetworkX 기반 가중치 데익스트라 (`nx.dijkstra_path` + 커스텀 weight 함수)
* **Hosting:** Firebase Hosting (정적 프론트엔드 + `/api/**` rewrite로 Functions 연동)
* **Architecture:** 서버리스 — Firebase Hosting / Cloud Functions / Firestore 3계층 구조

> 최초 기획 문서에는 FastAPI/Flask 자체 서버와 KakaoMap/Naver Map API가 언급되어 있었지만, 실제 구현은 위와 같이 Firebase 서버리스 스택 + Leaflet/OSM으로 대체되어 있습니다.

---

## 📂 프로젝트 구조 (Project Structure)

```text
OmniPath/
│
├── public/                      # Firebase Hosting에 배포되는 정적 프론트엔드
│   ├── index.html               # 메인 UI (출발지/도착지/프로필 선택, 결과·연석효과 카드)
│   ├── css/style.css
│   └── js/
│       ├── map.js               # Leaflet 지도 렌더링, 경로(Polyline)·마커 표시, UI 이벤트
│       └── api.js               # Cloud Functions 백엔드 통신 클라이언트
│
├── functions/                   # Firebase Cloud Functions (Python 3.11)
│   ├── main.py                  # 엔드포인트 정의: get_route / list_profiles_endpoint / curb_cut_effect
│   ├── requirements.txt         # firebase-functions, firebase-admin, networkx
│   └── algorithm/                # 핵심 라우팅 엔진
│       ├── routing.py           # 프로필별 가중치를 반영한 데익스트라 경로 탐색
│       ├── weights.py           # 6가지 이동성 프로필별 가중치 환산 로직
│       └── graph_builder.py     # Firestore nodes/edges → NetworkX 그래프 변환
│
├── data/                        # 초기 데이터 및 Firestore 시드 스크립트
│   ├── nodes.csv                # 노드(지점) 위/경도 샘플 데이터 (10개 지점)
│   ├── edges.csv                # 간선(도로) 속성 샘플 데이터 (경사도, 계단, 엘리베이터 등)
│   ├── seed_firestore.py        # 운영 Firestore로 CSV 업로드
│   └── seed_firestore_emul.py   # 로컬 Firestore 에뮬레이터로 CSV 업로드
│
├── firebase.json                # Hosting/Functions/Firestore/에뮬레이터 설정
├── firestore.rules              # 보안 규칙 (nodes/edges: 읽기 전체 허용, 쓰기 전체 차단)
├── firestore.indexes.json       # Firestore 인덱스 설정
├── .firebaserc                  # Firebase 프로젝트 ID 매핑
└── README.md
```

---

## 🧭 이동성 프로필별 가중치 (`functions/algorithm/weights.py`)

각 간선의 `distance / slope / has_stairs / has_elevator / has_braille_block` 속성을 아래 파라미터로 비용으로 환산합니다. `avoid_stairs=True`인 프로필은 엘리베이터 대체가 없는 계단 구간을 아예 통행 불가로 처리합니다.

| 프로필 ID | 라벨 | 계단 회피 | 계단 페널티 | 경사도 계수 | 엘리베이터 배수 | 점자블록 부재 페널티 |
|---|---|---|---|---|---|---|
| `wheelchair` | 휠체어 이용자 | ✅ 회피 | – | 4.0 | ×0.6 | – |
| `stroller` | 유모차 이용자 | ✅ 회피 | – | 3.0 | ×0.6 | – |
| `visually_impaired` | 시각장애인 | 통행 가능 | 2.0 | 1.0 | ×0.9 | 6.0 |
| `elderly` | 고령자 | 통행 가능 | 5.0 | 2.5 | ×0.7 | – |
| `carrier` | 캐리어 소지자 | 통행 가능 | 4.0 | 1.5 | ×0.7 | – |
| `temporary_injury` | 일시적 부상자(목발 등) | 통행 가능 | 6.0 | 3.0 | ×0.6 | – |

기본 프로필(`DEFAULT_PROFILE`)은 `wheelchair`입니다.

---

## 🔌 API 엔드포인트 (`functions/main.py`)

| 엔드포인트 | 메서드 | 파라미터 | 설명 |
|---|---|---|---|
| `/get_route` | GET/POST | `start`, `end`, `profile` | 지정 프로필 기준 최적 경로와 비용, 좌표가 포함된 경로를 반환 |
| `/list_profiles_endpoint` | GET | – | 선택 가능한 6개 프로필의 `{id: 라벨}` 매핑 반환 |
| `/curb_cut_effect` | GET/POST | `start`, `end` | 6개 프로필 전체의 경로를 한 번에 계산하고, 2개 이상 프로필이 공통 사용한 간선(연석 효과 구간)을 집계해 반환 |

모든 엔드포인트는 CORS가 전체 허용(`cors_origins="*"`)으로 설정되어 있습니다. Cloud Functions 인스턴스는 웜 스타트 시 그래프를 전역 캐시(`_graph_cache`)에 담아 재사용하므로, 매 요청마다 Firestore를 다시 읽지 않습니다.

---

## 🚀 시작하기 (Getting Started)

### 0. 사전 준비물

* [Firebase CLI](https://firebase.google.com/docs/cli) (`npm install -g firebase-tools`)
* Python 3.11
* Firebase 프로젝트 (또는 로컬 에뮬레이터만으로도 실행 가능)

### 1. 저장소 클론 및 Functions 의존성 설치

```bash
git clone https://github.com/gmstghost/OmniPath.git
cd OmniPath/functions

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. (선택) Firestore에 샘플 데이터 시드하기

로컬 에뮬레이터로 개발할 경우, Firebase 콘솔에서 발급받은 서비스 계정 키를 `data/serviceAccountKey.json`으로 저장한 뒤:

```bash
cd ../data
pip install firebase-admin

# 로컬 에뮬레이터에 시드 (firebase emulators:start를 먼저 실행해둔 상태여야 함)
python seed_firestore_emul.py

# 운영 Firestore에 시드하려면
python seed_firestore.py
```

### 3. Firebase 에뮬레이터로 로컬 실행

```bash
cd ..
firebase emulators:start --only functions,firestore,hosting
```

* Hosting: `http://127.0.0.1:5000`
* Functions: `http://127.0.0.1:5001/<PROJECT_ID>/us-central1`
* Firestore 에뮬레이터 UI: `http://127.0.0.1:4000/firestore`

`public/js/api.js`의 `BASE_URL`에 있는 `<PROJECT_ID>` 부분을 실제 Firebase 프로젝트 ID로 맞춰줘야 로컬 실행 시 정상적으로 호출됩니다(`.firebaserc` 참고).

### 4. 배포

```bash
firebase deploy --only functions,firestore,hosting
```

---

## ⚠️ 알려진 이슈 / TODO

* **Hosting rewrite 범위**: `firebase.json`의 rewrite 규칙이 `/api/**` 전체를 `get_route` 함수 하나로만 연결하고 있어, 배포 후에는 `/api/curb_cut_effect`, `/api/list_profiles_endpoint` 요청도 `get_route` 함수로 들어갑니다. 로컬 에뮬레이터(함수별 포트 직접 접근)에서는 문제없이 동작하지만, 운영 배포 시에는 rewrite를 함수별로 분리하거나 단일 라우터 함수로 통합하는 작업이 필요합니다.
* **샘플 데이터 규모**: `data/nodes.csv` / `edges.csv`는 지하철역 환승 구간을 가정한 10개 노드, 13개 간선짜리 테스트용 데이터입니다. 실서비스 규모의 보행 그래프 데이터는 별도로 구축해야 합니다.
* **프로필 목록 하드코딩**: `public/js/map.js`의 `SAMPLE_NODES` 목록이 백엔드가 아닌 프론트엔드에 하드코딩되어 있어, Firestore의 `nodes` 컬렉션이 바뀌면 별도로 동기화해야 합니다. `list_nodes` 엔드포인트를 추가해 동적으로 받아오는 것을 권장합니다(코드 주석에도 명시됨).

---

## 📝 이론적 배경 및 참고 문헌 (References)

본 프로젝트는 다음의 연구와 이론을 바탕으로 설계되었습니다.

* **이론적 배경:** 사라 헨드렌의 '몸과 환경의 부적합' 이론, Angela Glover Blackwell의 '연석 효과(Curb-Cut Effect)'.
* **참조 탐구:** 「파이썬 최단 경로 알고리즘과 이동성 프로필을 활용한 포용적 보행 경로 시스템 구축에 관한 탐구」 (안제욱, 2024).

---

**Contributors**

* Ahn Je-wook (안제욱) - *Project Lead & Algorithm Design*