import mockData from "@/mock/incidents.json";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
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

export async function getAnalytics() {
  const payload = await request("/analytics", { analytics: mockData.analytics });
  return payload?.analytics ?? payload;
}

export function getAnalyticsStats() {
  return request("/analytics/stats", mockData.stats);
}

export async function getDashboardData() {
  const [incidents, analyticsPayload, stats] = await Promise.all([
    getIncidents(),
    getAnalytics(),
    getAnalyticsStats(),
  ]);

  const analytics = analyticsPayload?.analytics ?? analyticsPayload;

  return { incidents, analytics, stats };
}

export function getIncidentById(incidentId) {
  return request(`/incidents/${incidentId}`, null);
}

export function getIncidentTimeline(incidentId) {
  return request(`/incidents/${incidentId}/timeline`, []);
}

async function mutation(path, method = "PUT", body = {}) {
  if (!API_BASE_URL) {
    await wait(MOCK_LATENCY_MS);
    return { success: true };
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }

  return response.json();
}

export function acknowledgeIncident(incidentId, engineer = "On-Call Engineer") {
  return mutation(`/api/incidents/${incidentId}/acknowledge`, "PUT", { engineer });
}

export function escalateIncident(incidentId) {
  return mutation(`/api/incidents/${incidentId}/escalate`, "PUT");
}

export function resolveIncident(incidentId, notes = "Resolved via dashboard") {
  return mutation(`/api/incidents/${incidentId}/resolve`, "PUT", { notes });
}
