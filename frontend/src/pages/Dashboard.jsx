import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, CheckCircle, Shield, Bot, FileText, Clock, Archive } from 'lucide-react';
import { Link } from 'react-router-dom';

const API = "http://localhost:8000";

const Dashboard = () => {
  const [stats, setStats] = useState({
    activeTasks: 0,
    criticalAlerts: 0,
    docsGenerated: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const [logsRes, repoRes] = await Promise.all([
          fetch(`${API}/api/logs`, { credentials: 'include' }),
          fetch(`${API}/api/repository/list`, { credentials: 'include' })
        ]);
        
        let active = 0, critical = 0, docs = 0;
        if(logsRes.ok) {
          const logs = await logsRes.json();
          active = logs.filter(l => l.status !== 'Done' && l.status !== 'Completed').length;
          critical = logs.filter(l => l.is_critical && l.status !== 'Done' && l.status !== 'Completed').length;
        }
        if(repoRes.ok) {
          const repo = await repoRes.json();
          docs = repo.length;
        }
        
        setStats({ activeTasks: active, criticalAlerts: critical, docsGenerated: docs });
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-neo-yellow p-6 rounded-neo border-neo border-neo-border shadow-neo gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase tracking-wider">Command Center</h1>
          <p className="font-bold border-t-2 border-black pt-1 mt-1">SYSTEM OVERVIEW & INTELLIGENCE</p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-12 w-12 border-4 border-neo-primary border-t-transparent"></div></div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="neo-card p-6 flex flex-col hover:-translate-y-1 transition-transform bg-white">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-bold text-gray-500 uppercase tracking-widest text-sm">Active Tasks</h3>
                <Activity className="w-6 h-6 text-neo-blue" strokeWidth={3} />
              </div>
              <span className="font-black text-4xl">{stats.activeTasks}</span>
            </div>
            
            <div className="neo-card p-6 flex flex-col hover:-translate-y-1 transition-transform bg-white">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-bold text-gray-500 uppercase tracking-widest text-sm">Critical Alerts</h3>
                <AlertTriangle className="w-6 h-6 text-neo-accent" strokeWidth={3} />
              </div>
              <span className="font-black text-4xl">{stats.criticalAlerts}</span>
            </div>

            <div className="neo-card p-6 flex flex-col hover:-translate-y-1 transition-transform bg-white">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-bold text-gray-500 uppercase tracking-widest text-sm">Saved Docs</h3>
                <Archive className="w-6 h-6 text-neo-green" strokeWidth={3} />
              </div>
              <span className="font-black text-4xl">{stats.docsGenerated}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="neo-card flex flex-col hover:-translate-y-1 transition-transform group">
              <div className="bg-neo-blue p-4 border-b-neo border-neo-border">
                <span className="font-bold text-lg leading-tight text-white uppercase">Quick Actions</span>
              </div>
              <div className="p-4 space-y-4 bg-white flex-1 flex flex-col">
                <Link to="/task-tracker" className="neo-btn-secondary w-full text-left flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-neo-blue" /> Go to Task Tracker
                </Link>
                <Link to="/threat-intel" className="neo-btn-secondary w-full text-left flex items-center gap-3">
                  <Shield className="w-5 h-5 text-neo-accent" /> Draft Security Advisory
                </Link>
                <Link to="/knowledge-sharing" className="neo-btn-secondary w-full text-left flex items-center gap-3">
                  <FileText className="w-5 h-5 text-neo-primary" /> Generate Presentation Slides
                </Link>
              </div>
            </div>

            <div className="neo-card flex flex-col hover:-translate-y-1 transition-transform group">
              <div className="bg-neo-primary p-4 border-b-neo border-neo-border">
                <span className="font-bold text-lg leading-tight text-white uppercase">Activity Feed</span>
              </div>
              <div className="p-4 space-y-4 bg-white flex-1 flex flex-col">
                <ul className="space-y-4">
                  <li className="flex gap-4">
                    <div className="mt-1 flex-shrink-0"><Archive className="h-5 w-5 text-neo-primary" strokeWidth={3}/></div>
                    <div>
                      <p className="text-sm font-black uppercase">Document Saved</p>
                      <p className="text-xs font-bold text-gray-600 mt-1">Supply Chain Security - KS</p>
                    </div>
                  </li>
                  <li className="flex gap-4">
                    <div className="mt-1 flex-shrink-0"><CheckCircle className="h-5 w-5 text-neo-green" strokeWidth={3}/></div>
                    <div>
                      <p className="text-sm font-black uppercase">Task Completed</p>
                      <p className="text-xs font-bold text-gray-600 mt-1">Phishing mailbox review.</p>
                    </div>
                  </li>
                  <li className="flex gap-4">
                    <div className="mt-1 flex-shrink-0"><Shield className="h-5 w-5 text-neo-accent" strokeWidth={3}/></div>
                    <div>
                      <p className="text-sm font-black uppercase">Critical TIA</p>
                      <p className="text-xs font-bold text-gray-600 mt-1">Advisory generated for CVE-2024.</p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;
