import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { formatCompactNumber, formatPercent } from "@/lib/utils";

function healthTone(value) {
  if (value < 78) return "bg-red-500";
  if (value < 86) return "bg-orange-500";
  return "bg-emerald-500";
}

export default function SystemHealth({ services }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Service Health</CardTitle>
        <p className="text-sm text-muted-foreground">Live operational posture by service</p>
      </CardHeader>
      <CardContent className="space-y-4">
        {services.map((service) => (
          <div key={service.service} className="space-y-2">
            <div className="flex items-center justify-between gap-3 text-sm">
              <span className="truncate font-medium">{service.service}</span>
              <span className="font-mono text-muted-foreground">{service.health}%</span>
            </div>
            <Progress value={service.health} indicatorClassName={healthTone(service.health)} />
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>{formatCompactNumber(service.events)} events</span>
              <span>{formatPercent(service.slo)} SLO</span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
