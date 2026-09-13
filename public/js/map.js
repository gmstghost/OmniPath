/**
 * map.js
 * 지도 렌더링과 경로(Polyline)/마커 표시, 그리고 컨트롤 패널 UI를 담당한다.
 * 지도 타일은 무료 OpenStreetMap 타일을 기본값으로 쓴다.
 * README에 언급된 KakaoMap/Naver Maps로 바꾸고 싶다면 이 파일의
 * L.tileLayer(...) 부분만 해당 SDK 초기화 코드로 교체하면 된다.
 */

// data/nodes.csv 의 샘플 지점 목록.
// 실서비스에서는 백엔드에 list_nodes 엔드포인트를 하나 추가해 여기서 fetch로 받아오는 것을 추천한다.
const SAMPLE_NODES = [
  { id: "N01", name: "출구1" },
  { id: "N02", name: "계단앞" },
  { id: "N03", name: "플랫폼A입구" },
  { id: "N04", name: "환승통로입구" },
  { id: "N05", name: "엘리베이터앞" },
  { id: "N06", name: "환승통로중간" },
  { id: "N07", name: "플랫폼B입구" },
  { id: "N08", name: "점자안내구역" },
  { id: "N09", name: "출구2" },
  { id: "N10", name: "경사로구간" },
];

const PROFILE_OPTIONS = [
  { id: "wheelchair", label: "휠체어 이용자" },
  { id: "stroller", label: "유모차 이용자" },
  { id: "visually_impaired", label: "시각장애인" },
  { id: "elderly", label: "고령자" },
  { id: "carrier", label: "캐리어 소지자" },
  { id: "temporary_injury", label: "일시적 부상자" },
];

let map;
let routeLayerGroup;
let selectedProfile = PROFILE_OPTIONS[0].id;

function initMap() {
  map = L.map("map").setView([37.5011, 127.0253], 18);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 20,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  routeLayerGroup = L.layerGroup().addTo(map);
}

function populateSelects() {
  const startSelect = document.getElementById("start-select");
  const endSelect = document.getElementById("end-select");

  SAMPLE_NODES.forEach(({ id, name }) => {
    const opt1 = new Option(`${name} (${id})`, id);
    const opt2 = new Option(`${name} (${id})`, id);
    startSelect.add(opt1);
    endSelect.add(opt2);
  });

  startSelect.value = "N01";
  endSelect.value = "N07"; // 계단 지름길 vs 엘리베이터 우회가 갈리는 구간 (연석 효과 시연용 기본값)
}

function populateProfileChips() {
  const container = document.getElementById("profile-chips");
  PROFILE_OPTIONS.forEach(({ id, label }, index) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip" + (index === 0 ? " active" : "");
    chip.textContent = label;
    chip.dataset.profileId = id;
    chip.addEventListener("click", () => {
      selectedProfile = id;
      container.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
    });
    container.appendChild(chip);
  });
}

function setStatus(message, isError = false) {
  const line = document.getElementById("status-line");
  line.textContent = message || "";
  line.style.color = isError ? "var(--color-hazard)" : "var(--color-teal)";
}

function drawPath(points, color) {
  const latlngs = points.map((p) => [p.lat, p.lng]);
  L.polyline(latlngs, { color, weight: 5, opacity: 0.85 }).addTo(routeLayerGroup);

  L.circleMarker(latlngs[0], { radius: 7, color, fillColor: color, fillOpacity: 1 })
    .bindTooltip(points[0].id)
    .addTo(routeLayerGroup);
  L.circleMarker(latlngs[latlngs.length - 1], { radius: 7, color, fillColor: color, fillOpacity: 1 })
    .bindTooltip(points[points.length - 1].id)
    .addTo(routeLayerGroup);

  map.fitBounds(latlngs, { padding: [40, 40] });
}

async function handleFindRoute() {
  const start = document.getElementById("start-select").value;
  const end = document.getElementById("end-select").value;

  document.getElementById("curb-cut-card").hidden = true;
  routeLayerGroup.clearLayers();
  setStatus("경로를 계산하는 중...");

  try {
    const result = await OmniPathAPI.getRoute(start, end, selectedProfile);

    drawPath(result.path, "#E8A33D");

    const resultCard = document.getElementById("result-card");
    resultCard.hidden = false;
    document.getElementById("result-cost").textContent =
      `${result.profile_label} 기준 비용 ${result.cost}`;

    const list = document.getElementById("result-path");
    list.innerHTML = "";
    result.path.forEach((node) => {
      const li = document.createElement("li");
      li.textContent = node.id;
      list.appendChild(li);
    });

    setStatus("");
  } catch (err) {
    document.getElementById("result-card").hidden = true;
    setStatus(err.message, true);
  }
}

const PROFILE_COLORS = {
  wheelchair: "#2E7D6B",
  stroller: "#3E8FB0",
  visually_impaired: "#8A5FB0",
  elderly: "#C97A3D",
  carrier: "#B5482E",
  temporary_injury: "#5A6B8C",
};

async function handleCurbCutEffect() {
  const start = document.getElementById("start-select").value;
  const end = document.getElementById("end-select").value;

  document.getElementById("result-card").hidden = true;
  routeLayerGroup.clearLayers();
  setStatus("프로필별 경로를 비교하는 중...");

  try {
    const result = await OmniPathAPI.getCurbCutEffect(start, end);

    // 프로필별 경로를 각기 다른 색의 가는 선으로 겹쳐 그려,
    // 여러 선이 겹치는 구간(=연석 효과 구간)이 지도 위에서 눈에 띄게 한다.
    let bounds = [];
    let offsetIndex = 0;
    Object.entries(result.per_profile).forEach(([profileId, entry]) => {
      if (!entry.path || entry.path.length < 2) return;
      const latlngs = entry.path.map((p) => [p.lat, p.lng]);
      bounds = bounds.concat(latlngs);
      L.polyline(latlngs, {
        color: PROFILE_COLORS[profileId] || "#888",
        weight: 4,
        opacity: 0.6,
        dashArray: offsetIndex % 2 === 0 ? null : "6 4",
      })
        .bindTooltip(entry.label)
        .addTo(routeLayerGroup);
      offsetIndex += 1;
    });
    if (bounds.length) map.fitBounds(bounds, { padding: [40, 40] });

    const card = document.getElementById("curb-cut-card");
    card.hidden = false;
    const list = document.getElementById("curb-cut-list");
    list.innerHTML = "";

    if (result.shared_edges.length === 0) {
      const li = document.createElement("li");
      li.textContent = "두 개 이상의 프로필이 공통으로 사용한 구간이 없습니다.";
      list.appendChild(li);
    } else {
      result.shared_edges.forEach(({ edge, profile_count }) => {
        const li = document.createElement("li");
        li.textContent = `${edge.replace("-", " ↔ ")} — ${profile_count}개 프로필 공통 이용`;
        list.appendChild(li);
      });
    }

    setStatus("");
  } catch (err) {
    setStatus(err.message, true);
  }
}

window.addEventListener("DOMContentLoaded", () => {
  initMap();
  populateSelects();
  populateProfileChips();

  document.getElementById("find-route-btn").addEventListener("click", handleFindRoute);
  document.getElementById("curb-cut-btn").addEventListener("click", handleCurbCutEffect);
});