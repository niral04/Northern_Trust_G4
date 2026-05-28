import { AlertTriangle, Info, ShieldAlert, SignalHigh } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn, severityColor } from "@/lib/utils";

const iconMap = {
  Critical: ShieldAlert,
  High: AlertTriangle,
  Medium: SignalHigh,
  Low: Info,
  Info,
};

export default function SeverityBadge({ severity }) {
  const Icon = iconMap[severity] ?? Info;

  return (
    <Badge variant="outline" className={cn("gap-1.5", severityColor(severity))}>
      <Icon className="size-3" />
      {severity}
    </Badge>
  );
}
