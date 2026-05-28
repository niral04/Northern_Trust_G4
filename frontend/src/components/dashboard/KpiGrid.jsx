import { Activity, AlarmClock, Bot, Flame, RadioTower, ShieldCheck } from "lucide-react";
import StatCard from "@/components/shared/StatCard";
import { formatCompactNumber, formatPercent } from "@/lib/utils";

export default function KpiGrid({ stats }) {
  const cards = [
    {
      title: "Active Incidents",
      value: stats.activeIncidents,
      delta: "+12.5%",
      detail: "vs last hour",
      icon: Flame,
      accent: "text-orange-300",
    },
    {
      title: "Critical",
      value: stats.criticalIncidents,
      delta: "+2 new",
      detail: "needs action",
      icon: Activity,
      accent: "text-red-300",
    },
    {
      title: "Mean Time To Resolve",
      value: `${stats.mttrMinutes}m`,
      delta: "-8.1%",
      deltaTone: "negative",
      detail: "faster today",
      icon: AlarmClock,
      accent: "text-cyan-300",
    },
    {
      title: "Automation Rate",
      value: formatPercent(stats.automationRate),
      delta: "+5.4%",
      detail: "auto-triaged",
      icon: Bot,
      accent: "text-emerald-300",
    },
    {
      title: "Events / Minute",
      value: formatCompactNumber(stats.eventsPerMinute),
      delta: "+18%",
      detail: "stream volume",
      icon: RadioTower,
      accent: "text-sky-300",
    },
    {
      title: "SLA Compliance",
      value: formatPercent(stats.slaCompliance),
      delta: "+1.2%",
      detail: "rolling 24h",
      icon: ShieldCheck,
      accent: "text-violet-300",
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {cards.map((card) => (
        <StatCard key={card.title} {...card} />
      ))}
    </div>
  );
}
