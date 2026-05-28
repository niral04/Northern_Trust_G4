import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const statusClasses = {
  Open: "border-red-500/30 bg-red-500/10 text-red-300",
  Investigating: "border-amber-500/30 bg-amber-500/10 text-amber-200",
  Mitigated: "border-cyan-500/30 bg-cyan-500/10 text-cyan-200",
  Resolved: "border-emerald-500/30 bg-emerald-500/10 text-emerald-200",
};

export default function StatusBadge({ status }) {
  return (
    <Badge variant="outline" className={cn("font-mono", statusClasses[status] ?? statusClasses.Open)}>
      {status}
    </Badge>
  );
}
