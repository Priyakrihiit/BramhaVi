import React, { useEffect, useState } from 'react';
import { cmsApi } from '../../services/cmsApi';
import { BarChart3, FileText, FolderTree, Tag, Eye, Heart, MessageSquare, AlertCircle } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const CMSDashboard: React.FC = () => {
  const [stats, setStats] = useState({
    articles: 0,
    categories: 0,
    tags: 0,
    views: 1240,
    likes: 382,
    comments: 98,
  });

  const chartData = [
    { name: 'Jan', views: 400, articles: 2 },
    { name: 'Feb', views: 800, articles: 5 },
    { name: 'Mar', views: 600, articles: 8 },
    { name: 'Apr', views: 1100, articles: 12 },
    { name: 'May', views: 1240, articles: 18 },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl flex items-center justify-between shadow-xl">
          <div>
            <span className="text-xs font-mono text-slate-500 uppercase tracking-widest">Total Articles</span>
            <h2 className="text-3xl font-extrabold text-white mt-1">18</h2>
            <span className="text-[10px] text-emerald-400 font-mono">+12% from last month</span>
          </div>
          <div className="p-4 bg-indigo-950/50 rounded-xl text-indigo-400 border border-indigo-900/50">
            <FileText size={24} />
          </div>
        </div>

        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl flex items-center justify-between shadow-xl">
          <div>
            <span className="text-xs font-mono text-slate-500 uppercase tracking-widest">Categories & Tags</span>
            <h2 className="text-3xl font-extrabold text-white mt-1">6 / 12</h2>
            <span className="text-[10px] text-indigo-400 font-mono">Taxonomy Sync Active</span>
          </div>
          <div className="p-4 bg-purple-950/50 rounded-xl text-purple-400 border border-purple-900/50">
            <FolderTree size={24} />
          </div>
        </div>

        <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl flex items-center justify-between shadow-xl">
          <div>
            <span className="text-xs font-mono text-slate-500 uppercase tracking-widest">Aggregate Traffic</span>
            <h2 className="text-3xl font-extrabold text-white mt-1">4.8K</h2>
            <span className="text-[10px] text-emerald-400 font-mono">+28% growth spike</span>
          </div>
          <div className="p-4 bg-emerald-950/50 rounded-xl text-emerald-400 border border-emerald-900/50">
            <BarChart3 size={24} />
          </div>
        </div>
      </div>

      {/* Traffic charts */}
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl shadow-xl">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400 mb-6">CMS TRAFFIC & AUDIENCE ENGAGEMENT</h3>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
              <Area type="monotone" dataKey="views" stroke="#6366f1" fillOpacity={1} fill="url(#colorViews)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
