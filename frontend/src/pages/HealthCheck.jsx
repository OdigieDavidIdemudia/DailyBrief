import React, { useState, useEffect } from 'react';
import { Bot, FileText, Upload, Send, File, ShieldCheck, Download, Edit3, Trash2, Plus } from 'lucide-react';

const HealthCheck = () => {
  const [file, setFile] = useState(null);
  const [notes, setNotes] = useState('');
  const [preparedBy, setPreparedBy] = useState('David Odigie');
  const [reviewedBy, setReviewedBy] = useState('Fatima Jinadu');
  
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [refining, setRefining] = useState(false);
  const [draft, setDraft] = useState(() => { const s = sessionStorage.getItem('hc_draft'); return s ? JSON.parse(s) : null; });
  useEffect(() => sessionStorage.setItem('hc_draft', JSON.stringify(draft)), [draft]);
  
  const [corrections, setCorrections] = useState('');
  const [saveToMemory, setSaveToMemory] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleRefine = async () => {
    if (!draft || !corrections.trim()) return;
    
    setRefining(true);
    try {
      // 1. Send refinement request
      const res = await fetch('/api/health-check/refine', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draft, corrections })
      });
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.error || "Refinement failed");
      
      setDraft(data.draft);
      
      // 2. Save to memory if checked
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

  const handleAnalyze = async () => {
    if (!file || !notes.trim()) {
      alert("Please upload a vendor report and provide your remediation notes.");
      return;
    }
    
    setLoading(true);
    setDraft(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_notes', notes);
    formData.append('prepared_by', preparedBy);
    formData.append('reviewed_by', reviewedBy);

    try {
      const res = await fetch('/api/health-check/analyze', {
        method: 'POST',
        credentials: 'include',
        body: formData
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        if (res.status === 401) {
          window.location.href = '/login';
          return;
        }
        throw new Error(data.detail || data.error || "Analysis failed.");
      }
      
      setDraft(data.draft);
      
    } catch (e) {
      alert("Error: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    if (!draft) return;
    
    setExporting(true);
    try {
      const res = await fetch('/api/health-check/export', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draft)
      });
      
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText);
      }
      
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Health_Check_Report.docx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      
    } catch (e) {
      alert("Export Error: " + e.message);
    } finally {
      setExporting(false);
    }
  };

  const updateDraftField = (field, value) => {
    setDraft(prev => ({ ...prev, [field]: value }));
  };

  const updateObservation = (index, field, value) => {
    setDraft(prev => {
      const newObs = [...prev.observations];
      newObs[index] = { ...newObs[index], [field]: value };
      return { ...prev, observations: newObs };
    });
  };

  const removeObservation = (index) => {
    setDraft(prev => {
      const newObs = prev.observations.filter((_, i) => i !== index);
      return { ...prev, observations: newObs };
    });
  };

  const addObservation = () => {
    setDraft(prev => ({
      ...prev,
      observations: [
        ...prev.observations,
        { title: 'New Observation', observation: '', remediation_text: '', status: 'Pending' }
      ]
    }));
  };

  return (
    <div className="flex flex-col h-[calc(100vh-200px)] space-y-6">
      <header className="shrink-0">
        <h2 className="text-3xl font-black text-neo-text">Health Check Remediation</h2>
        <p className="text-gray-600 font-bold mt-2">Generate standardized corporate reports from raw vendor findings using Magnitude AI.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 pb-8 flex-1 min-h-0">
        
        {/* Left Column: Input Form */}
        <div className="bg-white border-neo border-neo-border rounded-neo shadow-neo flex flex-col h-full overflow-hidden">
          <div className="bg-neo-blue p-4 lg:p-6 border-b-neo border-neo-border flex items-center gap-4 text-white shrink-0">
            <div className="bg-white p-3 rounded-neo border-neo border-neo-border shadow-neo-sm hidden sm:block">
              <ShieldCheck className="w-8 h-8 text-neo-blue" />
            </div>
            <div>
              <h3 className="font-black text-xl tracking-tight">Data Ingestion</h3>
              <p className="text-sm font-bold opacity-90">Upload vendor report and your actions</p>
            </div>
          </div>

          <div className="p-6 space-y-6 flex flex-col flex-1 overflow-y-auto">
            {/* Identities */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block font-bold text-sm mb-1 text-neo-text">Prepared By</label>
                <input 
                  type="text" 
                  value={preparedBy} 
                  onChange={(e) => setPreparedBy(e.target.value)} 
                  className="neo-input text-sm" 
                />
              </div>
              <div>
                <label className="block font-bold text-sm mb-1 text-neo-text">Reviewed By</label>
                <input 
                  type="text" 
                  value={reviewedBy} 
                  onChange={(e) => setReviewedBy(e.target.value)} 
                  className="neo-input text-sm" 
                />
              </div>
            </div>

            {/* File Upload */}
            <div>
              <label className="block font-bold text-sm mb-1 text-neo-text">Vendor Health Check Report (PDF/DOCX)</label>
              <div className="relative border-2 border-dashed border-gray-300 rounded-neo bg-gray-50 hover:bg-gray-100 transition-colors p-6 flex flex-col items-center justify-center cursor-pointer min-h-[120px]">
                <input 
                  type="file" 
                  accept=".pdf,.docx" 
                  onChange={handleFileChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                {file ? (
                  <div className="flex flex-col items-center text-green-600 text-center">
                    <File className="w-8 h-8 mb-2 shrink-0" />
                    <span className="font-bold text-sm break-all">{file.name}</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center text-gray-400 text-center">
                    <Upload className="w-8 h-8 mb-2 shrink-0" />
                    <span className="font-bold text-sm">Click or drag file to upload</span>
                  </div>
                )}
              </div>
            </div>

            {/* Notes Textarea */}
            <div className="flex flex-col flex-1">
              <label className="block font-bold text-sm mb-1 text-neo-text">Your Remediation Notes</label>
              <textarea 
                value={notes} 
                onChange={(e) => setNotes(e.target.value)}
                placeholder="List the actions you took to resolve the findings..."
                className="neo-input text-sm flex-1 resize-y min-h-[150px]"
              />
            </div>
          </div>

          <div className="p-4 border-t-neo border-neo-border bg-gray-50 shrink-0 flex justify-end">
             <button 
                onClick={handleAnalyze}
                disabled={loading || !file || !notes.trim()}
                className="neo-btn bg-neo-primary text-white px-8 flex items-center justify-center gap-2"
              >
                {loading ? <Bot className="w-5 h-5 animate-bounce"/> : <Send className="w-5 h-5" />} 
                {loading ? "Magnitude is Analyzing..." : "Build Draft"}
              </button>
          </div>
        </div>

        {/* Right Column: Output/Preview */}
        <div className="bg-white border-neo border-neo-border rounded-neo shadow-neo flex flex-col h-full overflow-hidden">
           <div className="bg-neo-yellow p-4 lg:p-6 border-b-neo border-neo-border flex items-center justify-between text-neo-text shrink-0">
            <div className="flex items-center gap-4">
              <div className="bg-white p-3 rounded-neo border-neo border-neo-border shadow-neo-sm hidden sm:block">
                <Edit3 className="w-8 h-8 text-neo-blue" />
              </div>
              <div>
                <h3 className="font-black text-xl tracking-tight">Draft Preview</h3>
                <p className="text-sm font-bold opacity-90">Review and tweak before export</p>
              </div>
            </div>
            {draft && (
              <button 
                onClick={handleExport}
                disabled={exporting}
                className="neo-btn bg-neo-green text-black flex items-center justify-center gap-2"
              >
                <Download className="w-5 h-5"/>
                {exporting ? "Exporting..." : "Export DOCX"}
              </button>
            )}
            </div>
          
          <div className="flex-1 overflow-y-auto bg-gray-200 p-4 lg:p-8 flex justify-center">
            <div className="space-y-6">
            {!draft ? (
              <div className="h-full flex flex-col items-center justify-center">
                 {loading ? (
                   <div className="flex flex-col items-center text-neo-blue animate-pulse">
                      <Bot className="w-16 h-16 mb-4" />
                      <p className="font-black text-lg">Magnitude is mapping observations...</p>
                      <p className="text-sm font-bold text-gray-500 text-center max-w-xs mt-2">
                        Reading a massive vendor report takes a few seconds. Stand by.
                      </p>
                   </div>
                 ) : (
                   <p className="text-gray-400 font-bold border-2 border-dashed border-gray-300 rounded-neo p-8 text-center max-w-sm">
                      Upload a vendor document and provide your notes to generate an editable draft preview.
                   </p>
                 )}
            </div>
) : (
              <div className="space-y-6">
                {/* Meta Fields */}
                <div className="bg-white p-4 rounded-neo border-neo border-neo-border shadow-neo-sm space-y-4">
                  <h4 className="font-black text-lg border-b-2 border-black pb-2">Document Metadata</h4>
                  
                  <div>
                    <label className="block text-xs font-bold uppercase text-gray-600 mb-1">Report Title</label>
                    <input 
                      type="text" 
                      value={draft.report_title} 
                      onChange={e => updateDraftField('report_title', e.target.value)} 
                      className="neo-input text-sm w-full font-bold" 
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-bold uppercase text-gray-600 mb-1">Prepared By</label>
                      <input type="text" value={draft.prepared_by} onChange={e => updateDraftField('prepared_by', e.target.value)} className="neo-input text-sm w-full" />
                    </div>
                    <div>
                      <label className="block text-xs font-bold uppercase text-gray-600 mb-1">Reviewed By</label>
                      <input type="text" value={draft.reviewed_by} onChange={e => updateDraftField('reviewed_by', e.target.value)} className="neo-input text-sm w-full" />
                    </div>
                  </div>
                </div>

                {/* Summaries */}
                <div className="bg-white p-4 rounded-neo border-neo border-neo-border shadow-neo-sm space-y-4">
                  <h4 className="font-black text-lg border-b-2 border-black pb-2">Summaries</h4>
                  
                  <div>
                    <label className="block text-xs font-bold uppercase text-gray-600 mb-1">Introduction</label>
                    <textarea 
                      value={draft.introduction} 
                      onChange={e => updateDraftField('introduction', e.target.value)} 
                      className="neo-input text-sm w-full min-h-[80px]" 
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold uppercase text-gray-600 mb-1">Conclusion</label>
                    <textarea 
                      value={draft.conclusion} 
                      onChange={e => updateDraftField('conclusion', e.target.value)} 
                      className="neo-input text-sm w-full min-h-[80px]" 
                    />
                  </div>
                </div>

                {/* Observations */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-black text-lg bg-neo-blue text-white px-4 py-1 border-neo border-neo-border shadow-neo-sm inline-block">Observations ({draft.observations.length})</h4>
                    <button onClick={addObservation} className="text-neo-blue hover:text-neo-primary transition-colors flex items-center font-bold text-sm gap-1">
                      <Plus className="w-4 h-4"/> Add Custom
                    </button>
                  </div>
                  
                  <div className="space-y-4">
                    {draft.observations.map((obs, idx) => (
                      <div key={idx} className="bg-white p-4 rounded-neo border-neo border-neo-border shadow-neo-sm relative group">
                        <button 
                          onClick={() => removeObservation(idx)}
                          className="absolute -right-2 -top-2 bg-red-500 text-white p-1.5 rounded-full border-2 border-black opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600 shadow-neo-sm"
                          title="Remove Observation"
                        >
                          <Trash2 className="w-4 h-4"/>
                        </button>

                        <div className="space-y-3">
                          <div className="flex gap-4">
                            <div className="flex-1">
                              <label className="block text-xs font-bold uppercase text-gray-600 mb-1">Title</label>
                              <input 
                                type="text" 
                                value={obs.title} 
                                onChange={e => updateObservation(idx, 'title', e.target.value)} 
                                className="neo-input text-sm w-full font-bold" 
                              />
                            </div>
                            <div className="w-32 shrink-0">
                              <label className="block text-xs font-bold uppercase text-gray-600 mb-1">Status</label>
                              <select 
                                value={obs.status}
                                onChange={e => updateObservation(idx, 'status', e.target.value)}
                                className="neo-input text-sm w-full font-bold cursor-pointer"
                              >
                                <option value="Closed">Closed</option>
                                <option value="Ongoing">Ongoing</option>
                                <option value="Pending">Pending</option>
                              </select>
                            </div>
                          </div>

                          <div>
                            <label className="block text-xs font-bold uppercase text-gray-600 mb-1">Vendor Observation</label>
                            <textarea 
                              value={obs.observation} 
                              onChange={e => updateObservation(idx, 'observation', e.target.value)} 
                              className="neo-input text-sm w-full min-h-[60px]" 
                            />
                          </div>

                          <div>
                            <label className="block text-xs font-bold uppercase text-neo-accent mb-1 flex items-center gap-1"><ShieldCheck className="w-3 h-3"/> Remediation Action</label>
                            <textarea 
                              value={obs.remediation_text} 
                              onChange={e => updateObservation(idx, 'remediation_text', e.target.value)} 
                              className="neo-input text-sm w-full min-h-[60px] border-neo-accent" 
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

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
                      placeholder="e.g. Make the conclusion shorter, don't use the word 'mitigated', or combine observation 1 and 2..."
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

export default HealthCheck;


