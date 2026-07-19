import React, { useState, useEffect } from 'react';
import { searchApi, SearchAnalytics as ISearchAnalytics } from '../../services/searchApi';
import { BarChart, Percent, Clock, Search } from 'lucide-react';

export const SearchAnalytics: React.FC = () => {
  const [analytics, setAnalytics] = useState<ISearchAnalytics[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      const res = await searchApi.getAnalytics();
      if (res.success && res.data) {
        setAnalytics(res.data);
      }
      setLoading(false);
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return <div className="text-center py-10 text-xs text-slate-500">Loading search performance indexes...</div>;
  }

  // Calculate aggregates
  const totalQueries = analytics.reduce((sum, item) => sum + item.total_queries, 0);
  const avgCTR = analytics.length > 0 ? analytics.reduce((sum, item) => sum + item.click_through_rate, 0) / analytics.length : 0;
  const avgDwell = analytics.length > 0 ? analytics.reduce((sum, item) => sum + item.avg_dwell_time, 0) / analytics.length : 0;

  return (
    <div className="space-y-6 font-sans text-xs">
      {/* Bento Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Card 1: Total Queries */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="bg-indigo-50 p-3 rounded-xl">
            <Search className="h-6 w-6 text-indigo-600" />
          </div>
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase font-mono block">Total Queries logged</span>
            <span className="text-lg font-bold text-slate-800">{totalQueries}</span>
          </div>
        </div>

        {/* Card 2: Average CTR */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="bg-emerald-50 p-3 rounded-xl">
            <Percent className="h-6 w-6 text-emerald-600" />
          </div>
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase font-mono block">Average Click CTR</span>
            <span className="text-lg font-bold text-slate-800">{(avgCTR * 100).toFixed(1)}%</span>
          </div>
        </div>

        {/* Card 3: Avg Dwell Time */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="bg-amber-50 p-3 rounded-xl">
            <Clock className="h-6 w-6 text-amber-600" />
          </div>
          <div>
            <span className="text-[10px] font-bold text-slate-400 uppercase font-mono block">Avg Result Dwell</span>
            <span className="text-lg font-bold text-slate-800">{avgDwell.toFixed(1)}s</span>
          </div>
        </div>
      </div>

      {/* Query Performance Table */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center gap-1.5 font-mono">
          <BarChart className="h-4 w-4 text-indigo-600" /> Query Performance Report
        </h3>
        {analytics.length === 0 ? (
          <div className="text-center py-10 text-slate-400">No query analytics logged yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 text-[10px] font-bold text-slate-400 uppercase font-mono">
                  <th className="py-2.5 pb-2">Query Term</th>
                  <th className="py-2.5 pb-2 text-right">Searches Count</th>
                  <th className="py-2.5 pb-2 text-right">Results returned</th>
                  <th className="py-2.5 pb-2 text-right">Click CTR</th>
                  <th className="py-2.5 pb-2 text-right font-mono">Avg Dwell</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50 text-slate-600">
                {analytics.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/50 transition">
                    <td className="py-2.5 font-semibold text-slate-800">{item.query_string}</td>
                    <td className="py-2.5 text-right font-mono">{item.total_queries}</td>
                    <td className="py-2.5 text-right font-mono">{item.total_results}</td>
                    <td className="py-2.5 text-right font-mono text-emerald-600">
                      {(item.click_through_rate * 100).toFixed(1)}%
                    </td>
                    <td className="py-2.5 text-right font-mono">{item.avg_dwell_time.toFixed(1)}s</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
