import { Bot, GitBranch, Radar, ShieldCheck } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const iconMap = {
  automation: Bot,
  escalation: GitBranch,
  mitigation: ShieldCheck,
  detection: Radar,
};

const toneMap = {
  automation: "text-cyan-300 bg-cyan-500/10 border-cyan-500/30",
  escalation: "text-orange-300 bg-orange-500/10 border-orange-500/30",
  mitigation: "text-emerald-300 bg-emerald-500/10 border-emerald-500/30",
  detection: "text-violet-300 bg-violet-500/10 border-violet-500/30",
};

export default function EventTimeline({ events }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Event Stream</CardTitle>
        <p className="text-sm text-muted-foreground">Latest classifier and escalation activity</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {events.map((event) => {
            const Icon = iconMap[event.type] ?? Radar;

            return (
              <div key={`${event.time}-${event.event}`} className="flex gap-3">
                <div className={cn("grid size-9 shrink-0 place-items-center rounded-md border", toneMap[event.type])}>
                  <Icon className="size-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-3">
                    <p className="truncate text-sm font-medium">{event.event}</p>
                    <span className="font-mono text-xs text-muted-foreground">{event.time}</span>
                  </div>
                  <div className="mt-2 h-px bg-border" />
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
