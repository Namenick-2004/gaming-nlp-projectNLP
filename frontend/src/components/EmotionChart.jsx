import AnalysisPanel, { MetricBars } from "./AnalysisPanel.jsx";
const names = { joy: ["ยินดี", "Joy"], anger: ["โกรธ", "Anger"], sadness: ["เศร้า", "Sadness"], surprise: ["ประหลาดใจ", "Surprise"], fear: ["กังวล / กลัว", "Fear"], neutral: ["เป็นกลาง", "Neutral"] };
const colors = { joy: "#d97706", anger: "#e11d48", sadness: "#6366f1", surprise: "#0891b2", fear: "#9333ea", neutral: "#94a3b8" };
export default function EmotionChart({ data, language = "th" }) {
  if (!data) return null;
  const en = language === "en";
  const items = Object.entries(names).map(([key, label]) => ({ key, name: label[en ? 1 : 0], value: data[key] || 0, color: colors[key] })).sort((a, b) => b.value - a.value);
  return <AnalysisPanel title={en ? "Emotional response" : "อารมณ์ของผู้ชม"} subtitle={en ? "Primary emotion in each comment" : "อารมณ์หลักของแต่ละความคิดเห็น เรียงตามสัดส่วน"} badge={en ? "6 emotions" : "6 อารมณ์"}><MetricBars items={items} /></AnalysisPanel>;
}
