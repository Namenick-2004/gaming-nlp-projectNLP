import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Eye, ThumbsUp, MessageCircle, Wand2 } from "lucide-react";
import { getVideo, runAnalysis, getSentimentTrend } from "../api/client.js";
import SentimentChart from "../components/SentimentChart.jsx";
import EmotionChart from "../components/EmotionChart.jsx";
import TopicChart from "../components/TopicChart.jsx";
import KeywordList from "../components/KeywordList.jsx";
import SentimentTrendChart from "../components/SentimentTrendChart.jsx";
import { ChartSkeleton, ErrorState } from "../components/Skeletons.jsx";

export default function VideoAnalysis({ language = "th" }) {
  const { videoId } = useParams();
  const [video, setVideo] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  const text = {
    th: {
      back: "กลับสู่หน้าหลัก",
      analysisError: "วิเคราะห์ไม่สำเร็จ กรุณาลองใหม่อีกครั้ง",
      summary: "สรุปโดย AI",
      generatedFrom: "สร้างจาก",
      comments: "ความคิดเห็น",
    },
    en: {
      back: "Back to Dashboard",
      analysisError: "Analysis failed. Please try again.",
      summary: "AI Summary",
      generatedFrom: "Generated from",
      comments: "comments",
    },
  }[language] || {
    back: "กลับสู่หน้าหลัก",
    analysisError: "วิเคราะห์ไม่สำเร็จ กรุณาลองใหม่อีกครั้ง",
    summary: "สรุปโดย AI",
    generatedFrom: "สร้างจาก",
    comments: "ความคิดเห็น",
  };

  useEffect(() => {
    setLoading(true);
    setError(null);
    // The trend endpoint reads persisted snapshots, so it must run after
    // the current analysis request has finished.
    Promise.all([getVideo(videoId), runAnalysis(videoId)])
      .then(async ([videoData, analysisData]) => {
        const trendData = await getSentimentTrend(videoId);
        setVideo(videoData);
        setAnalysis(analysisData);
        setTrend(trendData);
      })
      .catch((requestError) => {
        const detail = requestError.response?.data?.detail;
        const apiError = requestError.response?.data?.youtube_error;
        setError(apiError || detail || text.analysisError);
      })
      .finally(() => setLoading(false));
  }, [videoId, text.analysisError, retryCount]);

  return (
    <div className="space-y-6">
      <Link to="/" className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 transition hover:text-slate-900">
        <ArrowLeft size={16} /> {text.back}
      </Link>

      {video && (
        <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
          <div className="flex flex-col gap-4 p-4 sm:flex-row">
            <img src={video.thumbnail} alt={video.title} className="h-48 w-full rounded-2xl object-cover sm:w-64" />
            <div className="flex-1 space-y-3">
              <h1 className="text-xl font-bold text-slate-900">{video.title}</h1>
              <p className="text-sm font-medium text-slate-500">{video.channel}</p>
              <div className="flex flex-wrap gap-4 text-sm text-slate-600">
                <span className="inline-flex items-center gap-1.5"><Eye size={14} />{video.views.toLocaleString()}</span>
                <span className="inline-flex items-center gap-1.5"><ThumbsUp size={14} />{video.likes.toLocaleString()}</span>
                <span className="inline-flex items-center gap-1.5"><MessageCircle size={14} />{video.comment_count.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {error && (
        <ErrorState
          message={error}
          onRetry={() => setRetryCount((count) => count + 1)}
        />
      )}

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2">
          <ChartSkeleton /><ChartSkeleton /><ChartSkeleton /><ChartSkeleton />
        </div>
      ) : analysis && (
        <>
          <div className="grid gap-4 md:grid-cols-2">
            <SentimentChart data={analysis.sentiment} />
            <EmotionChart data={analysis.emotion} />
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <TopicChart data={analysis.categories} />
            <KeywordList keywords={analysis.keywords} language={language} />
          </div>
          {trend.length > 1 && <SentimentTrendChart data={trend} />}
          <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="mb-3 flex items-center gap-2 text-base font-bold text-slate-900">
              <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-violet-100 text-violet-600"><Wand2 size={16} /></span>
              {text.summary}
            </h3>
            <p className="leading-relaxed text-sm text-slate-700">{analysis.summary?.summary}</p>
            <p className="mt-3 text-xs text-slate-500">{text.generatedFrom} {analysis.summary?.based_on_comments} {text.comments}</p>
          </div>
        </>
      )}
    </div>
  );
}
