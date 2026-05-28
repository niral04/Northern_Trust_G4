import { Link } from "react-router-dom";
import EscalationCountdown from "@/components/shared/EscalationCountdown";

export default function IncidentCard({ incident, linkWrapper = true }) {
  const incidentKey = incident.incident_id ?? incident.id;

  const content = (
    <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-6 transition-all hover:border-orange-500">
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <span className="font-mono text-sm text-zinc-400">
          {incidentKey}
        </span>

        <span className="rounded-md bg-red-500/20 px-2 py-1 text-xs text-red-300">
          {incident.severity}
        </span>

        <span className="rounded-md bg-yellow-500/20 px-2 py-1 text-xs text-yellow-300">
          {incident.status}
        </span>

        {incident.escalation_level != null && (
          <span className="rounded-md bg-orange-500/20 px-2 py-1 text-xs text-orange-300">
            L{incident.escalation_level}
          </span>
        )}

        <EscalationCountdown
          incidentId={incidentKey}
          remainingSeconds={incident.remaining_seconds}
          status={incident.status}
          className="ml-auto"
        />
      </div>

      <h2 className="mb-2 text-2xl font-semibold text-white">
        {incident.title ?? incident.message}
      </h2>

      <p className="text-zinc-400">
        Service: {incident.service ?? incident.source} · Owner: {incident.assignee ?? incident.owner}
      </p>
    </div>
  );

  if (!linkWrapper) {
    return content;
  }

  return (
    <Link to={`/incidents/${incidentKey}`} className="block cursor-pointer">
      {content}
    </Link>
  );
}
