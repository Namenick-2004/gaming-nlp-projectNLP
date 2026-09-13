import { useNavigate } from "react-router-dom";
import { Eye, ThumbsUp, MessageCircle, Sparkles } from "lucide-react";

function formatCount(n) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
  return String(n);
}

export default function VideoCard({ video, language = "th", categoryName }) {
  const navigate = useNavigate();
  const label = language === "en" ? "Analyze" : "วิเคราะห์";

  return (
    <article className="group overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm transition duration-200 hover:-translate-y-1 hover:border-indigo-200 hover:shadow-lg">
      <div className="relative aspect-video overflow-hidden">
        <img
          src={video.thumbnail}
          alt={video.title}
          className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
        />
        {(categoryName || video.game_category) && (
          <span className="absolute left-2 top-2 rounded-full border border-white/10 bg-black/60 px-2 py-0.5 text-[10px] font-medium text-white backdrop-blur-sm">
            {categoryName || video.game_category}
          </span>
        )}
      </div>
      <div className="space-y-3 p-4">
        <h3 className="min-h-[3rem] text-[15px] font-bold leading-6 text-slate-900 line-clamp-2">{video.title}</h3>
        <p className="text-sm text-slate-500">{video.channel}</p>
        <div className="flex items-center gap-3 pt-1 text-xs text-slate-500">
          <span className="flex items-center gap-1"><Eye size={12} />{formatCount(video.views)}</span>
          <span className="flex items-center gap-1"><ThumbsUp size={12} />{formatCount(video.likes)}</span>
          <span className="flex items-center gap-1"><MessageCircle size={12} />{formatCount(video.comment_count)}</span>
        </div>
        <button
          onClick={() => navigate(`/video/${video.video_id}`)}
          className="mt-2 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-3 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:opacity-95"
        >
          <Sparkles size={14} /> {label}
        </button>
      </div>
    </article>
  );
}
