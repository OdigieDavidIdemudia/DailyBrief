import React, { useState, useEffect } from 'react';
import { Bot, Save, FileText, Send, CheckCircle, Table, Check, Edit3, X, AlertCircle, ShieldCheck, Download } from 'lucide-react';


const StandaloneTab = ({ showToast }) => {
  const [assessmentName, setAssessmentName] = useState('');
  const [scope, setScope] = useState('');
  const [rawNotes, setRawNotes] = useState('');
  const [generating, setGenerating] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [draft, setDraft] = useState(null);

  const handleGenerate = async () => {
    if (!assessmentName || !scope || !rawNotes) { showToast("Please fill all fields.", "error"); return; }
    setGenerating(true);
    try {
      const res = await fetch('http://localhost:8000/api/assessment/standalone/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ assessment_name: assessmentName, scope, raw_notes: rawNotes })
      });
      const data = await res.json();
      setDraft(data);
      showToast("Draft generated!", "success");
    } catch (e) {
      console.error(e);
      showToast("Generation failed", "error");
    } finally {
      setGenerating(false);
    }
  };

  const handleExport = async () => {
    if (!draft) return;
    setExporting(true);
    try {
      const res = await fetch('http://localhost:8000/api/assessment/standalone/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draft })
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `GTCO_${draft.assessment_name}_Report.docx`;
      a.click();
      showToast("Exported DOCX", "success");
    } catch (e) {
      showToast("Export failed", "error");
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="flex h-full gap-4">
      <div className="w-1/2 flex flex-col gap-4">
        <div className="p-4 bg-white shadow-neo border-2 border-black rounded-neo">
          <h2 className="font-black mb-4">STANDALONE CONFIGURATION REVIEW</h2>
          <div className="space-y-4">
            <input type="text" placeholder="Assessment Name (e.g. Cortex XDR)" value={assessmentName} onChange={e=>setAssessmentName(e.target.value)} className="neo-input w-full" />
            <input type="text" placeholder="Scope (e.g. Nigeria)" value={scope} onChange={e=>setScope(e.target.value)} className="neo-input w-full" />
            <textarea placeholder="Paste auditor raw notes..." value={rawNotes} onChange={e=>setRawNotes(e.target.value)} className="neo-input w-full h-64" />
            <button onClick={handleGenerate} disabled={generating} className="neo-btn bg-black text-white w-full flex justify-center items-center gap-2">
              {generating ? "Generating..." : "Generate Standalone Report"}
            </button>
          </div>
        </div>
      </div>
      <div className="w-1/2 bg-white shadow-neo border-2 border-black rounded-neo flex flex-col">
        <div className="p-4 border-b-2 border-black flex justify-between items-center bg-neo-yellow">
          <div className="font-black flex items-center gap-2"><FileText className="w-5 h-5"/> Live DOCX Preview</div>
          <button onClick={handleExport} disabled={exporting || !draft} className="neo-btn bg-white px-4 py-1 text-sm disabled:opacity-50">
            {exporting ? "Exporting..." : "Export DOCX"}
          </button>
        </div>
        <div className="p-4 flex-1 overflow-y-auto bg-gray-200 flex justify-center">
        <div className="bg-white w-full max-w-[816px] min-h-[1056px] shadow-lg p-12 font-serif text-sm border-4 border-black relative">
          
          {/* Cover Section */}
          <div className="mb-24 mt-12 text-center">
            <h1 className="text-3xl font-bold mb-2">Guaranty Trust Bank</h1>
            <h2 className="text-xl font-bold uppercase">{assessmentName || "[ASSESSMENT NAME]"}</h2>
            <h3 className="text-lg font-bold uppercase">({scope || "[SCOPE]"})</h3>
          </div>

          <div className="border-b-2 border-black mb-8" />

          {draft ? (
            <>
              {/* Introduction & Scope */}
              <div className="mb-8">
                <h3 className="font-bold text-lg border-b-2 border-black mb-4">Introduction</h3>
                <p className="mb-6">{draft.introduction}</p>

                <h3 className="font-bold text-lg border-b-2 border-black mb-4">Scope of Assessment</h3>
                <p className="mb-2">The scope of the {draft.assessment_name} assessment includes:</p>
                <ul className="list-disc pl-8 mb-6">
                  {draft.scope_items.map((item, i) => <li key={i}>{item}</li>)}
                </ul>
              </div>

              {/* Findings */}
              {draft.findings.map((f, i) => (
                <div key={i} className="mb-8">
                  <h4 className="font-bold text-md mb-4 uppercase">
                    {i+1}. {f.title} - <span className={`px-1 ${f.severity === 'HIGH' ? 'bg-red-500 text-white' : f.severity === 'MID' ? 'bg-yellow-400 text-black' : 'bg-green-400 text-black'}`}>{f.severity}</span>
                  </h4>
                  
                  <div className="bg-[#2E5FA2] text-white font-bold p-1 pl-2 mb-2">Observations</div>
                  <ul className="list-disc pl-8 mb-4">
                    {(f.observations && f.observations.length > 0) ? f.observations.map((obs, j) => <li key={j}>{obs}</li>) : <li>None identified.</li>}
                  </ul>

                  <div className="bg-[#2E5FA2] text-white font-bold p-1 pl-2 mb-2">Impact</div>
                  <ul className="list-disc pl-8 mb-4">
                    {(f.impact && f.impact.length > 0) ? f.impact.map((imp, j) => <li key={j}>{imp}</li>) : <li>None identified.</li>}
                  </ul>

                  <div className="bg-[#2E5FA2] text-white font-bold p-1 pl-2 mb-2">Recommendations</div>
                  <ul className="list-disc pl-8 mb-4">
                    {(f.recommendations && f.recommendations.length > 0) ? f.recommendations.map((rec, j) => <li key={j}>{rec}</li>) : <li>None identified.</li>}
                  </ul>
                </div>
              ))}
              
              <h3 className="font-bold text-lg border-b-2 border-black mb-4">CONCLUSION</h3>
              <p>This concludes the {draft.assessment_name} configuration review.</p>
            </>
          ) : (
            <div className="text-center text-gray-400 mt-32 font-bold uppercase tracking-widest border-2 border-dashed border-gray-300 p-12">
              [ Assessment Findings Will Populate Here ]
            </div>
          )}
        </div>
      </div>
      </div>
    </div>
  );
};

const AssessmentPipeline = () => {

  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
  const showToast = (message, type = 'success') => {
    setToast({ show: true, message, type });
    setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 3000);
  };

  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [state, setState] = useState({
    subsidiary: { subsidiary_name: '', country: '', engagement_ref: '', assessment_period_start: '', assessment_period_end: '', lead_assessor: '' },
    tools: {}
  });
  
  const [activeTool, setActiveTool] = useState('NAC');

  useEffect(() => {
    fetch('http://localhost:8000/api/assessment/state')
      .then(r => r.json())
      .then(data => setState(data))
      .catch(e => console.error("Failed to load state", e));
  }, []);

  const saveState = async (newState) => {
    setState(newState);
    try {
      await fetch('http://localhost:8000/api/assessment/state', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newState)
      });
    } catch(e) { console.error(e); }
  };

  const updateSubsidiary = (field, value) => {
    const newState = { ...state, subsidiary: { ...state.subsidiary, [field]: value } };
    saveState(newState);
  };

  const getTool = (toolId) => {
    if (!state.tools[toolId]) {
      return {
        tool_id: toolId,
        tool_display_name: toolId,
        assessment_date: new Date().toISOString().split('T')[0],
        performed_by: state.subsidiary.lead_assessor || '',
        status: 'in_progress',
        findings: [],
        advisories: []
      };
    }
    return state.tools[toolId];
  };

  const updateTool = (toolId, updatedTool) => {
    const newState = { ...state, tools: { ...state.tools, [toolId]: updatedTool } };
    saveState(newState);
  };

  const TOOL_OPTIONS = [
    { id: 'NAC', name: 'NAC (e.g. Forescout)' },
    { id: 'ActiveDirectory', name: 'Active Directory' },
    { id: 'PAM', name: 'PAM' },
    { id: 'SIEM', name: 'SIEM' },
    { id: 'XDR', name: 'XDR' },
    { id: 'DAM', name: 'DAM' },
    { id: 'FIM', name: 'FIM' },
    { id: 'DLP', name: 'DLP' },
    { id: 'WebProxy', name: 'Web Proxy' },
    { id: 'VirtualDevicesNetworks', name: 'Virtual Devices & Networks' }
  ];

  return (
    <div className="h-full flex flex-col relative overflow-hidden bg-white">
      <div className="flex-none p-4 lg:p-6 bg-white border-b-neo border-neo-border z-10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-neo-primary rounded-neo border-neo border-black flex items-center justify-center shadow-neo-sm">
            <ShieldCheck className="w-6 h-6 text-black" />
          </div>
          <div>
            <h1 className="text-2xl font-black uppercase tracking-tight">Assessment Pipeline</h1>
            <p className="text-sm font-bold text-gray-600">Tool Findings & Tracker Generation</p>
          </div>
        </div>
        
        <div className="flex bg-gray-100 rounded-neo border-2 border-black p-1 shadow-neo-sm">
          <button 
            onClick={() => setActiveTab('dashboard')}
            className={`px-4 py-2 font-bold text-sm rounded transition-colors ${activeTab === 'dashboard' ? 'bg-white border-2 border-black shadow-sm' : 'text-gray-600 hover:bg-gray-200'}`}
          >
            Dashboard / Macro
          </button>
          <button 
            onClick={() => setActiveTab('assessment')}
            className={`px-4 py-2 font-bold text-sm rounded transition-colors ${activeTab === 'assessment' ? 'bg-white border-2 border-black shadow-sm' : 'text-gray-600 hover:bg-gray-200'}`}
          >
            Tool Assessment / Micro
          </button>
            <button onClick={() => setActiveTab('standalone')} className={`px-4 py-2 font-bold text-sm rounded transition-colors ${activeTab === 'standalone' ? 'bg-white border-2 border-black shadow-sm' : 'text-gray-600 hover:bg-gray-200'}`}>Config Review (Standalone)</button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {activeTab === 'dashboard' ? (
          <DashboardTab 
            state={state} 
            updateSubsidiary={updateSubsidiary} 
            TOOL_OPTIONS={TOOL_OPTIONS}
          />
        ) : (
          <AssessmentTab 
            toolId={activeTool} 
            setToolId={setActiveTool} 
            tool={getTool(activeTool)} 
            updateTool={(t) => updateTool(activeTool, t)}
            subsidiary={state.subsidiary}
            TOOL_OPTIONS={TOOL_OPTIONS}
          />
        )}
      </div>
    </div>
  );
};

const DashboardTab = ({ state, updateSubsidiary, TOOL_OPTIONS }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [exporting, setExporting] = useState(false);

  const fetchDashboard = async () => {
    if (!state.subsidiary.subsidiary_name) return;
    try {
      const res = await fetch(`http://localhost:8000/api/assessment/dashboard?subsidiary_name=${encodeURIComponent(state.subsidiary.subsidiary_name)}`);
      const data = await res.json();
      setDashboardData(data);
    } catch(e) { console.error(e); }
  };

  useEffect(() => {
    fetchDashboard();
  }, [state.subsidiary.subsidiary_name]);


  const [exportingExSum, setExportingExSum] = useState(false);
  const handleExportExSum = async () => {
    if (!state.subsidiary.subsidiary_name) { showToast("Enter a subsidiary name first.", "error"); return; }
    setExportingExSum(true);
    showToast("AI is generating the Executive Summary. This may take 30 seconds...", "success");
    try {
      const res1 = await fetch('http://localhost:8000/api/assessment/executive-summary/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state })
      });
      if (!res1.ok) throw new Error("Failed to generate draft");
      const draft = await res1.json();
      
      const res2 = await fetch('http://localhost:8000/api/assessment/executive-summary/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draft })
      });
      if (!res2.ok) throw new Error("Failed to export DOCX");
      const blob = await res2.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `GTCO_Executive_Summary.docx`;
      a.click();
      showToast("Executive Summary downloaded!", "success");
    } catch(e) {
      console.error(e);
      showToast("Failed to generate Executive Summary.", "error");
    } finally {
      setExportingExSum(false);
    }
  };

  const handleExportExcel = async () => {
    if (!state.subsidiary.subsidiary_name) { showToast("Enter a subsidiary name first.", "error"); return; }
    setExporting(true);
    
    const toolsToExport = Object.values(state.tools).filter(t => t.status === 'ready_to_generate' || t.status === 'logged_to_master' || t.status === 'closed');
    
    try {
      const res = await fetch('http://localhost:8000/api/assessment/export/excel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subsidiary_name: state.subsidiary.subsidiary_name,
          tools: toolsToExport
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      
      const a = document.createElement('a');
      a.href = `http://localhost:8000${data.download_url}`;
      a.download = data.download_url.split('/').pop();
      a.click();
      
      fetchDashboard();
      
    } catch(e) { console.error(e); showToast("Failed to export Excel.", "error"); }
    finally { setExporting(false); }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="neo-card">
        <div className="bg-neo-bg border-b-neo border-neo-border p-4">
          <h2 className="text-xl font-black uppercase tracking-wider">Subsidiary Profile</h2>
        </div>
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 bg-white">
          <div><label className="block text-xs font-bold uppercase mb-1">Subsidiary Name</label><input type="text" value={state.subsidiary.subsidiary_name} onChange={e=>updateSubsidiary('subsidiary_name', e.target.value)} className="neo-input w-full font-bold" placeholder="e.g. GTBank UK" /></div>
          <div><label className="block text-xs font-bold uppercase mb-1">Country</label><input type="text" value={state.subsidiary.country} onChange={e=>updateSubsidiary('country', e.target.value)} className="neo-input w-full" /></div>
          <div><label className="block text-xs font-bold uppercase mb-1">Engagement Ref</label><input type="text" value={state.subsidiary.engagement_ref} onChange={e=>updateSubsidiary('engagement_ref', e.target.value)} className="neo-input w-full font-mono" /></div>
          <div><label className="block text-xs font-bold uppercase mb-1">Start Date</label><input type="date" value={state.subsidiary.assessment_period_start} onChange={e=>updateSubsidiary('assessment_period_start', e.target.value)} className="neo-input w-full" /></div>
          <div><label className="block text-xs font-bold uppercase mb-1">End Date</label><input type="date" value={state.subsidiary.assessment_period_end} onChange={e=>updateSubsidiary('assessment_period_end', e.target.value)} className="neo-input w-full" /></div>
          <div><label className="block text-xs font-bold uppercase mb-1">Lead Assessor</label><input type="text" value={state.subsidiary.lead_assessor} onChange={e=>updateSubsidiary('lead_assessor', e.target.value)} className="neo-input w-full" /></div>
        </div>
      </div>

      <div className="neo-card bg-white">
        <div className="p-4 border-b-neo border-neo-border flex justify-between items-center bg-gray-50">
          <h2 className="text-xl font-black uppercase tracking-wider flex items-center gap-2"><Table className="w-5 h-5"/> Tool Tracker Dashboard</h2>
          <button onClick={handleExportExcel} disabled={exporting || !state.subsidiary.subsidiary_name} className="neo-btn bg-neo-primary text-white flex items-center gap-2 font-bold px-4 py-1.5 text-sm disabled:opacity-50">
            {exporting ? <Bot className="w-4 h-4 animate-spin"/> : <Download className="w-4 h-4"/>} Write Ready Tools to Master Excel
          </button>
            <button onClick={handleExportExSum} disabled={exportingExSum || !state.subsidiary.subsidiary_name} className="neo-btn bg-black text-white flex items-center gap-2 font-bold px-4 py-1.5 text-sm disabled:opacity-50 ml-2">{exportingExSum ? <Bot className="w-4 h-4 animate-spin"/> : <FileText className="w-4 h-4"/>} Generate Executive Summary</button>
        </div>
        {dashboardData ? (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b-2 border-black bg-gray-100">
                <th className="p-3 font-black text-sm uppercase">Tool Name</th>
                <th className="p-3 font-black text-sm uppercase">Total Findings</th>
                <th className="p-3 font-black text-sm uppercase">High/Crit</th>
                <th className="p-3 font-black text-sm uppercase">Status</th>
              </tr>
            </thead>
            <tbody>
              {TOOL_OPTIONS.map(opt => {
                const toolStatus = dashboardData.tools_status[opt.id];
                if (!toolStatus) return null;
                return (
                  <tr key={opt.id} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="p-3 font-bold">{opt.name}</td>
                    <td className="p-3 font-mono">{toolStatus.finding_count}</td>
                    <td className="p-3 font-mono text-red-600">{toolStatus.high_critical_count}</td>
                    <td className="p-3">
                      <span className={`text-xs font-black uppercase px-2 py-1 rounded border border-black ${toolStatus.status === 'in_progress' ? 'bg-yellow-200 text-black' : toolStatus.status === 'ready_to_generate' ? 'bg-green-400 text-black' : 'bg-gray-300 text-black'}`}>
                        {toolStatus.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <p className="text-gray-500 text-sm p-4">No dashboard data available yet. Configure subsidiary name to load.</p>
        )}
      </div>
    </div>
  );
};

const AssessmentTab = ({ toolId, setToolId, tool, updateTool, subsidiary, TOOL_OPTIONS }) => {
  const [inputMode, setInputMode] = useState('single'); // 'single' or 'bulk'
  const [obs, setObs] = useState({ segment_sector: '', title: '', raw_note: '', severity: 'HIGH' });
  const [bulkNote, setBulkNote] = useState('');
  const [generating, setGenerating] = useState(false);
  const [exportingDocx, setExportingDocx] = useState(false);

  const handleLogObservation = async () => {
    if (inputMode === 'single') {
      if (!obs.title || !obs.raw_note) { showToast("Title and Note are required.", "error"); return; }
      
      setGenerating(true);
      try {
        const res = await fetch('http://localhost:8000/api/assessment/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tool_display_name: tool.tool_display_name,
            observation: obs
          })
        });
        const finding = await res.json();
        
        const newFindings = [...tool.findings, finding];
        updateTool({ ...tool, findings: newFindings });
        setObs({ ...obs, title: '', raw_note: '' }); // reset form
      } catch(e) { console.error(e); showToast("Failed to generate finding.", "error"); }
      finally { setGenerating(false); }
    } else {
      if (!bulkNote.trim()) { showToast("Please paste your raw notes.", "error"); return; }
      
      setGenerating(true);
      try {
        const res = await fetch('http://localhost:8000/api/assessment/generate/bulk', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tool_display_name: tool.tool_display_name,
            raw_bulk_notes: bulkNote
          })
        });
        const findings = await res.json();
        
        const newFindings = [...tool.findings, ...findings];
        updateTool({ ...tool, findings: newFindings });
        setBulkNote(''); // reset form
      } catch(e) { console.error(e); showToast("Failed to parse bulk notes.", "error"); }
      finally { setGenerating(false); }
    }
  };

  const handleExportDocx = async () => {
    if (!subsidiary.subsidiary_name) { showToast("Configure subsidiary name in Dashboard first.", "error"); return; }
    setExportingDocx(true);
    try {
      const res = await fetch('http://localhost:8000/api/assessment/export/docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subsidiary_name: subsidiary.subsidiary_name,
          tool: tool
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      
      const a = document.createElement('a');
      a.href = `http://localhost:8000${data.download_url}`;
      a.download = data.download_url.split('/').pop();
      a.click();
    } catch(e) { console.error(e); showToast("Failed to export DOCX.", "error"); }
    finally { setExportingDocx(false); }
  };

  const deleteFinding = (idx) => {
    const arr = [...tool.findings];
    arr.splice(idx, 1);
    updateTool({ ...tool, findings: arr });
  };
  
  const toggleReview = (idx) => {
    const f = [...tool.findings];
    f[idx].reviewed = !f[idx].reviewed;
    const allReviewed = f.every(finding => finding.reviewed);
    updateTool({ ...tool, findings: f, status: allReviewed ? 'ready_to_generate' : 'in_progress' });
  };

  return (
    <div className="flex h-full overflow-hidden">
      {/* LEFT: Inputs & Feed */}
      <div className="w-1/2 flex flex-col border-r-neo border-neo-border">
        
        <div className="p-4 bg-gray-50 border-b-neo border-neo-border shrink-0">
           <label className="block text-xs font-bold uppercase text-gray-600 mb-1">Select Tool to Assess</label>
           <select value={toolId} onChange={e => setToolId(e.target.value)} className="neo-input text-lg font-black w-full bg-white">
             {TOOL_OPTIONS.map(opt => <option key={opt.id} value={opt.id}>{opt.name}</option>)}
           </select>
        </div>
        
        <div className="p-4 shrink-0 border-b-2 border-dashed border-gray-300 bg-white">
           <div className="flex justify-between items-center mb-3">
             <h3 className="font-bold text-sm uppercase flex items-center gap-2"><Edit3 className="w-4 h-4"/> Log Observation</h3>
             <div className="flex bg-gray-100 rounded border border-black p-0.5 text-xs">
                <button 
                  onClick={() => setInputMode('single')}
                  className={`px-2 py-1 font-bold rounded transition-colors ${inputMode === 'single' ? 'bg-neo-primary text-white' : 'text-gray-600 hover:bg-gray-200'}`}
                >
                  Single
                </button>
                <button 
                  onClick={() => setInputMode('bulk')}
                  className={`px-2 py-1 font-bold rounded transition-colors ${inputMode === 'bulk' ? 'bg-neo-primary text-white' : 'text-gray-600 hover:bg-gray-200'}`}
                >
                  Bulk Parse
                </button>
             </div>
           </div>
           
           {inputMode === 'single' ? (
             <>
               <div className="grid grid-cols-2 gap-2 mb-2">
                 <input type="text" placeholder="Segment (e.g. Policy & Access)" value={obs.segment_sector} onChange={e=>setObs({...obs, segment_sector: e.target.value})} className="neo-input text-sm" />
                 <select value={obs.severity} onChange={e=>setObs({...obs, severity: e.target.value})} className="neo-input text-sm font-bold">
                   <option value="CRITICAL">CRITICAL</option>
                   <option value="HIGH">HIGH</option>
                   <option value="MEDIUM">MEDIUM</option>
                   <option value="LOW">LOW</option>
                 </select>
               </div>
               <input type="text" placeholder="Title (e.g. Outdated Switches)" value={obs.title} onChange={e=>setObs({...obs, title: e.target.value})} className="neo-input text-sm w-full mb-2 font-bold" />
               <textarea placeholder="Raw field note... Magnitude will draft Impact & Recs." value={obs.raw_note} onChange={e=>setObs({...obs, raw_note: e.target.value})} className="neo-input text-sm w-full min-h-[60px] mb-2" />
             </>
           ) : (
             <textarea 
               placeholder="Paste all raw auditor notes here. Magnitude will automatically extract multiple findings..." 
               value={bulkNote} 
               onChange={e=>setBulkNote(e.target.value)} 
               className="neo-input text-sm w-full min-h-[120px] mb-2" 
             />
           )}
           
           <button onClick={handleLogObservation} disabled={generating} className="neo-btn bg-black text-white w-full flex items-center justify-center gap-2">
             {generating ? <Bot className="w-4 h-4 animate-spin"/> : <Bot className="w-4 h-4"/>}
             {generating ? "Magnitude Drafting..." : (inputMode === 'single' ? "Log & Draft Impact/Rec" : "Bulk Parse & Draft All")}
           </button>
        </div>

        {/* Feed */}
        <div className="flex-1 overflow-y-auto p-4 bg-gray-100 space-y-4">
          {tool.findings.map((finding, idx) => (
             <div key={idx} className={`p-4 rounded-neo border-2 ${finding.reviewed ? 'border-green-500 bg-green-50' : 'border-black bg-white'} relative`}>
               <button onClick={() => deleteFinding(idx)} className="absolute top-2 right-10 text-gray-400 hover:text-red-500">
                  <X className="w-4 h-4"/>
               </button>
               <div className="flex justify-between items-start mb-2">
                 <h4 className="font-black text-sm w-3/4">{finding.title} <span className="text-gray-500 ml-2">({finding.severity})</span></h4>
                 <button onClick={() => toggleReview(idx)} className={`p-1 rounded-neo border-2 border-black ${finding.reviewed ? 'bg-green-500 text-white' : 'bg-gray-200'}`}>
                   <Check className="w-4 h-4"/>
                 </button>
               </div>
               <p className="text-xs text-gray-500 italic mb-2">Note: {finding.raw_note}</p>
               
               <div className="bg-neo-accent/10 p-2 rounded border border-neo-accent mb-2">
                 <strong className="text-xs uppercase text-neo-accent block">Impact (Magnitude)</strong>
                 <p className="text-sm">{finding.impact}</p>
               </div>
               <div className="bg-neo-blue/10 p-2 rounded border border-neo-blue">
                 <strong className="text-xs uppercase text-neo-blue block">Recommendation (Magnitude)</strong>
                 <p className="text-sm">{finding.recommendation}</p>
               </div>
             </div>
          ))}
          {tool.findings.length === 0 && (
            <div className="text-center text-gray-500 font-bold p-8">No findings logged for {tool.tool_display_name} yet.</div>
          )}
        </div>
      </div>

      {/* RIGHT: DOCX Preview */}
      <div className="w-1/2 flex flex-col bg-white">
        <div className="p-4 bg-neo-yellow border-b-neo border-neo-border flex justify-between items-center shrink-0">
          <div className="font-black flex items-center gap-2"><FileText className="w-5 h-5"/> Live DOCX Preview</div>
          <button onClick={handleExportDocx} disabled={exportingDocx || tool.findings.length === 0} className="neo-btn bg-white text-black border-2 border-black px-4 py-1 flex items-center gap-2 text-sm disabled:opacity-50">
            {exportingDocx ? <Bot className="w-4 h-4 animate-spin"/> : <Send className="w-4 h-4"/>} 
            Export DOCX 
            {tool.findings.length > 0 && tool.findings.some(f => !f.reviewed) && <span className="bg-red-500 text-white text-[10px] px-1 rounded ml-1">DRAFT</span>}
          </button>
        </div>
        <div className="flex-1 overflow-y-auto bg-gray-200 p-4 lg:p-8 flex justify-center">
          <div className="bg-white w-full max-w-[816px] min-h-[1056px] shadow-lg p-10 lg:p-16 font-serif text-sm">
            
            {/* Dummy Header */}
            <div className="border-b-2 border-black pb-4 mb-8 flex justify-between items-end">
              <div>
                <h1 className="text-3xl font-bold uppercase tracking-tight text-gray-800">Technical Assessment</h1>
                <h2 className="text-xl text-gray-600 mt-1">{tool.tool_display_name}</h2>
              </div>
              <div className="text-right text-xs font-bold text-gray-500 uppercase">
                <p>{subsidiary.subsidiary_name || '[SUBSIDIARY NAME]'}</p>
                <p>{subsidiary.assessment_period_start || '[DATE]'} - {subsidiary.assessment_period_end || '[DATE]'}</p>
              </div>
            </div>

            <div className="space-y-4 mb-8 text-gray-700">
              <p>This document outlines the findings observed during the technical assessment of the <strong>{tool.tool_display_name}</strong> solution deployed at <strong>{subsidiary.subsidiary_name || '[SUBSIDIARY]'}</strong>.</p>
              <p>The objective of this assessment is to identify configuration gaps, security risks, and areas for improvement within the {tool.tool_display_name} environment, and to provide actionable recommendations for remediation.</p>
            </div>
            
            {/* Wireframe Table */}
            {tool.findings.length > 0 ? (
              <table className="w-full border-collapse border border-gray-300 text-left text-xs mb-8">
                <thead>
                  <tr className="bg-gray-100 border-b border-gray-300">
                    <th className="p-3 font-bold border-r border-gray-300 w-1/6">Ref / Sector</th>
                    <th className="p-3 font-bold border-r border-gray-300 w-1/3">Observation & Title</th>
                    <th className="p-3 font-bold border-r border-gray-300 w-1/12 text-center">Risk</th>
                    <th className="p-3 font-bold">Impact & Recommendation</th>
                  </tr>
                </thead>
                <tbody>
                  {tool.findings.map((f, i) => (
                    <tr key={i} className="border-b border-gray-300 align-top">
                      <td className="p-3 border-r border-gray-300 font-bold text-gray-600">
                        {tool.tool_display_name.substring(0, 3).toUpperCase()}-{String(i+1).padStart(2, '0')}
                        <div className="text-[10px] uppercase mt-2 font-normal">{f.segment_sector}</div>
                      </td>
                      <td className="p-3 border-r border-gray-300">
                        <strong className="block mb-1">{f.title}</strong>
                        <span className="text-gray-600">{f.raw_note}</span>
                      </td>
                      <td className="p-3 border-r border-gray-300 text-center font-bold">
                        {f.severity}
                      </td>
                      <td className="p-3 space-y-2">
                        <div>
                          <strong className="block text-[10px] uppercase text-gray-500">Impact</strong>
                          <span>{f.impact}</span>
                        </div>
                        <div>
                          <strong className="block text-[10px] uppercase text-gray-500">Recommendation</strong>
                          <span>{f.recommendation}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="border-2 border-dashed border-gray-300 p-8 text-center text-gray-400 font-bold uppercase tracking-widest mt-10">
                [ Assessment Findings Will Populate Here ]
              </div>
            )}
            
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssessmentPipeline;

