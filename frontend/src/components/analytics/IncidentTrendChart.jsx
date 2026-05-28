import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function IncidentTrendChart({ data }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Incident Volume</CardTitle>
        <p className="text-sm text-muted-foreground">Severity trend across the current operating day</p>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ left: -22, right: 12, top: 10, bottom: 0 }}>
              <defs>
                <linearGradient id="criticalFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0.02} />
                </linearGradient>
                <linearGradient id="highFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f97316" stopOpacity={0.28} />
                  <stop offset="95%" stopColor="#f97316" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#27272f" strokeDasharray="4 4" vertical={false} />
              <XAxis dataKey="time" stroke="#a1a1aa" tickLine={false} axisLine={false} />
              <YAxis stroke="#a1a1aa" tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{
                  background: "#15151a",
                  border: "1px solid #27272f",
                  borderRadius: 8,
                  color: "#fafafa",
                }}
              />
              <Area type="monotone" dataKey="critical" stroke="#ef4444" fill="url(#criticalFill)" strokeWidth={2} />
              <Area type="monotone" dataKey="high" stroke="#f97316" fill="url(#highFill)" strokeWidth={2} />
              <Area type="monotone" dataKey="medium" stroke="#f59e0b" fill="transparent" strokeWidth={2} />
              <Area type="monotone" dataKey="low" stroke="#22c55e" fill="transparent" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
