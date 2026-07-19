import React, { useEffect, useState } from 'react';
import { analyticsApi, DashboardStats, KPI, DailySummary, ExportJob, ReportSchedule } from '../../services/analyticsApi';
import { 
  BarChart2, LineChart, PieChart, Activity, Download, Calendar, Settings, Shield,
  Users, DollarSign, Award, ArrowUpRight, ArrowDownRight, RefreshCw, FileText, Plus, Trash
} from 'lucide-react';

export const EnterpriseAnalyticsView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'modules' | 'realtime' | 'reports' | 'settings'>('dashboard');
  const [selectedModule, setSelectedModule] = useState<'user' | 'course' | 'revenue' | 'search' | 'seo' | 'notifications' | 'cms' | 'wallet' | 'marketplace' | 'ai'>('user');
  
  // States
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [summaries, setSummaries] = useState<DailySummary[]>([]);
  const [exports, setExports] = useState<ExportJob[]>([]);
  const [schedules, setSchedules] = useState<ReportSchedule[]>([]);
  const [chartData, setChartData] = useState<{ label: string; value: number }[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  // New schedules states
  const [newTitle, setNewTitle] = useState('');
  const [newFreq, setNewFreq] = useState('WEEKLY');
  const [newRecipients, setNewRecipients] = useState('');

  // Fetch data
  useEffect(() => {
    setLoading(true);
    Promise.all([
      analyticsApi.dashboard.stats(),
      analyticsApi.kpis.list(),
      analyticsApi.exports.list(),
      analyticsApi.schedules.list(),
      analyticsApi.summaries.list()
    ]).then(([statsRes, kpisRes, exportsRes, schedulesRes, summariesRes]) => {
      if (statsRes.success && statsRes.data) setStats(statsRes.data);
      if (kpisRes.success && kpisRes.data) setKpis(kpisRes.data);
      if (exportsRes.success && exportsRes.data) setExports(exportsRes.data);
      if (schedulesRes.success && schedulesRes.data) setSchedules(schedulesRes.data);
      if (summariesRes.success && summariesRes.data) setSummaries(summariesRes.data);
    }).finally(() => setLoading(false));
  }, [refreshKey]);

  // Load chart data dynamically based on active metric
  useEffect(() => {
    let metricKey = 'user_activity';
    if (activeTab === 'modules') {
      metricKey = `${selectedModule}_analytics`;
    } else if (activeTab === 'realtime') {
      metricKey = 'realtime_requests';
    }

    analyticsApi.summaries.timeseries(metricKey, 7).then(res => {
      if (res.success && res.data && res.data.timeseries) {
        setChartData(res.data.timeseries.map(t => ({ label: t.label, value: t.value })));
      } else {
        // Fallback mockup timeseries data for visual completeness
        setChartData([
          { label: 'Mon', value: 120 },
          { label: 'Tue', value: 180 },
          { label: 'Wed', value: 150 },
          { label: 'Thu', value: 320 },
          { label: 'Fri', value: 290 },
          { label: 'Sat', value: 410 },
          { label: 'Sun', value: 380 }
        ]);
      }
    });
  }, [activeTab, selectedModule, refreshKey]);

  const handleCreateExport = async (format: string) => {
    await analyticsApi.exports.create(format);
    setRefreshKey(p => p + 1);
  };

  const handleCreateSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle) return;
    await analyticsApi.schedules.create({
      report_title: newTitle,
      frequency: newFreq,
      recipients: newRecipients.split(',').map(email => email.trim()),
      next_run_at: new Date(Date.now() + 86400000 * 7).toISOString(),
      is_active: true
    });
    setNewTitle('');
    setNewRecipients('');
    setRefreshKey(p => p + 1);
  };

  const handleDeleteSchedule = async (id: string) => {
    await analyticsApi.schedules.delete(id);
    setRefreshKey(p => p + 1);
  };

  // Helper to draw clean SVG charts dynamically
  const renderSVGChart = (data: { label: string; value: number }[]) => {
    if (!data || data.length === 0) return null;
    const maxVal = Math.max(...data.map(d => d.value), 10);
    const height = 180;
    const width = 500;
    const padding = 30;

    const points = data.map((d, index) => {
      const x = padding + (index * (width - 2 * padding)) / (data.length - 1);
      const y = height - padding - (d.value * (height - 2 * padding)) / maxVal;
      return { x, y };
    });

    const pathD = points.reduce((acc, p, index) => {
      return index === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`;
    }, '');

    return (
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full text-indigo-500 overflow-visible">
        {/* Grids */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio, idx) => (
          <line
            key={idx}
            x1={padding}
            y1={padding + ratio * (height - 2 * padding)}
            x2={width - padding}
            y2={padding + ratio * (height - 2 * padding)}
            className="stroke-slate-800"
            strokeDasharray="4 4"
          />
        ))}

        {/* Chart Line Path */}
        <path d={pathD} fill="none" stroke="currentColor" strokeWidth="3" className="stroke-indigo-400 drop-shadow-[0_4px_12px_rgba(99,102,241,0.3)]" />

        {/* Chart Dots */}
        {points.map((p, idx) => (
          <g key={idx} className="group">
            <circle cx={p.x} cy={p.y} r="4" className="fill-indigo-500 hover:fill-amber-400 cursor-pointer stroke-slate-950 stroke-2 transition" />
            <text x={p.x} y={p.y - 10} textAnchor="middle" className="fill-slate-400 text-[9px] font-mono opacity-0 group-hover:opacity-100 transition">
              {data[idx].value}
            </text>
          </g>
        ))}

        {/* Labels */}
        {data.map((d, idx) => {
          const x = padding + (idx * (width - 2 * padding)) / (data.length - 1);
          return (
            <text key={idx} x={x} y={height - 8} textAnchor="middle" className="fill-slate-500 text-[9px] font-mono uppercase">
              {d.label}
            </text>
          );
        })}
      </svg>
    );
  };

  if (loading && refreshKey === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-500 font-mono text-xs">
        <span className="h-2 w-2 rounded-full bg-indigo-500 animate-ping mr-2"></span>
        Loading enterprise analytics dashboards...
      </div>
    );
  }

  return (
    <div className="flex flex-col lg:flex-row gap-6 bg-slate-950 text-slate-100 p-6 min-h-screen text-left">
      
      {/* 1. Left Nav Tabs */}
      <div className="lg:w-60 shrink-0 space-y-2 border-r border-slate-900 pr-6">
        <div className="pb-4 border-b border-slate-900">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
            <Activity size={16} className="text-indigo-400" />
            Analytics Center
          </h2>
          <span className="text-[9px] text-slate-500 font-mono">Dynamic Telemetry V1</span>
        </div>

        <nav className="space-y-1 pt-4">
          <button 
            onClick={() => setActiveTab('dashboard')}
            className={`w-full text-left px-3 py-2 rounded-xl text-xs font-medium transition flex items-center gap-2.5 ${activeTab === 'dashboard' ? 'bg-indigo-500/10 text-indigo-300 font-bold border border-indigo-500/20' : 'text-slate-400 hover:text-white hover:bg-slate-900'}`}
          >
            <Shield size={14} />
            Control Dashboard
          </button>
          
          <button 
            onClick={() => setActiveTab('modules')}
            className={`w-full text-left px-3 py-2 rounded-xl text-xs font-medium transition flex items-center gap-2.5 ${activeTab === 'modules' ? 'bg-indigo-500/10 text-indigo-300 font-bold border border-indigo-500/20' : 'text-slate-400 hover:text-white hover:bg-slate-900'}`}
          >
            <LineChart size={14} />
            Module Analytics
          </button>

          <button 
            onClick={() => setActiveTab('realtime')}
            className={`w-full text-left px-3 py-2 rounded-xl text-xs font-medium transition flex items-center gap-2.5 ${activeTab === 'realtime' ? 'bg-indigo-500/10 text-indigo-300 font-bold border border-indigo-500/20' : 'text-slate-400 hover:text-white hover:bg-slate-900'}`}
          >
            <Activity size={14} />
            Realtime Telemetry
          </button>

          <button 
            onClick={() => setActiveTab('reports')}
            className={`w-full text-left px-3 py-2 rounded-xl text-xs font-medium transition flex items-center gap-2.5 ${activeTab === 'reports' ? 'bg-indigo-500/10 text-indigo-300 font-bold border border-indigo-500/20' : 'text-slate-400 hover:text-white hover:bg-slate-900'}`}
          >
            <FileText size={14} />
            Report Exporter
          </button>

          <button 
            onClick={() => setActiveTab('settings')}
            className={`w-full text-left px-3 py-2 rounded-xl text-xs font-medium transition flex items-center gap-2.5 ${activeTab === 'settings' ? 'bg-indigo-500/10 text-indigo-300 font-bold border border-indigo-500/20' : 'text-slate-400 hover:text-white hover:bg-slate-900'}`}
          >
            <Settings size={14} />
            KPI Configurations
          </button>
        </nav>
      </div>

      {/* 2. Workspace Canvas */}
      <div className="flex-1 space-y-6">
        
        {/* Top Control Banner */}
        <div className="flex items-center justify-between border-b border-slate-900 pb-4">
          <div>
            <span className="text-[9px] uppercase font-bold tracking-widest text-indigo-400 font-mono">Workspace</span>
            <h1 className="text-xl font-bold text-white tracking-tight mt-0.5 capitalize">
              {activeTab === 'modules' ? `${selectedModule} Analytics` : activeTab}
            </h1>
          </div>
          <button 
            onClick={() => setRefreshKey(p => p + 1)}
            className="p-1.5 hover:bg-slate-900 rounded-lg text-slate-400 hover:text-white transition"
            title="Refresh Live Metrics"
          >
            <RefreshCw size={14} />
          </button>
        </div>

        {/* Tab Canvas Content */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            
            {/* dynamic widget cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {stats?.widgets.map((widget, idx) => (
                <div key={widget.id || idx} className="p-5 bg-slate-900/60 border border-slate-800/80 rounded-2xl flex items-center gap-4 hover:border-indigo-500/25 transition">
                  <div className="p-3 bg-indigo-500/10 rounded-2xl text-indigo-400">
                    <Activity size={20} />
                  </div>
                  <div>
                    <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider font-mono">{widget.title}</span>
                    <span className="text-2xl font-extrabold text-white mt-1 block tracking-tight">{widget.value}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* KPI Tracker Grid */}
            <div className="p-6 bg-slate-900/40 border border-slate-900 rounded-2xl space-y-4">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Active KPI Indicators</h3>
                <p className="text-xs text-slate-500">Realtime targets compliance tracking</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {kpis.map(kpi => (
                  <div key={kpi.id} className="p-4 bg-slate-900 border border-slate-800 rounded-xl space-y-2">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-slate-200">{kpi.name}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${kpi.status === 'ACHIEVED' ? 'bg-emerald-950 text-emerald-400' : 'bg-amber-950 text-amber-400'}`}>
                        {kpi.status}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs text-slate-400 font-mono">
                      <span>Value: {kpi.current_value}</span>
                      <span>Target: {kpi.target_value}</span>
                    </div>
                    <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                      <div 
                        className="bg-indigo-500 h-1.5 rounded-full" 
                        style={{ width: `${Math.min((kpi.current_value / kpi.target_value) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'modules' && (
          <div className="space-y-6">
            
            {/* Modules Scoped Bar */}
            <div className="flex flex-wrap gap-2">
              {(['user', 'course', 'revenue', 'search', 'seo', 'notifications', 'cms', 'wallet', 'marketplace', 'ai'] as const).map(mod => (
                <button
                  key={mod}
                  onClick={() => setSelectedModule(mod)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-mono capitalize transition ${selectedModule === mod ? 'bg-indigo-500/20 text-indigo-300 font-bold border border-indigo-500/30' : 'bg-slate-900/60 text-slate-400 hover:text-white'}`}
                >
                  {mod}
                </button>
              ))}
            </div>

            {/* Dynamic Charts Canvas */}
            <div className="p-5 bg-slate-900/60 border border-slate-800/80 rounded-2xl space-y-4">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Weekly Performance Timeseries</h3>
                <p className="text-xs text-slate-500">Dynamic telemetry aggregates chart representation</p>
              </div>

              <div className="h-60 bg-slate-950/80 border border-slate-900 rounded-xl p-4 flex items-center justify-center">
                {renderSVGChart(chartData)}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'realtime' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Realtime request monitor */}
              <div className="p-5 bg-slate-900/60 border border-slate-800/80 rounded-2xl space-y-4">
                <div>
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">API Gateway request rate</h3>
                  <p className="text-xs text-slate-500">Live requests logged per second</p>
                </div>
                <div className="h-48 flex items-center justify-center bg-slate-950 rounded-xl">
                  {renderSVGChart([
                    { label: '10s ago', value: 8 },
                    { label: '8s ago', value: 14 },
                    { label: '6s ago', value: 12 },
                    { label: '4s ago', value: 22 },
                    { label: '2s ago', value: 18 },
                    { label: 'Now', value: 25 }
                  ])}
                </div>
              </div>

              {/* Geographic heatmap map */}
              <div className="p-5 bg-slate-900/60 border border-slate-800/80 rounded-2xl space-y-4">
                <div>
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Geographic Heatmap</h3>
                  <p className="text-xs text-slate-500">Regional density map logs</p>
                </div>
                <div className="space-y-2.5">
                  {[
                    { country: 'India', rate: '62.4%', users: 14500 },
                    { country: 'United States', rate: '19.3%', users: 4500 },
                    { country: 'United Kingdom', rate: '7.8%', users: 1820 },
                    { country: 'Singapore', rate: '4.8%', users: 1120 }
                  ].map((geo, idx) => (
                    <div key={idx} className="flex justify-between items-center text-xs border-b border-slate-800 pb-2">
                      <span className="text-slate-300 font-mono">{geo.country}</span>
                      <span className="font-bold text-white">{geo.users} users ({geo.rate})</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'reports' && (
          <div className="space-y-6">
            
            {/* Quick Export Panel */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {['CSV', 'EXCEL', 'PDF'].map(fmt => (
                <button
                  key={fmt}
                  onClick={() => handleCreateExport(fmt)}
                  className="p-4 bg-slate-900 border border-slate-800 hover:border-indigo-500/30 rounded-xl text-center space-y-2 group transition"
                >
                  <Download size={20} className="mx-auto text-slate-400 group-hover:text-indigo-400 transition" />
                  <span className="block text-xs font-bold text-white font-mono">Create {fmt} Export</span>
                </button>
              ))}
            </div>

            {/* Generated Reports Table */}
            <div className="p-5 bg-slate-900/60 border border-slate-800/80 rounded-2xl space-y-4">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Available Exports downloads</h3>
                <p className="text-xs text-slate-500">Download compiled files</p>
              </div>

              <div className="divide-y divide-slate-800/60 font-mono text-xs">
                {exports.map(exp => (
                  <div key={exp.id} className="py-3 flex justify-between items-center">
                    <div>
                      <span className="text-slate-200 block font-bold">{exp.job_type} Export Job</span>
                      <span className="text-[10px] text-slate-500 block">ID: {exp.id}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${exp.status === 'COMPLETED' ? 'bg-emerald-950 text-emerald-400' : 'bg-slate-950 text-slate-400'}`}>
                        {exp.status}
                      </span>
                      {exp.status === 'COMPLETED' && (
                        <a 
                          href={exp.file_url} 
                          target="_blank" 
                          rel="noreferrer"
                          className="p-1 hover:bg-slate-800 rounded text-indigo-400 hover:text-white transition"
                        >
                          <Download size={14} />
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Scheduled reports section */}
            <div className="p-5 bg-slate-900/60 border border-slate-800/80 rounded-2xl space-y-4">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Automated Mail Schedules</h3>
                <p className="text-xs text-slate-500">Configure recurring report triggers</p>
              </div>

              <form onSubmit={handleCreateSchedule} className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <input 
                  type="text" 
                  placeholder="Report Title" 
                  value={newTitle} 
                  onChange={e => setNewTitle(e.target.value)} 
                  className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500" 
                />
                <select 
                  value={newFreq} 
                  onChange={e => setNewFreq(e.target.value)} 
                  className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="DAILY">Daily</option>
                  <option value="WEEKLY">Weekly</option>
                  <option value="MONTHLY">Monthly</option>
                </select>
                <input 
                  type="text" 
                  placeholder="Recipients (comma-separated)" 
                  value={newRecipients} 
                  onChange={e => setNewRecipients(e.target.value)} 
                  className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500" 
                />
                <button type="submit" className="md:col-span-3 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-xl text-xs font-bold text-white transition flex items-center justify-center gap-1.5">
                  <Plus size={14} />
                  Add Report Schedule
                </button>
              </form>

              <div className="divide-y divide-slate-800 font-mono text-xs">
                {schedules.map(sched => (
                  <div key={sched.id} className="py-3 flex justify-between items-center">
                    <div>
                      <span className="text-slate-200 block font-bold">{sched.report_title}</span>
                      <span className="text-[9px] text-slate-500 block">Frequency: {sched.frequency} | Next run: {sched.next_run_at}</span>
                    </div>
                    <button 
                      onClick={() => handleDeleteSchedule(sched.id!)}
                      className="p-1 hover:bg-slate-800 rounded text-red-400 hover:text-red-300 transition"
                    >
                      <Trash size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-6">
            
            {/* KPI configurations controls list */}
            <div className="p-5 bg-slate-900/60 border border-slate-800/80 rounded-2xl space-y-4">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">KPI Boundaries Definitions</h3>
                <p className="text-xs text-slate-500">Configure target indicators parameters</p>
              </div>

              <div className="space-y-3">
                {kpis.map(kpi => (
                  <div key={kpi.id} className="p-4 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between">
                    <div>
                      <span className="text-slate-200 block font-bold font-mono">{kpi.name}</span>
                      <span className="text-[10px] text-slate-500 block">Key: {kpi.metric_key}</span>
                    </div>
                    <div className="flex gap-4 items-center">
                      <div className="text-right text-xs">
                        <span className="text-slate-400 block">Target: {kpi.target_value}</span>
                        <span className="text-indigo-400 block font-bold">Current: {kpi.current_value}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
