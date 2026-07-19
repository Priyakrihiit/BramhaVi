import React, { useEffect, useState } from 'react';
import { cmsApi } from '../../services/cmsApi';
import { History, RotateCcw } from 'lucide-react';

export const RevisionHistory: React.FC = () => {
  const [revisions, setRevisions] = useState<any[]>([]);

  const loadRevisions = async () => {
    const res = await cmsApi.revisions.list();
    if (res.success && res.data) {
      setRevisions(res.data);
    }
  };

  useEffect(() => {
    loadRevisions();
  }, []);

  const handleRollback = async (id: string) => {
    const res = await cmsApi.revisions.rollback(id);
    if (res.success) {
      alert('Content rolled back successfully!');
      loadRevisions();
    }
  };

  return (
    <div className="p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
      <div>
        <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Editorial Revisions History</h3>
        <p className="text-xs text-slate-500">Track and revert pages, articles, or blog changes back to clean snapshots</p>
      </div>

      <div className="space-y-3">
        {revisions.length === 0 ? (
          <div className="p-8 text-center bg-slate-950 border border-slate-850 rounded-xl text-slate-500 text-xs italic">
            No revisions indexed yet. Revisions auto-build on every article update.
          </div>
        ) : (
          revisions.map(rev => (
            <div key={rev.id} className="p-4 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between">
              <div className="flex items-center gap-3">
                <History className="text-indigo-400" size={16} />
                <div>
                  <span className="block font-semibold text-slate-200 text-xs">{rev.change_summary || 'Manual Save Point'}</span>
                  <span className="block text-[10px] text-slate-500 font-mono">MODEL: {rev.content_type} | VERSION: {rev.version_number} | BY: {rev.author_name || 'System'}</span>
                </div>
              </div>
              <button
                onClick={() => handleRollback(rev.id)}
                className="px-2.5 py-1 bg-indigo-950 text-indigo-400 border border-indigo-900/50 rounded-lg text-[10px] hover:bg-indigo-900/20 transition flex items-center gap-1"
              >
                <RotateCcw size={10} /> Rollback
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
