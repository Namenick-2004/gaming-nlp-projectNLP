import { useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import VideoAnalysis from "./pages/VideoAnalysis.jsx";

export default function App() {
  const [language, setLanguage] = useState("th");

  return (
    <Layout language={language} setLanguage={setLanguage}>
      <Routes>
        <Route path="/" element={<Dashboard language={language} />} />
        <Route path="/video/:videoId" element={<VideoAnalysis language={language} />} />
        <Route path="/evaluation" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
