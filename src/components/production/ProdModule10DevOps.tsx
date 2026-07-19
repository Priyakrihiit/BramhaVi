/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  FileText,
  Activity,
  CheckCircle,
  AlertTriangle,
  Play,
  RotateCcw,
  Sliders,
  Database,
  CloudLightning,
  Check
} from 'lucide-react';

interface DevOpsTask {
  name: string;
  category: 'BACKUP' | 'DOCKER' | 'RESTORE' | 'HEALTH';
  lastRun: string;
  status: 'SUCCESS' | 'FAILED' | 'PENDING';
}

export const ProdModule10DevOps: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'docker' | 'backups' | 'validation'>('docker');
  const [tasks, setTasks] = useState<DevOpsTask[]>([
    { name: 'Automated DB Snapshot to AWS S3', category: 'BACKUP', lastRun: 'Today 03:00', status: 'SUCCESS' },
    { name: 'Redis Cache Pruning Script', category: 'HEALTH', lastRun: 'Today 04:00', status: 'SUCCESS' },
    { name: 'Nginx Configuration Reload', category: 'DOCKER', lastRun: '2026-07-06 18:22', status: 'SUCCESS' },
    { name: 'Database Schema Sync Migration', category: 'RESTORE', lastRun: '2026-07-05 11:10', status: 'SUCCESS' }
  ]);

  const [consoleOutput, setConsoleOutput] = useState<string[]>([
    '$ docker-compose ps',
    'Name                     Command               State           Ports',
    '-------------------------------------------------------------------------',
    'bv-nginx-ingress-1      nginx -g daemon off;   Up (healthy)    0.0.0.0:3000->3000',
    'bv-gunicorn-app-1       gunicorn server.wsgi   Up (healthy)    8000/tcp',
    'bv-redis-cache-1        docker-entrypoint.sh   Up (healthy)    6379/tcp',
    'bv-celery-worker-1      celery -A tasks work   Up (healthy)    -'
  ]);

  const runBackup = () => {
    setConsoleOutput(prev => [
      ...prev,
      '$ python manage.py backup_to_s3',
      '[Backup] Initiating automatic PostgreSQL cluster dump...',
      '[Backup] Encrypting archive with AES-256...',
      '[Backup] Uploading 14.2 MB snapshot to Amazon S3 bucket "bv-backups"...',
      '[Backup] Success: Backup completed and registered in AWS database log ledger.'
    ]);
    const newTask: DevOpsTask = {
      name: `Manual Backup Snapshot ${Math.random().toString(36).substring(2, 6)}`,
      category: 'BACKUP',
      lastRun: 'Just Now',
      status: 'SUCCESS'
    };
    setTasks([newTask, ...tasks]);
  };

  const runDisasterTest = () => {
    setConsoleOutput(prev => [
      ...prev,
      '$ python manage.py test_disaster_recovery',
      '[Disaster Recovery] Simulating container collapse...',
      '[Disaster Recovery] Launching failover node on secondary GCP zone...',
      '[Disaster Recovery] Remounting S3 storage clusters...',
      '[Disaster Recovery] Restoring Redis replication rings...',
      '[Disaster Recovery] Success: Node recovered in 4.2 seconds.'
    ]);
  };

  return (
    <div id="devops-root" className="space-y-6">
      {/* DevOps Tabs */}
      <div className="flex border-b border-slate-900 pb-3 gap-2">
        <button
          onClick={() => setActiveTab('docker')}
          className={`px-4 py-1.5 rounded-lg text-xs font-bold font-sans transition ${activeTab === 'docker' ? 'bg-indigo-600 text-white' : 'bg-slate-900/40 text-slate-400 hover:bg-slate-900'}`}
        >
          Docker & Nginx State
        </button>
        <button
          onClick={() => setActiveTab('backups')}
          className={`px-4 py-1.5 rounded-lg text-xs font-bold font-sans transition ${activeTab === 'backups' ? 'bg-indigo-600 text-white' : 'bg-slate-900/40 text-slate-400 hover:bg-slate-900'}`}
        >
          Automated Backups
        </button>
        <button
          onClick={() => setActiveTab('validation')}
          className={`px-4 py-1.5 rounded-lg text-xs font-bold font-sans transition ${activeTab === 'validation' ? 'bg-indigo-600 text-white' : 'bg-slate-900/40 text-slate-400 hover:bg-slate-900'}`}
        >
          Environment Validation
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 text-left">
        {/* Tab content panel */}
        <div className="lg:col-span-8 space-y-4">
          {activeTab === 'docker' && (
            <div className="bg-[#050914] border border-indigo-950/40 rounded-xl p-4 space-y-3">
              <div className="flex justify-between items-center pb-2 border-b border-slate-900">
                <span className="text-xs font-bold text-slate-300 font-sans">Active Container Topology</span>
                <span className="text-[10px] text-emerald-400 font-mono font-bold">UPTIME: 14 DAYS</span>
              </div>
              <p className="text-[11px] text-slate-500 font-sans leading-relaxed">
                Nginx routes reverse-proxy ingress to port 3000, forwarding API endpoints to the Gunicorn Django application while balancing socket channels via Redis.
              </p>

              <div className="space-y-2 pt-2">
                <div className="flex items-center justify-between text-xs bg-slate-950 p-2.5 rounded-lg border border-slate-900">
                  <span className="font-mono text-slate-300">Nginx Reverse Proxy Ingress</span>
                  <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-950 px-2 py-0.5 rounded font-mono font-bold">HEALTHY</span>
                </div>
                <div className="flex items-center justify-between text-xs bg-slate-950 p-2.5 rounded-lg border border-slate-900">
                  <span className="font-mono text-slate-300">Gunicorn (WSGI Server)</span>
                  <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-950 px-2 py-0.5 rounded font-mono font-bold">HEALTHY</span>
                </div>
                <div className="flex items-center justify-between text-xs bg-slate-950 p-2.5 rounded-lg border border-slate-900">
                  <span className="font-mono text-slate-300">Celery Worker Daemon Cluster</span>
                  <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-950 px-2 py-0.5 rounded font-mono font-bold">HEALTHY</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'backups' && (
            <div className="bg-[#050914] border border-slate-900 rounded-xl p-4 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-900">
                <div>
                  <h4 className="text-xs font-bold text-slate-300 font-sans">Durable Database Snapshots</h4>
                  <p className="text-[10px] text-slate-500 font-sans">Backup processes store replicas in AWS S3.</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={runBackup}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold font-sans px-3.5 py-1.5 rounded-lg transition flex items-center gap-1 shrink-0"
                  >
                    <Database className="w-3.5 h-3.5" /> Back Up Now
                  </button>
                  <button
                    onClick={runDisasterTest}
                    className="bg-slate-950 border border-slate-900 hover:bg-slate-900 text-slate-300 text-xs font-bold font-sans px-3.5 py-1.5 rounded-lg transition flex items-center gap-1 shrink-0"
                  >
                    <CloudLightning className="w-3.5 h-3.5" /> Disaster Failover Test
                  </button>
                </div>
              </div>

              <div className="space-y-2 max-h-[180px] overflow-y-auto pr-1">
                {tasks.map((task, i) => (
                  <div key={i} className="flex justify-between items-center text-xs bg-slate-950 p-2.5 rounded-lg border border-slate-900 hover:border-indigo-950/40 transition">
                    <div className="space-y-0.5">
                      <p className="font-bold text-slate-300">{task.name}</p>
                      <p className="text-[10px] text-slate-500 font-mono">Last Run: {task.lastRun}</p>
                    </div>
                    <span className="text-[9px] bg-emerald-500/10 text-emerald-400 border border-emerald-950 px-2 py-0.5 rounded font-mono font-bold">
                      {task.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'validation' && (
            <div className="bg-[#050914] border border-slate-900 rounded-xl p-4 space-y-3">
              <div className="pb-2 border-b border-slate-900">
                <span className="text-xs font-bold text-slate-300 font-sans">Production Environment Configurations</span>
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between p-2.5 bg-slate-950 rounded-lg border border-slate-900">
                  <span className="text-slate-400 font-mono">DB_HOST Connection Address</span>
                  <span className="text-emerald-400 font-mono">postgres.bv-cluster.internal (VERIFIED)</span>
                </div>
                <div className="flex justify-between p-2.5 bg-slate-950 rounded-lg border border-slate-900">
                  <span className="text-slate-400 font-mono">REDIS_URL Connectivity Cache</span>
                  <span className="text-emerald-400 font-mono">redis://redis.cache:6379 (VERIFIED)</span>
                </div>
                <div className="flex justify-between p-2.5 bg-slate-950 rounded-lg border border-slate-900">
                  <span className="text-slate-400 font-mono">AWS_S3_BUCKET Storage Target</span>
                  <span className="text-emerald-400 font-mono">s3://bv-galaxy-production-s3 (VERIFIED)</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* DevOps Console Logs Terminal */}
        <div className="lg:col-span-4 bg-slate-950 border border-slate-900 rounded-xl p-4 flex flex-col justify-between h-full min-h-[300px]">
          <div className="space-y-4">
            <div className="flex items-center gap-1.5 text-slate-300">
              <Sliders className="w-4 h-4 text-indigo-400" />
              <span className="text-xs font-bold font-mono uppercase tracking-wider">DevOps Output Logger</span>
            </div>

            <div className="bg-black rounded-lg p-3.5 font-mono text-[9px] text-emerald-400 h-[210px] overflow-y-auto space-y-1.5 border border-slate-900 leading-normal">
              {consoleOutput.map((log, i) => (
                <div key={i} className="break-all whitespace-pre-wrap leading-relaxed border-b border-slate-900/40 pb-1 last:border-0">
                  {log}
                </div>
              ))}
            </div>
          </div>

          <div className="pt-3 border-t border-slate-900 mt-4">
            <span className="text-[10px] text-slate-500 font-mono leading-none flex items-center gap-1">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> Uptime backup systems fully automated.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProdModule10DevOps;
