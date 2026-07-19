import React, { useEffect, useState } from 'react';
import { cmsApi } from '../../services/cmsApi';
import { ShieldAlert, CheckCircle, Clock, RotateCw } from 'lucide-react';

export const WorkflowManager: React.FC = () => {
  const [workflows, setWorkflows] = useState<any[]>([]);

  const loadWorkflows = async () => {
    const res = await cmsApi.workflow.list();
    if (res.success && res.data) {
      setWorkflows(res.data);
    }
  };

  useEffect(() => {
    loadWorkflows();
  }, []);

  const handleTransition = async (id: string, targetStatus: string) => {
    const res = await cmsApi.workflow.transition(id, targetStatus, 'Approved via CMS Dashboard Panel');
    if (res.success) {
      loadWorkflows();
    }
  };

  return (
    <div className="p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
      <div>
        <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Editorial Review Workflows</h3>
        <p className="text-xs text-slate-500">Approve editorial state progressions, review logs, and manage assignments</p>
      </div>

      <div className="space-y-3">
        {workflows.length === 0 ? (
          <div className="p-8 text-center bg-slate-950 border border-slate-850 rounded-xl text-slate-500 text-xs italic">
            No workflows in review cycles.
          </div>
        ) : (
          workflows.map(wf => (
            <div key={wf.id} className="p-4 bg-slate-950 border border-slate-800 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <ShieldAlert className="text-amber-400" size={16} />
                <div>
                  <span className="block font-semibold text-slate-200 text-xs">Article: {wf.article_title || 'Untitled Draft'}</span>
                  <span className="block text-[10px] text-slate-500 font-mono">STATUS: {wf.status} | REVIEWER: {wf.assigned_to_name || 'Unassigned'}</span>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleTransition(wf.id, 'approved')}
                  className="px-2.5 py-1 bg-emerald-950 text-emerald-400 border border-emerald-900/50 rounded-lg text-[10px] hover:bg-emerald-900/20 transition flex items-center gap-1"
                >
                  <CheckCircle size={10} /> Approve
                </button>
                <button
                  onClick={() => handleTransition(wf.id, 'changes_requested')}
                  className="px-2.5 py-1 bg-red-950 text-red-400 border border-red-900/50 rounded-lg text-[10px] hover:bg-red-900/20 transition flex items-center gap-1"
                >
                  <Clock size={10} /> Request Changes
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
