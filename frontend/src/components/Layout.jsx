import { Link } from "react-router-dom";
import { Trophy, Sparkles, Globe2 } from "lucide-react";

const labels = {
  th: {
    brand: "แดชบอร์ดวิเคราะห์กีฬา",
    language: "ภาษา",
  },
  en: {
    brand: "Sports NLP Dashboard",
    language: "Language",
  },
};

export default function Layout({ children, language, setLanguage }) {
  const t = labels[language] || labels.th;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-50 text-slate-900">
      <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 backdrop-blur-xl shadow-[0_1px_0_rgba(15,23,42,0.04)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-3 font-bold text-lg text-slate-900">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 text-white shadow-lg shadow-violet-200">
              <Trophy size={22} />
            </div>
            <span>{t.brand}</span>
          </Link>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-2 py-1.5 text-xs font-medium text-slate-600">
              <Globe2 size={14} />
              <span>{t.language}</span>
            </div>
            <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 p-1">
              {[
                { code: "th", label: "ไทย" },
                { code: "en", label: "EN" },
              ].map((item) => (
                <button
                  key={item.code}
                  type="button"
                  onClick={() => setLanguage(item.code)}
                  className={`rounded-full px-2.5 py-1 text-xs font-semibold transition ${
                    language === item.code
                      ? "bg-slate-900 text-white shadow-sm"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>

            <span
              className="inline-flex items-center gap-1.5 rounded-full border border-indigo-200 bg-indigo-50 px-3.5 py-2 text-sm font-medium text-indigo-700 transition hover:border-indigo-300 hover:bg-indigo-100"
            >
              <Sparkles size={16} /> Gemini
            </span>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">{children}</main>
    </div>
  );
}
