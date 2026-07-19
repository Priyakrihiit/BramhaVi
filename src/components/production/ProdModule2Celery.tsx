/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  Server,
  Activity,
  AlertTriangle,
  Clock,
  RefreshCw,
  Play,
  RotateCcw,
  Cpu,
  Database,
  Terminal,
  Layers,
  CheckCircle2
} from 'lucide-react';

interface CeleryJob {
  id: string;
  name: string;
  queue: string;
  runtime: string;
  status: 'RUNNING' | 'FAILED' | 'SUCCESS' | 'RETRYING' | 'SCHEDULED';
  startedAt: string;
  worker: string;
}

export const ProdModule2Celery: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'running' | 'failed' | 'scheduled' | 'retries'>('running');
  const [workers, setWorkers] = useState([
    { name: 'celery-worker-default@bv-node-1', status: 'ACTIVE', concurrency: 8, completed: 14205, activeJobs: 3 },
    { name: 'celery-worker-highpriority@bv-node-1', status: 'ACTIVE', concurrency: 4, completed: 89042, activeJobs: 1 },
    { name: 'celery-worker-beatengine@bv-node-2', status: 'ACTIVE', concurrency: 2, completed: 3410, activeJobs: 0 }
  ]);

  const [jobs, setJobs] = useState<CeleryJob[]>([
    { id: 'task-a49e-108b', name: 'bv_galaxy.tasks.enroll_student', queue: 'default', runtime: '240ms', status: 'RUNNING', startedAt: '23:01:40', worker: 'celery-worker-default@bv-node-1' },
    { id: 'task-1d90-ffb2', name: 'bv_galaxy.tasks.generate_pdf_invoice', queue: 'default', runtime: '120ms', status: 'RUNNING', startedAt: '23:01:43', worker: 'celery-worker-default@bv-node-1' },
    { id: 'task-f492-c102', name: 'bv_galaxy.tasks.send_twilio_dispatch', queue: 'highpriority', runtime: '1.2s', status: 'RUNNING', startedAt: '23:01:44', worker: 'celery-worker-highpriority@bv-node-1' },
    { id: 'task-e028-2bb1', name: 'bv_galaxy.tasks.rebuild_search_index', queue: 'default', runtime: '4.5s', status: 'FAILED', startedAt: '22:45:10', worker: 'celery-worker-default@bv-node-1' },
    { id: 'task-922c-df20', name: 'bv_galaxy.tasks.sync_ledger_entries', queue: 'highpriority', runtime: '310ms', status: 'FAILED', startedAt: '22:12:15', worker: 'celery-worker-highpriority@bv-node-1' },
    { id: 'task-cron-01', name: 'bv_galaxy.tasks.auto_backup_database', queue: 'beatengine', runtime: '-', status: 'SCHEDULED', startedAt: 'Tomorrow 03:00', worker: 'celery-worker-beatengine@bv-node-2' },
    { id: 'task-cron-02', name: 'bv_galaxy.tasks.calculate_affiliate_payouts', queue: 'beatengine', runtime: '-', status: 'SCHEDULED', startedAt: 'Daily 00:00', worker: 'celery-worker-beatengine@bv-node-2' },
    { id: 'task-retry-40', name: 'bv_galaxy.tasks.post_webhook_alert', queue: 'default', runtime: '800ms', status: 'RETRYING', startedAt: '22:58:10', worker: 'celery-worker-default@bv-node-1' }
  ]);

  const [consoleLogs, setConsoleLogs] = useState<string[]>([
    '[23:01:00] [Celery Beat] Scheduler: Sending due task bv_galaxy.tasks.auto_backup_database',
    '[23:01:12] [Worker default] Received task: bv_galaxy.tasks.enroll_student[task-a49e-108b]',
    '[23:01:13] [Worker default] Task bv_galaxy.tasks.enroll_student[task-a49e-108b] succeeded in 240ms',
    '[23:01:43] [Worker default] Received task: bv_galaxy.tasks.generate_pdf_invoice[task-1d90-ffb2]'
  ]);

  const retryTask = (id: string) => {
    setJobs(jobs.map(j => {
      if (j.id === id) {
        return { ...j, status: 'RUNNING', startedAt: 'Just Now' };
      }
      return j;
    }));
    setConsoleLogs(prev => [
      ...prev,
      `[23:01:48] [Admin Trigger] Manual retry submitted for Celery Task ID: ${id}`
    ]);
  };

  const triggerTask = (taskName: string) => {
    const newTaskId = `task-manual-${Math.random().toString(36).substring(2, 6)}`;
    const newJob: CeleryJob = {
      id: newTaskId,
      name: taskName,
      queue: 'default',
      runtime: 'Pending',
      status: 'RUNNING',
      startedAt: 'Just Now',
      worker: 'celery-worker-default@bv-node-1'
    };
    setJobs([newJob, ...jobs]);
    setConsoleLogs(prev => [
      ...prev,
      `[23:01:49] [Worker default] Enqueued new task ${taskName}[${newTaskId}] via Celery delay()`
    ]);
  };

  const filteredJobs = jobs.filter(j => {
    if (activeTab === 'running') return j.status === 'RUNNING';
    if (activeTab === 'failed') return j.status === 'FAILED';
    if (activeTab === 'scheduled') return j.status === 'SCHEDULED';
    if (activeTab === 'retries') return j.status === 'RETRYING';
    return true;
  });

  return (
    <div id="celery-dashboard-root" className="space-y-6">
      {/* Worker Health Nodes */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {workers.map((worker, i) => (
          <div key={i} className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 text-left">
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-2">
                <Server className="w-4 h-4 text-emerald-400 shrink-0" />
                <h4 className="text-xs font-bold text-white truncate max-w-[150px] font-mono">{worker.name}</h4>
              </div>
              <span className="text-[9px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-950 font-mono">
                {worker.status}
              </span>
            </div>
            <div className="grid grid-cols-3 gap-2 mt-4 text-center">
              <div className="bg-[#0b1329] p-2 rounded-lg border border-indigo-950/40">
                <p className="text-[10px] text-slate-500 font-sans">Concurrency</p>
                <p className="text-xs font-bold text-slate-300 font-mono mt-0.5">{worker.concurrency} Cores</p>
              </div>
              <div className="bg-[#0b1329] p-2 rounded-lg border border-indigo-950/40">
                <p className="text-[10px] text-slate-500 font-sans">Active Jobs</p>
                <p className="text-xs font-bold text-slate-300 font-mono mt-0.5">{worker.activeJobs}</p>
              </div>
              <div className="bg-[#0b1329] p-2 rounded-lg border border-indigo-950/40">
                <p className="text-[10px] text-slate-500 font-sans">Completed</p>
                <p className="text-xs font-bold text-emerald-400 font-mono mt-0.5">{worker.completed}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Jobs Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8 bg-slate-950/40 border border-indigo-950/30 rounded-xl p-4 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-900">
            <div className="flex flex-wrap gap-1">
              {(['running', 'failed', 'scheduled', 'retries'] as const).map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold capitalize transition font-sans ${activeTab === tab ? 'bg-indigo-600 text-white' : 'bg-slate-900/50 text-slate-400 hover:bg-slate-900'}`}
                >
                  {tab} ({jobs.filter(j => {
                    if (tab === 'running') return j.status === 'RUNNING';
                    if (tab === 'failed') return j.status === 'FAILED';
                    if (tab === 'scheduled') return j.status === 'SCHEDULED';
                    if (tab === 'retries') return j.status === 'RETRYING';
                    return false;
                  }).length})
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => triggerTask('bv_galaxy.tasks.rebuild_search_index')}
                className="bg-slate-900 border border-slate-800 text-[10px] text-indigo-400 hover:text-indigo-300 px-3 py-1.5 rounded-lg transition font-mono flex items-center gap-1"
              >
                <Play className="w-3 h-3" /> Trigger Manual Index
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-900 text-[10px] text-slate-500 uppercase tracking-wider font-mono">
                  <th className="py-2">Task Name / ID</th>
                  <th className="py-2">Queue</th>
                  <th className="py-2">Runtime</th>
                  <th className="py-2">Started / Status</th>
                  <th className="py-2 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900/40 text-xs font-mono">
                {filteredJobs.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-950/20 group">
                    <td className="py-3">
                      <div className="text-slate-300 font-bold truncate max-w-[200px]">{job.name}</div>
                      <div className="text-[10px] text-slate-600 mt-0.5">{job.id}</div>
                    </td>
                    <td className="py-3">
                      <span className="text-[10px] bg-slate-900 text-indigo-400 border border-indigo-950 px-2 py-0.5 rounded">
                        {job.queue}
                      </span>
                    </td>
                    <td className="py-3 text-slate-400">{job.runtime}</td>
                    <td className="py-3">
                      <div className="text-slate-500">{job.startedAt}</div>
                      <span className={`text-[9px] font-bold ${job.status === 'RUNNING' ? 'text-amber-400' : job.status === 'FAILED' ? 'text-rose-400' : 'text-slate-500'}`}>
                        {job.status}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      {job.status === 'FAILED' && (
                        <button
                          onClick={() => retryTask(job.id)}
                          className="text-[10px] bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 border border-indigo-950 px-2 py-1 rounded transition flex items-center gap-1 ml-auto"
                        >
                          <RotateCcw className="w-3 h-3" /> Retry Task
                        </button>
                      )}
                      {job.status === 'RUNNING' && (
                        <span className="inline-block h-2 w-2 rounded-full bg-amber-400 animate-ping mr-3"></span>
                      )}
                    </td>
                  </tr>
                ))}
                {filteredJobs.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-slate-600 text-xs italic">
                      No background jobs currently in this queue status.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Live Logs from Celery Beat / Broker */}
        <div className="lg:col-span-4 bg-[#050914] border border-slate-900 rounded-xl p-4 flex flex-col justify-between h-full min-h-[350px] text-left">
          <div className="space-y-4">
            <div className="flex items-center gap-1.5 text-slate-300">
              <Terminal className="w-4 h-4 text-indigo-400" />
              <h5 className="text-xs font-black tracking-wider font-mono uppercase">Celery Logs Stream</h5>
            </div>

            <div className="bg-black/80 rounded-lg p-3 font-mono text-[10px] text-emerald-400 h-[240px] overflow-y-auto space-y-2 border border-slate-900 leading-normal">
              {consoleLogs.map((log, i) => (
                <div key={i} className="break-all whitespace-pre-wrap">
                  {log}
                </div>
              ))}
            </div>
          </div>

          <div className="pt-3 border-t border-slate-900 mt-4">
            <div className="flex items-center gap-2 text-[10px] text-slate-500 font-mono">
              <Activity className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
              <span>Broker Connection: RabbitMQ/Redis Stable</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProdModule2Celery;
