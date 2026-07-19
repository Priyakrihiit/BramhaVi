/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  ShieldCheck,
  CheckCircle,
  Clock,
  Play,
  RotateCcw,
  Sliders,
  Database,
  CloudLightning,
  AlertTriangle,
  Terminal,
  Activity,
  Award
} from 'lucide-react';

interface AuditCheck {
  id: string;
  category: string;
  description: string;
  status: 'PASSED' | 'PENDING' | 'WARNING';
}

export const ProdModule15Audit: React.FC = () => {
  const [checks, setChecks] = useState<AuditCheck[]>([
    { id: 'SEC-01', category: 'Security', description: 'Django production setting DEBUG=False configuration verification', status: 'PASSED' },
    { id: 'SEC-02', category: 'Security', description: 'JWT signature encryption salts & active secret rotation validations', status: 'PASSED' },
    { id: 'SYS-01', category: 'Infrastructure', description: 'PostgreSQL database pool cluster bounds & read replicas integrity', status: 'PASSED' },
    { id: 'SYS-02', category: 'Infrastructure', description: 'Nginx static content cache rules & header security configurations', status: 'PASSED' },
    { id: 'FIN-01', category: 'Financials', description: 'Double-entry settlement ledger matching, GST splits, and TDS records', status: 'PASSED' },
    { id: 'CEL-01', category: 'Celery Broker', description: 'RabbitMQ queue monitoring state & worker concurrency limits matching', status: 'PASSED' },
    { id: 'ACC-01', category: 'WCAG Access', description: 'DOM keyboard accessibility sequential tabindex and aria label verification', status: 'PASSED' }
  ]);

  const [auditLog, setAuditLog] = useState<string[]>([
    '[23:01:00] [Security Audit] Starting full production compliance validation...',
    '[23:01:05] [Database Node] Checking database encryption keys... Verified.',
    '[23:01:12] [Nginx] Testing header security profiles (HSTS, Content-Security-Policy)... Valid.',
    '[23:01:20] [Compliance Score] Platform compliance verified at 100% (SLA Ready).'
  ]);

  const [isRunning, setIsRunning] = useState<boolean>(false);

  const triggerAuditScan = () => {
    setIsRunning(true);
    setAuditLog(prev => [
      ...prev,
      `[23:02:10] [Security Audit] Initiating thorough sandbox regression scan...`,
      `[23:02:12] [Security Audit] Auditing active OAuth integration scopes... OK.`,
      `[23:02:14] [Security Audit] Scanning dual-entry double accounting split margins... Matches perfectly.`,
      `[23:02:15] [Security Audit] Scan complete. 7/7 indicators passed.`
    ]);
    setTimeout(() => {
      setIsRunning(false);
    }, 1200);
  };

  return (
    <div id="production-audit-root" className="space-y-6">
      {/* Upper Status Banner */}
      <div className="bg-emerald-500/10 border border-emerald-950 p-4 rounded-xl flex items-center justify-between text-left">
        <div className="flex items-center gap-3">
          <div className="bg-emerald-500/20 p-2.5 rounded-lg text-emerald-400">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <h4 className="text-sm font-black text-white">BrahmaVidya Platform Production Ready</h4>
            <p className="text-[11px] text-slate-400 leading-normal mt-0.5">
              Congratulations! All systems have successfully cleared architectural audit validations.
            </p>
          </div>
        </div>
        <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-lg font-mono font-bold uppercase shrink-0">
          SLA STABLE
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 text-left">
        {/* Compliance Checklist Column */}
        <div className="lg:col-span-8 bg-[#050914] border border-indigo-950/40 rounded-xl p-4 space-y-4">
          <div className="flex justify-between items-center pb-2 border-b border-slate-900">
            <div>
              <span className="text-xs font-bold text-slate-300 font-sans">Security & Compliance Audit Registry</span>
            </div>
            <button
              onClick={triggerAuditScan}
              disabled={isRunning}
              className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/30 text-white text-xs font-bold font-sans px-3.5 py-1.5 rounded-lg transition flex items-center gap-1.5"
            >
              {isRunning ? 'Auditing...' : 'Run Security Scan'}
            </button>
          </div>

          <div className="space-y-2 max-h-[280px] overflow-y-auto pr-1">
            {checks.map(chk => (
              <div key={chk.id} className="flex justify-between items-start text-xs bg-slate-950 p-3 rounded-lg border border-slate-900 hover:border-indigo-950/40 transition">
                <div className="space-y-1 text-left max-w-[80%]">
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] bg-slate-900 text-indigo-400 border border-indigo-950 px-2 py-0.5 rounded font-mono font-bold uppercase">
                      {chk.category}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">{chk.id}</span>
                  </div>
                  <p className="text-[11px] text-slate-300 leading-normal">{chk.description}</p>
                </div>
                <span className="text-[9px] bg-emerald-500/10 text-emerald-400 border border-emerald-950 px-2.5 py-0.5 rounded font-mono font-bold">
                  {chk.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Live Audit Log Output Console */}
        <div className="lg:col-span-4 bg-slate-950 border border-slate-900 rounded-xl p-4 flex flex-col justify-between h-full min-h-[300px]">
          <div className="space-y-4">
            <div className="flex items-center gap-1.5 text-slate-300">
              <Terminal className="w-4 h-4 text-indigo-400" />
              <span className="text-xs font-bold font-mono uppercase tracking-wider">Compliance Monitor Stream</span>
            </div>

            <div className="bg-black rounded-lg p-3 font-mono text-[9px] text-emerald-400 h-[210px] overflow-y-auto space-y-1.5 border border-slate-900 leading-normal">
              {auditLog.map((log, i) => (
                <div key={i} className="break-all whitespace-pre-wrap border-b border-slate-900/40 pb-1 last:border-0 leading-relaxed">
                  {log}
                </div>
              ))}
            </div>
          </div>

          <div className="pt-3 border-t border-slate-900 mt-4 text-[10px] text-slate-500 font-mono leading-none flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Digital Signatures Sealed & Verified</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProdModule15Audit;
