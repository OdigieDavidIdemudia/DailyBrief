import React, { useState, useEffect } from 'react';
import { Settings, Plus, Trash2, Save, Send, Lock, CheckCircle } from 'lucide-react';

const Configure = () => {
  const [blueprints, setBlueprints] = useState([]);
  
  // New Blueprint form state
  const [newTitle, setNewTitle] = useState('');
  const [newCategory, setNewCategory] = useState('Daily');
  const [newPriority, setNewPriority] = useState('Standard');
  
  // Telegram Config state
  const [telegramConfig, setTelegramConfig] = useState({ telegram_enabled: false, bot_token: '', chat_id: '' });
  
  // Roster Lock state
  const [locking, setLocking] = useState(false);
  const [lockSuccess, setLockSuccess] = useState(false);
  
  // Tab state
  const [activeTab, setActiveTab] = useState('blueprints');
  
  // AI Keys state
  const [aiKeys, setAiKeys] = useState(['']);
  const [savingAi, setSavingAi] = useState(false);

  useEffect(() => {
    fetchBlueprints();
    fetchTelegram();
    fetchAiKeys();
  }, []);

  const fetchAiKeys = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/settings/ai-keys', { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        if (data.keys && data.keys.length > 0) setAiKeys(data.keys);
      }
    } catch(e) {}
  };

  const handleSaveAiKeys = async () => {
    setSavingAi(true);
    try {
      const res = await fetch('http://localhost:8000/api/settings/ai-keys', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keys: aiKeys })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      alert(data.message || 'AI API keys saved!');
    } catch (e) {
      alert(e.message || 'Error saving keys');
    } finally {
      setSavingAi(false);
    }
  };

  const addAiKey = () => setAiKeys([...aiKeys, '']);
  const updateAiKey = (idx, val) => {
    const next = [...aiKeys];
    next[idx] = val;
    setAiKeys(next);
  };
  const removeAiKey = (idx) => {
    if (aiKeys.length === 1) return;
    setAiKeys(aiKeys.filter((_, i) => i !== idx));
  };

  const fetchBlueprints = async () => {
    const res = await fetch('http://localhost:8000/api/blueprints', { credentials: 'include' });
    if(res.ok) setBlueprints(await res.json());
  };

  const fetchTelegram = async () => {
    const res = await fetch('http://localhost:8000/api/settings/telegram', { credentials: 'include' });
    if(res.ok) setTelegramConfig(await res.json());
  };

  const handleAddBlueprint = async (e) => {
    e.preventDefault();
    if (!newTitle) return;
    const res = await fetch('http://localhost:8000/api/blueprints', { credentials: 'include', 
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ title: newTitle, category: newCategory, priority: newPriority })
    });
    if (res.ok) {
      setNewTitle('');
      fetchBlueprints();
    }
  };

  const handleDeleteBlueprint = async (id) => {
    await fetch(`http://localhost:8000/api/blueprints/${id}`, { credentials: 'include',  method: 'DELETE' });
    fetchBlueprints();
  };

  const handleSaveTelegram = async () => {
    await fetch('http://localhost:8000/api/settings/telegram', { credentials: 'include', 
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(telegramConfig)
    });
    alert('Telegram settings saved!');
  };

  const handleTestTelegram = async () => {
    const res = await fetch('http://localhost:8000/api/settings/telegram/test', { credentials: 'include', 
      method: 'POST'
    });
    const msg = await res.json();
    alert(msg.message || msg.detail || 'Test sent!');
  };

  const handleLockRoster = async () => {
    if (!confirm('Are you sure you want to provision tasks for the remainder of this month based on your current blueprints?')) return;
    
    setLocking(true);
    try {
      const res = await fetch('http://localhost:8000/api/roster/lock', { credentials: 'include',  method: 'POST' });
      const data = await res.json();
      if (res.ok) {
        setLockSuccess(true);
        setTimeout(() => setLockSuccess(false), 3000);
      } else {
        alert(data.detail || 'Failed to lock roster');
      }
    } catch (e) {
      alert('Network error');
    } finally {
      setLocking(false);
    }
  };

  return (
    <div className="h-full flex flex-col relative overflow-hidden bg-white">
      <div className="flex-none p-4 lg:p-6 bg-white border-b-neo border-neo-border z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="bg-neo-blue p-3 rounded-neo border-neo border-neo-border shadow-neo-sm">
            <Settings className="w-8 h-8 text-black" />
          </div>
          <div>
            <h1 className="text-2xl font-black uppercase tracking-tight">Configuration</h1>
            <p className="text-sm font-bold text-gray-600">System Preferences & Setup</p>
          </div>
        </div>

        <div className="flex bg-gray-100 rounded-neo border-2 border-black p-1 shadow-neo-sm w-full md:w-auto overflow-x-auto">
          <button 
            onClick={() => setActiveTab('blueprints')}
            className={`px-4 py-2 font-bold text-sm rounded whitespace-nowrap transition-colors ${activeTab === 'blueprints' ? 'bg-white border-2 border-black shadow-sm' : 'text-gray-600 hover:bg-gray-200'}`}
          >
            Blueprints
          </button>
          <button 
            onClick={() => setActiveTab('ai_engine')}
            className={`px-4 py-2 font-bold text-sm rounded whitespace-nowrap transition-colors ${activeTab === 'ai_engine' ? 'bg-white border-2 border-black shadow-sm' : 'text-gray-600 hover:bg-gray-200'}`}
          >
            Magnitude AI
          </button>
          <button 
            onClick={() => setActiveTab('integrations')}
            className={`px-4 py-2 font-bold text-sm rounded whitespace-nowrap transition-colors ${activeTab === 'integrations' ? 'bg-white border-2 border-black shadow-sm' : 'text-gray-600 hover:bg-gray-200'}`}
          >
            Integrations
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 bg-gray-50">
        {activeTab === 'blueprints' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start max-w-6xl mx-auto">
            <div className="neo-card">
              <div className="bg-neo-bg border-b-neo border-neo-border p-4">
                <h2 className="text-xl font-black uppercase tracking-wider">Create Task Blueprint</h2>
              </div>
              <div className="p-6 space-y-6">
                <form onSubmit={handleAddBlueprint} className="flex flex-col gap-4">
                  <div>
                    <label className="text-xs font-bold uppercase block mb-1">Task Name</label>
                    <input 
                      type="text" 
                      placeholder="e.g., Security Audit" 
                      value={newTitle} 
                      onChange={e=>setNewTitle(e.target.value)} 
                      className="neo-input w-full font-bold"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs font-bold uppercase block mb-1">Category</label>
                      <select value={newCategory} onChange={e=>setNewCategory(e.target.value)} className="neo-input w-full font-bold">
                        <option value="Daily">Daily Routine</option>
                        <option value="Monthly">Monthly Task</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs font-bold uppercase block mb-1">Priority</label>
                      <select value={newPriority} onChange={e=>setNewPriority(e.target.value)} className="neo-input w-full font-bold">
                        <option value="Standard">Standard</option>
                        <option value="Low">Low</option>
                        <option value="High">High</option>
                        <option value="Critical">Critical</option>
                      </select>
                    </div>
                  </div>
                  <button type="submit" className="neo-btn bg-neo-primary text-white flex justify-center gap-2 mt-2 font-bold"><Plus/> Add to Roster</button>
                </form>

                {blueprints.length > 0 && (
                  <div className="space-y-3 pt-4 border-t-neo border-neo-border max-h-[350px] overflow-y-auto pr-2 custom-scrollbar">
                    {blueprints.map(bp => (
                      <div key={bp.id} className="flex justify-between items-center bg-white border-neo border-neo-border p-3 rounded-neo shadow-neo-sm">
                        <div className="flex flex-col">
                          <span className="font-bold">{bp.title}</span>
                          <span className="text-xs font-bold text-gray-500 uppercase">{bp.category} � {bp.priority}</span>
                        </div>
                        <button onClick={() => handleDeleteBlueprint(bp.id)} className="text-neo-accent hover:text-red-700 bg-red-100 p-2 rounded-neo border-neo border-neo-border">
                          <Trash2 className="w-5 h-5"/>
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="neo-card bg-neo-yellow h-fit">
              <div className="p-6 space-y-4">
                <h2 className="text-xl font-black uppercase tracking-wider flex items-center gap-2">
                  <Lock className="w-6 h-6"/> Provision Month
                </h2>
                <p className="font-bold text-sm">
                  Finalize all blueprints. Once locked, tasks for the remainder of this month will be deployed to your dashboard instantly.
                </p>
                <button 
                  onClick={handleLockRoster} 
                  disabled={locking || lockSuccess}
                  className={`neo-btn w-full flex justify-center items-center gap-2 text-lg font-black ${lockSuccess ? 'bg-neo-green text-black' : 'bg-green-800 text-white'}`}
                >
                  {locking ? (
                    <span className="animate-pulse">Processing...</span>
                  ) : lockSuccess ? (
                    <><CheckCircle/> Roster Locked</>
                  ) : (
                    <><Lock/> Lock Tasks for Month</>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'ai_engine' && (
          <div className="max-w-3xl mx-auto">
            <div className="neo-card">
              <div className="bg-neo-bg border-b-neo border-neo-border p-4">
                <h2 className="text-xl font-black uppercase tracking-wider">Magnitude AI Configuration</h2>
              </div>
              <div className="p-6 space-y-4 bg-white">
                <p className="font-bold text-sm text-gray-600">
                  Provide Gemini API keys for Magnitude AI. Round-robin load balancing will automatically cycle through these keys if rate limits are hit across modules (TIA, Downtime, Assessment).
                </p>
                <div className="space-y-3">
                  {aiKeys.map((k, idx) => (
                    <div key={idx} className="flex gap-2">
                      <input 
                        type="password" 
                        className="neo-input font-mono flex-1" 
                        value={k}
                        onChange={e => updateAiKey(idx, e.target.value)}
                        placeholder="AIzaSy..."
                      />
                      <button 
                        onClick={() => removeAiKey(idx)} 
                        disabled={aiKeys.length === 1}
                        className="neo-btn-secondary p-3 bg-red-100 hover:bg-red-200 text-red-700 disabled:opacity-50"
                      >
                        <Trash2 className="w-5 h-5"/>
                      </button>
                    </div>
                  ))}
                </div>
                
                <div className="flex gap-4 pt-4 border-t-neo border-neo-border">
                  <button onClick={addAiKey} className="neo-btn-secondary flex items-center justify-center gap-2 font-bold w-1/3">
                    <Plus className="w-4 h-4"/> Add Key
                  </button>
                  <button 
                    onClick={handleSaveAiKeys} 
                    disabled={savingAi}
                    className="neo-btn bg-black text-white flex items-center justify-center gap-2 font-bold w-2/3"
                  >
                    {savingAi ? 'Saving...' : <><Save className="w-4 h-4"/> Save API Keys</>}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'integrations' && (
          <div className="max-w-3xl mx-auto">
            <div className="neo-card flex flex-col h-fit">
              <div className="bg-neo-bg border-b-neo border-neo-border p-4">
                <h2 className="text-xl font-black uppercase tracking-wider">Telegram Integration</h2>
              </div>
              <div className="p-6 space-y-5 bg-white">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-black uppercase">Enable Notifications</label>
                  <input 
                    type="checkbox"
                    checked={telegramConfig.telegram_enabled || false}
                    onChange={e => setTelegramConfig({...telegramConfig, telegram_enabled: e.target.checked})}
                    className="w-6 h-6 border-neo border-neo-border rounded-sm cursor-pointer accent-neo-accent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-black uppercase mb-1">Bot Token</label>
                  <input 
                    type="password" 
                    className="neo-input font-mono" 
                    value={telegramConfig.bot_token || ''}
                    onChange={e => setTelegramConfig({...telegramConfig, bot_token: e.target.value})}
                    placeholder="e.g. 123456789:ABCdefGhI..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-black uppercase mb-1">Chat ID</label>
                  <input 
                    type="text" 
                    className="neo-input font-mono" 
                    value={telegramConfig.chat_id || ''}
                    onChange={e => setTelegramConfig({...telegramConfig, chat_id: e.target.value})}
                    placeholder="e.g. -100123456789"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4 mt-6">
                  <button onClick={handleTestTelegram} className="neo-btn-secondary flex justify-center gap-2 font-bold bg-gray-100">
                    <Send className="w-4 h-4"/> Test
                  </button>
                  <button onClick={handleSaveTelegram} className="neo-btn bg-neo-primary text-white flex justify-center gap-2 font-bold">
                    <Save className="w-4 h-4"/> Save
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Configure;
