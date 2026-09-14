import React, { useState, useEffect } from 'react';
import { Bot, FileText, Upload, Send, ShieldCheck, Download, Edit3, Trash2, Plus, Radar, CheckCircle, AlertCircle } from 'lucide-react';
import MagnitudePreviewBuilder from '../components/MagnitudePreviewBuilder';

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
  
  // Restore background loading state
  useEffect(() => {
    if (window.tiaPromise) {
      setLoading(true);
      window.tiaPromise.then(data => {
        if (data && data.draft) {
          setDraft(data.draft);
          sessionStorage.setItem('tia_draft', JSON.stringify(data.draft));
        }
        setLoading(false);
      }).catch(e => {
        setLoading(false);
      });
    }
  }, []);
  
  const [inputMode, setInputMode] = useState('manual');
  const [bulkInput, setBulkInput] = useState('');
  
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
  const showToast = (message, type = 'success') => {
    setToast({ show: true, message, type });
    setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 4000);
  };
  
  const [draft, setDraft] = useState(() => { const s = sessionStorage.getItem('tia_draft'); return s ? JSON.parse(s) : null; });
  useEffect(() => sessionStorage.setItem('tia_draft', JSON.stringify(draft)), [draft]);
  
  const [corrections, setCorrections] = useState('');
  const [saveToMemory, setSaveToMemory] = useState(false);

  const handleGenerate = async () => {
    let payloadText = '';
    let payloadIocs = '';
    
    if (inputMode === 'bulk') {
      if (!bulkInput.trim()) { showToast("Please provide the raw feed.", "error"); return; }
      payloadText = bulkInput;
    } else {
      if (!threat.raw_text.trim()) { showToast("Please provide a threat description.", "error"); return; }
      payloadText = threat.raw_text;
      payloadIocs = rawIocs;
    }
    
    setLoading(true);
    setDraft(null);

    sessionStorage.removeItem('tia_draft');
    
    const payload = {
      threat: {
        ...threat,
        raw_text: payloadText,
        severity_hint: threat.severity_hint === "" ? null : threat.severity_hint,
        source_urls: threat.source_urls.split(',').map(s => s.trim()).filter(s => s)
      },
      raw_iocs: payloadIocs,
      session_id: '12345',
      generation_options: {
        auto_enrich_iocs: true
      }
    };

    const fetchPromise = (async () => {
      const res = await fetch('/api/tia/generate', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.error || "Failed");
      return data;
    })();

    window.tiaPromise = fetchPromise;

    try {
      const data = await fetchPromise;
      setDraft(data.draft);
      sessionStorage.setItem('tia_draft', JSON.stringify(data.draft));
      showToast("Advisory generated successfully!", "success");
    } catch (e) {
      showToast('Error: ' + e.message, 'error');
    } finally {
      setLoading(false);
      window.tiaPromise = null;
    }
  };

  const handleRefine = async () => {
    if (!draft || !corrections.trim()) return;
    
    setRefining(true);
    try {
      const res = await fetch('/api/tia/refine', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draft, corrections })
      });
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.error || "Refinement failed");
      
      setDraft(data.draft);
      
      if (saveToMemory) {
        await fetch('/api/memory/add', {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ instruction: corrections })
        });
      }
      
      setCorrections('');
      setSaveToMemory(false);
      showToast("Advisory refined successfully!", "success");
    } catch(e) {
      showToast('Refinement Error: ' + e.message, 'error');
    } finally {
      setRefining(false);
    }
  };

  const handleExport = async (format) => {
    if (!draft) return;
    setExporting(true);
    try {
      const res = await fetch('/api/tia/export', {
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
      a.download = `${draft.report_id || 'TIA'} ${draft.title || 'Draft'}.${format === 'structured_json' ? 'json' : format}`.replace(/[<>:"/\\|?*]/g, '');
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      showToast("Export successful!", "success");
    } catch(e) {
      showToast('Export Error: ' + e.message, 'error');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-neo-bg relative">
      <div className="flex-none p-6 bg-white border-b-neo border-neo-border flex items-center justify-between z-10 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-neo-blue rounded-neo border-neo border-neo-border flex items-center justify-center text-white shadow-neo">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black uppercase tracking-wider text-neo-text">Threat Intelligence</h1>
            <p className="text-sm font-bold text-gray-600">Generate structured TIA reports</p>
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* LEFT PANEL: Inputs */}
        <div className="w-full lg:w-1/2 flex flex-col border-r-neo border-neo-border bg-white z-0">
          <div className="flex border-b-neo border-neo-border bg-white shrink-0">
            <button 
              onClick={() => setInputMode('manual')}
              className={inputMode === 'manual' ? "flex-1 py-3 text-sm font-black uppercase transition-colors bg-white border-b-4 border-b-black" : "flex-1 py-3 text-sm font-black uppercase transition-colors bg-gray-100 text-gray-500"}
            >
              Manual Entry
            </button>
            <button 
              onClick={() => setInputMode('bulk')}
              className={inputMode === 'bulk' ? "flex-1 py-3 text-sm font-black uppercase transition-colors border-l-neo border-neo-border bg-neo-yellow border-b-4 border-b-black" : "flex-1 py-3 text-sm font-black uppercase transition-colors border-l-neo border-neo-border bg-gray-100 text-gray-500"}
            >
              Bulk / Raw Feed
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-6">
            {inputMode === 'bulk' ? (
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase flex justify-between">
                  <span>Raw Intelligence Feed</span>
                  <span className="text-neo-accent">Auto-parse</span>
                </label>
                <textarea 
                  value={bulkInput}
                  onChange={e => setBulkInput(e.target.value)}
                  placeholder="Paste unformatted blog posts, threat bulletins, or a raw dump of IOCs here. Magnitude will structure it..."
                  className="neo-input text-sm w-full min-h-[400px]"
                />
              </div>
            ) : (
              <>
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
              </>
            )}
            
            <button 
              onClick={handleGenerate}
              disabled={loading}
              className="neo-btn bg-black text-white w-full py-4 text-lg flex items-center justify-center gap-2 mt-4"
            >
              <Bot className={loading ? "w-6 h-6 animate-spin" : "w-6 h-6"}/>
              {loading ? 'Magnitude Processing...' : 'Generate Advisory'}
            </button>
          </div>
        </div>

        {/* RIGHT PANEL: Preview */}
        <div className="w-full lg:w-1/2 flex flex-col bg-gray-50 z-0">
          {draft && (
            <div className="bg-neo-blue p-4 flex items-center justify-between shrink-0 text-white border-b-neo border-neo-border">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5"/>
                <span className="font-black">Draft Preview</span>
              </div>
              <div className="flex gap-2">
                <button onClick={() => handleExport('csv')} disabled={exporting} className="neo-btn bg-white text-black text-xs py-1 px-3 flex items-center gap-1 border-2 border-black">
                  <Download className="w-3 h-3"/> IOC CSV
                </button>
                <button onClick={() => handleExport('structured_json')} className="neo-btn bg-white text-black text-xs py-1 px-3 border-2 border-black">JSON</button>
                <button onClick={() => handleExport('docx')} disabled={exporting} className="neo-btn bg-neo-green text-black flex items-center gap-2 text-sm border-2 border-black">
                  <Download className="w-4 h-4"/> {exporting ? 'Exporting...' : 'Export DOCX'}
                </button>
              </div>
            </div>
          )}

          <div className="flex-1 overflow-y-auto p-4 lg:p-8 flex justify-center bg-gray-200">
            {!draft ? (
              loading ? (
                <MagnitudePreviewBuilder moduleType="tia" />
              ) : (
                <div className="h-full flex flex-col items-center justify-center pt-20">
                  <p className="text-gray-400 font-bold border-2 border-dashed border-gray-300 rounded-neo p-8 text-center max-w-sm">Submit a threat description. Magnitude will research missing facts and generate a formatted advisory.</p>
                </div>
              )
            ) : (
              <div className="bg-white w-full max-w-[816px] min-h-[1056px] shadow-lg p-10 lg:p-16 font-serif text-sm space-y-6">
                <h1 className="text-3xl font-bold uppercase tracking-tight text-gray-800 border-b-2 border-black pb-4 mb-8">Threat Intelligence Advisory</h1>
                
                <div className="space-y-4">
                  <div className="bg-black text-white p-4 rounded-neo flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="text-xs font-bold opacity-60 uppercase tracking-widest">Report ID</p>
                      <p className="font-black text-lg">{draft.report_id}</p>
                    </div>
                  </div>
                  <div>
                    <h3 className="font-bold text-lg border-b-2 border-black pb-2 mb-2">1. Threat Summary</h3>
                    <p>{draft.summary}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-bold border-b border-gray-300 mb-2">Actor</h4>
                      <p>{draft.actor_profile}</p>
                    </div>
                  </div>
                </div>
                
                <div className="pt-8 border-t-4 border-black mt-12">
                  <h4 className="font-black text-lg uppercase tracking-wider mb-2 flex items-center gap-2">
                    <Edit3 className="w-5 h-5"/> Refine Draft
                  </h4>
                  <textarea 
                    value={corrections}
                    onChange={e => setCorrections(e.target.value)}
                    placeholder="e.g. Add more detail about the ransomware family..."
                    className="neo-input text-sm w-full min-h-[80px] mb-4 bg-white" 
                  />
                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2 text-xs font-bold uppercase cursor-pointer">
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
                      className="neo-btn bg-black text-white px-6 py-2 flex items-center gap-2"
                    >
                      {refining ? 'Rewriting...' : 'Regenerate Draft'}
                    </button>
                  </div>
                </div>

              </div>
            )}
          </div>
        </div>
      </div>
      
      {toast.show && (
        <div className="fixed bottom-6 right-6 z-50 animate-bounce">
          <div className={toast.type === 'error' ? "px-6 py-4 rounded-neo border-neo border-neo-border shadow-neo flex items-center gap-3 font-black text-lg bg-red-500 text-white" : "px-6 py-4 rounded-neo border-neo border-neo-border shadow-neo flex items-center gap-3 font-black text-lg bg-neo-green text-black"}>
            {toast.type === 'error' ? <AlertCircle className="w-6 h-6"/> : <CheckCircle className="w-6 h-6"/>}
            {toast.message}
          </div>
        </div>
      )}
    </div>
  );
};

export default ThreatIntelligence;

