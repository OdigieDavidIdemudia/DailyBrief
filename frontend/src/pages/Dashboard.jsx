import React, { useState, useEffect } from 'react';
import { Save, Search, Download, Check, FileText, X, Bot, AlertTriangle, MessageSquare, Mail } from 'lucide-react';

const Dashboard = () => {
  const [blueprints, setBlueprints] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  
  // Handover Modal State
  const [showHandoverModal, setShowHandoverModal] = useState(false);
  const [reportType, setReportType] = useState('handover');
  const [subsidiaryName, setSubsidiaryName] = useState('');
  const [handoverType, setHandoverType] = useState('false'); // false = leave, true = returning
  const [duration, setDuration] = useState('');
  const [location, setLocation] = useState('Processing Centre');
  const [draft, setDraft] = useState(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [bpRes, logsRes] = await Promise.all([
        fetch('http://localhost:8000/api/blueprints', { credentials: 'include' }),
        fetch('http://localhost:8000/api/logs', { credentials: 'include' })
      ]);
      if(bpRes.ok) setBlueprints(await bpRes.json());
      if(logsRes.ok) setLogs(await logsRes.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateLog = async (id, field, value) => {
    try {
      const res = await fetch(`http://localhost:8000/api/logs/${id}`, { credentials: 'include', 
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [field]: value })
      });
      if (res.ok) {
        fetchData();
      }
    } catch (e) {
      alert("Failed to update log: " + e.message);
    }
  };

  const generateDraft = async () => {
    setGenerating(true);
    setDraft(null);
    try {
      const payload = reportType === 'handover' ? {
        logs: logs,
        handover_type: handoverType === 'true',
        duration: duration,
        location: location
      } : {
        logs: logs,
        subsidiary_name: subsidiaryName
      };

      const endpoint = reportType === 'handover' ? '/api/generate-handover-draft' : '/api/generate-subsidiary-draft';
      const res = await fetch(`http://localhost:8000${endpoint}`, { credentials: 'include', 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      setDraft(JSON.stringify(data, null, 2));
    } catch(e) {
      alert(e.message);
    } finally {
      setGenerating(false);
    }
  };

  const exportDocx = async () => {
    try {
      const endpoint = reportType === 'handover' ? '/api/export-handover' : '/api/export-subsidiary-report';
      const res = await fetch(`http://localhost:8000${endpoint}`, { credentials: 'include', 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: draft
      });
      if(!res.ok) throw new Error(await res.text());
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportType}_report.docx`;
      document.body.appendChild(a);
      a.click();
    } catch(e) {
      alert(e.message);
    }
  };

  const filteredLogs = logs.filter(log => {
    const bp = blueprints.find(b => b.id === log.blueprint_id);
    const matchesSearch = (bp?.title || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === 'All' || bp?.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  if (loading) return <div className="text-xl font-bold p-8 border-neo border-neo-border bg-neo-yellow shadow-neo inline-block ml-8 mt-8">Loading tasks...</div>;

  return (
    <div className="space-y-6 relative">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-neo-yellow p-6 rounded-neo border-neo border-neo-border shadow-neo gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase tracking-wider">Today's Tasks</h1>
          <p className="font-bold border-t-2 border-black pt-1 mt-1">{new Date().toDateString()}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button onClick={() => setShowHandoverModal(true)} className="neo-btn bg-neo-primary text-white flex items-center gap-2">
            <FileText className="w-5 h-5"/> View Handover
          </button>
          <button className="neo-btn bg-neo-green text-black flex items-center gap-2">
            <Check className="w-5 h-5"/> End Shift
          </button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-4 bg-white p-4 rounded-neo border-neo border-neo-border shadow-neo-sm">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 text-black w-5 h-5" />
          <input 
            type="text" 
            placeholder="Search tasks by name..." 
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="neo-input pl-10 text-lg"
          />
        </div>
        <select 
          value={categoryFilter}
          onChange={e => setCategoryFilter(e.target.value)}
          className="neo-input w-full md:w-64 font-bold text-lg cursor-pointer"
        >
          <option value="All">All Categories</option>
          <option value="Daily">Daily Routine</option>
          <option value="Monthly">Monthly</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredLogs.map((log) => {
          const bp = blueprints.find(b => b.id === log.blueprint_id);
          const priorityColor = bp?.priority === 'Critical' ? 'bg-red-500 text-white' : bp?.priority === 'High' ? 'bg-orange-400' : 'bg-white';

          return (
            <div key={log.id} className="neo-card flex flex-col hover:-translate-y-1 transition-transform group">
              <div className="bg-neo-blue p-4 border-b-neo border-neo-border flex justify-between items-start group-hover:bg-neo-primary group-hover:text-white transition-colors gap-2">
                <span className="font-bold text-lg leading-tight">{bp?.title || 'Unknown Task'}</span>
                <div className="flex flex-col gap-1 items-end shrink-0">
                  <span className="text-xs font-black bg-white text-black px-2 py-1 border-neo border-neo-border shadow-neo-sm whitespace-nowrap">{bp?.category}</span>
                  <span className={`text-[10px] font-black uppercase px-2 py-0.5 border-neo border-neo-border shadow-neo-sm whitespace-nowrap ${priorityColor}`}>{bp?.priority}</span>
                </div>
              </div>
              <div className="p-4 space-y-4 bg-white flex-1 flex flex-col">
                <div>
                  <label className="text-xs font-bold uppercase block mb-1">Status</label>
                  <select 
                    value={log.status} 
                    onChange={e => handleUpdateLog(log.id, 'status', e.target.value)}
                    className={`neo-input font-bold cursor-pointer ${log.status === 'Blocked' || log.status === 'Flagged' ? 'bg-neo-accent text-white border-neo-border' : log.status === 'Completed' ? 'bg-neo-green' : ''}`}
                  >
                    <option value="Pending">Pending</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                    <option value="Flagged">Flagged</option>
                    <option value="Blocked">Blocked</option>
                  </select>
                </div>
                
                <div className="flex flex-col gap-3">
                  <div>
                    <label className="text-xs font-bold uppercase block mb-1 text-gray-700 flex items-center gap-1"><FileText className="w-3 h-3"/> Summary</label>
                    <textarea 
                      className="neo-input w-full min-h-[80px] resize-y text-sm" 
                      defaultValue={log.summary || ''}
                      onBlur={e => handleUpdateLog(log.id, 'summary', e.target.value)}
                      placeholder="What did you do?"
                    />
                  </div>
                  
                  <div>
                    <label className="text-xs font-bold uppercase block mb-1 text-gray-700 flex items-center gap-1"><AlertTriangle className="w-3 h-3"/> Challenges</label>
                    <textarea 
                      className="neo-input w-full min-h-[60px] resize-y text-sm" 
                      defaultValue={log.challenges || ''}
                      onBlur={e => handleUpdateLog(log.id, 'challenges', e.target.value)}
                      placeholder="Any roadblocks?"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-bold uppercase block mb-1 text-gray-700 flex items-center gap-1"><Mail className="w-3 h-3"/> Mail Trail</label>
                    <input 
                      type="text"
                      className="neo-input w-full text-sm" 
                      defaultValue={log.mail_trail || ''}
                      onBlur={e => handleUpdateLog(log.id, 'mail_trail', e.target.value)}
                      placeholder="e.g. Email to IT Helpdesk..."
                    />
                  </div>
                </div>

                <div className="flex items-center gap-3 pt-4 border-t-2 border-dashed border-gray-300 mt-auto">
                  <input 
                    type="checkbox" 
                    id={`crit-${log.id}`}
                    checked={log.is_critical} 
                    onChange={e => handleUpdateLog(log.id, 'is_critical', e.target.checked)}
                    className="w-6 h-6 border-neo border-neo-border rounded-sm cursor-pointer accent-neo-accent"
                  />
                  <label htmlFor={`crit-${log.id}`} className="font-black text-sm text-neo-accent cursor-pointer uppercase">Mark as Critical</label>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Handover Modal */}
      {showHandoverModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-neo-bg border-neo border-neo-border rounded-neo shadow-neo-xl w-full max-w-3xl flex flex-col max-h-[90vh]">
            <div className="p-4 border-b-neo border-neo-border bg-neo-primary text-white flex justify-between items-center">
              <h2 className="text-2xl font-black flex items-center gap-2"><Bot className="w-8 h-8"/> AI Handover & Subsidiary Generator</h2>
              <button onClick={() => setShowHandoverModal(false)} className="hover:text-neo-yellow transition-colors"><X className="w-8 h-8"/></button>
            </div>
            
            <div className="p-6 overflow-y-auto space-y-8">
              <div className="flex flex-col md:flex-row gap-6 p-6 bg-white border-neo border-neo-border shadow-neo">
                <label className="font-black flex items-center gap-3 text-lg cursor-pointer">
                  <input type="radio" className="w-5 h-5 accent-neo-primary" name="reportType" checked={reportType==='handover'} onChange={()=>setReportType('handover')}/> Handover Document
                </label>
                <label className="font-black flex items-center gap-3 text-lg cursor-pointer">
                  <input type="radio" className="w-5 h-5 accent-neo-primary" name="reportType" checked={reportType==='subsidiary'} onChange={()=>setReportType('subsidiary')}/> Subsidiary Report
                </label>
              </div>

              {reportType === 'subsidiary' && (
                <div className="bg-white p-6 border-neo border-neo-border shadow-neo-sm">
                  <label className="font-black block mb-2 text-lg">Subsidiary Name</label>
                  <input type="text" className="neo-input text-lg" value={subsidiaryName} onChange={e=>setSubsidiaryName(e.target.value)} placeholder="e.g. Acme Corp"/>
                </div>
              )}

              {reportType === 'handover' && (
                <div className="space-y-6 bg-white p-6 border-neo border-neo-border shadow-neo-sm">
                  <div className="flex flex-col md:flex-row gap-6">
                    <label className="font-black flex items-center gap-3 cursor-pointer">
                      <input type="radio" className="w-5 h-5 accent-neo-primary" name="handoverType" checked={handoverType==='false'} onChange={()=>setHandoverType('false')}/> Going on Leave
                    </label>
                    <label className="font-black flex items-center gap-3 cursor-pointer">
                      <input type="radio" className="w-5 h-5 accent-neo-primary" name="handoverType" checked={handoverType==='true'} onChange={()=>setHandoverType('true')}/> Returning (Update)
                    </label>
                  </div>
                  <div>
                    <label className="font-black block mb-2">Duration / Leave Reason</label>
                    <input type="text" className="neo-input" value={duration} onChange={e=>setDuration(e.target.value)} placeholder="e.g. I will be out of office from 29th Sept..."/>
                  </div>
                  <div>
                    <label className="font-black block mb-2">Location</label>
                    <input type="text" className="neo-input" value={location} onChange={e=>setLocation(e.target.value)} />
                  </div>
                </div>
              )}

              {generating ? (
                <div className="p-12 text-center font-black text-neo-primary animate-pulse border-neo border-neo-border bg-white shadow-neo flex flex-col items-center gap-4">
                  <Bot className="w-16 h-16 animate-bounce" />
                  <span className="text-xl">Magnitude AI is analyzing logs and generating draft...</span>
                </div>
              ) : draft ? (
                <div className="bg-white p-4 border-neo border-neo-border shadow-neo">
                  <label className="font-black block mb-2 flex items-center justify-between">
                    <span>Review JSON Draft</span>
                    <span className="text-xs bg-neo-yellow px-2 py-1 border-2 border-black">Editable</span>
                  </label>
                  <textarea 
                    className="neo-input w-full h-80 font-mono text-sm leading-relaxed bg-gray-50"
                    value={draft}
                    onChange={e => setDraft(e.target.value)}
                  />
                </div>
              ) : null}
            </div>

            <div className="p-4 border-t-neo border-neo-border bg-white flex flex-wrap justify-end gap-4 rounded-b-neo">
              <button onClick={() => setShowHandoverModal(false)} className="neo-btn-secondary text-lg">Cancel</button>
              <button onClick={generateDraft} className="neo-btn bg-neo-yellow text-black flex items-center gap-2 text-lg"><Bot className="w-5 h-5"/> Generate Draft</button>
              {draft && (
                <button onClick={exportDocx} className="neo-btn bg-neo-blue text-white flex items-center gap-2 text-lg"><Download className="w-5 h-5"/> Export DOCX</button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
