import React, { useState } from 'react';
import { SearchAnalytics } from './SearchAnalytics';
import { SearchAdmin } from './SearchAdmin';
import { ShieldCheck, BarChart, Sliders } from 'lucide-react';

export const SearchDashboard: React.FC = () => {
  const [panelTab, setPanelTab] = useState<'analytics' | 'config'>('analytics');

  return (
    <div className="bg-slate-50 min-h-screen text-slate-900 pb-12 font-sans text-xs">
      {/* Header Banner */}
      <div className="bg-slate-950 text-white py-10 px-6 shadow-sm border-b border-slate-900">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <span className="bg-indigo-500/20 text-indigo-300 text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase tracking-wider flex items-center gap-1 w-fit">
              <ShieldCheck className="h-3.5 w-3.5" /> Administrative Dashboard
            </span>
            <h1 className="text-2xl font-bold tracking-tight">Search Control Center</h1>
            <p className="text-slate-400 text-xs">
              Monitor click CTR, track popular keywords, adjust ranking boosts, configure search facets, and register synonym mappings.
            </p>
          </div>
          <div className="flex bg-slate-900 border border-slate-800 p-1.5 rounded-xl gap-1">
            <button
              onClick={() => setPanelTab('analytics')}
              className={`px-4 py-2 rounded-lg font-bold transition flex items-center gap-1.5 cursor-pointer ${
                panelTab === 'analytics' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <BarChart className="h-4 w-4" /> Analytics
            </button>
            <button
              onClick={() => setPanelTab('config')}
              className={`px-4 py-2 rounded-lg font-bold transition flex items-center gap-1.5 cursor-pointer ${
                panelTab === 'config' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Sliders className="h-4 w-4" /> Configuration
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 mt-8">
        {panelTab === 'analytics' ? <SearchAnalytics /> : <SearchAdmin />}
      </div>
    </div>
  );
};
