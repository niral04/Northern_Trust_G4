import { Activity, ArrowUpRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { formatCompactNumber, formatPercent } from "@/lib/utils";

function tone(value) {
  if (value < 78) return "bg-red-500";
  if (value < 86) return "bg-orange-500";
  return "bg-emerald-500";
}

export default function ServiceHealthTable({ services }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Service Reliability</CardTitle>
        <p className="text-sm text-muted-foreground">Operational quality by source service</p>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="text-xs uppercase text-muted-foreground">
              <tr className="border-b border-border">
                <th className="pb-3 font-medium">Service</th>
                <th className="pb-3 font-medium">Health</th>
                <th className="pb-3 font-medium">Events</th>
                <th className="pb-3 font-medium">SLO</th>
                <th className="pb-3 font-medium">Trend</th>
              </tr>
            </thead>
            <tbody>
              {services.map((service) => (
                <tr key={service.service} className="border-b border-border/70 last:border-0">
                  <td className="py-4">
                    <div className="flex items-center gap-2">
                      <Activity className="size-4 text-cyan-300" />
                      <span className="font-medium">{service.service}</span>
                    </div>
                  </td>
                  <td className="py-4">
                    <div className="flex min-w-44 items-center gap-3">
                      <Progress value={service.health} indicatorClassName={tone(service.health)} />
                      <span className="w-10 font-mono text-xs text-muted-foreground">{service.health}%</span>
                    </div>
                  </td>
                  <td className="py-4 font-mono text-muted-foreground">{formatCompactNumber(service.events)}</td>
                  <td className="py-4 font-mono text-muted-foreground">{formatPercent(service.slo)}</td>
                  <td className="py-4">
                    <span className="inline-flex items-center gap-1 rounded-md bg-emerald-500/10 px-2 py-1 text-xs text-emerald-300">
                      <ArrowUpRight className="size-3" />
                      stable
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
