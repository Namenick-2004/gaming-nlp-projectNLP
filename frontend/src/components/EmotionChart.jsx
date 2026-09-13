import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from "recharts";

const EMOJI = { joy: "😊", anger: "😡", surprise: "😮", sadness: "😢", fear: "😨", neutral: "😐" };
const COLORS = { joy: "#facc15", anger: "#ef4444", surprise: "#38bdf8", sadness: "#818cf8", fear: "#a855f7", neutral: "#94a3b8" };

export default function EmotionChart({ data }) {
  if (!data) return null;
  const chartData = Object.keys(EMOJI).map((k) => ({ name: `${EMOJI[k]} ${k}`, key: k, value: data[k] ?? 0 }));

  return (
    <div className="glass-card p-4">
      <h3 className="font-semibold mb-2">❤️ Emotion Analysis</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 10 }}>
          <XAxis type="number" hide domain={[0, 100]} />
          <YAxis type="category" dataKey="name" width={90} tick={{ fill: "#cbd5e1", fontSize: 12 }} />
          <Tooltip formatter={(v) => `${v}%`} contentStyle={{ background: "#151b2e", border: "none", borderRadius: 8 }} />
          <Bar dataKey="value" radius={[0, 6, 6, 0]}>
            {chartData.map((entry) => (
              <Cell key={entry.key} fill={COLORS[entry.key]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-slate-400 text-center">Based on {data.sample_size} comments</p>
    </div>
  );
}
