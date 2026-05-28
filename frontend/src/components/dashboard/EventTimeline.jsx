import { Bot, GitBranch, Radar, ShieldCheck, AlertTriangle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const iconMap = {
  automation: Bot,
  escalation: GitBranch,
  mitigation: ShieldCheck,
  detection: Radar,
  acknowledgement: ShieldCheck,
  invalid: AlertTriangle,
  ESCALATED: GitBranch,
  AUTO_ESCALATED: GitBranch,
  ACKNOWLEDGED: ShieldCheck,
  RESOLVED: ShieldCheck,
  INVALID_TRANSITION_ATTEMPT: AlertTriangle,
};

const toneMap = {
  automation: "text-cyan-300 bg-cyan-500/10 border-cyan-500/30",
  escalation: "text-orange-300 bg-orange-500/10 border-orange-500/30",
  mitigation: "text-emerald-300 bg-emerald-500/10 border-emerald-500/30",
  detection: "text-violet-300 bg-violet-500/10 border-violet-500/30",
  acknowledgement: "text-yellow-300 bg-yellow-500/10 border-yellow-500/30",
  invalid: "text-red-300 bg-red-500/10 border-red-500/30",
};

function resolveType(event) {
  return event.type ?? event.event_type ?? "detection";
}

export default function EventTimeline({ events = [] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Event Stream</CardTitle>
        <p className="text-sm text-muted-foreground">Live classifier, escalation, and audit activity</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <AnimatePresence initial={false}>
            {events.map((event, index) => {
              const type = resolveType(event);
              const Icon = iconMap[type] ?? Radar;

              return (
                <motion.div
                  key={event.id ?? `${event.time}-${event.event}-${index}`}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex gap-3"
                >
                  <div className={cn("grid size-9 shrink-0 place-items-center rounded-md border", toneMap[type] ?? toneMap.detection)}>
                    <Icon className="size-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-3">
                      <p className="truncate text-sm font-medium">
                        {event.event_type ?? event.event ?? event.action}
                      </p>
                      <span className="font-mono text-xs text-muted-foreground">
                        {event.time ?? event.timestamp}
                      </span>
                    </div>
                    <p className="mt-1 truncate text-xs text-muted-foreground">
                      {event.description ?? event.action} · {event.actor ?? event.user ?? "system"}
                    </p>
                    <div className="mt-2 h-px bg-border" />
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      </CardContent>
    </Card>
  );
}
