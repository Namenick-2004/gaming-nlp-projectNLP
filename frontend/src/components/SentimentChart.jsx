import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import AnalysisPanel, { sentimentLabels, sentimentColors, percent } from "./AnalysisPanel.jsx";

export default function SentimentChart({ data, language = "th" }) {
  if (!data) return null;
  const en = language === "en";
  const labels = sentimentLabels[en ? "en" : "th"];
  const items = Object.keys(labels).map((key) => ({ key, name: labels[key], value: data[key] || 0 }));
  const top = [...items].sort((a, b) => b.value - a.value)[0];
  return <AnalysisPanel title={en ? "Audience sentiment" : "ภาพรวมความรู้สึก"} subtitle={en ? "Share of analyzed comments" : "สัดส่วนจากความคิดเห็นที่นำมาวิเคราะห์"} badge={`${data.sample_size ?? 0} ${en ? "comments" : "ความคิดเห็น"}`}>
    <div className="relative mx-auto h-56 max-w-xs">
      <ResponsiveContainer width="100%" height="100%"><PieChart>
        <Pie data={items} dataKey="value" nameKey="name" innerRadius={72} outerRadius={94} paddingAngle={2} stroke="none" startAngle={90} endAngle={-270}>
          {items.map((item) => <Cell key={item.key} fill={sentimentColors[item.key]} />)}
        </Pie>
        <Tooltip formatter={percent} contentStyle={{ borderRadius: 12, border: "1px solid #e2e8f0", color: "#0f172a" }} />
      </PieChart></ResponsiveContainer>
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold tabular-nums tracking-tight text-slate-900">{percent(top.value)}</span>
        <span className="mt-1 text-sm text-slate-500">{top.value ? top.name : (en ? "No data" : "ยังไม่มีข้อมูล")}</span>
      </div>
    </div>
    <ul className="mt-4 grid grid-cols-3 divide-x divide-slate-100 rounded-xl border border-slate-100 bg-slate-50 py-4">
      {items.map((item) => <li key={item.key} className="text-center">
        <div className="mb-2 flex items-center justify-center gap-1.5 text-xs text-slate-600"><span className="h-2 w-2 rounded-full" style={{ background: sentimentColors[item.key] }} />{item.name}</div>
        <strong className="text-lg tabular-nums text-slate-900">{percent(item.value)}</strong>
      </li>)}
    </ul>
  </AnalysisPanel>;
}
