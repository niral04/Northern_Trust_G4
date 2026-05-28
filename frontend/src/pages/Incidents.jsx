import { useCallback, useEffect, useState } from "react";
import { Search, Filter, X } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import IncidentCard from "@/components/dashboard/IncidentCard";
import LoadingState from "@/components/shared/LoadingState";
import PageHeader from "@/components/shared/PageHeader";
import { getIncidents } from "@/services/api";
import { useIncidentWebSocket } from "@/hooks/useIncidentWebSocket";

export default function Incidents() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filters, setFilters] = useState({
    severity: "all",
    status: "all",
    service: "all",
  });
  const [showFilters, setShowFilters] = useState(false);

  const loadIncidents = async () => {
    setLoading(true);
    const data = await getIncidents();
    setIncidents(data);
    setLoading(false);
  };

  useEffect(() => {
    loadIncidents();
  }, []);

  const patchIncident = useCallback((incidentId, patch) => {
    setIncidents((current) =>
      current.map((incident) =>
        (incident.id === incidentId || incident.incident_id === incidentId)
          ? { ...incident, ...patch, status: patch.status ?? incident.status }
          : incident,
      ),
    );
  }, []);

  const onDashboardUpdate = useCallback((payload) => {
    if (payload.incidents) {
      setIncidents(payload.incidents);
    }
  }, []);

  useIncidentWebSocket({
    enabled: Boolean(import.meta.env.VITE_API_BASE_URL),
    onDashboardUpdate,
    onIncidentPatch: patchIncident,
  });

  const severities = ["all", "Critical", "High", "Medium", "Low"];
  const statuses = ["all", "open", "acknowledged", "escalated", "resolved"];
  const services = ["all", ...new Set(incidents.map((i) => i.service ?? i.source).filter(Boolean))];

  const filteredIncidents = incidents.filter((incident) => {
    const title = (incident.title ?? incident.message ?? "").toLowerCase();
    const incidentId = String(incident.id ?? incident.incident_id ?? "").toLowerCase();

    if (
      searchTerm
      && !title.includes(searchTerm.toLowerCase())
      && !incidentId.includes(searchTerm.toLowerCase())
    ) {
      return false;
    }
    if (
      filters.severity !== "all"
      && incident.severity?.toLowerCase() !== filters.severity.toLowerCase()
    ) {
      return false;
    }
    if (
      filters.status !== "all"
      && incident.status?.toLowerCase() !== filters.status.toLowerCase()
    ) {
      return false;
    }
    if (
      filters.service !== "all"
      && (incident.service ?? incident.source) !== filters.service
    ) {
      return false;
    }
    return true;
  });

  const activeFilterCount =
    Object.values(filters).filter((v) => v !== "all").length
    + (searchTerm ? 1 : 0);

  const clearFilters = () => {
    setFilters({ severity: "all", status: "all", service: "all" });
    setSearchTerm("");
  };

  if (loading) return <LoadingState />;

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Incident Management"
        title="All Incidents"
        description="View, filter, and manage all incidents with live escalation countdowns"
      />

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by ID or title..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="h-10 w-full rounded-md border border-input bg-background pl-10 pr-4 text-sm"
          />
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium ${
            showFilters || activeFilterCount > 0
              ? "bg-primary text-primary-foreground"
              : "bg-secondary text-secondary-foreground"
          }`}
        >
          <Filter className="h-4 w-4" /> Filters
          {activeFilterCount > 0 && (
            <span className="ml-1 rounded-full bg-red-500 px-1.5 py-0.5 text-xs text-white">
              {activeFilterCount}
            </span>
          )}
        </button>
      </div>

      {showFilters && (
        <Card>
          <CardContent className="pt-6">
            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <label className="mb-2 block text-sm font-medium">Severity</label>
                <select
                  value={filters.severity}
                  onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  {severities.map((s) => (
                    <option key={s} value={s}>{s === "all" ? "All" : s}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium">Status</label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  {statuses.map((s) => (
                    <option key={s} value={s}>{s === "all" ? "All" : s}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium">Service</label>
                <select
                  value={filters.service}
                  onChange={(e) => setFilters({ ...filters, service: e.target.value })}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  {services.map((s) => (
                    <option key={s} value={s}>{s === "all" ? "All" : s}</option>
                  ))}
                </select>
              </div>
            </div>
            {activeFilterCount > 0 && (
              <button
                onClick={clearFilters}
                className="mt-4 flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
              >
                <X className="h-3 w-3" /> Clear all filters
              </button>
            )}
          </CardContent>
        </Card>
      )}

      <p className="text-sm text-muted-foreground">
        Showing {filteredIncidents.length} of {incidents.length} incidents
      </p>

      <div className="space-y-3">
        {filteredIncidents.map((incident) => (
          <IncidentCard
            key={incident.incident_id ?? incident.id}
            incident={incident}
          />
        ))}
      </div>

      {filteredIncidents.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <p className="text-muted-foreground">No incidents found</p>
          <button
            onClick={clearFilters}
            className="mt-2 text-sm text-primary hover:underline"
          >
            Clear filters
          </button>
        </div>
      )}
    </div>
  );
}
