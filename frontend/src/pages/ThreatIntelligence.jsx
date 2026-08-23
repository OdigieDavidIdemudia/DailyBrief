import React, { useState, useEffect } from 'react';
import { Bot, FileText, Upload, Send, ShieldCheck, Download, Edit3, Trash2, Plus, Radar } from 'lucide-react';

const ThreatIntelligence = () => {
  const [threat, setThreat] = useState(() => { const s = sessionStorage.getItem('tia_threat'); return s ? JSON.parse(s) : {
    raw_text: '',
    title: '',
    date: '',
    how: '',
    severity_hint: '',
    source_urls: '' 
  } });
  useEffect(() => sessionStorage.setItem('tia_threat', JSON.stringify(threat)), [threat]);
  const [rawIocs, setRawIocs] = useState(() => sessionStorage.getItem('tia_rawIocs') || '');
  useEffect(() => sessionStorage.setItem('tia_rawIocs', rawIocs), [rawIocs]);
  
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [refining, setRefining] = useState(false);
  const [draft, setDraft] = useState(() => { const s = sessionStorage.getItem('tia_draft'); return s ? JSON.parse(s) : null; });
  useEffect(() => sessionStorage.setItem('tia_draft', JSON.stringify(draft)), [draft]);
  
  const [corrections, setCorrections] = useState('');
  const [saveToMemory, setSaveToMemory] = useState(false);

  const handleGenerate = async () => {
    if (!threat.raw_text.trim()) {
      alert("Please provide a threat description.");
      return;
    }
    
    setLoading(true);
    setDraft(null);

    const payload = {
      threat: {
        ...threat,
        severity_hint: threat.severity_hint === "" ? null : threat.severity_hint,
        source_urls: threat.source_urls.split(',').map(s => s.trim()).filter(s => s)
      },
      raw_iocs: rawIocs,
      generation_options: {
        auto_enrich_iocs: true
      }
    };

    try {
      const res = await fetch('http://localhost:8000/api/tia/generate', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.error || "Generation failed.");
      setDraft(data.draft);
    } catch (e) {
      alert("Error: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRefine = async () => {
    if (!draft || !corrections.trim()) return;
    
    setRefining(true);
    try {
      const res = await fetch('http://localhost:8000/api/tia/refine', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draft, corrections })
      });
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.error || "Refinement failed");
      
      setDraft(data.draft);
      
      if (saveToMemory) {
        await fetch('http://localhost:8000/api/memory/add', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ instruction: corrections })
        });
      }
      
      setCorrections('');
      setSaveToMemory(false);
    } catch (e) {
      alert("Error: " + e.message);
    } finally {
      setRefining(false);
    }
  };

  const handleExport = async (format) => {
    if (!draft) return;
    setExporting(true);
    
    try {
      const res = await fetch('http://localhost:8000/api/tia/export', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draft, format })
      });
      
      if (!res.ok) throw new Error("Export failed");
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${draft.report_id.replace(/\//g, '_')}.${format === 'structured_json' ? 'json' : 'docx'}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      alert("Export Error: " + e.message);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="h-full flex flex-col relative overflow-hidden bg-white">
      <div className="flex-none p-4 lg:p-6 bg-white border-b-neo border-neo-border z-10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-neo-primary rounded-neo border-neo border-black flex items-center justify-center shadow-neo-sm">
            <Radar className="w-6 h-6 text-black" />
          </div>
          <div>
            <h1 className="text-2xl font-black uppercase tracking-tight">Threat Intelligence</h1>
            <p className="text-sm font-bold text-gray-600">Generate structured TIA reports</p>
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* LEFT PANEL: Inputs */}
        <div className="w-full lg:w-1/2 flex flex-col border-r-neo border-neo-border bg-white z-0">
          <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-6">
            <div>
              <label className="block text-xs font-bold uppercase text-gray-600 mb-1">Threat Description (Required)</label>
              <textarea 
                value={threat.raw_text}
                onChange={e => setThreat({...threat, raw_text: e.target.value})}
                placeholder="Paste a threat feed alert or describe the threat..."
                className="neo-input text-sm w-full min-h-[120px]"
              />
            </div>
            
            <div>
              <label className="block text-xs font-bold uppercase text-gray-600 mb-1">Source URLs (Comma-separated)</label>
              <input 
                type="text"
                value={threat.source_urls}
                onChange={e => setThreat({...threat, source_urls: e.target.value})}
                placeholder="https://vendor.com/blog"
                className="neo-input text-sm w-full"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold uppercase text-gray-600 mb-1">Suggested Title</label>
                <input 
                  type="text"
                  value={threat.title}
                  onChange={e => setThreat({...threat, title: e.target.value})}
                  className="neo-input text-sm w-full"
                />
              </div>
              <div>
                <label className="block text-xs font-bold uppercase text-gray-600 mb-1">Severity Hint</label>
                <select 
                  value={threat.severity_hint}
                  onChange={e => setThreat({...threat, severity_hint: e.target.value})}
                  className="neo-input text-sm w-full font-bold cursor-pointer"
                >
                  <option value="">Auto-assess</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </div>

            <div className="pt-4 border-t-2 border-black border-dashed">
              <label className="block text-xs font-bold uppercase text-gray-600 mb-2">Raw IOCs</label>
              <textarea 
                value={rawIocs}
                onChange={e => setRawIocs(e.target.value)}
                placeholder="Paste raw IOCs here (Magnitude will parse and categorize domains, IPs, hashes, etc.)"
                className="neo-input text-sm w-full min-h-[100px]"
              />
            </div>

            <button 
              onClick={handleGenerate}
              disabled={loading}
              className="neo-btn bg-black text-white w-full py-4 text-lg flex items-center justify-center gap-2 mt-4"
            >
              <Bot className={`w-6 h-6 ${loading ? 'animate-spin' : ''}`}/>
              {loading ? 'Magnitude Processing...' : 'Generate Advisory'}
            </button>
          </div>
        </div>

        {/* RIGHT PANEL: Preview */}
        <div className="w-full lg:w-1/2 flex flex-col bg-gray-50 z-0">
          {draft && (
            <div className="flex-none p-4 bg-white border-b-neo border-neo-border flex justify-between items-center shadow-sm">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-neo-accent" />
                <span className="font-black">Draft Preview</span>
              </div>
              <div className="flex gap-2">
                <button onClick={() => handleExport('structured_json')} className="neo-btn bg-white text-black text-xs py-1 px-3">JSON</button>
                <button onClick={() => handleExport('docx')} disabled={exporting} className="neo-btn bg-neo-green text-black flex items-center gap-2 text-sm">
                  <Download className="w-4 h-4"/> {exporting ? 'Exporting...' : 'Export DOCX'}
                </button>
              </div>
            </div>
          )}

          <div className="flex-1 overflow-y-auto p-4 lg:p-8 flex justify-center bg-gray-200">
            <div className="bg-white w-full max-w-[816px] min-h-[1056px] shadow-lg p-10 lg:p-16 font-serif text-sm space-y-6">
<h1 className="text-3xl font-bold uppercase tracking-tight text-gray-800 border-b-2 border-black pb-4 mb-8">Threat Intelligence Advisory</h1>
{!draft ? (
<div className="h-full flex flex-col items-center justify-center pt-20">
{loading ? (
<div className="flex flex-col items-center text-neo-blue animate-pulse">
<Bot className="w-16 h-16 mb-4" />
<p className="font-black text-lg">Researching and Generating...</p>
<p className="text-sm font-bold text-gray-500 text-center max-w-xs mt-2">Running 7-stage pipeline (web scraping, gap filling, structuring)</p>
</div>
) : (
<p className="text-gray-400 font-bold border-2 border-dashed border-gray-300 rounded-neo p-8 text-center max-w-sm">Submit a threat description. Magnitude will research missing facts and generate a formatted advisory.</p>
)}
</div>
) : (
<div className="space-y-4">

                {/* 1. Report Header Strip */}
                <div className="bg-black text-white p-4 rounded-neo flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-xs font-bold opacity-60 uppercase tracking-widest">Report ID</p>
                    <p className="font-black text-lg">{draft.report_id}</p>
                  </div>
                  <div>
                    <p className="text-xs font-bold opacity-60 uppercase tracking-widest">Date</p>
                    <p className="font-bold text-sm">{draft.date}</p>
                  </div>
                  <div>
                    <p className="text-xs font-bold opacity-60 uppercase tracking-widest">Author</p>
                    <p className="font-bold text-sm">{draft.prepared_by}</p>
                  </div>
                  <div>
                    <span className={`px-3 py-1 font-black text-sm border-2 border-white rounded ${
                      draft.severity_assessed?.toLowerCase() === 'critical' ? 'bg-red-600' :
                      draft.severity_assessed?.toLowerCase() === 'high' ? 'bg-orange-500' :
                      draft.severity_assessed?.toLowerCase() === 'medium' ? 'bg-yellow-400 text-black border-black' :
                      'bg-green-500'
                    }`}>
                      {draft.severity_assessed?.toUpperCase() || 'UNKNOWN'}
                    </span>
                  </div>
                </div>

                {/* 2. Executive Summary */}
                <div className="bg-white p-5 rounded-neo border-neo border-neo-border shadow-neo-sm">
                  <h3 className="font-black text-sm uppercase tracking-widest text-gray-500 mb-2">Executive Summary</h3>
                  <p className="text-sm leading-relaxed">{draft.executive_summary}</p>
                  {draft.cve?.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {draft.cve.map((c, i) => (
                        <span key={i} className="text-xs font-bold bg-neo-accent text-white px-2 py-0.5 border-2 border-black">{c}</span>
                      ))}
                    </div>
                  )}
                </div>

                {/* 3. Quick Stats Row */}
                <div className="grid grid-cols-3 gap-3">
                  <div className="bg-white p-4 rounded-neo border-neo border-neo-border shadow-neo-sm text-center">
                    <p className="text-3xl font-black">{(draft.iocs || []).length}</p>
                    <p className="text-xs font-bold text-gray-500 uppercase">IOCs</p>
                  </div>
                  <div className="bg-white p-4 rounded-neo border-neo border-neo-border shadow-neo-sm text-center">
                    <p className="text-3xl font-black">{(draft.detection_rules || []).length}</p>
                    <p className="text-xs font-bold text-gray-500 uppercase">Detection Rules</p>
                  </div>
                  <div className="bg-white p-4 rounded-neo border-neo border-neo-border shadow-neo-sm text-center">
                    <p className="text-3xl font-black">{(draft.references || []).length}</p>
                    <p className="text-xs font-bold text-gray-500 uppercase">References</p>
                  </div>
                </div>

                {/* Affected Assets chips */}
                {(draft.affected_assets || []).length > 0 && (
                  <div className="bg-white p-4 rounded-neo border-neo border-neo-border shadow-neo-sm">
                    <p className="text-xs font-bold uppercase tracking-widest text-gray-500 mb-2">Affected Assets</p>
                    <div className="flex flex-wrap gap-2">
                      {draft.affected_assets.map((a, i) => (
                        <span key={i} className="text-xs font-bold bg-neo-yellow px-2 py-1 border-2 border-black">{a}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* 4. IOC Table */}
                {(draft.iocs || []).length > 0 && (
                  <div className="bg-white rounded-neo border-neo border-neo-border shadow-neo-sm overflow-hidden">
                    <div className="bg-neo-blue text-white px-4 py-2 flex items-center justify-between">
                      <h3 className="font-black text-sm">Indicators of Compromise</h3>
                      <span className="text-xs font-bold bg-white text-neo-blue px-2 py-0.5 border-2 border-white">{draft.iocs.length} total</span>
                    </div>
                    <div className="divide-y-2 divide-gray-100">
                      {(draft.iocs || []).map((ioc, idx) => (
                        <div key={idx} className="px-4 py-2 text-xs flex items-start justify-between gap-3">
                          <div className="flex items-start gap-2 min-w-0">
                            <span className="font-black uppercase text-neo-blue shrink-0 w-12 text-xs">{ioc.type?.replace('file_hash_', '').replace(/_/g, ' ')}</span>
                            <div className="min-w-0">
                              <p className="font-mono font-bold text-gray-800 truncate text-xs" title={ioc.value}>{ioc.value}</p>
                              {ioc.context && <p className="text-gray-500 mt-0.5 text-xs">{ioc.context}</p>}
                            </div>
                          </div>
                          <div className="flex flex-col items-end gap-1 shrink-0">
                            <span className={`font-bold px-1.5 py-0.5 border border-black text-xs ${
                              ioc.confidence === 'confirmed' ? 'bg-green-100 text-green-800' :
                              ioc.confidence === 'high' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-gray-100'
                            }`}>{ioc.confidence}</span>
                            {ioc.provenance === 'magnitude_research' && (
                              <span className="text-xs bg-neo-accent text-white px-1.5 py-0.5 font-bold border border-black">AI</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Corrections */}
                <div className="bg-neo-accent/10 p-4 lg:p-6 rounded-neo border-neo border-neo-accent shadow-neo-sm">
                  <h4 className="font-black text-lg text-neo-accent mb-2 flex items-center gap-2">
                    <Bot className="w-6 h-6"/> Ask Magnitude to correct this draft
                  </h4>
                  <textarea 
                    value={corrections}
                    onChange={e => setCorrections(e.target.value)}
                    placeholder="e.g. Add more detail about the ransomware family..."
                    className="neo-input text-sm w-full min-h-[80px] mb-4 bg-white" 
                  />
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <label className="flex items-center gap-2 font-bold text-sm cursor-pointer hover:text-neo-blue">
                      <input 
                        type="checkbox" 
                        checked={saveToMemory} 
                        onChange={(e) => setSaveToMemory(e.target.checked)}
                        className="w-5 h-5 rounded border-2 border-black text-neo-blue focus:ring-black cursor-pointer"
                      />
                      Save this instruction to Magnitude's permanent memory
                    </label>
                    <button 
                      onClick={handleRefine}
                      disabled={refining || !corrections.trim()}
                      className="neo-btn bg-black text-white flex items-center gap-2 disabled:opacity-50"
                    >
                      <Bot className={`w-5 h-5 ${refining ? 'animate-spin' : ''}`}/>
                      {refining ? 'Rewriting...' : 'Regenerate Draft'}
                    </button>
                  </div>
                </div>

              </div>
            )}
            </div>
            </div>
          </div>
        </div>
      </div>
    );
};

export default ThreatIntelligence;
