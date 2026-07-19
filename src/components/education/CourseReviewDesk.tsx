/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Button, Input, Textarea, Badge, DataTable } from '../DesignSystem';
import { ShieldCheck, MessageSquare, Check, X, AlertCircle } from 'lucide-react';

export const CourseReviewDesk: React.FC = () => {
  const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null);
  
  // Pending review courses mock state
  const [courses, setCourses] = useState([
    { id: '1', title: 'Mental Divisibility Rules via Vedic Math', instructor: 'Dr. Vivek Sharma', status: 'PENDING', date: 'Jul 8, 2026' },
    { id: '2', title: 'React Performance Benchmarks', instructor: 'Rahul Sharma', status: 'NEEDS_CHANGES', date: 'Jul 5, 2026' }
  ]);

  const [reviewComment, setReviewComment] = useState('');

  const handleUpdateStatus = (id: string, newStatus: string) => {
    setCourses(prev => prev.map(c => c.id === id ? { ...c, status: newStatus } : c));
    setSelectedCourseId(null);
    setReviewComment('');
    alert(`Course audit status updated to ${newStatus} on directory ledger.`);
  };

  const selectedCourse = courses.find(c => c.id === selectedCourseId);

  // 1. DETAIL REVIEW DRAWER/CARD
  if (selectedCourseId && selectedCourse) {
    return (
      <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-6 text-left">
        <button 
          onClick={() => setSelectedCourseId(null)}
          className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 hover:text-indigo-300 transition"
        >
          ← Return to Review Queue
        </button>

        <div className="border-b border-indigo-950/45 pb-4">
          <Badge variant={selectedCourse.status === 'PENDING' ? 'warning' : 'error'}>{selectedCourse.status}</Badge>
          <h3 className="text-base font-black text-white mt-1.5 leading-snug">{selectedCourse.title}</h3>
          <span className="text-[10px] text-slate-500 font-mono">SUBMITTED BY: {selectedCourse.instructor.toUpperCase()} // RECEIVED: {selectedCourse.date}</span>
        </div>

        <div className="space-y-4">
          <h4 className="text-xs font-bold text-slate-350 uppercase tracking-wider">Audit Checkpoints</h4>
          <ul className="space-y-2 text-xs text-slate-400">
            <li className="flex items-center gap-2"><Check size={12} className="text-emerald-500" /> Syllabus hierarchy matches schema guidelines.</li>
            <li className="flex items-center gap-2"><Check size={12} className="text-emerald-500" /> Resource download blueprints check passes security check.</li>
          </ul>
        </div>

        {/* Audit actions forms */}
        <div className="space-y-4 pt-4 border-t border-indigo-950/45">
          <Textarea 
            label="Audit Notes & Recommendations Feedback" 
            placeholder="Write detailed recommendations or improvement lists for the instructor..." 
            value={reviewComment}
            onChange={(e) => setReviewComment(e.target.value)}
          />
          <div className="flex gap-2">
            <Button size="sm" onClick={() => handleUpdateStatus(selectedCourse.id, 'APPROVED')} className="flex items-center gap-1.5 bg-emerald-650 hover:bg-emerald-550 border-emerald-500/20 text-[11px] py-2">
              <Check size={13} /> Approve course
            </Button>
            <Button size="sm" variant="warning" onClick={() => handleUpdateStatus(selectedCourse.id, 'NEEDS_CHANGES')} className="flex items-center gap-1.5 text-[11px] py-2">
              <AlertCircle size={13} /> Request adjustments
            </Button>
            <Button size="sm" variant="danger" onClick={() => handleUpdateStatus(selectedCourse.id, 'REJECTED')} className="flex items-center gap-1.5 text-[11px] py-2">
              <X size={13} /> Reject submission
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // 2. AUDIT QUEUE TABLE LIST
  return (
    <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-6 text-left">
      <div>
        <h3 className="text-sm font-bold text-white flex items-center gap-1.5 uppercase tracking-wider">
          <ShieldCheck size={16} className="text-indigo-400" /> Academic Moderation Desk
        </h3>
        <p className="text-xs text-slate-400 mt-0.5">Audit pending program designs, course modules, teacher applications, and ledger certificate requests.</p>
      </div>

      <DataTable 
        headers={['Program Title', 'Author Teacher', 'Status', 'Logged Date', 'Audit Actions']} 
        rows={courses.map(c => [
          c.title,
          c.instructor,
          <Badge variant={c.status === 'PENDING' ? 'warning' : 'error'}>{c.status}</Badge>,
          c.date,
          <Button size="sm" variant="outline" className="text-[10px] py-1" onClick={() => setSelectedCourseId(c.id)}>
            Inspect Outlines
          </Button>
        ])}
      />
    </div>
  );
};

export default CourseReviewDesk;
