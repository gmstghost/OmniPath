# 🚶‍♂️ OmniPath (포용적 보행 경로 안내 시스템)

**OmniPath**는 기존 지도 서비스의 '물리적 최단 거리' 중심 경로 안내가 가진 한계를 극복하고, 사용자의 신체적 조건과 상황에 맞춘 '이동성 프로필'을 기반으로 최적의 보행 경로를 안내하는 포용적 내비게이션 시스템입니다.

이 프로젝트는 무장애(Barrier-Free) 설계가 소수만을 위한 배려가 아니라 모두를 위한 보편적 인프라임을 증명하는 '연석 효과(Curb-Cut Effect)'를 알고리즘과 데이터 시각화를 통해 실증하는 것을 목표로 합니다.

---

## ✨ 핵심 기능 (Key Features)

* **6가지 맞춤형 이동성 프로필 제공**
* 휠체어 이용자, 유모차 이용자, 시각장애인, 고령자, 캐리어 소지자, 일시적 부상자 등 6가지 프로필 중 하나를 선택하여 맞춤형 경로를 탐색할 수 있습니다.




* **보행 환경 기반 가중치 라우팅 알고리즘**
* 파이썬 기반의 최단 경로 알고리즘(데익스트라 등)을 수정하여, 물리적 거리뿐만 아니라 **경사도, 계단 및 단차, 엘리베이터, 점자블록 유무**를 비용(가중치)으로 환산하여 경로를 탐색합니다.




* **교통 약자 보행 장벽 회피 시스템**
* 계단 등 특정 프로필에게 통행 불가능한 구간을 회피하고, 다소 우회하더라도 엘리베이터나 완만한 경사로를 포함한 안전한 경로를 우선 제시합니다.




* **연석 효과(Curb-Cut Effect) 시각화**
* 휠체어 이용자를 위한 엘리베이터가 캐리어 소지자나 고령자에게도 동일하게 최적 경로로 선택되는 현상을 지도상에 시각적으로 구현하여 공통의 편익을 증명합니다.





---

## 🛠 기술 스택 (Tech Stack)

* **Frontend:** HTML5, CSS3, JavaScript (Fetch API), KakaoMap API (또는 Naver/Leaflet)
* **Backend:** Python 3.9+, FastAPI (또는 Flask)
* **Algorithm & Data:** NetworkX (그래프 데이터 연산), Pandas
* **Architecture:** RESTful API 기반 Client-Server 구조

---

## 📂 프로젝트 구조 (Project Structure)

```text
OmniPath/
│
├── frontend/                   # 사용자 인터페이스 및 지도 시각화 (HTML/JS)
│   ├── index.html              # 메인 UI
│   ├── css/style.css           
│   └── js/
│       ├── map.js              # 지도 렌더링 및 경로(Polyline), 마커 표시
│       └── api.js              # 파이썬 백엔드 API 통신
│
├── backend/                    # 최단 경로 산출 API 서버
│   ├── main.py                 # FastAPI/Flask 서버 실행 및 라우터 설정
│   ├── requirements.txt        # 파이썬 패키지 의존성
│   │
│   ├── algorithm/              # 핵심 라우팅 엔진 (CVCLSIMMS 구조 활용)
│   │   ├── routing.py          # 데익스트라/A* 알고리즘 수정 모델 구현
│   │   ├── weights.py          # 6가지 이동성 프로필별 가중치 환산 로직
│   │   └── graph_builder.py    # 3차원 보행 환경 데이터 그래프 변환
│   │
│   └── data/                   
│       ├── nodes.csv           # 노드(지점) 위/경도 데이터
│       └── edges.csv           # 간선(도로) 속성 데이터 (경사도, 계단, 엘리베이터 등)
│
└── README.md                   

```

---

## 🚀 시작하기 (Getting Started)

### 1. 환경 설정 및 백엔드 실행

파이썬 가상환경을 생성하고 필요한 패키지를 설치한 뒤 서버를 실행합니다.

```bash
# 레포지토리 클론
git clone https://github.com/사용자명/OmniPath.git
cd OmniPath/backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 서버 실행 (FastAPI 기준)
uvicorn main:app --reload

```

### 2. 프론트엔드 실행

웹 브라우저에서 `frontend/index.html` 파일을 열어 서비스를 확인합니다.
(또는 VS Code의 Live Server 익스텐션을 사용하여 실행합니다.)

---

## 📝 이론적 배경 및 참고 문헌 (References)

본 프로젝트는 다음의 연구와 이론을 바탕으로 설계되었습니다.

* **이론적 배경:** 사라 헨드렌의 '몸과 환경의 부적합' 이론, Angela Glover Blackwell의 '연석 효과(Curb-Cut Effect)'.


* **참조 탐구:** 「파이썬 최단 경로 알고리즘과 이동성 프로필을 활용한 포용적 보행 경로 시스템 구축에 관한 탐구」 (안제욱, 2024).



---

**Contributors**

* Ahn Je-wook (안제욱) - *Project Lead & Algorithm Design*