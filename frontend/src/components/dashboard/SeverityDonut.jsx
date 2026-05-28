import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const COLORS = {
  Critical: "#ef4444",
  High: "#f97316",
  Medium: "#f59e0b",
  Low: "#22c55e",
};

export default function SeverityDonut({ data }) {
  const total = data.reduce((sum, item) => sum + item.value, 0);
  const percentageBase = total || 1;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Severity Mix</CardTitle>
        <p className="text-sm text-muted-foreground">Current open incident distribution</p>
      </CardHeader>
      <CardContent>
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Tooltip
                contentStyle={{
                  background: "#15151a",
                  border: "1px solid #27272f",
                  borderRadius: 8,
                  color: "#fafafa",
                }}
              />
              <Pie data={data} dataKey="value" innerRadius={58} outerRadius={88} paddingAngle={3}>
                {data.map((entry) => (
                  <Cell key={entry.name} fill={COLORS[entry.name]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {data.map((item) => (
            <div key={item.name} className="flex items-center justify-between rounded-md border border-border bg-muted/30 px-3 py-2">
              <span className="flex items-center gap-2 text-sm text-muted-foreground">
                <span className="size-2 rounded-full" style={{ backgroundColor: COLORS[item.name] }} />
                {item.name}
              </span>
              <span className="font-mono text-sm">{Math.round((item.value / percentageBase) * 100)}%</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
