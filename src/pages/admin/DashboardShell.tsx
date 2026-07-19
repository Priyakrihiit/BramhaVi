/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useState } from 'react';
import { api, PlatformStats, ActivityLog, TaskSummary } from '../../services/api';
import { Users, Award, Shield, DollarSign, Activity } from 'lucide-react';

export const DashboardShell: React.FC = () => {
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [tasks, setTasks] = useState<TaskSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.stats.get(), api.activities.list(), api.tasks.list()])
      .then(([statsRes, logsRes, tasksRes]) => {
        if (statsRes.success && statsRes.data) setStats(statsRes.data);
        if (logsRes.success && logsRes.data) setLogs(logsRes.data);
        if (tasksRes.success && tasksRes.data) setTasks(tasksRes.data);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 text-slate-500 font-mono text-xs">
        <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-ping mr-2"></span>
        Compiling administrative summary stats...
      </div>
    );
  }

  return (
    <React.Fragment>
      <div id="bvg-admin-dashboard" className="space-y-6">
        
        {/* Core Stats Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl flex items-center gap-4">
            <div className="p-2 bg-indigo-500/10 rounded-xl text-indigo-400">
              <Users size={20} />
            </div>
            <div>
              <span className="block text-[10px] text-slate-500 font-bold uppercase font-mono">Total Students</span>
              <span className="text-xl font-bold text-white mt-0.5 block">{stats?.totalStudents.value}</span>
            </div>
          </div>

          <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl flex items-center gap-4">
            <div className="p-2 bg-amber-500/10 rounded-xl text-amber-400">
              <Award size={20} />
            </div>
            <div>
              <span className="block text-[10px] text-slate-500 font-bold uppercase font-mono">Issued Certs</span>
              <span className="text-xl font-bold text-white mt-0.5 block">{stats?.totalCourses.value}</span>
            </div>
          </div>

          <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl flex items-center gap-4">
            <div className="p-2 bg-emerald-500/10 rounded-xl text-emerald-400">
              <DollarSign size={20} />
            </div>
            <div>
              <span className="block text-[10px] text-slate-500 font-bold uppercase font-mono">Platform Revenue</span>
              <span className="text-xl font-bold text-white mt-0.5 block">{stats?.totalRevenue.value}</span>
            </div>
          </div>

          <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl flex items-center gap-4">
            <div className="p-2 bg-red-500/10 rounded-xl text-red-400">
              <Shield size={20} />
            </div>
            <div>
              <span className="block text-[10px] text-slate-500 font-bold uppercase font-mono">System Load</span>
              <span className="text-xl font-bold text-white mt-0.5 block">0.08% / C8</span>
            </div>
          </div>
        </div>

        {/* Task lists & Audit logs splits */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Action Tasks */}
          <div className="lg:col-span-5 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">System Tasks Outstanding</h3>
              <p className="text-xs text-slate-500">Requires supervisor cryptographic signatures and approvals</p>
            </div>

            <div className="divide-y divide-slate-800">
              {tasks.map(task => (
                <div key={task.id} className="py-2.5 flex items-center justify-between text-xs">
                  <span className="text-slate-300 font-medium">{task.name}</span>
                  <span className={`font-mono font-bold bg-slate-950 px-2 py-0.5 rounded border border-slate-800 ${task.color}`}>
                    {task.count} PENDING
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Core Logs Feed */}
          <div className="lg:col-span-7 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Administrative Ledger Logs</h3>
                <p className="text-xs text-slate-500">Chronological list of all dynamic operations</p>
              </div>
              <Activity className="text-slate-600 animate-pulse" size={16} />
            </div>

            <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
              {logs.map((log, idx) => (
                <div key={idx} className="p-2.5 bg-slate-950 border border-slate-850 rounded-xl flex justify-between items-start text-[11px] gap-4">
                  <p className="text-slate-300 leading-relaxed">{log.text}</p>
                  <span className="text-slate-600 whitespace-nowrap font-mono">{log.time}</span>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </React.Fragment>
  );
};

export default DashboardShell;
