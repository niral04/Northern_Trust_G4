import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

function formatCountdown(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

export default function EscalationCountdown({
  incidentId,
  remainingSeconds = 0,
  status,
  className,
}) {
  const [seconds, setSeconds] = useState(remainingSeconds ?? 0);
  const active = ["open", "acknowledged"].includes((status || "").toLowerCase());

  useEffect(() => {
    setSeconds(remainingSeconds ?? 0);
  }, [remainingSeconds, incidentId]);

  useEffect(() => {
    if (!active || seconds <= 0) {
      return undefined;
    }

    const timer = window.setInterval(() => {
      setSeconds((current) => Math.max(0, current - 1));
    }, 1000);

    return () => window.clearInterval(timer);
  }, [active, seconds, incidentId]);

  if (!active) {
    return null;
  }

  const isUrgent = seconds > 0 && seconds < 60;
  const isCritical = seconds > 0 && seconds < 30;

  return (
    <span
      className={cn(
        "font-mono text-xs font-semibold",
        isCritical && "animate-pulse text-red-400",
        isUrgent && !isCritical && "text-orange-400",
        !isUrgent && "text-zinc-300",
        className,
      )}
      title={`Incident ${incidentId}`}
    >
      Escalates in: {formatCountdown(seconds)}
    </span>
  );
}
