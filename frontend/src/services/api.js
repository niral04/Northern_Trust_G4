import mockData from "@/mock/incidents.json";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const MOCK_LATENCY_MS = 350;
const SEVERITIES = ["Critical", "High", "Medium", "Low"];

function wait(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function titleCase(value, fallback = "Unknown") {
  if (!value) return fallback;

  return String(value)
    .toLowerCase()
    .split(/[\s_-]+/)
    .filter(Boolean)
    .map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`)
    .join(" ");
}

function toNumber(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

function formatTime(value) {
  if (!value) return "--:--";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);

  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function emptySeverityDistribution() {
  return SEVERITIES.map((name) => ({ name, value: 0 }));
}

function normalizeIncident(raw) {
  if (!raw) return null;

  const id = String(raw.incident_id ?? raw.id);
  const service = raw.service ?? raw.source ?? raw.alert_type ?? raw.workflow_path ?? "incident-service";
  const severity = titleCase(raw.severity, "Low");
  const status = titleCase(raw.status, "Open");
  const createdAt = raw.createdAt ?? raw.created_at ?? new Date().toISOString();
  const updatedAt = raw.updatedAt ?? raw.updated_at ?? raw.resolved_at ?? raw.acknowledged_at ?? createdAt;
  const description = raw.description ?? raw.message ?? raw.title ?? "No incident description available.";

  return {
    ...raw,
    id,
    backendId: raw.id,
    title: raw.title ?? `[${titleCase(raw.alert_type, "Alert")}] ${description}`,
    service,
    severity,
    status,
    owner: raw.owner ?? raw.assignee ?? "OnCallEngineer",
    region: raw.region ?? "global",
    createdAt,
    updatedAt,
    signals: toNumber(raw.signals ?? raw.escalation_level, 0),
    description,
    classificationReason:
      raw.classificationReason ??
      raw.workflow_path ??
      raw.priority ??
      `${severity} ${titleCase(raw.alert_type, "alert")} routed to ${raw.assignee ?? "on-call"}`,
    timeline: raw.timeline ?? buildTimeline(raw, status, createdAt, updatedAt),
    escalationHistory: raw.escalationHistory ?? buildEscalationHistory(raw),
  };
}

function buildTimeline(raw, status, createdAt, updatedAt) {
  const timeline = [
    {
      time: formatTime(createdAt),
      action: "Incident created",
      user: raw.source ?? "System",
    },
  ];

  if (raw.acknowledged_at) {
    timeline.push({
      time: formatTime(raw.acknowledged_at),
      action: "Incident acknowledged",
      user: raw.assignee ?? "On-call",
    });
  }

  if (raw.escalation_level > 0 || status === "Escalated") {
    timeline.push({
      time: formatTime(raw.last_escalated_at ?? updatedAt),
      action: "Incident escalated",
      user: "Escalation engine",
    });
  }

  if (raw.resolved_at || status === "Resolved") {
    timeline.push({
      time: formatTime(raw.resolved_at ?? updatedAt),
      action: "Incident resolved",
      user: raw.assignee ?? "On-call",
    });
  }

  return timeline;
}

function buildEscalationHistory(raw) {
  const currentLevel = toNumber(raw.escalation_level, 0);

  return [1, 2, 3].map((level) => ({
    level,
    role: level === 1 ? "Primary On-call" : level === 2 ? "Senior Engineer" : "Engineering Manager",
    person: level === 1 ? raw.assignee ?? "OnCallEngineer" : "Escalation contact",
    status:
      currentLevel >= level
        ? "Escalated"
        : raw.status === "ACKNOWLEDGED" && level === 1
          ? "Acknowledged"
          : "Pending",
  }));
}

function normalizeIncidents(payload) {
  const incidents = Array.isArray(payload)
    ? payload
    : Array.isArray(payload?.incidents)
      ? payload.incidents
      : [];

  return incidents.map(normalizeIncident).filter(Boolean);
}

function normalizeStats(payload, incidents = []) {
  const stats = payload?.stats ?? payload ?? {};
  const normalizedIncidents = incidents.map(normalizeIncident).filter(Boolean);
  const activeStatuses = new Set(["Open", "Acknowledged", "Escalated", "Investigating"]);

  const backendActiveIncidents =
    stats.activeIncidents ??
    stats.active_incidents ??
    (stats.open == null ? undefined : stats.open + (stats.acknowledged ?? 0) + (stats.escalated ?? 0));
  const activeIncidents =
    backendActiveIncidents ??
    normalizedIncidents.filter((incident) => activeStatuses.has(incident.status)).length;

  return {
    activeIncidents: toNumber(activeIncidents),
    criticalIncidents: toNumber(
      stats.criticalIncidents ??
        stats.critical_incidents ??
        stats.critical ??
        normalizedIncidents.filter((incident) => incident.severity === "Critical").length,
    ),
    mttrMinutes: toNumber(stats.mttrMinutes ?? stats.mttr_minutes ?? stats.avg_mttr ?? 0),
    automationRate: toNumber(stats.automationRate ?? stats.automation_rate ?? 0),
    eventsPerMinute: toNumber(stats.eventsPerMinute ?? stats.events_per_minute ?? normalizedIncidents.length),
    slaCompliance: toNumber(stats.slaCompliance ?? stats.sla_compliance ?? 100),
  };
}

function countBy(items, key) {
  return items.reduce((counts, item) => {
    const value = item[key] ?? "Unknown";
    counts[value] = (counts[value] ?? 0) + 1;
    return counts;
  }, {});
}

function normalizeAnalytics(payload, incidents = []) {
  const analytics = payload?.analytics ?? payload ?? {};
  const normalizedIncidents = incidents.map(normalizeIncident).filter(Boolean);
  const severityCounts = countBy(normalizedIncidents, "severity");
  const services = Object.entries(countBy(normalizedIncidents, "service"));

  const severityDistribution = Array.isArray(analytics.severityDistribution)
    ? analytics.severityDistribution
    : Array.isArray(analytics.severity_breakdown)
      ? emptySeverityDistribution().map((item) => ({
          ...item,
          value: toNumber(
            analytics.severity_breakdown.find((row) => titleCase(row.severity) === item.name)?.count,
          ),
        }))
      : emptySeverityDistribution().map((item) => ({
          ...item,
          value: toNumber(severityCounts[item.name]),
        }));

  const trend = Array.isArray(analytics.trend)
    ? analytics.trend
    : buildTrend(normalizedIncidents);

  return {
    trend,
    severityDistribution,
    responseTimes: Array.isArray(analytics.responseTimes)
      ? analytics.responseTimes
      : buildResponseTimes(services, normalizedIncidents),
    timeline: Array.isArray(analytics.timeline)
      ? analytics.timeline
      : buildAnalyticsTimeline(normalizedIncidents),
    serviceHealth: Array.isArray(analytics.serviceHealth)
      ? analytics.serviceHealth
      : buildServiceHealth(services),
  };
}

function buildTrend(incidents) {
  const buckets = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"];
  const rows = buckets.map((time) => ({ time, critical: 0, high: 0, medium: 0, low: 0 }));

  incidents.forEach((incident) => {
    const date = new Date(incident.createdAt);
    const hour = Number.isNaN(date.getTime()) ? 0 : date.getHours();
    const bucketIndex = Math.min(Math.floor(hour / 3), rows.length - 1);
    const severityKey = incident.severity.toLowerCase();

    if (severityKey in rows[bucketIndex]) {
      rows[bucketIndex][severityKey] += 1;
    }
  });

  return rows;
}

function buildResponseTimes(services, incidents) {
  if (!services.length) return mockData.analytics.responseTimes;

  return services.map(([service, count]) => ({
    service,
    detect: Math.max(1, Math.min(10, count * 2)),
    ack: Math.max(2, Math.min(15, count * 3)),
    resolve: Math.max(15, Math.round((incidents.find((incident) => incident.service === service)?.mttr_minutes ?? 30) + count * 4)),
  }));
}

function buildAnalyticsTimeline(incidents) {
  if (!incidents.length) return mockData.analytics.timeline;

  return incidents.slice(0, 5).map((incident) => ({
    time: formatTime(incident.updatedAt ?? incident.createdAt),
    event: `${incident.status} ${incident.id}: ${incident.title}`,
    type: incident.status === "Escalated" ? "escalation" : incident.status === "Resolved" ? "mitigation" : "detection",
  }));
}

function buildServiceHealth(services) {
  if (!services.length) return mockData.analytics.serviceHealth;

  return services.map(([service, events]) => ({
    service,
    health: Math.max(65, 100 - events * 7),
    events,
    slo: Math.max(90, 99.5 - events),
  }));
}

async function request(path, fallback, options = {}) {
  if (!API_BASE_URL) {
    await wait(MOCK_LATENCY_MS);
    return fallback;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers ?? {}),
      },
      ...options,
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

export async function getIncidents() {
  const payload = await request("/incidents", mockData.incidents);
  return normalizeIncidents(payload);
}

export async function getIncident(id) {
  const fallback = mockData.incidents.find((incident) => incident.id === id) ?? mockData.incidents[0];
  const payload = await request(`/incidents/${id}`, { success: true, incident: fallback });
  return normalizeIncident(payload?.incident ?? payload);
}

export async function getAnalytics() {
  const [payload, incidents] = await Promise.all([
    request("/analytics", mockData.analytics),
    getIncidents(),
  ]);

  return normalizeAnalytics(payload, incidents);
}

export async function getAnalyticsStats() {
  const [payload, incidents] = await Promise.all([
    request("/analytics/stats", mockData.stats),
    getIncidents(),
  ]);

  return normalizeStats(payload, incidents);
}

export async function updateIncidentStatus(id, action) {
  const actionPath = action.toLowerCase();
  const body = actionPath === "resolve" ? { note: "Resolved from dashboard" } : { actor: "Dashboard User" };
  const payload = await request(`/incidents/${id}/${actionPath}`, null, {
    method: "PUT",
    body: JSON.stringify(body),
  });

  return normalizeIncident(payload?.incident ?? payload);
}

export async function getDashboardData() {
  const incidents = await getIncidents();
  const [analyticsPayload, statsPayload] = await Promise.all([
    request("/analytics", mockData.analytics),
    request("/analytics/stats", mockData.stats),
  ]);

  return {
    incidents,
    analytics: normalizeAnalytics(analyticsPayload, incidents),
    stats: normalizeStats(statsPayload, incidents),
  };
}
