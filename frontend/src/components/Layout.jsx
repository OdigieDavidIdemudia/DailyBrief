import React from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, AlertCircle, Settings, ShieldAlert, LogOut, Radar, ShieldCheck, BookOpen } from 'lucide-react';

const Layout = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    // Basic logout logic
    document.cookie = "tholder_session_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Threat Intel', path: '/threat-intel', icon: Radar },
    { name: 'Downtime Register', path: '/downtime', icon: AlertCircle },
    { name: 'Health Check', path: '/health-check', icon: ShieldAlert },
    { name: 'Assessment', path: '/assessment', icon: ShieldCheck },
    { name: 'Knowledge Sharing', path: '/knowledge-sharing', icon: BookOpen },
    { name: 'Configuration', path: '/configure', icon: Settings },
  ];

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
        
        <nav className="flex-1 p-4 space-y-3">
          {navItems.map((item) => (
            <Link
              key={item.name}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-neo border-neo transition-all font-bold ${
                location.pathname === item.path 
                  ? 'bg-neo-yellow border-neo-border shadow-neo translate-x-1 -translate-y-1' 
                  : 'bg-transparent border-transparent text-gray-600 hover:border-neo-border hover:shadow-neo hover:-translate-y-1 hover:translate-x-1 hover:bg-white'
              }`}
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </Link>
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
            {navItems.find(i => i.path === location.pathname)?.name || 'Daily BRIEF'}
          </h2>
        </header>
        <div className="flex-1 overflow-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;
