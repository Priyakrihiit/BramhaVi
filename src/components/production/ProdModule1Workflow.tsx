/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  Play,
  Pause,
  Plus,
  Trash2,
  Settings,
  GitPullRequest,
  CheckCircle,
  Mail,
  FileText,
  Bell,
  BarChart,
  UserCheck,
  DollarSign,
  Wallet,
  Shield,
  Layers,
  ArrowRight
} from 'lucide-react';

interface WorkflowNode {
  id: string;
  type: string;
  title: string;
  desc: string;
  icon: any;
  status: 'ACTIVE' | 'PAUSED' | 'IDLE';
  config: Record<string, string | number | boolean>;
}

export const ProdModule1Workflow: React.FC = () => {
  const [trigger, setTrigger] = useState<string>('COURSE_PURCHASE');
  const [nodes, setNodes] = useState<WorkflowNode[]>([
    { id: '1', type: 'enrollment', title: 'Create Enrollment', desc: 'Auto enroll student in LMS course', icon: Layers, status: 'ACTIVE', config: { autoActivate: true } },
    { id: '2', type: 'invoice', title: 'Generate Invoice', desc: 'Generate GST-compliant SaaS invoice', icon: FileText, status: 'ACTIVE', config: { includeTax: true } },
    { id: '3', type: 'email', title: 'Send Welcome Email', desc: 'Send customized email template', icon: Mail, status: 'ACTIVE', config: { template: 'course_welcome' } },
    { id: '4', type: 'notification', title: 'In-App Notification', desc: 'Alert student and dispatcher queues', icon: Bell, status: 'ACTIVE', config: { channel: 'all' } },
    { id: '5', type: 'analytics', title: 'Update Analytics', desc: 'Recalculate Recharts statistics', icon: BarChart, status: 'ACTIVE', config: { metric: 'sales_revenue' } },
    { id: '6', type: 'referral', title: 'Award Referral', desc: 'Distribute multi-level affiliate commission', icon: UserCheck, status: 'ACTIVE', config: { affiliateTier: 1 } },
    { id: '7', type: 'commission', title: 'Award Teacher Commission', desc: 'Transfer revenue share to teacher', icon: DollarSign, status: 'ACTIVE', config: { pctShare: 70 } },
    { id: '8', type: 'wallet', title: 'Update Wallet Ledger', desc: 'Record double-entry transaction record', icon: Wallet, status: 'ACTIVE', config: { ledgerType: 'credit' } },
    { id: '9', type: 'audit', title: 'Generate Audit Logs', desc: 'Store SHA256 cryptographic sign log', icon: Shield, status: 'ACTIVE', config: { securityLevel: 'INFO' } }
  ]);

  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [activeStep, setActiveStep] = useState<number>(-1);
  const [simulationLogs, setSimulationLogs] = useState<string[]>([]);

  const addNode = () => {
    const newNode: WorkflowNode = {
      id: String(nodes.length + 1),
      type: 'custom',
      title: 'Custom Integration',
      desc: 'Webhook or custom API integration trigger',
      icon: GitPullRequest,
      status: 'IDLE',
      config: { url: 'https://api.bvgalaxy.com/webhook' }
    };
    setNodes([...nodes, newNode]);
    setSimulationLogs([...simulationLogs, `Added Custom Integration node`]);
  };

  const removeNode = (id: string) => {
    setNodes(nodes.filter(n => n.id !== id));
    setSimulationLogs([...simulationLogs, `Removed node ID: ${id}`]);
  };

  const toggleNodeStatus = (id: string) => {
    setNodes(nodes.map(n => {
      if (n.id === id) {
        const nextStatus = n.status === 'ACTIVE' ? 'PAUSED' : 'ACTIVE';
        return { ...n, status: nextStatus };
      }
      return n;
    }));
  };

  const runSimulation = () => {
    if (isSimulating) return;
    setIsSimulating(true);
    setActiveStep(0);
    setSimulationLogs([`[Trigger] Visual Workflow started with event: "${trigger}"`]);

    const activeNodes = nodes.filter(n => n.status === 'ACTIVE');
    let step = 0;

    const interval = setInterval(() => {
      if (step < activeNodes.length) {
        const node = activeNodes[step];
        setSimulationLogs(prev => [
          ...prev,
          `[Success] Executing step ${step + 1}: ${node.title} -> ${node.desc}`
        ]);
        setActiveStep(nodes.indexOf(node));
        step++;
      } else {
        clearInterval(interval);
        setIsSimulating(false);
        setActiveStep(-1);
        setSimulationLogs(prev => [...prev, `[Finished] Workflow execution completed successfully.`]);
      }
    }, 1000);
  };

  return (
    <div id="prod-module-1-root" className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-slate-950/40 p-4 rounded-xl border border-slate-900">
        <div>
          <h3 className="text-sm font-black text-white">Visual Event Trigger Configuration</h3>
          <p className="text-[11px] text-slate-500">Choose the workflow pipeline root event.</p>
        </div>
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <select
            value={trigger}
            onChange={(e) => setTrigger(e.target.value)}
            className="bg-[#0f172a] border border-indigo-950 text-xs text-indigo-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-sans"
          >
            <option value="COURSE_PURCHASE">On Course Purchase (Default)</option>
            <option value="USER_SIGNUP">On Academic User Registration</option>
            <option value="CERTIFICATE_EARNED">On Certificate Issuance</option>
            <option value="AFFILIATE_REDEEM">On Affiliate Link Redeem</option>
          </select>

          <button
            onClick={runSimulation}
            disabled={isSimulating}
            className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-bold font-sans transition ${isSimulating ? 'bg-amber-600/20 text-amber-400 border border-amber-900/40' : 'bg-indigo-600 hover:bg-indigo-500 text-white border border-indigo-500/20'}`}
          >
            {isSimulating ? <Pause className="w-3.5 h-3.5 animate-pulse" /> : <Play className="w-3.5 h-3.5" />}
            {isSimulating ? 'Running...' : 'Dry Run Pipeline'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Visual Map of Workflow Nodes */}
        <div className="lg:col-span-8 space-y-4">
          <div className="flex justify-between items-center">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">Workflow Pipeline Nodes</h4>
            <button
              onClick={addNode}
              className="flex items-center gap-1 text-[10px] bg-slate-900 border border-slate-800 text-slate-300 hover:text-white px-2.5 py-1 rounded-lg transition font-mono"
            >
              <Plus className="w-3 h-3" /> Add Node
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[420px] overflow-y-auto pr-1">
            {nodes.map((node, idx) => {
              const IconComponent = node.icon;
              const isCurrentlyExecuting = idx === activeStep;
              const isPaused = node.status === 'PAUSED';

              return (
                <div
                  key={node.id}
                  className={`p-3.5 rounded-xl border text-left transition flex flex-col justify-between ${
                    isCurrentlyExecuting
                      ? 'bg-indigo-950/50 border-indigo-500/80 shadow-[0_0_15px_rgba(99,102,241,0.15)]'
                      : isPaused
                      ? 'bg-slate-950/20 border-slate-900 text-slate-500'
                      : 'bg-slate-950/60 border-indigo-950/40 hover:border-indigo-900/60'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <div className={`p-2 rounded-lg ${isCurrentlyExecuting ? 'bg-indigo-600 text-white animate-bounce' : isPaused ? 'bg-slate-900 text-slate-600' : 'bg-slate-900 text-indigo-400'}`}>
                        <IconComponent className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-500 font-mono">Step #{idx + 1}</span>
                        <h5 className={`text-xs font-bold ${isPaused ? 'text-slate-500' : 'text-slate-200'}`}>{node.title}</h5>
                      </div>
                    </div>

                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => toggleNodeStatus(node.id)}
                        className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono border ${node.status === 'ACTIVE' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-950' : 'bg-slate-900 text-slate-500 border-slate-800'}`}
                      >
                        {node.status}
                      </button>
                      <button
                        onClick={() => removeNode(node.id)}
                        className="text-slate-500 hover:text-rose-400 p-1 rounded transition"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  </div>

                  <p className="text-[10px] text-slate-400 mt-2 line-clamp-1 font-sans">{node.desc}</p>

                  <div className="mt-3 pt-2.5 border-t border-slate-900 flex justify-between items-center">
                    <span className="text-[9px] text-slate-600 font-mono">TYPE: {node.type.toUpperCase()}</span>
                    <button className="text-[10px] text-slate-400 hover:text-indigo-400 flex items-center gap-0.5 font-mono">
                      <Settings className="w-3 h-3" /> Config
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Live Simulation Trace Logs */}
        <div className="lg:col-span-4 bg-[#050914]/80 rounded-xl p-4 border border-indigo-950/60 flex flex-col justify-between h-full text-left min-h-[300px]">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-black text-slate-300 tracking-wider font-mono">Pipeline Execution Logs</span>
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            </div>
            <div className="bg-slate-950 rounded-lg p-3 h-[240px] overflow-y-auto space-y-1.5 border border-slate-900 font-mono text-[10px] text-slate-400">
              {simulationLogs.map((log, i) => (
                <div key={i} className="leading-relaxed border-b border-slate-900/40 pb-1 last:border-0">
                  <span className="text-slate-600 mr-1">[{new Date().toLocaleTimeString()}]</span>
                  <span className={log.includes('[Success]') ? 'text-emerald-400' : log.includes('[Trigger]') ? 'text-indigo-400' : log.includes('[Finished]') ? 'text-indigo-300 font-bold' : 'text-slate-400'}>
                    {log}
                  </span>
                </div>
              ))}
              {simulationLogs.length === 0 && (
                <div className="text-slate-600 italic text-center py-20 font-sans">
                  Click "Dry Run Pipeline" to watch visual automation execution.
                </div>
              )}
            </div>
          </div>

          <div className="pt-3 border-t border-slate-900/80">
            <p className="text-[10px] text-slate-500 leading-normal font-sans">
              All visual nodes are backed by micro-services mapped via Celery events in production architecture.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProdModule1Workflow;
