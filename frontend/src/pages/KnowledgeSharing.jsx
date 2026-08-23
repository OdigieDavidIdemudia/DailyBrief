import React, { useState, useEffect } from "react";
import { Bot, BookOpen, Download, FileText, Presentation, ChevronDown, ChevronUp, RefreshCw } from "lucide-react";

const API = "http://localhost:8000";


const KnowledgeSharing = () => {
  const [topic, setTopic] = useState(() => sessionStorage.getItem("ks_topic") || "");
  const [audience, setAudience] = useState(() => sessionStorage.getItem("ks_audience") || "Security Team");
  const [details, setDetails] = useState(() => sessionStorage.getItem("ks_details") || "");
  const [draft, setDraft] = useState(() => { const s = sessionStorage.getItem("ks_draft"); return s ? JSON.parse(s) : null; });
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [corrections, setCorrections] = useState("");
  const [refining, setRefining] = useState(false);
  const [expandedSlide, setExpandedSlide] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => sessionStorage.setItem("ks_topic", topic), [topic]);
  useEffect(() => sessionStorage.setItem("ks_audience", audience), [audience]);
  useEffect(() => sessionStorage.setItem("ks_details", details), [details]);
  useEffect(() => { if (draft) sessionStorage.setItem("ks_draft", JSON.stringify(draft)); }, [draft]);

  const handleGenerate = async () => {
    if (!topic.trim() || !details.trim()) { setError("Please fill in the topic and details."); return; }
    setLoading(true); setError("");
    try {
      const res = await fetch(`${API}/api/ks/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ input_data: { topic, target_audience: audience, details } })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Generation failed");
      setDraft(data.draft);
      setExpandedSlide(0);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const handleRefine = async () => {
    if (!corrections.trim()) return;
    setRefining(true);
    try {
      const res = await fetch(`${API}/api/ks/refine`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ draft, corrections })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setDraft(data.draft); setCorrections("");
    } catch (e) { setError(e.message); }
    finally { setRefining(false); }
  };

  const handleExport = async (format) => {
    setExporting(true);
    try {
      const res = await fetch(`${API}/api/ks/export`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ draft, format })
      });
      if (!res.ok) throw new Error("Export failed");
      const blob = await res.blob();
      const ext = format === "pptx" ? "pptx" : "txt";
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a"); a.href = url;
      a.download = `${draft.presentation_title?.replace(/\s+/g, "_") || "KS"}.${ext}`;
      a.click(); URL.revokeObjectURL(url);
    } catch (e) { setError(e.message); }
    finally { setExporting(false); }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-200px)] space-y-6">
      <header className="shrink-0">
        <h2 className="text-3xl font-black text-neo-text">Knowledge Sharing</h2>
        <p className="text-gray-600 font-bold mt-2">Turn your notes into a professional presentation and presenter guide with Magnitude AI.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pb-8 flex-1 min-h-0">

        {/* LEFT: Input */}
        <div className="bg-white border-neo border-neo-border rounded-neo shadow-neo flex flex-col h-full overflow-hidden">
          <div className="bg-neo-blue p-4 lg:p-6 border-b-neo border-neo-border flex items-center gap-4 text-white shrink-0">
            <div className="bg-white p-3 rounded-neo border-neo border-neo-border shadow-neo-sm hidden sm:block">
              <BookOpen className="w-8 h-8 text-neo-blue" />
            </div>
            <div>
              <h3 className="font-black text-xl tracking-tight">Session Input</h3>
              <p className="text-sm font-bold opacity-90">Tell Magnitude what you want to share</p>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-5">
            {error && <div className="bg-red-100 border-2 border-red-500 text-red-700 p-3 rounded-neo font-bold text-sm">{error}</div>}

            <div>
              <label className="block font-black text-sm uppercase tracking-wider text-neo-text mb-2">Topic / Title <span className="text-red-500">*</span></label>
              <input
                type="text"
                value={topic}
                onChange={e => setTopic(e.target.value)}
                placeholder="e.g. Introduction to Phishing Detection Techniques"
                className="neo-input w-full"
              />
            </div>

            <div>
              <label className="block font-black text-sm uppercase tracking-wider text-neo-text mb-2">Target Audience</label>
              <input
                type="text"
                value={audience}
                onChange={e => setAudience(e.target.value)}
                placeholder="e.g. L1 Analysts, Security Team, Management"
                className="neo-input w-full"
              />
            </div>

            <div>
              <label className="block font-black text-sm uppercase tracking-wider text-neo-text mb-2">Details / Notes <span className="text-red-500">*</span></label>
              <textarea
                value={details}
                onChange={e => setDetails(e.target.value)}
                placeholder="Paste your raw notes, bullet points, article summaries — anything you want to teach. Magnitude will structure it into slides."
                className="neo-input w-full min-h-[200px]"
              />
            </div>

            <button
              onClick={handleGenerate}
              disabled={loading}
              className="neo-btn bg-black text-white w-full py-4 text-lg flex items-center justify-center gap-2"
            >
              <Bot className={`w-6 h-6 ${loading ? "animate-spin" : ""}`} />
              {loading ? "Magnitude is building slides..." : "Generate Presentation"}
            </button>
          </div>
        </div>

        {/* RIGHT: Preview */}
        <div className="bg-white border-neo border-neo-border rounded-neo shadow-neo flex flex-col h-full overflow-hidden">
          <div className="bg-neo-yellow p-4 lg:p-6 border-b-neo border-neo-border flex items-center justify-between shrink-0">
            <div className="flex items-center gap-4">
              <div className="bg-white p-3 rounded-neo border-neo border-neo-border shadow-neo-sm hidden sm:block">
                <FileText className="w-8 h-8 text-neo-blue" />
              </div>
              <div>
                <h3 className="font-black text-xl tracking-tight">Draft Preview</h3>
                <p className="text-sm font-bold opacity-90">Review slides and presenter notes</p>
              </div>
            </div>
            {draft && (
              <div className="flex gap-2">
                <button
                  onClick={() => handleExport("pptx")}
                  disabled={exporting}
                  className="neo-btn bg-neo-blue text-white flex items-center gap-2 text-sm"
                >
                  <Download className="w-4 h-4" /> PPTX
                </button>
                <button
                  onClick={() => handleExport("txt")}
                  disabled={exporting}
                  className="neo-btn bg-black text-white flex items-center gap-2 text-sm"
                >
                  <Download className="w-4 h-4" /> TXT Guide
                </button>
              </div>
            )}
          </div>

          <div className="flex-1 overflow-y-auto p-4 lg:p-6 bg-gray-100">
            {!draft ? (
              <div className="h-full flex flex-col items-center justify-center">
                {loading ? (
                  <div className="flex flex-col items-center text-neo-blue animate-pulse">
                    <Bot className="w-16 h-16 mb-4" />
                    <p className="font-black text-lg">Building your presentation...</p>
                    <p className="text-sm font-bold text-gray-500 text-center max-w-xs mt-2">Structuring slides, writing bullets, scripting notes.</p>
                  </div>
                ) : (
                  <div className="text-center">
                    {/* 16:9 wireframe placeholder */}
                    <div className="bg-white border-2 border-dashed border-gray-300 rounded-neo w-80 h-44 flex items-center justify-center mb-4 mx-auto">
                      <p className="text-gray-400 font-bold text-sm">Slide Preview</p>
                    </div>
                    {/* A4 wireframe placeholder */}
                    <div className="bg-white border-2 border-dashed border-gray-300 rounded-neo w-56 h-72 flex items-center justify-center mx-auto">
                      <p className="text-gray-400 font-bold text-sm">Presenter Guide</p>
                    </div>
                    <p className="text-gray-500 font-bold mt-4 text-sm">Fill in your topic and notes to generate</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {/* Header card */}
                <div className="bg-black text-white p-4 rounded-neo">
                  <p className="font-black text-lg">{draft.presentation_title}</p>
                  <div className="flex flex-wrap gap-4 mt-2 text-xs font-bold opacity-70">
                    <span>Audience: {draft.target_audience}</span>
                    <span>Author: {draft.author}</span>
                    <span>Date: {draft.date}</span>
                  </div>
                </div>

                {/* Stats row */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-white p-4 rounded-neo border-neo border-neo-border text-center shadow-neo-sm">
                    <p className="text-3xl font-black">{(draft.slides || []).length}</p>
                    <p className="text-xs font-bold text-gray-500 uppercase">Slides</p>
                  </div>
                  <div className="bg-white p-4 rounded-neo border-neo border-neo-border text-center shadow-neo-sm">
                    <p className="text-3xl font-black">{(draft.slides || []).reduce((a, s) => a + (s.bullets?.length || 0), 0)}</p>
                    <p className="text-xs font-bold text-gray-500 uppercase">Bullet Points</p>
                  </div>
                </div>

                {/* Slides accordion */}
                <div className="space-y-2">
                  {(draft.slides || []).map((slide, idx) => (
                    <div key={idx} className="bg-white rounded-neo border-neo border-neo-border shadow-neo-sm overflow-hidden">
                      {/* Slide header / 16:9 preview label */}
                      <button
                        onClick={() => setExpandedSlide(expandedSlide === idx ? -1 : idx)}
                        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50"
                      >
                        <div className="flex items-center gap-3">
                          <span className="bg-neo-blue text-white font-black text-xs px-2 py-1 rounded border-2 border-black">
                            {String(slide.slide_number).padStart(2, "0")}
                          </span>
                          <span className="font-black text-sm">{slide.title}</span>
                        </div>
                        {expandedSlide === idx ? <ChevronUp className="w-4 h-4 shrink-0" /> : <ChevronDown className="w-4 h-4 shrink-0" />}
                      </button>

                      {expandedSlide === idx && (
                        <div className="border-t-2 border-gray-100">
                          {/* 16:9 slide wireframe */}
                          <div className="bg-gray-900 p-4 mx-4 mt-3 rounded-neo" style={{aspectRatio: "16/9"}}>
                            <p className="text-white font-black text-sm mb-2">{slide.title}</p>
                            <ul className="space-y-1">
                              {slide.bullets?.map((b, bi) => (
                                <li key={bi} className="text-gray-300 text-xs flex items-start gap-2">
                                  <span className="text-neo-yellow shrink-0">▸</span>{b}
                                </li>
                              ))}
                            </ul>
                          </div>
                          {/* Presenter notes A4-style */}
                          <div className="bg-amber-50 border-t-2 border-dashed border-amber-200 mx-4 mb-3 p-3 mt-2 rounded-neo">
                            <p className="text-xs font-black uppercase text-amber-700 mb-1">📢 Presenter Notes</p>
                            <p className="text-xs text-gray-700 leading-relaxed">{slide.presenter_script}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Refine */}
                <div className="bg-neo-accent/10 p-4 rounded-neo border-neo border-neo-accent shadow-neo-sm">
                  <h4 className="font-black text-base text-neo-accent mb-2 flex items-center gap-2">
                    <Bot className="w-5 h-5" /> Ask Magnitude to adjust
                  </h4>
                  <textarea
                    value={corrections}
                    onChange={e => setCorrections(e.target.value)}
                    placeholder="e.g. Add a slide about real-world examples, simplify the technical language..."
                    className="neo-input text-sm w-full min-h-[60px] mb-3 bg-white"
                  />
                  <button
                    onClick={handleRefine}
                    disabled={refining || !corrections.trim()}
                    className="neo-btn bg-black text-white flex items-center gap-2 disabled:opacity-50"
                  >
                    <RefreshCw className={`w-4 h-4 ${refining ? "animate-spin" : ""}`} />
                    {refining ? "Refining..." : "Regenerate"}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeSharing;
