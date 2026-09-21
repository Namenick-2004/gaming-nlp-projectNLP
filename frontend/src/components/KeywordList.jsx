import AnalysisPanel from "./AnalysisPanel.jsx";
export default function KeywordList({ keywords = [], language = "th" }) {
  const en = language === "en";
  const items = [...keywords].sort((a, b) => b.count - a.count);
  const max = Math.max(1, ...items.map((item) => item.count));
  return <AnalysisPanel title={en ? "Leading keywords" : "คำสำคัญที่พบมากที่สุด"} subtitle={en ? "Number of sampled comments containing each keyword" : "จำนวนความคิดเห็นในกลุ่มตัวอย่างที่มีคำนี้"} badge={en ? "Top keywords" : "คำสำคัญ"}>
    {items.length ? <ol className="divide-y divide-slate-100">{items.map((item, index) => <li key={item.keyword} className="flex items-center gap-3 py-3.5 first:pt-0">
      <span className="w-6 shrink-0 text-xs font-semibold tabular-nums text-slate-400">{String(index + 1).padStart(2, "0")}</span>
      <div className="min-w-0 flex-1"><p className="break-words text-sm font-medium leading-6 text-slate-800">{item.keyword}</p><div className="mt-2 h-1 rounded-full bg-slate-100"><div className="h-full rounded-full bg-indigo-300" style={{ width: `${item.count / max * 100}%` }} /></div></div>
      <span className="shrink-0 rounded-md bg-indigo-50 px-2.5 py-1 text-sm font-semibold tabular-nums text-indigo-700">{item.count}</span>
    </li>)}</ol> : <p className="py-12 text-center text-sm text-slate-500">{en ? "No keywords yet" : "ยังไม่มีคำสำคัญ"}</p>}
  </AnalysisPanel>;
}
