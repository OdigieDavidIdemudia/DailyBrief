import React, { useState, useEffect } from 'react';
import { Bot, Download, Send, FileText } from 'lucide-react';

const Downtime = () => {
  const [brief, setBrief] = useState(() => sessionStorage.getItem('dt_brief') || '');
  useEffect(() => sessionStorage.setItem('dt_brief', brief), [brief]);
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [draft, setDraft] = useState(() => { const s = sessionStorage.getItem('dt_draft'); return s ? JSON.parse(s) : null; });
  useEffect(() => sessionStorage.setItem('dt_draft', JSON.stringify(draft)), [draft]);
  const [exporting, setExporting] = useState(false);
  const [refining, setRefining] = useState(false);
  
  const [corrections, setCorrections] = useState('');
  const [saveToMemory, setSaveToMemory] = useState(false);

  const handleRefine = async () => {
    if (!draft || !corrections.trim()) return;
    
    setRefining(true);
    try {
      const res = await fetch('/api/downtime/refine', {
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
    } catch (e) {
      alert("Error: " + e.message);
    } finally {
      setRefining(false);
    }
  };

  const handleAskMagnitude = async () => {
    if (!brief.trim()) return;
    
    const newMsg = { role: 'user', content: brief };
    setChatHistory([...chatHistory, newMsg]);
    setBrief('');
    setLoading(true);

    try {
      const res = await fetch('/api/downtime/chat', { credentials: 'include', 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brief: newMsg.content, history: chatHistory })
      });
      const data = await res.json();
      
      if (!res.ok) {
        if (res.status === 401) {
          window.location.href = '/login';
          return;
        }
        throw new Error(data.detail || data.error || "API Error: " + res.status);
      }
      
      if (data.status === 'complete') {
        setDraft(data.draft);
        setChatHistory(prev => [...prev, { role: 'bot', content: "I have generated the complete Downtime Report draft for your review." }]);
      } else {
        const botReply = data.questions ? data.questions.join(" ") : (data.reply || "Could you provide more details?");
        setChatHistory(prev => [...prev, { role: 'bot', content: botReply }]);
      }
    } catch (e) {
      alert("Error: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    if (!draft) return;
    setExporting(true);
    
    const payload = {
        format: format,
        downtime_id: draft.downtime_id || `SOC/${new Date().toLocaleDateString('en-GB').replace(/\//g, '')}/${Math.floor(Math.random()*1000)}`,
        start_date: draft.start_date || '',
        start_time: draft.start_time || '',
        end_date: draft.end_date || '',
        end_time: draft.end_time || '',
        duration: draft.duration || '',
        system_affected: draft.system_affected || '',
        severity: draft.severity || 'High',
        reported_by: draft.reported_by || 'David Odigie',
        position: draft.position || 'Security Monitoring Analyst',
        internal_communication: draft.internal_communication || '',
        external_communication: draft.external_communication || '',
        resource: draft.resource || '',
        impact_summary: draft.impact_summary || '',
        detection_and_notification: draft.detection_and_notification || '',
        root_cause_analysis: draft.root_cause_analysis || '',
        mitigation_and_recovery: draft.mitigation_and_recovery || '',
        preventive_measures: draft.preventive_measures || ''
      };

    try {
      const res = await fetch('/api/downtime/export', { credentials: 'include', 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!res.ok) throw new Error("Export failed");
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Downtime_Report_${payload.downtime_id.replace(/\//g, '_')}.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      alert(e.message);
    } finally {
      setExporting(false);
    }
  };

  const handleInputChange = (field, value) => {
    setDraft(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="flex flex-col h-full space-y-6">
      <header>
        <h2 className="text-3xl font-black text-neo-text">Downtime Register</h2>
        <p className="text-gray-600 font-bold mt-2">Generate standard incident reports with Magnitude AI</p>
      </header>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-8 min-h-0 pb-8">
        
        {/* Left Column: Chat */}
        <div className="flex flex-col bg-white border-neo border-neo-border rounded-neo shadow-neo h-full overflow-hidden">
          <div className="bg-neo-blue p-6 border-b-neo border-neo-border flex items-center gap-4 text-white shrink-0">
            <div className="bg-white p-3 rounded-neo border-neo border-neo-border shadow-neo-sm">
              <Bot className="w-8 h-8 text-neo-blue" />
            </div>
            <div>
              <h3 className="font-black text-xl tracking-tight">Magnitude AI</h3>
              <p className="text-sm font-bold opacity-90">Downtime Incident Assistant</p>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50">
            {chatHistory.length === 0 && (
              <div className="text-center text-gray-500 font-bold mt-10">
                Describe the downtime incident here.
              </div>
            )}
            {chatHistory.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] p-4 rounded-neo border-neo border-neo-border font-bold text-sm leading-relaxed ${
                  msg.role === 'user' ? 'bg-neo-yellow shadow-neo-sm' : 'bg-white shadow-neo-sm text-gray-800'
                }`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white p-4 rounded-neo border-neo border-neo-border shadow-neo-sm font-bold animate-pulse text-neo-primary flex items-center gap-2">
                  <Bot className="w-5 h-5 animate-bounce"/> Thinking...
                </div>
              </div>
            )}
            </div>
<div className="p-4 border-t-neo border-neo-border bg-white shrink-0">
            <div className="flex gap-2">
              <input
                type="text"
                value={brief}
                onChange={(e) => setBrief(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAskMagnitude()}
                placeholder="e.g. QRadar went down at 9am because of disk space..."
                className="flex-1 neo-input"
                disabled={loading}
              />
              <button 
                onClick={handleAskMagnitude}
                disabled={loading || !brief.trim()}
                className="neo-btn bg-neo-primary text-white px-6 flex items-center justify-center gap-2"
              >
                <Send className="w-5 h-5" /> Build
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Editable Draft */}
        <div className="flex flex-col bg-white border-neo border-neo-border rounded-neo shadow-neo h-full overflow-hidden">
          <div className="p-6 border-b-neo border-neo-border flex justify-between items-center bg-gray-50 shrink-0">
            <h3 className="font-black text-xl bg-neo-yellow inline-block px-3 py-1 border-neo border-neo-border shadow-neo-sm transform -rotate-1">Draft Preview</h3>
            <div className="flex gap-2">
              <button 
                onClick={() => handleExport('pdf')}
                disabled={!draft || exporting}
                className="neo-btn bg-neo-accent text-white flex items-center gap-2 text-sm px-4 py-2"
              >
                <FileText className="w-4 h-4"/> PDF
              </button>
              <button 
                onClick={() => handleExport('docx')}
                disabled={!draft || exporting}
                className="neo-btn bg-[#10b981] text-white flex items-center gap-2 text-sm px-4 py-2"
              >
                <Download className="w-4 h-4"/> DOCX
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-6 bg-gray-200 flex justify-center">
            <div className="bg-white w-full max-w-[816px] min-h-[1056px] shadow-lg p-10 lg:p-16 font-serif text-sm space-y-6">
<h1 className="text-3xl font-bold uppercase tracking-tight text-gray-800 border-b-2 border-black pb-4 mb-8">Downtime & Incident Report</h1>
{!draft ? (
<div className="h-full flex flex-col items-center justify-center p-20">
<p className="text-gray-400 font-bold border-2 border-dashed border-gray-300 rounded-neo p-8 text-center w-full">Draft will appear here.</p>
</div>
) : (
<div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="block font-bold text-sm mb-1 text-neo-text">Downtime ID</label>
                    <input type="text" value={draft.downtime_id || `SOC/${new Date().toLocaleDateString('en-GB').replace(/\//g, '')}/${Math.floor(Math.random()*1000)}`} onChange={(e) => handleInputChange('downtime_id', e.target.value)} className="neo-input text-sm" />
                  </div>
                  <div>
                    <label className="block font-bold text-sm mb-1 text-neo-text">Start Date</label>
                    <input type="text" value={draft.start_date || ''} onChange={(e) => handleInputChange('start_date', e.target.value)} className="neo-input text-sm" placeholder="DD/MM/YYYY" />
                  </div>
                  <div>
                    <label className="block font-bold text-sm mb-1 text-neo-text">Start Time</label>
                    <input type="text" value={draft.start_time || ''} onChange={(e) => handleInputChange('start_time', e.target.value)} className="neo-input text-sm" placeholder="HH:MM" />
                  </div>
                  <div>
                    <label className="block font-bold text-sm mb-1 text-neo-text">End Date</label>
                    <input type="text" value={draft.end_date || ''} onChange={(e) => handleInputChange('end_date', e.target.value)} className="neo-input text-sm" placeholder="DD/MM/YYYY" />
                  </div>
                  <div>
                    <label className="block font-bold text-sm mb-1 text-neo-text">End Time</label>
                    <input type="text" value={draft.end_time || ''} onChange={(e) => handleInputChange('end_time', e.target.value)} className="neo-input text-sm" placeholder="HH:MM" />
                  </div>
                  <div>
                    <label className="block font-bold text-sm mb-1 text-neo-text">Duration</label>
                    <input type="text" value={draft.duration || ''} onChange={(e) => handleInputChange('duration', e.target.value)} className="neo-input text-sm" placeholder="e.g. 5 Hours" />
                  </div>
                  <div>
                    <label className="block font-bold text-sm mb-1 text-neo-text">Severity Level</label>
                    <input type="text" value={draft.severity || 'High'} onChange={(e) => handleInputChange('severity', e.target.value)} className="neo-input text-sm" />
                  </div>
                  <div className="col-span-2">
                    <label className="block font-bold text-sm mb-1 text-neo-text">System Affected</label>
                    <input type="text" value={draft.system_affected || ''} onChange={(e) => handleInputChange('system_affected', e.target.value)} className="neo-input text-sm" />
                  </div>
                </div>

                {['impact_summary', 'detection_and_notification', 'root_cause_analysis', 'mitigation_and_recovery', 'preventive_measures', 'internal_communication', 'external_communication', 'resource'].map((key) => (
                  <div key={key} className="flex flex-col gap-1">
                    <label className="font-black text-neo-blue uppercase text-sm tracking-wider">{key.replace(/_/g, ' ')}</label>
                    <textarea 
                      value={draft[key] || ''} 
                      onChange={(e) => handleInputChange(key, e.target.value)}
                      className="neo-input min-h-[100px] text-sm"
                    />
                  </div>
                  ))}

                {/* Corrections Loop */}
                <div className="mt-8 bg-neo-accent/10 p-4 lg:p-6 rounded-neo border-neo border-neo-accent shadow-neo-sm">
                  <h4 className="font-black text-lg text-neo-accent mb-2 flex items-center gap-2">
                    <Bot className="w-6 h-6"/> Ask Magnitude to correct this draft
                  </h4>
                  <p className="text-sm font-bold text-gray-700 mb-4">
                    Are there stylistic issues? Too much jargon? Tell Magnitude how to rewrite this.
                  </p>
                  
                  <textarea 
                    value={corrections}
                    onChange={e => setCorrections(e.target.value)}
                    placeholder="e.g. Make the impact summary shorter, simplify the jargon in root cause..."
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

export default Downtime;

