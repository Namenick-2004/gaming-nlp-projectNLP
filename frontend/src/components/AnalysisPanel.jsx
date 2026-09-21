export const sentimentLabels = {
  th: { positive: "เชิงบวก", neutral: "เป็นกลาง", negative: "เชิงลบ" },
  en: { positive: "Positive", neutral: "Neutral", negative: "Negative" },
};
export const sentimentColors = { positive: "#059669", neutral: "#94a3b8", negative: "#e11d48" };
export const percent = (value) => `${Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 1 })}%`;

export default function AnalysisPanel({ title, subtitle, badge, children, className = "" }) {
  return <section className={`min-w-0 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6 ${className}`}>
    <div className="mb-6 flex items-start justify-between gap-3">
      <div><h2 className="text-base font-bold tracking-tight text-slate-900">{title}</h2>
        {subtitle && <p className="mt-1.5 text-xs leading-5 text-slate-500">{subtitle}</p>}</div>
      {badge && <span className="shrink-0 rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-semibold tabular-nums text-slate-600">{badge}</span>}
    </div>{children}
  </section>;
}

export function MetricBars({ items }) {
  return <ul className="space-y-4">{items.map((item) => <li key={item.key}>
    <div className="mb-2 flex items-center justify-between gap-3 text-sm">
      <span className="font-medium text-slate-700">{item.name}</span>
      <span className="font-semibold tabular-nums text-slate-900">{percent(item.value)}</span>
    </div>
    <div className="h-2 overflow-hidden rounded-full bg-slate-100" aria-hidden="true">
      <div className="h-full rounded-full" style={{ width: `${Math.min(100, Math.max(0, item.value || 0))}%`, background: item.color || '#6366f1' }} />
    </div>
  </li>)}</ul>;
}
