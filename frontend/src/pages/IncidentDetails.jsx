import { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Clock, User, Server, AlertTriangle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import SeverityBadge from "@/components/shared/SeverityBadge";
import StatusBadge from "@/components/shared/StatusBadge";
import LoadingState from "@/components/shared/LoadingState";
import EscalationCountdown from "@/components/shared/EscalationCountdown";
import AuditTimeline from "@/components/shared/AuditTimeline";
import { useToast } from "@/context/ToastContext";
import { useIncidentWebSocket } from "@/hooks/useIncidentWebSocket";
import {
  acknowledgeIncident,
  escalateIncident,
  getIncidentById,
  getIncidentTimeline,
  resolveIncident,
} from "@/services/api";

export default function IncidentDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { pushToast } = useToast();

  const [incident, setIncident] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("timeline");

  const loadIncident = useCallback(async () => {
    setLoading(true);
    try {
      const [incidentData, timelineData] = await Promise.all([
        getIncidentById(id),
        getIncidentTimeline(id),
      ]);

      if (incidentData) {
        setIncident({
          ...incidentData,
          id: incidentData.incident_id ?? incidentData.id ?? id,
          title: incidentData.title ?? incidentData.message,
          service: incidentData.service ?? incidentData.source,
          owner: incidentData.owner ?? incidentData.assignee,
          createdAt: incidentData.createdAt ?? incidentData.created_at,
          description: incidentData.message ?? incidentData.description,
          classificationReason: `Classified as ${incidentData.severity} ${incidentData.alert_type ?? ""} incident`,
        });
      }

      setTimeline(Array.isArray(timelineData) ? timelineData : []);
    } catch (error) {
      console.error(error);
      pushToast("Failed to load incident", "danger");
    } finally {
      setLoading(false);
    }
  }, [id, pushToast]);

  useEffect(() => {
    loadIncident();
  }, [loadIncident]);

  const patchIncident = useCallback((incidentId, patch) => {
    if (incidentId !== id && incidentId !== incident?.incident_id) {
      return;
    }
    setIncident((current) => (current ? { ...current, ...patch, status: patch.status ?? current.status } : current));
  }, [id, incident?.incident_id]);

  const onTimelineEvent = useCallback((event) => {
    if (event.incident_id !== id && event.incident_id !== incident?.incident_id) {
      return;
    }
    setTimeline((current) => [...current, event]);
  }, [id, incident?.incident_id]);

  useIncidentWebSocket({
    enabled: Boolean(import.meta.env.VITE_API_BASE_URL),
    onIncidentPatch: patchIncident,
    onTimelineEvent,
  });

  const handleAction = async (action) => {
    try {
      if (action === "Acknowledge") {
        await acknowledgeIncident(id);
        pushToast("Incident acknowledged", "success");
      }
      if (action === "Escalate") {
        await escalateIncident(id);
        pushToast("Incident escalated", "warning");
      }
      if (action === "Resolve") {
        await resolveIncident(id);
        pushToast("Incident resolved", "success");
      }
      await loadIncident();
    } catch (error) {
      pushToast(error.message || `${action} failed`, "danger");
    }
  };

  if (loading) return <LoadingState />;

  if (!incident) {
    return (
      <div className="py-20 text-center">
        Incident not found
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate("/incidents")}
        className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Incidents
      </button>

      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-sm text-muted-foreground">
                  {incident.id}
                </span>
                <SeverityBadge severity={incident.severity} />
                <StatusBadge status={incident.status} />
                <EscalationCountdown
                  incidentId={incident.id}
                  remainingSeconds={incident.remaining_seconds}
                  status={incident.status}
                />
              </div>

              <h1 className="text-2xl font-bold">{incident.title}</h1>
              <p className="text-muted-foreground">{incident.description}</p>
            </div>

            <div className="flex gap-2">
              <Button
                className="bg-blue-600 hover:bg-blue-700"
                onClick={() => handleAction("Acknowledge")}
              >
                Acknowledge
              </Button>
              <Button
                className="bg-red-600 hover:bg-red-700"
                onClick={() => handleAction("Escalate")}
              >
                Escalate
              </Button>
              <Button
                className="bg-green-600 hover:bg-green-700"
                onClick={() => handleAction("Resolve")}
              >
                Resolve
              </Button>
            </div>
          </div>

          <div className="mt-6 grid gap-4 border-t pt-6 sm:grid-cols-2 lg:grid-cols-4">
            <div className="flex items-center gap-2">
              <Server className="h-4 w-4" />
              <div>
                <p className="text-xs text-muted-foreground">Service</p>
                <p className="text-sm font-medium">{incident.service}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <User className="h-4 w-4" />
              <div>
                <p className="text-xs text-muted-foreground">Owner</p>
                <p className="text-sm font-medium">{incident.owner}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              <div>
                <p className="text-xs text-muted-foreground">Created</p>
                <p className="text-sm font-medium">
                  {new Date(incident.createdAt).toLocaleString()}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              <div>
                <p className="text-xs text-muted-foreground">Classification</p>
                <p className="truncate text-sm font-medium">
                  {incident.classificationReason}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="border-b">
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab("timeline")}
            className={`pb-3 text-sm font-medium ${
              activeTab === "timeline"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground"
            }`}
          >
            📜 Audit Timeline
          </button>
          <button
            onClick={() => setActiveTab("escalation")}
            className={`pb-3 text-sm font-medium ${
              activeTab === "escalation"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground"
            }`}
          >
            ⬆️ Escalation Level {incident.escalation_level ?? 0}
          </button>
        </div>
      </div>

      {activeTab === "timeline" && (
        <Card>
          <CardHeader>
            <CardTitle>Enterprise Audit Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <AuditTimeline events={timeline} />
          </CardContent>
        </Card>
      )}

      {activeTab === "escalation" && (
        <Card>
          <CardHeader>
            <CardTitle>Escalation Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Current assignee: <strong>{incident.assignee ?? incident.owner}</strong>
            </p>
            <p className="text-sm text-muted-foreground">
              Escalation level: <strong>{incident.escalation_level ?? 0}</strong>
            </p>
            <EscalationCountdown
              incidentId={incident.id}
              remainingSeconds={incident.remaining_seconds}
              status={incident.status}
              className="text-base"
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
