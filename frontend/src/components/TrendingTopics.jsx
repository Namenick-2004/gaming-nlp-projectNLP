import { Flame } from "lucide-react";

export default function TrendingTopics({ topics = [] }) {
  return (
    <div className="glass-card p-4">
      <h3 className="font-semibold mb-3 flex items-center gap-1.5"><Flame size={16} className="text-orange-400" /> Trending Topics</h3>
      <div className="space-y-2">
        {topics.map((t) => (
          <div key={t.topic || t.name} className="flex items-center justify-between text-sm">
            <span>{t.topic || t.name}</span>
            <span className="text-emerald-400 text-xs">↑ {t.growth_percent}%</span>
          </div>
        ))}
        {topics.length === 0 && <p className="text-xs text-slate-500">No trend data yet — analyze a few videos first.</p>}
      </div>
    </div>
  );
}
