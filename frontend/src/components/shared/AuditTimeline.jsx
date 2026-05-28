import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

const toneByType = {
  escalation: "border-orange-500/40 bg-orange-500/10 text-orange-200",
  AUTO_ESCALATED: "border-orange-500/40 bg-orange-500/10 text-orange-200",
  ESCALATED: "border-orange-500/40 bg-orange-500/10 text-orange-200",
  mitigation: "border-emerald-500/40 bg-emerald-500/10 text-emerald-200",
  RESOLVED: "border-emerald-500/40 bg-emerald-500/10 text-emerald-200",
  acknowledgement: "border-yellow-500/40 bg-yellow-500/10 text-yellow-200",
  ACKNOWLEDGED: "border-yellow-500/40 bg-yellow-500/10 text-yellow-200",
  invalid: "border-red-500/40 bg-red-500/10 text-red-200",
  INVALID_TRANSITION_ATTEMPT: "border-red-500/40 bg-red-500/10 text-red-200",
  detection: "border-violet-500/40 bg-violet-500/10 text-violet-200",
};

function resolveTone(event) {
  const key = event.type || event.event_type;
  return toneByType[key] ?? toneByType.detection;
}

export default function AuditTimeline({ events = [], title = "Audit Timeline" }) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
      <AnimatePresence initial={false}>
        {events.map((event, index) => (
          <motion.div
            key={event.id ?? `${event.timestamp}-${event.event_type}-${index}`}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex gap-3"
          >
            <div
              className={cn(
                "mt-1 h-2 w-2 shrink-0 rounded-full border",
                resolveTone(event),
              )}
            />
            <div className="flex-1 border-b border-border/50 pb-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-medium">
                    {event.event_type || event.action || event.event}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {event.description || event.action}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Actor: {event.actor || event.user || "system"}
                  </p>
                  {(event.previous_assignee || event.new_assignee) && (
                    <p className="text-xs text-muted-foreground">
                      {event.previous_assignee ?? "—"} → {event.new_assignee ?? "—"}
                      {event.escalation_level != null
                        ? ` · Level ${event.escalation_level}`
                        : ""}
                    </p>
                  )}
                </div>
                <span className="font-mono text-xs text-muted-foreground">
                  {event.time || event.timestamp}
                </span>
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
