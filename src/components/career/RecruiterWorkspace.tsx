/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Button, Input, Textarea, Select, Badge, DataTable } from '../DesignSystem';
import { ShieldCheck, Plus, Briefcase, Users, Calendar } from 'lucide-react';

export const RecruiterWorkspace: React.FC = () => {
  const [showPostForm, setShowPostForm] = useState(false);
  const [jobTitle, setJobTitle] = useState('');
  const [salary, setSalary] = useState('');

  // Recruiters vacancy state
  const [vacancies, setVacancies] = useState([
    { title: 'Vedic Math mental division teacher', applications: 24, status: 'OPEN' }
  ]);

  const handlePostJob = (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobTitle.trim() || !salary.trim()) return;
    setVacancies(prev => [...prev, { title: jobTitle, applications: 0, status: 'OPEN' }]);
    setJobTitle('');
    setSalary('');
    setShowPostForm(false);
    alert('Vacancy published successfully on career directory.');
  };

  return (
    <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl text-left space-y-6">
      
      {/* Header bar controls */}
      <div className="flex justify-between items-center border-b border-indigo-950/45 pb-4">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-1.5 uppercase tracking-wider">
            <ShieldCheck size={16} className="text-indigo-400 animate-pulse" /> Recruiter Management Console
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">Post new job openings, manage candidates, and schedule technical interviews.</p>
        </div>

        <Button size="sm" onClick={() => setShowPostForm(!showPostForm)} className="flex items-center gap-1.5 text-[11px] py-2 shrink-0">
          <Plus size={14} /> Publish Vacancy
        </Button>
      </div>

      {/* Post job form overlay */}
      {showPostForm && (
        <form onSubmit={handlePostJob} className="p-5 bg-slate-950 border border-indigo-950 rounded-xl space-y-4 animate-slide-down">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block border-b border-indigo-950/30 pb-2 mb-2">Publish Job Details</span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label="Job Title" placeholder="Senior Django dev" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} required />
            <Input label="Salary Range / mo" placeholder="₹80,000 - ₹120,000" value={salary} onChange={(e) => setSalary(e.target.value)} required />
          </div>
          <Textarea label="Job Description & Responsibilities" />
          <div className="flex gap-2 justify-end">
            <Button size="sm" type="submit">Submit Vacancy</Button>
            <Button size="sm" variant="ghost" onClick={() => setShowPostForm(false)}>Cancel</Button>
          </div>
        </form>
      )}

      {/* Stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="p-5 bg-slate-950 border border-indigo-950 rounded-2xl flex items-center gap-3">
          <div className="p-2.5 bg-indigo-950 text-indigo-400 rounded-xl"><Briefcase size={16} /></div>
          <div>
            <span className="block text-[8px] uppercase font-bold text-slate-500 font-mono">Job Openings</span>
            <strong className="text-sm font-black text-white font-mono">{vacancies.length} Active</strong>
          </div>
        </div>
        <div className="p-5 bg-slate-950 border border-indigo-950 rounded-2xl flex items-center gap-3">
          <div className="p-2.5 bg-indigo-950 text-indigo-400 rounded-xl"><Users size={16} /></div>
          <div>
            <span className="block text-[8px] uppercase font-bold text-slate-500 font-mono">Candidates applied</span>
            <strong className="text-sm font-black text-white font-mono">15 Applied</strong>
          </div>
        </div>
      </div>

      {/* Candidate applicants list table */}
      <div className="space-y-3">
        <strong className="block text-xs text-slate-200">Active Job Vacancies Pipeline</strong>
        <DataTable 
          headers={['Vacancy Title', 'Applications Count', 'Pipeline Status']} 
          rows={vacancies.map(v => [
            v.title,
            v.applications,
            <Badge variant="success">{v.status}</Badge>
          ])}
        />
      </div>

      {/* Candidate applications review logs */}
      <div className="space-y-3 pt-6 border-t border-indigo-950/40">
        <strong className="block text-xs text-slate-200">Pending Candidate Applications</strong>
        <DataTable 
          headers={['Candidate Name', 'Applied Role', 'ATS matching percentage', 'Pipeline Status']} 
          rows={[
            ['Priya', 'Vedic Math mental division teacher', <strong className="text-emerald-450 font-mono">92% Match</strong>, <Badge variant="warning">UNDER_REVIEW</Badge>]
          ]}
        />
      </div>

    </div>
  );
};

export default RecruiterWorkspace;
