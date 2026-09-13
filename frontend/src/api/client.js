/**
 * Thin Axios wrapper around the FastAPI backend. Every function here
 * maps 1:1 to a backend endpoint from README's "API Endpoints" table
 * — components should never construct URLs themselves.
 */
import axios from "axios";

// Fail visibly instead of leaving the dashboard in its loading state forever
// when the real YouTube API or the backend is unavailable.
const api = axios.create({ baseURL: "/api", timeout: 20_000 });

export const getTrendingVideos = (maxResults = 20, query = "") =>
  api.get(`/videos/trending`, { params: { max_results: maxResults, query } }).then((r) => r.data.items);

export const getLatestVideos = (maxResults = 20, query = "") =>
  api.get(`/videos/latest`, { params: { max_results: maxResults, query } }).then((r) => r.data.items);

export const getMostViewedVideos = (maxResults = 20, query = "") =>
  api.get(`/videos/most-viewed`, { params: { max_results: maxResults, query } }).then((r) => r.data.items);

export const getMostCommentedVideos = (maxResults = 20, query = "") =>
  api.get(`/videos/most-commented`, { params: { max_results: maxResults, query } }).then((r) => r.data.items);

export const getVideo = (videoId) => api.get(`/videos/${videoId}`).then((r) => r.data);

export const getGamingTrends = () => api.get(`/gaming-trends`).then((r) => r.data);

export const runAnalysis = (videoId) =>
  api.post(`/analysis/${videoId}/run`).then((r) => r.data);

export const getSentiment = (videoId) => api.get(`/analysis/${videoId}/sentiment`).then((r) => r.data);
export const getEmotion = (videoId) => api.get(`/analysis/${videoId}/emotion`).then((r) => r.data);
export const getTopics = (videoId) => api.get(`/analysis/${videoId}/topics`).then((r) => r.data);
export const getKeywords = (videoId) => api.get(`/analysis/${videoId}/keywords`).then((r) => r.data);
export const getSummary = (videoId) => api.get(`/analysis/${videoId}/summary`).then((r) => r.data);
export const getSentimentTrend = (videoId) => api.get(`/analysis/${videoId}/trends`).then((r) => r.data);

export default api;
