import { useEffect, useState } from "react";
import { Flame, Sparkles, BarChart3, Search, X } from "lucide-react";
import { getSportsTrends, getTrendingVideos, getLatestVideos, getMostViewedVideos, getMostCommentedVideos } from "../api/client.js";
import VideoCard from "../components/VideoCard.jsx";
import { VideoCardSkeleton, EmptyState, ErrorState } from "../components/Skeletons.jsx";

const tabsByLang = {
  th: [
    { key: "trending", label: "ยอดนิยม" },
    { key: "latest", label: "ล่าสุด" },
    { key: "most-viewed", label: "ผู้ชมมากที่สุด" },
    { key: "most-commented", label: "คอมเมนต์มากที่สุด" },
  ],
  en: [
    { key: "trending", label: "Trending" },
    { key: "latest", label: "Latest" },
    { key: "most-viewed", label: "Most Viewed" },
    { key: "most-commented", label: "Most Commented" },
  ],
};

const fetchers = {
  trending: getTrendingVideos,
  latest: getLatestVideos,
  "most-viewed": getMostViewedVideos,
  "most-commented": getMostCommentedVideos,
};

function formatCount(value) {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return String(value ?? 0);
}

export default function Dashboard({ language = "th" }) {
  const [tab, setTab] = useState("trending");
  const [searchInput, setSearchInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [videos, setVideos] = useState([]);
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const videoLimit = tab === "trending" ? 10 : 16;

  const text = {
    th: {
      hero: "กีฬาที่กำลังได้รับความนิยม",
      heroSub: "ติดตามแนวโน้มกีฬาที่มีการพูดถึงและการมีส่วนร่วมจากชุมชนอย่างต่อเนื่อง",
      title: "กีฬายอดนิยม",
      noVideos: "ไม่พบวิดีโอ",
      noVideosSub: "ลองสลับแท็บอื่น หรือตรวจสอบคีย์ YouTube API",
      fetchError: "ไม่สามารถโหลดข้อมูลได้ กรุณาตรวจสอบว่า Backend กำลังทำงานอยู่",
      searchPlaceholder: "ค้นหากีฬา เช่น ฟุตบอล หรือ วอลเลย์บอล",
      search: "ค้นหากีฬา",
    },
    en: {
      hero: "Trending sports",
      heroSub: "Monitor the sports generating the strongest attention and community engagement.",
      title: "Trending Sports",
      noVideos: "No videos found",
      noVideosSub: "Try another tab or check the YouTube API key.",
      fetchError: "Unable to load data. Please check whether the backend is running.",
      searchPlaceholder: "Search sports, e.g. football or volleyball",
      search: "Search sports",
    },
  }[language] || {
    hero: "กีฬาที่กำลังได้รับความนิยม",
    heroSub: "ติดตามแนวโน้มกีฬาที่มีการพูดถึงและการมีส่วนร่วมจากชุมชนอย่างต่อเนื่อง",
    title: "กีฬายอดนิยม",
    noVideos: "ไม่พบวิดีโอ",
    noVideosSub: "ลองสลับแท็บอื่น หรือตรวจสอบคีย์ YouTube API",
    fetchError: "ไม่สามารถโหลดข้อมูลได้ กรุณาตรวจสอบว่า Backend กำลังทำงานอยู่",
    searchPlaceholder: "ค้นหากีฬา เช่น ฟุตบอล หรือ วอลเลย์บอล",
    search: "ค้นหากีฬา",
  };

  useEffect(() => {
    setLoading(true);
    setError(null);
    const fetcher = fetchers[tab];
    let active = true;
    Promise.all([fetcher(videoLimit, searchQuery), getSportsTrends()])
      .then(([videoList, trendData]) => {
        if (!active) return;
        setVideos(videoList.slice(0, videoLimit));
        setTrends(trendData);
      })
      .catch(() => { if (active) setError(text.fetchError); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [tab, searchQuery, text.fetchError, videoLimit]);

  const submitSearch = (event) => {
    event.preventDefault();
    setSearchQuery(searchInput.trim());
  };

  const clearSearch = () => {
    setSearchInput("");
    setSearchQuery("");
  };

  return (
    <div className="space-y-8">
      <section className="relative overflow-hidden rounded-[28px] border border-indigo-100 bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950 p-6 text-white shadow-[0_24px_60px_-24px_rgba(79,70,229,0.65)]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(99,102,241,0.45),transparent_30%),radial-gradient(circle_at_bottom_left,_rgba(168,85,247,0.35),transparent_35%)]" />
        <div className="relative z-10 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-xl space-y-3">
            <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-indigo-100">
              <Sparkles size={12} />
              Live Insight
            </span>
            <h2 className="text-3xl font-black tracking-tight sm:text-4xl">{text.hero}</h2>
            <p className="max-w-lg text-sm text-slate-200 sm:text-base">{text.heroSub}</p>
          </div>

          <div className="grid w-full max-w-md grid-cols-2 gap-3 text-left">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-3 backdrop-blur-sm">
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-slate-300">
                <Flame size={14} /> Trend
              </div>
              <div className="mt-2 text-2xl font-black">{trends?.trending_sports?.length ?? 0}</div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-3 backdrop-blur-sm">
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-slate-300">
                <BarChart3 size={14} /> Score
              </div>
              <div className="mt-2 text-2xl font-black">{trends?.overall_sentiment ? "AI" : "Live"}</div>
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-[0_18px_50px_-30px_rgba(15,23,42,0.18)]">
        <div className="mb-4 flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-orange-100 text-orange-500">
            <Flame size={18} />
          </span>
          <h2 className="text-xl font-bold text-slate-900">{text.title}</h2>
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {trends?.trending_sports?.slice(0, 4).map((g) => (
            <div key={g.name} className="group flex min-h-[94px] items-center justify-between rounded-2xl border border-slate-200 bg-gradient-to-br from-slate-50 via-white to-indigo-50 p-4 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-md">
              <div className="min-w-0 pr-3">
                <p className="truncate text-base font-semibold text-slate-800">{g.name}</p>
              </div>
              <span className="inline-flex shrink-0 items-center rounded-full bg-emerald-100 px-2.5 py-1 text-sm font-bold text-emerald-700">
                {formatCount(g.views)} views
              </span>
            </div>
          ))}
        </div>
      </section>

      <section>
        <form onSubmit={submitSearch} className="mb-4 flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Search size={18} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder={text.searchPlaceholder}
              aria-label={text.searchPlaceholder}
              className="h-11 w-full rounded-xl border border-slate-200 bg-white pl-10 pr-10 text-sm text-slate-900 outline-none transition focus:border-indigo-400 focus:ring-4 focus:ring-indigo-100"
            />
            {searchInput && (
              <button type="button" onClick={clearSearch} aria-label="Clear search" className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700">
                <X size={16} />
              </button>
            )}
          </div>
          <button type="submit" className="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700">
            <Search size={16} /> {text.search}
          </button>
        </form>

        <div className="mb-5 flex flex-wrap gap-2" role="tablist" aria-label="Video filters">
          {tabsByLang[language || "th"].map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`rounded-full border px-4 py-2 text-sm font-semibold transition ${
                tab === t.key
                  ? "border-transparent bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md"
                  : "border-slate-200 bg-white text-slate-600 hover:border-indigo-200 hover:text-slate-900"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {error ? (
          <ErrorState message={error} onRetry={() => setTab((current) => current)} />
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {loading
              ? Array.from({ length: videoLimit }).map((_, i) => <VideoCardSkeleton key={i} />)
              : videos.length === 0
              ? <EmptyState title={text.noVideos} subtitle={text.noVideosSub} />
              : videos.map((v, index) => <VideoCard key={v.video_id} video={v} language={language} rank={tab === "trending" ? index + 1 : undefined} />)}
          </div>
        )}
      </section>
    </div>
  );
}
