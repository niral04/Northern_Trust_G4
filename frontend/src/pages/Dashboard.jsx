import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Download, RadioTower } from "lucide-react";
import EventTimeline from "@/components/dashboard/EventTimeline";
import IncidentFeed from "@/components/dashboard/IncidentFeed";
import KpiGrid from "@/components/dashboard/KpiGrid";
import SeverityDonut from "@/components/dashboard/SeverityDonut";
import SystemHealth from "@/components/dashboard/SystemHealth";
import LoadingState from "@/components/shared/LoadingState";
import PageHeader from "@/components/shared/PageHeader";
import { Button } from "@/components/ui/button";
import { getDashboardData } from "@/services/api";

export default function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    let mounted = true;

    getDashboardData().then((payload) => {
      if (mounted) {
        setData(payload);
      }
    });

    return () => {
      mounted = false;
    };
  }, []);

  if (!data) {
    return <LoadingState />;
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <PageHeader
        eyebrow="Ops Overview"
        title="Event-Driven Incident Management"
        description="A real-time command center for alert classification, incident routing, escalation, and operational analytics."
        actions={
          <>
            <Button variant="outline">
              <Download className="size-4" />
              Export
            </Button>
            <Button>
              <RadioTower className="size-4" />
              Stream Live
            </Button>
          </>
        }
      />

      <KpiGrid stats={data.stats} />

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.5fr)_minmax(360px,0.8fr)]">
        <IncidentFeed incidents={data.incidents} />
        <div className="grid gap-6">
          <SeverityDonut data={data.analytics.severityDistribution} />
          <EventTimeline events={data.analytics.timeline} />
          <SystemHealth services={data.analytics.serviceHealth} />
        </div>
      </div>
    </motion.div>
  );
}
