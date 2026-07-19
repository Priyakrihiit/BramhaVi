/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Button, DataTable, Badge } from '../DesignSystem';
import { Award, ShieldCheck, FileText, Check, X } from 'lucide-react';

export const PublisherWorkspace: React.FC = () => {
  const [selectedSubId, setSelectedSubId] = useState<string | null>(null);

  // Review requests queue
  const [submissions, setSubmissions] = useState([
    { id: 'sub-1', title: 'Mental Algebra Deviations shortcuts', author: 'Dr. Vivek Sharma', status: 'PENDING', date: 'Jul 8, 2026' }
  ]);

  const handleAuditApprove = (id: string, decision: 'APPROVED' | 'REJECTED') => {
    setSubmissions(prev => prev.map(s => s.id === id ? { ...s, status: decision } : s));
    setSelectedSubId(null);
    alert(`Publishing submission updated to ${decision} on registry archive.`);
  };

  const selectedSub = submissions.find(s => s.id === selectedSubId);

  // 1. DETAIL PREVIEW
  if (selectedSubId && selectedSub) {
    return (
      <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-6 text-left">
        <button 
          onClick={() => setSelectedSubId(null)}
          className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 hover:text-indigo-300 transition"
        >
          ← Return to Submissions Queue
        </button>

        <div className="border-b border-indigo-950/45 pb-4">
          <Badge variant="warning">{selectedSub.status}</Badge>
          <h3 className="text-base font-black text-white mt-1.5 leading-snug">{selectedSub.title}</h3>
          <span className="text-[10px] text-slate-500 font-mono">AUTHOR: {selectedSub.author.toUpperCase()} // RECEIVED: {selectedSub.date}</span>
        </div>

        <div className="space-y-4">
          <h4 className="text-xs font-bold text-slate-350 uppercase tracking-wider">Publishing Checks</h4>
          <ul className="space-y-2 text-xs text-slate-400">
            <li className="flex items-center gap-2"><Check size={12} className="text-emerald-500" /> ISBN format validated successfully.</li>
            <li className="flex items-center gap-2"><Check size={12} className="text-emerald-500" /> Plagiarism scan check registers healthy.</li>
          </ul>
        </div>

        <div className="flex gap-2 pt-4 border-t border-indigo-950/45">
          <Button size="sm" onClick={() => handleAuditApprove(selectedSub.id, 'APPROVED')} className="flex items-center gap-1 bg-emerald-650 hover:bg-emerald-555 text-[11px] py-2">
            <Check size={12} /> Approve publication
          </Button>
          <Button size="sm" variant="danger" onClick={() => handleAuditApprove(selectedSub.id, 'REJECTED')} className="flex items-center gap-1 text-[11px] py-2">
            <X size={12} /> Reject publication
          </Button>
        </div>
      </div>
    );
  }

  // 2. MAIN QUEUE LIST
  return (
    <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-6 text-left">
      <div>
        <h3 className="text-sm font-bold text-white flex items-center gap-1.5 uppercase tracking-wider">
          <ShieldCheck size={16} className="text-indigo-400" /> Licensed Publisher Desk
        </h3>
        <p className="text-xs text-slate-400 mt-0.5">Approve author manuscripts, audit licensing contracts, and monitor royalty payouts splits.</p>
      </div>

      <div className="space-y-6">
        <div className="space-y-3">
          <strong className="block text-xs text-slate-200">Manuscrips Review Queue</strong>
          <DataTable 
            headers={['Submission Name', 'Author', 'Status', 'Date Logged', 'Review Actions']} 
            rows={submissions.map(s => [
              s.title,
              s.author,
              <Badge variant={s.status === 'APPROVED' ? 'success' : 'warning'}>{s.status}</Badge>,
              s.date,
              <Button size="sm" variant="outline" className="text-[10px] py-1" onClick={() => setSelectedSubId(s.id)}>
                Inspect Manuscript
              </Button>
            ])}
          />
        </div>

        <div className="space-y-3 pt-6 border-t border-indigo-950/40">
          <strong className="block text-xs text-slate-200">Royalty Contracts Registry</strong>
          <DataTable 
            headers={['Author Name', 'Royalty split percentage', 'Status', 'Signing Date']} 
            rows={[
              ['Dr. Vivek Sharma', '70% Author // 30% BVG Publisher', <Badge variant="success">ACTIVE</Badge>, 'Jan 12, 2026']
            ]}
          />
        </div>
      </div>
    </div>
  );
};

export default PublisherWorkspace;
