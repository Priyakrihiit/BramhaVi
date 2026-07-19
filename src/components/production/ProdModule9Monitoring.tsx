/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import {
  Cpu,
  Database,
  Activity,
  Shield,
  Zap,
  HardDrive,
  RefreshCw,
  Clock
} from 'lucide-react';

interface MetricItem {
  time: string;
  cpu: number;
  ram: number;
  redis: number;
  dbPool: number;
  responseTime: number;
}

export const ProdModule9Monitoring: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricItem[]>([
    { time: '22:10', cpu: 14, ram: 42, redis: 18, dbPool: 8, responseTime: 120 },
    { time: '22:20', cpu: 22, ram: 45, redis: 20, dbPool: 12, responseTime: 140 },
    { time: '22:30', cpu: 18, ram: 44, redis: 22, dbPool: 10, responseTime: 130 },
    { time: '22:40', cpu: 34, ram: 52, redis: 34, dbPool: 24, responseTime: 195 },
    { time: '22:50', cpu: 28, ram: 49, redis: 28, dbPool: 18, responseTime: 160 },
    { time: '23:00', cpu: 15, ram: 43, redis: 19, dbPool: 9, responseTime: 110 }
  ]);

  const [dbStatus, setDbStatus] = useState<'HEALTHY' | 'LOADED'>('HEALTHY');
  const [redisUsage, setRedisUsage] = useState<string>('24.2 MB / 512 MB');

  const addLivePoint = () => {
    const lastPoint = metrics[metrics.length - 1];
    const newCpu = Math.min(100, Math.max(10, lastPoint.cpu + Math.floor(Math.random() * 21) - 10));
    const newRam = Math.min(100, Math.max(10, lastPoint.ram + Math.floor(Math.random() * 5) - 2));
    const newRedis = Math.min(100, Math.max(10, lastPoint.redis + Math.floor(Math.random() * 5) - 2));
    const newDb = Math.min(50, Math.max(2, lastPoint.dbPool + Math.floor(Math.random() * 7) - 3));
    const newTime = new Date().toLocaleTimeString().substring(0, 5);
    const newResp = Math.floor(90 + Math.random() * 120);

    setMetrics(prev => [...prev.slice(1), {
      time: newTime,
      cpu: newCpu,
      ram: newRam,
      redis: newRedis,
      dbPool: newDb,
      responseTime: newResp
    }]);
  };

  return (
    <div id="monitoring-root" className="space-y-6">
      {/* Real-time Health Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 text-left">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">Average CPU Load</span>
            <Cpu className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-lg font-black text-white mt-1 font-mono">
            {metrics[metrics.length - 1].cpu}%
          </p>
          <span className="text-[9px] text-slate-500 font-sans block mt-0.5">8 Cores Allocation</span>
        </div>

        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 text-left">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">RAM Consumption</span>
            <HardDrive className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-lg font-black text-white mt-1 font-mono">
            {metrics[metrics.length - 1].ram}%
          </p>
          <span className="text-[9px] text-slate-500 font-sans block mt-0.5">1.96 GB / 4.00 GB</span>
        </div>

        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 text-left">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">Redis Cache Key Count</span>
            <Zap className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-lg font-black text-white mt-1 font-mono">{redisUsage.split(' ')[0]} MB</p>
          <span className="text-[9px] text-slate-500 font-sans block mt-0.5">Redis Cluster Live</span>
        </div>

        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 text-left">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">Database State</span>
            <Database className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-lg font-black text-emerald-400 mt-1 font-mono">{dbStatus}</p>
          <span className="text-[9px] text-slate-500 font-sans block mt-0.5">PostgreSQL Pool: {metrics[metrics.length - 1].dbPool} open</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 text-left">
        {/* Resource Area Chart */}
        <div className="lg:col-span-8 bg-slate-950/40 border border-indigo-950/30 rounded-xl p-4 space-y-4">
          <div className="flex justify-between items-center pb-2 border-b border-slate-900">
            <div>
              <h4 className="text-xs font-black text-white uppercase tracking-wider font-mono">Platform Infrastructure Stream</h4>
              <p className="text-[10px] text-slate-500 mt-0.5">Continuous container health metrics.</p>
            </div>
            <button
              onClick={addLivePoint}
              className="bg-slate-900 hover:bg-slate-950 text-indigo-400 border border-slate-800 text-[10px] font-mono px-2.5 py-1.5 rounded-lg transition flex items-center gap-1"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Sample Live Point
            </button>
          </div>

          <div className="h-[220px] w-full font-mono text-[10px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={metrics}>
                <defs>
                  <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorRam" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ec4899" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#ec4899" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#0f172a" />
                <XAxis dataKey="time" stroke="#475569" />
                <YAxis stroke="#475569" />
                <Tooltip contentStyle={{ backgroundColor: '#020617', borderColor: '#1e293b' }} />
                <Area type="monotone" dataKey="cpu" stroke="#6366f1" fillOpacity={1} fill="url(#colorCpu)" name="CPU %" />
                <Area type="monotone" dataKey="ram" stroke="#ec4899" fillOpacity={1} fill="url(#colorRam)" name="RAM %" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Live Response Speed Tracker */}
        <div className="lg:col-span-4 bg-slate-950/40 border border-slate-900 rounded-xl p-4 flex flex-col justify-between h-full min-h-[280px]">
          <div className="space-y-4">
            <div className="flex items-center gap-1.5 border-b border-slate-900 pb-2 text-slate-300">
              <Clock className="w-4 h-4 text-indigo-400" />
              <span className="text-xs font-bold font-mono uppercase tracking-wider">REST Ingress Latency</span>
            </div>

            <div className="bg-[#050914] rounded-lg p-4 border border-slate-900 text-center space-y-2">
              <span className="text-[10px] text-slate-500 font-mono">Average Response Delay</span>
              <p className="text-2xl font-black text-indigo-400 font-mono">
                {metrics[metrics.length - 1].responseTime} ms
              </p>
              <span className="text-[9px] bg-emerald-500/10 text-emerald-400 border border-emerald-950 px-2 py-0.5 rounded font-mono inline-block">
                SLA COMPLIANT (99.9%)
              </span>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-900 mt-4 text-[10px] text-slate-500 font-mono leading-relaxed space-y-1">
            <div className="flex justify-between">
              <span>Nginx Compression:</span>
              <span className="text-slate-300">Gzip Enabled</span>
            </div>
            <div className="flex justify-between">
              <span>HTTP/2 Stream:</span>
              <span className="text-slate-300">Active</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProdModule9Monitoring;
