import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Clock, User, Server, AlertTriangle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import SeverityBadge from "@/components/shared/SeverityBadge";
import StatusBadge from "@/components/shared/StatusBadge";
import LoadingState from "@/components/shared/LoadingState";
import { getIncident, updateIncidentStatus } from "@/services/api";

export default function IncidentDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("timeline");

  const handleAction = async (action) => {
    try {
      const updatedIncident = await updateIncidentStatus(id, action);

      if (updatedIncident) {
        setIncident(updatedIncident);
      }
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    let mounted = true;

    setLoading(true);

    getIncident(id)
      .then((payload) => {
        if (mounted) {
          setIncident(payload);
        }
      })
      .finally(() => {
        if (mounted) {
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [id]);

  if (loading) return <LoadingState />;

  if (!incident) {
    return (
      <div className="text-center py-20">
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
              </div>

              <h1 className="text-2xl font-bold">
                {incident.title}
              </h1>

              <p className="text-muted-foreground">
                {incident.description}
              </p>
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
                <p className="text-xs text-muted-foreground">
                  Service
                </p>

                <p className="text-sm font-medium">
                  {incident.service}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <User className="h-4 w-4" />

              <div>
                <p className="text-xs text-muted-foreground">
                  Owner
                </p>

                <p className="text-sm font-medium">
                  {incident.owner}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />

              <div>
                <p className="text-xs text-muted-foreground">
                  Created
                </p>

                <p className="text-sm font-medium">
                  {new Date(incident.createdAt).toLocaleString()}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />

              <div>
                <p className="text-xs text-muted-foreground">
                  Classification
                </p>

                <p className="text-sm font-medium truncate">
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
            📜 Timeline
          </button>

          <button
            onClick={() => setActiveTab("escalation")}
            className={`pb-3 text-sm font-medium ${
              activeTab === "escalation"
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground"
            }`}
          >
            ⬆️ Escalation History
          </button>
        </div>
      </div>

      {activeTab === "timeline" && (
        <Card>
          <CardHeader>
            <CardTitle>Event Timeline</CardTitle>
          </CardHeader>

          <CardContent>
            <div className="space-y-4">
              {incident.timeline.map((event, idx) => (
                <div key={idx} className="flex gap-3">
                  <div className="h-2 w-2 rounded-full bg-primary mt-2"></div>

                  <div className="flex-1 pb-4">
                    <div className="flex justify-between">
                      <p className="font-medium">
                        {event.action}
                      </p>

                      <span className="text-xs text-muted-foreground font-mono">
                        {event.time}
                      </span>
                    </div>

                    <p className="text-sm text-muted-foreground">
                      by {event.user}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === "escalation" && (
        <Card>
          <CardHeader>
            <CardTitle>Escalation Chain</CardTitle>
          </CardHeader>

          <CardContent>
            <div className="space-y-4">
              {incident.escalationHistory.map((level, idx) => (
                <div
                  key={idx}
                  className="flex justify-between p-4 rounded-lg bg-muted/30"
                >
                  <div>
                    <p className="font-medium">
                      Level {level.level}: {level.role}
                    </p>

                    <p className="text-sm text-muted-foreground">
                      {level.person}
                    </p>
                  </div>

                  <p
                    className={`text-sm ${
                      level.status.includes("escalated")
                        ? "text-orange-500"
                        : level.status.includes("Acknowledged")
                        ? "text-green-500"
                        : "text-muted-foreground"
                    }`}
                  >
                    {level.status}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}