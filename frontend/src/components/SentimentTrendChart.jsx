import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip, Legend, CartesianGrid } from "recharts";

export default function SentimentTrendChart({ data }) {
  if (!data || data.length === 0) return null;
  return (
    <div className="glass-card p-4">
      <h3 className="font-semibold mb-2">📈 Sentiment Trend Over Time</h3>
      <p className="text-xs text-slate-400 mb-2">Compare snapshots to see how sentiment shifted after a patch/update.</p>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e2740" />
          <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 10 }} tickFormatter={(d) => new Date(d).toLocaleDateString()} />
          <YAxis tick={{ fill: "#94a3b8", fontSize: 10 }} />
          <Tooltip contentStyle={{ background: "#151b2e", border: "none", borderRadius: 8 }} />
          <Legend />
          <Line type="monotone" dataKey="positive" stroke="#22c55e" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="neutral" stroke="#94a3b8" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="negative" stroke="#ef4444" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
