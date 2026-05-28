import { motion } from "framer-motion";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export default function StatCard({
  title,
  value,
  delta,
  deltaTone = "positive",
  icon: Icon,
  accent = "text-primary",
  detail,
}) {
  const DeltaIcon = deltaTone === "negative" ? ArrowDownRight : ArrowUpRight;

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
    >
      <Card className="overflow-hidden">
        <CardContent className="p-5">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <p className="text-sm text-muted-foreground">{title}</p>
              <p className="mt-3 text-3xl font-semibold tracking-normal">{value}</p>
            </div>
            {Icon ? (
              <div className={cn("rounded-md border border-border bg-muted p-2.5", accent)}>
                <Icon className="size-5" />
              </div>
            ) : null}
          </div>
          <div className="mt-4 flex flex-wrap items-center gap-2 text-sm">
            {delta ? (
              <span
                className={cn(
                  "inline-flex items-center gap-1 rounded-md px-2 py-1 font-medium",
                  deltaTone === "negative"
                    ? "bg-emerald-500/10 text-emerald-300"
                    : "bg-orange-500/10 text-orange-300",
                )}
              >
                <DeltaIcon className="size-3.5" />
                {delta}
              </span>
            ) : null}
            {detail ? <span className="text-muted-foreground">{detail}</span> : null}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
