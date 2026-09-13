import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

const COLORS = { positive: "#22c55e", neutral: "#94a3b8", negative: "#ef4444" };

export default function SentimentChart({ data }) {
  if (!data) return null;
  const chartData = [
    { name: "Positive", value: data.positive, key: "positive" },
    { name: "Neutral", value: data.neutral, key: "neutral" },
    { name: "Negative", value: data.negative, key: "negative" },
  ];

  return (
    <div className="glass-card p-4">
      <h3 className="font-semibold mb-2">😊 Sentiment Analysis</h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={chartData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={2}>
            {chartData.map((entry) => (
              <Cell key={entry.key} fill={COLORS[entry.key]} />
            ))}
          </Pie>
          <Tooltip formatter={(v) => `${v}%`} contentStyle={{ background: "#151b2e", border: "none", borderRadius: 8 }} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      <p className="text-xs text-slate-400 text-center">Based on {data.sample_size} comments</p>
    </div>
  );
}
