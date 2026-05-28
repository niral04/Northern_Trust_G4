import { Loader2 } from "lucide-react";

export default function LoadingState({ label = "Loading telemetry" }) {
  return (
    <div className="flex min-h-[280px] items-center justify-center rounded-lg border border-border bg-card">
      <div className="flex items-center gap-3 text-sm text-muted-foreground">
        <Loader2 className="size-4 animate-spin text-primary" />
        {label}
      </div>
    </div>
  );
}
