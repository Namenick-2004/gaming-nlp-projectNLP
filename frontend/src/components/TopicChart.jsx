import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";

export default function TopicChart({ data }) {
  if (!data || !data.categories?.length) return null;
  const chartData = data.categories.map((c) => ({ name: c.category, value: c.percentage }));

  return (
    <div className="glass-card p-4">
      <h3 className="font-semibold mb-2">🗂️ Topic Analysis</h3>
      <ResponsiveContainer width="100%" height={Math.max(180, chartData.length * 32)}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 10 }}>
          <XAxis type="number" hide domain={[0, 100]} />
          <YAxis type="category" dataKey="name" width={90} tick={{ fill: "#cbd5e1", fontSize: 12 }} />
          <Tooltip formatter={(v) => `${v}%`} contentStyle={{ background: "#151b2e", border: "none", borderRadius: 8 }} />
          <Bar dataKey="value" fill="#3b82f6" radius={[0, 6, 6, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
