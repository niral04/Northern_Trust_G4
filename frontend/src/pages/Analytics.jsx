import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { CalendarRange, FileDown } from "lucide-react";
import IncidentTrendChart from "@/components/analytics/IncidentTrendChart";
import ResponseTimeChart from "@/components/analytics/ResponseTimeChart";
import ServiceHealthTable from "@/components/analytics/ServiceHealthTable";
import SeverityBarChart from "@/components/analytics/SeverityBarChart";
import LoadingState from "@/components/shared/LoadingState";
import PageHeader from "@/components/shared/PageHeader";
import StatCard from "@/components/shared/StatCard";
import { Button } from "@/components/ui/button";
import { getAnalytics, getAnalyticsStats } from "@/services/api";
import { AlarmClock, Bot, Gauge, ShieldCheck } from "lucide-react";
import { formatPercent } from "@/lib/utils";

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    let mounted = true;

    Promise.all([getAnalytics(), getAnalyticsStats()]).then(([analyticsPayload, statsPayload]) => {
      if (mounted) {
        setAnalytics(analyticsPayload);
        setStats(statsPayload);
      }
    });

    return () => {
      mounted = false;
    };
  }, []);

  if (!analytics || !stats) {
    return <LoadingState label="Loading analytics" />;
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <PageHeader
        eyebrow="Analytics"
        title="Incident Intelligence"
        description="Operational patterns, response performance, and service reliability from the event stream."
        actions={
          <>
            <Button variant="outline">
              <CalendarRange className="size-4" />
              Last 24h
            </Button>
            <Button>
              <FileDown className="size-4" />
              Report
            </Button>
          </>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="MTTR"
          value={`${stats.mttrMinutes}m`}
          delta="-8.1%"
          deltaTone="negative"
          detail="rolling mean"
          icon={AlarmClock}
          accent="text-cyan-300"
        />
        <StatCard
          title="Automation Coverage"
          value={formatPercent(stats.automationRate)}
          delta="+5.4%"
          detail="runbook assisted"
          icon={Bot}
          accent="text-emerald-300"
        />
        <StatCard
          title="SLA Compliance"
          value={formatPercent(stats.slaCompliance)}
          delta="+1.2%"
          detail="24h window"
          icon={ShieldCheck}
          accent="text-violet-300"
        />
        <StatCard
          title="Risk Index"
          value="28"
          delta="-6 pts"
          deltaTone="negative"
          detail="weighted score"
          icon={Gauge}
          accent="text-orange-300"
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.4fr)_minmax(340px,0.8fr)]">
        <IncidentTrendChart data={analytics.trend} />
        <SeverityBarChart data={analytics.severityDistribution} />
      </div>

      <ResponseTimeChart data={analytics.responseTimes} />
      <ServiceHealthTable services={analytics.serviceHealth} />
    </motion.div>
  );
}
