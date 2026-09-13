import { TrendingUp } from "lucide-react";

const texts = {
  th: {
    title: "คำสำคัญยอดนิยม",
    times: "ครั้ง",
  },
  en: {
    title: "Top Keywords",
    times: "times",
  },
};

export default function KeywordList({ keywords, language = "th" }) {
  if (!keywords || keywords.length === 0) return null;

  const t = texts[language] || texts.th;

  return (
    <div className="glass-card overflow-hidden border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 bg-slate-50 px-5 py-4">
        <h3 className="flex items-center gap-2 text-base font-bold text-slate-900">
          <span className="text-xl">🔑</span>
          {t.title}
        </h3>
      </div>
      <div className="space-y-2 p-4">
        {keywords.map((k) => (
          <div key={k.keyword} className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5">
            <div className="min-w-0">
              <span className="block truncate font-semibold text-slate-800">{k.keyword}</span>
              <span className="text-xs text-slate-500">{k.count} {t.times}</span>
            </div>
            <span className="ml-3 inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-600">
              <TrendingUp size={12} /> +{k.trend_percent}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
