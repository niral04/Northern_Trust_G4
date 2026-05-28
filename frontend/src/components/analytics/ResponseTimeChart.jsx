import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function ResponseTimeChart({ data }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Response Time by Service</CardTitle>
        <p className="text-sm text-muted-foreground">Detection, acknowledgement, and resolution in minutes</p>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ left: -22, right: 12, top: 10, bottom: 0 }}>
              <CartesianGrid stroke="#27272f" strokeDasharray="4 4" vertical={false} />
              <XAxis dataKey="service" stroke="#a1a1aa" tickLine={false} axisLine={false} />
              <YAxis stroke="#a1a1aa" tickLine={false} axisLine={false} />
              <Tooltip
                cursor={{ fill: "rgba(255,255,255,0.04)" }}
                contentStyle={{
                  background: "#15151a",
                  border: "1px solid #27272f",
                  borderRadius: 8,
                  color: "#fafafa",
                }}
              />
              <Legend iconType="circle" />
              <Bar dataKey="detect" name="Detect" fill="#22d3ee" radius={[6, 6, 0, 0]} />
              <Bar dataKey="ack" name="Ack" fill="#f59e0b" radius={[6, 6, 0, 0]} />
              <Bar dataKey="resolve" name="Resolve" fill="#ef4444" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
