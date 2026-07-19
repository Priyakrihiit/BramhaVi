/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useLayoutStore } from '../stores/layoutStore';
import DynamicSidebar from '../components/DynamicSidebar';
import { useThemeStore } from '../stores/themeStore';
import { api } from '../services/api';
import { Layout, LogOut, RefreshCw, Home, Users, Bell } from 'lucide-react';

interface AdminLayoutProps {
  children: React.ReactNode;
}

export const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const { currentUser, logout } = useAuthStore();
  const { navigateTo, activeAdminTab } = useLayoutStore();
  const { theme } = useThemeStore();
  const [logs, setLogs] = useState<any[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const refreshLogs = async () => {
    setIsRefreshing(true);
    try {
      const res = await api.activities.list();
      if (res.success && res.data) {
        setLogs(res.data.slice(0, 5));
      }
    } catch (err) {
      console.error('Failed fetching activities log:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    refreshLogs();
    const interval = setInterval(refreshLogs, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <React.Fragment>
      <div id="bvg-admin-wrapper" className="min-h-screen flex flex-col bg-slate-950 text-slate-100 font-sans">
        
        {/* Master Admin Header */}
        <header id="bvg-admin-header" className="bg-[#0b1329] border-b border-indigo-950/80 px-6 py-3 flex items-center justify-between z-40 shrink-0">
          <div className="flex items-center gap-3">
            <button onClick={() => navigateTo('/')} className="p-1.5 hover:bg-slate-900 rounded-lg text-slate-400 hover:text-white transition" title="Return to Home Portal">
              <Home size={18} />
            </button>
            <div className="h-4 w-[1px] bg-indigo-950/80"></div>
            <h2 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
              BrahmaVidya Control Center
              <span className="text-[9px] bg-red-950/50 border border-red-900/50 text-red-400 font-mono font-bold uppercase tracking-widest px-2 py-0.5 rounded">
                SECURE SUPERVISOR MODE
              </span>
            </h2>
          </div>

          <div className="flex items-center gap-4 text-xs">
            {/* Realtime Alert Indicator */}
            <div className="flex items-center gap-1.5 bg-slate-900/60 border border-indigo-950 px-2.5 py-1 rounded-full text-slate-400 font-mono">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>LEDGER BACKEND COMPLIANT</span>
            </div>

            {/* Admin session user card */}
            <div className="flex items-center gap-3 border-l border-indigo-950/80 pl-4">
              <div className="text-right">
                <span className="block font-semibold text-slate-200">{currentUser?.fullName}</span>
                <span className="block text-[10px] text-indigo-400 font-mono">Operator Token Active</span>
              </div>
              <button
                onClick={logout}
                className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-900 transition"
                title="Invalidate Supervisor Token"
              >
                <LogOut size={15} />
              </button>
            </div>
          </div>
        </header>

        {/* Dashboard Workspace Layout */}
        <div className="flex-1 flex overflow-hidden">
          
          {/* Dynamic Sidebar */}
          <DynamicSidebar />

          {/* Sub Tab Panel Workspace Content */}
          <main id="bvg-admin-canvas" className="flex-1 overflow-y-auto bg-slate-950 flex flex-col p-6 space-y-6 text-left">
            
            {/* Header tab banner */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-indigo-950/40 pb-4">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-widest text-indigo-400 font-mono">Control Tab</span>
                <h1 className="text-2xl font-extrabold tracking-tight text-white capitalize mt-0.5">
                  {activeAdminTab.replace('-', ' ')} PANEL
                </h1>
              </div>

              {/* Real-time Activity feed snapshot */}
              <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-xl p-3 flex items-center gap-3 text-xs shadow-md">
                <Bell className="text-indigo-400 shrink-0" size={16} />
                <div className="flex-1 min-w-0">
                  <span className="text-[9px] uppercase font-bold text-slate-500 font-mono block">Real-time audit ticker</span>
                  <p className="truncate text-slate-300 italic">
                    {logs.length > 0 ? logs[0].text : 'Awaiting state updates...'}
                  </p>
                </div>
                <button
                  onClick={refreshLogs}
                  disabled={isRefreshing}
                  className="p-1 hover:bg-slate-800 rounded text-slate-500 hover:text-white transition"
                >
                  <RefreshCw size={12} className={isRefreshing ? 'animate-spin' : ''} />
                </button>
              </div>
            </div>

            {/* Active nested page content slot */}
            <div className="flex-1">
              {children}
            </div>

          </main>
        </div>
      </div>
    </React.Fragment>
  );
};

export default AdminLayout;
