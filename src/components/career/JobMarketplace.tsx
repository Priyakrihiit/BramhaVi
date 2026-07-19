/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Button, Select, Badge, DataTable } from '../DesignSystem';
import { Search, Briefcase, Calendar, CheckCircle, Clock, MapPin, X } from 'lucide-react';

export const JobMarketplace: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  // Dynamic vacancies catalog mock state
  const [jobs, setJobs] = useState([
    { id: 'job-1', title: 'Senior Vedic Mathematics Tutor', company: 'Academic Galaxy', salary: '₹60,000 - ₹80,000 / mo', location: 'Remote', type: 'Full-time', skills: ['Vedic Math', 'Teaching'] },
    { id: 'job-2', title: 'Django Backend Engineer', company: 'BVG Tech solutions', salary: '₹120,000 - ₹150,000 / mo', location: 'Hybrid', type: 'Contract', skills: ['Django', 'Celery'] }
  ]);

  const [applications, setApplications] = useState([
    { id: 'app-1', jobTitle: 'SaaS Suite Developer', company: 'Acme LLC', status: 'INTERVIEW', date: 'Jul 8, 2026', interviewTime: 'Jul 15, 3:00 PM' }
  ]);

  const handleApply = (jobTitle: string, company: string) => {
    setApplications(prev => [
      ...prev,
      { id: `app-${prev.length + 1}`, jobTitle, company, status: 'PENDING', date: 'Today', interviewTime: 'TBD' }
    ]);
    setSelectedJobId(null);
    alert(`Application submitted successfully for ${jobTitle} at ${company}.`);
  };

  const selectedJob = jobs.find(j => j.id === selectedJobId);

  // 1. DYNAMIC JOB DETAIL OVERLAY
  if (selectedJobId && selectedJob) {
    return (
      <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-6 text-left animate-zoom-in">
        <button 
          onClick={() => setSelectedJobId(null)}
          className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 hover:text-indigo-300 transition cursor-pointer"
        >
          ← Return to Marketplace Search
        </button>

        <div className="border-b border-indigo-950/45 pb-4">
          <Badge variant="primary">{selectedJob.type}</Badge>
          <h3 className="text-base font-black text-white mt-1.5 leading-snug">{selectedJob.title}</h3>
          <div className="flex gap-4 text-[10px] text-slate-500 font-mono mt-1">
            <span className="flex items-center gap-1"><MapPin size={11} /> {selectedJob.company} ({selectedJob.location})</span>
            <span>•</span>
            <span>{selectedJob.salary}</span>
          </div>
        </div>

        <div className="space-y-3 text-xs">
          <strong className="block text-slate-350 uppercase tracking-widest text-[9px]">Syllabus Requirements</strong>
          <p className="text-slate-400 leading-relaxed">Responsible for developing core written math tutorial modules and conducting live sessions checkouts.</p>
          <div className="flex flex-wrap gap-1.5 pt-2">
            {selectedJob.skills.map(s => <Badge key={s} variant="info">{s}</Badge>)}
          </div>
        </div>

        <div className="flex gap-2 pt-4 border-t border-indigo-950/45">
          <Button size="sm" onClick={() => handleApply(selectedJob.title, selectedJob.company)}>Apply for Role</Button>
          <Button size="sm" variant="outline" onClick={() => setSelectedJobId(null)}>Cancel</Button>
        </div>
      </div>
    );
  }

  // 2. MAIN VACANCIES SEARCH GRID
  return (
    <div className="space-y-8 text-left">
      
      {/* Search Header banner filters */}
      <div className="flex flex-col sm:flex-row gap-3 pt-2">
        <input
          type="text"
          placeholder="Search jobs by title or skills..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 bg-slate-900 border border-indigo-950 rounded-xl py-3 px-4 text-xs text-slate-200 focus:outline-none"
        />
        <Select>
          <option>All Locations</option>
          <option>Remote only</option>
          <option>Hybrid</option>
        </Select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Vacancies lists cards */}
        <div className="lg:col-span-8 space-y-4">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Active Job Vacancies</h4>
          <div className="grid grid-cols-1 gap-4">
            {jobs.map(j => (
              <div key={j.id} className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div className="space-y-1">
                  <span className="text-[9px] font-bold bg-indigo-950 text-indigo-400 font-mono px-2 py-0.5 rounded uppercase tracking-wider">{j.company}</span>
                  <h4 className="text-sm font-bold text-white pt-1 leading-snug">{j.title}</h4>
                  <div className="flex gap-4 text-[10px] text-slate-500 font-mono">
                    <span>{j.location}</span>
                    <span>•</span>
                    <span>{j.salary}</span>
                  </div>
                </div>
                <Button size="sm" onClick={() => setSelectedJobId(j.id)} className="text-[11px] py-2 shrink-0">
                  Inspect Details
                </Button>
              </div>
            ))}
          </div>
        </div>

        {/* Applications tracker timeline */}
        <div className="lg:col-span-4 space-y-4">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Applied Tracking Pipeline</h4>
          <div className="space-y-3">
            {applications.map(app => (
              <div key={app.id} className="p-4 bg-slate-900 border border-indigo-950 rounded-2xl space-y-3">
                <div className="flex justify-between items-start">
                  <div className="text-xs">
                    <strong className="block text-white leading-tight">{app.jobTitle}</strong>
                    <span className="text-[10px] text-slate-500 font-mono">{app.company}</span>
                  </div>
                  <Badge variant={app.status === 'INTERVIEW' ? 'success' : 'warning'}>{app.status}</Badge>
                </div>
                {app.status === 'INTERVIEW' && (
                  <div className="p-2.5 bg-indigo-950/20 border border-indigo-900/40 rounded-xl text-[10px] text-indigo-400 flex items-center gap-1.5">
                    <Calendar size={12} /> Live Interview: {app.interviewTime}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
};

export default JobMarketplace;
