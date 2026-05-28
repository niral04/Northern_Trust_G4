import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import IncidentCard from "@/components/dashboard/IncidentCard";

export default function IncidentFeed({ incidents }) {
  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <div>
          <CardTitle>Active Incident Queue</CardTitle>

          <p className="mt-1 text-sm text-muted-foreground">
            Prioritized by severity and freshness
          </p>
        </div>

        <span className="rounded-md border border-red-500/30 bg-red-500/10 px-2.5 py-1 font-mono text-xs text-red-200">
          {incidents.length} open
        </span>
      </CardHeader>

      <CardContent className="space-y-3">
        {incidents.map((incident) => (
          <Link
            key={incident.id}
            to={`/incidents/${incident.id}`}
            className="block"
          >
            <IncidentCard incident={incident} />
          </Link>
        ))}
      </CardContent>
    </Card>
  );
}