import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, AlertCircle, Settings, ShieldAlert, LogOut, Radar, ShieldCheck, BookOpen, Archive, ChevronDown, ChevronRight } from 'lucide-react';

const Layout = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Categories state
  const [expandedCats, setExpandedCats] = useState({
    'Operations': true,
    'Assurance': true,
    'Intelligence': true,
    'System': true
  });

  const toggleCat = (cat) => {
    setExpandedCats(prev => ({ ...prev, [cat]: !prev[cat] }));
  };

  const handleLogout = async () => {
    document.cookie = "tholder_session_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    navigate('/login');
  };

  const menuCategories = [
    {
      title: 'Operations',
      items: [
        { name: 'Dashboard', path: '/', icon: LayoutDashboard },
        { name: 'Task Tracker', path: '/task-tracker', icon: AlertCircle }
      ]
    },
    {
      title: 'Assurance',
      items: [
        { name: 'Downtime Register', path: '/downtime', icon: AlertCircle },
        { name: 'Health Check', path: '/health-check', icon: ShieldAlert },
        { name: 'Assessment', path: '/assessment', icon: ShieldCheck }
      ]
    },
    {
      title: 'Intelligence',
      items: [
        { name: 'Threat Intel', path: '/threat-intel', icon: Radar },
        { name: 'Knowledge Sharing', path: '/knowledge-sharing', icon: BookOpen }
      ]
    },
    {
      title: 'System',
      items: [
        { name: 'Repository', path: '/repository', icon: Archive },
        { name: 'Configuration', path: '/configure', icon: Settings }
      ]
    }
  ];

  const getPageTitle = () => {
    for (const cat of menuCategories) {
      const found = cat.items.find(i => i.path === location.pathname);
      if (found) return found.name;
    }
    return 'Daily BRIEF';
  };

  return (
    <div className="flex h-screen bg-neo-bg">
      {/* Sidebar */}
      <aside className="w-64 bg-neo-surface border-r-neo border-neo-border flex flex-col z-10 shadow-neo">
        <div className="p-6 border-b-neo border-neo-border">
          <h1 className="text-2xl font-bold text-neo-primary flex items-center gap-2">
            <ShieldAlert className="w-8 h-8" />
            Daily BRIEF
          </h1>
        </div>
        
        <nav className="flex-1 p-4 space-y-4 overflow-y-auto" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
          <style>{`nav::-webkit-scrollbar { display: none; }`}</style>
          {menuCategories.map((cat) => (
            <div key={cat.title} className="space-y-1">
              <button 
                onClick={() => toggleCat(cat.title)}
                className="w-full flex items-center justify-between px-4 py-2 text-left text-xs font-bold uppercase tracking-wider text-gray-500 hover:text-gray-900 transition-colors"
              >
                <span>{cat.title}</span>
                {expandedCats[cat.title] ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </button>
              
              <div className={`space-y-1 overflow-hidden transition-all ${expandedCats[cat.title] ? 'block' : 'hidden'}`}>
                {cat.items.map((item) => {
                  const isActive = location.pathname === item.path || (location.pathname === '/dashboard' && item.path === '/');
                  return (
                    <Link
                      key={item.name}
                      to={item.path}
                      className={`flex items-center gap-3 px-4 py-3 rounded-neo border-neo transition-all font-bold ${
                        isActive 
                          ? 'bg-neo-yellow border-neo-border shadow-neo translate-x-1 -translate-y-1' 
                          : 'bg-transparent border-transparent text-gray-600 hover:border-neo-border hover:shadow-neo hover:-translate-y-1 hover:translate-x-1 hover:bg-white'
                      }`}
                    >
                      <item.icon className="w-5 h-5" />
                      {item.name}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="p-4 border-t-neo border-neo-border">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-neo-primary border-neo border-neo-border flex items-center justify-center text-white font-bold">
              ID
            </div>
            <div>
              <p className="text-sm font-bold text-neo-text user-name">Idemudia</p>
              <p className="text-xs font-semibold text-gray-500">Security Analyst</p>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="w-full neo-btn-secondary flex items-center justify-center gap-2 text-red-600 hover:text-white hover:bg-red-500"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-neo-surface border-b-neo border-neo-border p-4 shadow-sm z-0">
          <h2 className="text-xl font-bold">
            {getPageTitle()}
          </h2>
        </header>
        <div className="flex-1 overflow-auto p-8 bg-white" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
           <style>{`div::-webkit-scrollbar { display: none; }`}</style>
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
