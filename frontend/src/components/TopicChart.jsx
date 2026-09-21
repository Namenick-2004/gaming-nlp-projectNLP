import AnalysisPanel, { MetricBars } from "./AnalysisPanel.jsx";
const names = { athlete: ["นักกีฬา", "Athletes"], team: ["ทีม / สโมสร", "Team"], coach_tactics: ["โค้ชและแผนการเล่น", "Coaching & tactics"], referee: ["กรรมการ", "Refereeing"], competition: ["การแข่งขัน", "Competition"], performance: ["ผลงานการเล่น", "Performance"], injury: ["อาการบาดเจ็บ", "Injuries"], ranking: ["อันดับการแข่งขัน", "Rankings"], transfer: ["การย้ายทีม", "Transfers"], venue_tickets: ["สนามและบัตรเข้าชม", "Venue & tickets"], broadcast_fans: ["การถ่ายทอดและแฟนกีฬา", "Broadcast & fans"], other: ["อื่น ๆ", "Other"] };
export default function TopicChart({ data, language = "th" }) {
  const en = language === "en";
  const items = (data?.categories || []).map((c) => ({ key: c.category, name: names[c.category]?.[en ? 1 : 0] || c.category, value: c.percentage })).sort((a, b) => b.value - a.value);
  return <AnalysisPanel title={en ? "Topics in the conversation" : "ประเด็นที่ผู้ชมพูดถึง"} subtitle={en ? "One comment may cover multiple topics; totals may exceed 100%." : "หนึ่งความคิดเห็นอาจมีหลายประเด็น ผลรวมจึงอาจเกิน 100%"} badge={`${items.length} ${en ? "topics" : "ประเด็น"}`}>
    {items.length ? <MetricBars items={items} /> : <p className="py-12 text-center text-sm text-slate-500">{en ? "No topics yet" : "ยังไม่มีข้อมูลประเด็น"}</p>}
  </AnalysisPanel>;
}
