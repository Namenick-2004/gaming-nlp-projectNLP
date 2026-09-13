import { useState } from "react";

const EXAMPLE = {
  model_name: "sentiment",
  accuracy: 0.87,
  macro_f1: 0.85,
  per_class: [
    { label: "negative", precision: 0.88, recall: 0.84, f1: 0.86, support: 120 },
    { label: "neutral", precision: 0.81, recall: 0.79, f1: 0.80, support: 95 },
    { label: "positive", precision: 0.90, recall: 0.92, f1: 0.91, support: 140 },
  ],
  confusion_matrix: [[101, 12, 7], [10, 75, 10], [5, 6, 129]],
  labels: ["negative", "neutral", "positive"],
};

function ReportView({ report, language = "th" }) {
  if (!report) return null;

  const labels = {
    th: {
      accuracy: "ความแม่นยำ",
      macroF1: "Macro F1",
      microF1: "Micro F1",
      perClass: "เมตริกต่อคลาส",
      label: "คลาส",
      precision: "Precision",
      recall: "Recall",
      f1: "F1",
      support: "จำนวนตัวอย่าง",
      matrix: "เมทริกซ์สับสน",
    },
    en: {
      accuracy: "Accuracy",
      macroF1: "Macro F1",
      microF1: "Micro F1",
      perClass: "Per-class metrics",
      label: "Label",
      precision: "Precision",
      recall: "Recall",
      f1: "F1",
      support: "Support",
      matrix: "Confusion Matrix",
    },
  }[language] || {
    accuracy: "ความแม่นยำ",
    macroF1: "Macro F1",
    microF1: "Micro F1",
    perClass: "เมตริกต่อคลาส",
    label: "คลาส",
    precision: "Precision",
    recall: "Recall",
    f1: "F1",
    support: "จำนวนตัวอย่าง",
    matrix: "เมทริกซ์สับสน",
  };

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-3">
        <Stat label={labels.accuracy} value={report.accuracy} />
        <Stat label={labels.macroF1} value={report.macro_f1} />
        <Stat label={labels.microF1} value={report.micro_f1 ?? "-"} />
      </div>

      <div className="glass-card overflow-x-auto p-4">
        <h4 className="mb-2 font-bold text-slate-900">{labels.perClass}</h4>
        <table className="w-full text-sm">
          <thead className="text-slate-500">
            <tr>
              <th className="py-1 text-left">{labels.label}</th>
              <th className="py-1 text-center">{labels.precision}</th>
              <th className="py-1 text-center">{labels.recall}</th>
              <th className="py-1 text-center">{labels.f1}</th>
              <th className="py-1 text-center">{labels.support}</th>
            </tr>
          </thead>
          <tbody>
            {report.per_class?.map((row) => (
              <tr key={row.label} className="border-t border-slate-200">
                <td className="py-2 font-medium text-slate-700">{row.label}</td>
                <td className="py-2 text-center">{row.precision}</td>
                <td className="py-2 text-center">{row.recall}</td>
                <td className="py-2 text-center">{row.f1}</td>
                <td className="py-2 text-center">{row.support}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {report.confusion_matrix?.length > 0 && (
        <div className="glass-card overflow-x-auto p-4">
          <h4 className="mb-2 font-bold text-slate-900">{labels.matrix}</h4>
          <table className="mx-auto text-sm">
            <thead>
              <tr>
                <th></th>
                {report.labels.map((l) => (
                  <th key={l} className="px-3 py-1 text-slate-500">{l}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {report.confusion_matrix.map((row, i) => (
                <tr key={i}>
                  <td className="pr-3 text-slate-500">{report.labels[i]}</td>
                  {row.map((cell, j) => (
                    <td key={j} className={`px-3 py-1 text-center ${i === j ? "rounded bg-emerald-100 text-emerald-700" : "rounded bg-slate-100 text-slate-700"}`}>
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="glass-card p-4 text-center">
      <p className="text-2xl font-bold text-slate-900">{typeof value === "number" ? (value * 100).toFixed(1) + "%" : value}</p>
      <p className="mt-1 text-xs font-medium text-slate-500">{label}</p>
    </div>
  );
}

export default function ModelEvaluation({ language = "th" }) {
  const [raw, setRaw] = useState("");
  const [report, setReport] = useState(EXAMPLE);
  const [parseError, setParseError] = useState(null);

  const text = {
    th: {
      title: "ประเมินโมเดล",
      helper: "วางข้อมูล JSON จากไฟล์ *_evaluation_report.json ที่สร้างจากคำสั่ง Python ลงในช่องด้านล่าง",
      placeholder: "วางข้อมูล JSON ของรายงานประเมินผลที่นี่",
      load: "โหลดรายงาน",
      invalid: "JSON ไม่ถูกต้อง กรุณาเช็คข้อมูลอีกครั้ง",
    },
    en: {
      title: "Model Evaluation",
      helper: "Paste the JSON output from the generated evaluation report below to view the model metrics.",
      placeholder: "Paste evaluation_report.json here",
      load: "Load report",
      invalid: "Invalid JSON. Please check the file contents again.",
    },
  }[language] || {
    title: "ประเมินโมเดล",
    helper: "วางข้อมูล JSON จากไฟล์ *_evaluation_report.json ที่สร้างจากคำสั่ง Python ลงในช่องด้านล่าง",
    placeholder: "วางข้อมูล JSON ของรายงานประเมินผลที่นี่",
    load: "โหลดรายงาน",
    invalid: "JSON ไม่ถูกต้อง กรุณาเช็คข้อมูลอีกครั้ง",
  };

  const handleLoad = () => {
    try {
      setReport(JSON.parse(raw));
      setParseError(null);
    } catch {
      setParseError(text.invalid);
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <h1 className="text-2xl font-bold text-slate-900">{text.title}</h1>
        <p className="mt-2 text-sm text-slate-500">{text.helper}</p>
      </div>

      <div className="glass-card space-y-3 p-4">
        <textarea
          value={raw}
          onChange={(e) => setRaw(e.target.value)}
          placeholder={text.placeholder}
          className="h-32 w-full rounded-xl border border-slate-200 bg-slate-50 p-3 font-mono text-xs text-slate-700 outline-none transition focus:border-indigo-300 focus:ring-2 focus:ring-indigo-100"
        />
        <button onClick={handleLoad} className="rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:opacity-95">
          {text.load}
        </button>
        {parseError && <p className="text-xs text-red-600">{parseError}</p>}
      </div>

      <ReportView report={report} language={language} />
    </div>
  );
}
