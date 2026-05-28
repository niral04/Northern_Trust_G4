import mockData from "@/mock/incidents.json";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
const MOCK_LATENCY_MS = 350;

function wait(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

async function request(path, fallback) {
  if (!API_BASE_URL) {
    await wait(MOCK_LATENCY_MS);
    return fallback;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.warn(`Using mock fallback for ${path}`, error);
    await wait(MOCK_LATENCY_MS);
    return fallback;
  }
}

export function getIncidents() {
  return request("/incidents", mockData.incidents);
}

export function getAnalytics() {
  return request("/analytics", mockData.analytics);
}

export function getAnalyticsStats() {
  return request("/analytics/stats", mockData.stats);
}

export async function getDashboardData() {
  const [incidents, analytics, stats] = await Promise.all([
    getIncidents(),
    getAnalytics(),
    getAnalyticsStats(),
  ]);

  return { incidents, analytics, stats };
}
