import { Clock, MapPin, RadioTower, UserRound } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import SeverityBadge from "@/components/shared/SeverityBadge";
import StatusBadge from "@/components/shared/StatusBadge";
import { formatCompactNumber } from "@/lib/utils";

function formatTime(dateString) {
  return new Intl.DateTimeFormat("en", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(dateString));
}

export default function IncidentCard({ incident }) {
  return (
    <Card className="transition hover:border-primary/40 hover:bg-muted/20">
      <CardContent className="p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-xs text-muted-foreground">{incident.id}</span>
              <SeverityBadge severity={incident.severity} />
              <StatusBadge status={incident.status} />
            </div>
            <h3 className="mt-3 text-base font-semibold tracking-normal">{incident.title}</h3>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">{incident.description}</p>
          </div>
          <div className="font-mono text-xs text-muted-foreground sm:text-right">
            <div className="flex items-center gap-1.5 sm:justify-end">
              <Clock className="size-3.5" />
              {formatTime(incident.updatedAt)}
            </div>
          </div>
        </div>

        <div className="mt-4 grid gap-2 text-xs text-muted-foreground sm:grid-cols-2 xl:grid-cols-4">
          <span className="flex min-w-0 items-center gap-2">
            <RadioTower className="size-3.5 shrink-0 text-cyan-300" />
            <span className="truncate">{incident.service}</span>
          </span>
          <span className="flex min-w-0 items-center gap-2">
            <UserRound className="size-3.5 shrink-0 text-emerald-300" />
            <span className="truncate">{incident.owner}</span>
          </span>
          <span className="flex min-w-0 items-center gap-2">
            <MapPin className="size-3.5 shrink-0 text-orange-300" />
            <span className="truncate">{incident.region}</span>
          </span>
          <span className="font-mono">{formatCompactNumber(incident.signals)} signals</span>
        </div>
      </CardContent>
    </Card>
  );
}
