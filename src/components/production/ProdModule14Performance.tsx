/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  Zap,
  Activity,
  CheckCircle,
  Database,
  CloudLightning,
  RefreshCw,
  BarChart,
  HardDrive
} from 'lucide-react';

export const ProdModule14Performance: React.FC = () => {
  const [cacheStatus, setCacheStatus] = useState<string>('CACHE_HIT (92.4%)');
  const [gzipSavings, setGzipSavings] = useState<string>('78% (Save 420 KB / page)');
  const [queryCount, setQueryCount] = useState<number>(3);
  const [optimizationLog, setOptimizationLog] = useState<string[]>([
    '[23:01:00] [Nginx] Content-Encoding: gzip successfully applied to application index bundles.',
    '[23:01:10] [Database] Django queryset optimization: Prefetch/Select related index applied.',
    '[23:01:45] [Cache] Warmup triggered for Course Listing templates. Saved in Redis memory cluster.'
  ]);

  const runCacheClear = () => {
    setCacheStatus('CACHE_CLEARED (Warming...)');
    setOptimizationLog(prev => [
      ...prev,
      `[23:02:10] [Admin Trigger] Manual FLUSHALL triggered on Redis Node cluster. Clearing 4,204 key index records...`,
      `[23:02:12] [Cache Warmup] Automated scheduler warming popular courses and landing metrics into static caches.`
    ]);
    setTimeout(() => {
      setCacheStatus('CACHE_HIT (96.2%)');
    }, 1500);
  };

  const runIndexOptimization = () => {
    setQueryCount(1);
    setOptimizationLog(prev => [
      ...prev,
      `[23:02:14] [Database Engine] Optimization scan identified unindexed foreign keys in dynamic tables.`,
      `[23:02:15] [Database Engine] Applied CREATE INDEX CONCURRENTLY on target enrollment profiles.`,
      `[23:02:16] [Database Engine] Average query density reduced from 3 requests to 1 request.`
    ]);
  };

  return (
    <div id="performance-optimization-root" className="space-y-6">
      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 space-y-2">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">Redis Cache Ratio</span>
            <Zap className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-sm font-black text-white mt-2 font-mono">{cacheStatus}</p>
          <span className="text-[9px] text-slate-500 font-sans block mt-0.5">High-speed key hit telemetry</span>
        </div>

        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 space-y-2">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">Nginx Payload Savings</span>
            <HardDrive className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-sm font-black text-white mt-2 font-mono">{gzipSavings}</p>
          <span className="text-[9px] text-slate-500 font-sans block mt-0.5">Static bundle Gzip compression</span>
        </div>

        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 space-y-2">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">Queries Per Request</span>
            <Database className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-sm font-black text-white mt-2 font-mono">{queryCount} SQL Calls</p>
          <span className="text-[9px] text-slate-500 font-sans block mt-0.5">Optimized via select_related</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 text-left">
        {/* Diagnostics & Operations Panel */}
        <div className="lg:col-span-8 bg-[#050914] border border-indigo-950/40 rounded-xl p-4 space-y-4">
          <div className="flex justify-between items-center pb-2 border-b border-slate-900">
            <div>
              <span className="text-xs font-bold text-slate-300 font-sans">Performance Operations Control Panel</span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={runCacheClear}
                className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold font-sans px-3.5 py-1.5 rounded-lg transition shrink-0"
              >
                Flush Redis Cache
              </button>
              <button
                onClick={runIndexOptimization}
                className="bg-slate-950 border border-slate-900 hover:bg-slate-900 text-slate-300 text-xs font-bold font-sans px-3.5 py-1.5 rounded-lg transition shrink-0"
              >
                Optimize SQL Indexes
              </button>
            </div>
          </div>

          <div className="space-y-3">
            <h5 className="text-[10px] text-slate-500 font-mono uppercase tracking-wider">Optimization Log Terminal</h5>
            <div className="bg-slate-950 border border-slate-900 rounded-xl p-3.5 font-mono text-[10px] text-emerald-400 space-y-1.5 h-[150px] overflow-y-auto leading-normal">
              {optimizationLog.map((log, idx) => (
                <div key={idx} className="break-all whitespace-pre-wrap">
                  {log}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Database Optimizers Overview */}
        <div className="lg:col-span-4 bg-slate-950/40 border border-slate-900 rounded-xl p-4 flex flex-col justify-between h-full min-h-[250px]">
          <div className="space-y-4">
            <div className="flex items-center gap-1.5 border-b border-slate-900 pb-2 text-slate-300">
              <BarChart className="w-4 h-4 text-indigo-400" />
              <span className="text-xs font-bold font-sans uppercase tracking-wider font-mono">Query Execution Metrics</span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between p-2.5 bg-[#050914] rounded-lg border border-slate-900">
                <span className="text-slate-400">Database Index State:</span>
                <span className="text-emerald-400 font-mono font-bold">100% COVERED</span>
              </div>
              <div className="flex justify-between p-2.5 bg-[#050914] rounded-lg border border-slate-900">
                <span className="text-slate-400">Nginx Compression Savings:</span>
                <span className="text-emerald-400 font-mono font-bold">78% COMPRESSED</span>
              </div>
              <div className="flex justify-between p-2.5 bg-[#050914] rounded-lg border border-slate-900">
                <span className="text-slate-400">Static Files CDN Caching:</span>
                <span className="text-emerald-400 font-mono font-bold">ACTIVE (S3 INTEGRATION)</span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-900 mt-4 text-[10px] text-slate-500 leading-normal">
            Query benchmarks comply with core high-speed latency SLAs (under 200ms per client route).
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProdModule14Performance;
