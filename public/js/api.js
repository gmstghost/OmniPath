/**
 * api.js
 * Firebase Cloud Functions(Python) 백엔드와 통신하는 얇은 클라이언트.
 *
 * 로컬 에뮬레이터로 개발할 때는 BASE_URL을 에뮬레이터 주소로,
 * 배포 후에는 firebase.json의 hosting rewrite("/api/**")를 통해
 * 같은 도메인에서 그대로 접근할 수 있습니다.
 *
 *   로컬 에뮬레이터 예시:
 *     http://127.0.0.1:5001/<PROJECT_ID>/us-central1
 *   배포 후 (Hosting rewrite 사용 시):
 *     /api
 */
const OmniPathAPI = (() => {
  const isLocalhost = ["localhost", "127.0.0.1"].includes(window.location.hostname);

  // TODO: <PROJECT_ID>를 실제 Firebase 프로젝트 ID로 바꿔주세요.
  const BASE_URL = isLocalhost
    ? "http://127.0.0.1:5001/omnipath-27168/us-central1"
    : "/api";

  async function getRoute(start, end, profile) {
    const query = new URLSearchParams({ start, end, profile }).toString();
    const res = await fetch(`${BASE_URL}/get_route?${query}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "경로를 찾지 못했습니다.");
    return data;
  }

  async function getCurbCutEffect(start, end) {
    const res = await fetch(`${BASE_URL}/curb_cut_effect?start=${start}&end=${end}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "분석에 실패했습니다.");
    return data;
  }

  async function listProfiles() {
    const res = await fetch(`${BASE_URL}/list_profiles_endpoint`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "프로필 목록을 불러오지 못했습니다.");
    return data.profiles;
  }

  return { getRoute, getCurbCutEffect, listProfiles };
})();