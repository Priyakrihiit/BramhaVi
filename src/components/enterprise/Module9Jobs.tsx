/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
export interface JobPosting {
  id: string;
  title: string;
  company: string;
  location: string;
  salaryRange: string;
  description: string;
  skillsRequired: string[];
  type: 'FULL_TIME' | 'PART_TIME' | 'CONTRACT';
  postedAt: string;
}

export interface JobApplication {
  id: string;
  jobId: string;
  jobTitle: string;
  candidateId: string;
  candidateName: string;
  resumeUrl: string;
  coverLetter: string;
  status: 'SUBMITTED' | 'SHORTLISTED' | 'REJECTED' | 'APPLIED';
  appliedAt: string;
}

import { Briefcase, MapPin, DollarSign, Plus, FileText, Send, CheckCircle, Search, ExternalLink } from 'lucide-react';

export const Module9Jobs: React.FC = () => {
  const { currentUser } = useAuthStore();
  const [jobs, setJobs] = useState<JobPosting[]>([
    {
      id: 'job-1',
      title: 'Full Stack Django + React Engineer',
      company: 'BrahmaVidya Tech Solutions',
      location: 'Pune (Hybrid)',
      salaryRange: '₹12,00,000 - ₹18,00,000 per annum',
      description: 'Looking for a Senior Django + React Architect capable of building SaaS multi-tenant frameworks, implementing RBAC controls, and optimizing Redis job brokers.',
      skillsRequired: ['Django', 'Django REST Framework', 'React', 'TypeScript', 'PostgreSQL', 'Redis'],
      type: 'FULL_TIME',
      postedAt: '2026-07-05'
    },
    {
      id: 'job-2',
      title: 'Vedic Math Curriculum Designer',
      company: 'BrahmaVidya Academy',
      location: 'Remote',
      salaryRange: '₹8,00,000 - ₹11,00,000 per annum',
      description: 'Join our academic team to build next-generation visual curriculum frameworks using ancient Vedic mathematics sutras.',
      skillsRequired: ['Vedic Math', 'Curriculum Design', 'Instructional Writing'],
      type: 'PART_TIME',
      postedAt: '2026-07-06'
    }
  ]);

  const [applications, setApplications] = useState<JobApplication[]>([
    {
      id: 'app-1',
      jobId: 'job-1',
      jobTitle: 'Full Stack Django + React Engineer',
      candidateId: currentUser?.id || 'user-student',
      candidateName: currentUser?.fullName || 'Rahul Sharma',
      resumeUrl: '#',
      coverLetter: 'I am highly experienced in building enterprise SaaS ecosystems using Django REST Framework and React as specified in BV Galaxy architecture.',
      status: 'SHORTLISTED',
      appliedAt: '2026-07-05'
    }
  ]);

  const [activeTab, setActiveTab] = useState<'FIND' | 'POST' | 'TRACK'>('FIND');

  // Form states
  const [newTitle, setNewTitle] = useState('');
  const [newCompany, setNewCompany] = useState('');
  const [newLoc, setNewLoc] = useState('');
  const [newSal, setNewSal] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newSkills, setNewSkills] = useState('');
  const [newType, setNewType] = useState<'FULL_TIME' | 'PART_TIME' | 'CONTRACT'>('FULL_TIME');

  // Application Modal state
  const [applyingJob, setApplyingJob] = useState<JobPosting | null>(null);
  const [coverText, setCoverText] = useState('');
  const [appSubmittedMsg, setAppSubmittedMsg] = useState(false);

  const handlePostJob = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle || !newCompany || !newDesc) return;

    const newJob: JobPosting = {
      id: `job-${Date.now()}`,
      title: newTitle,
      company: newCompany,
      location: newLoc || 'Remote',
      salaryRange: newSal || 'Competitive Compensation',
      description: newDesc,
      skillsRequired: newSkills.split(',').map(s => s.trim()).filter(Boolean),
      type: newType,
      postedAt: new Date().toISOString().split('T')[0]
    };

    setJobs(prev => [newJob, ...prev]);
    setActiveTab('FIND');
    
    // Reset fields
    setNewTitle('');
    setNewCompany('');
    setNewLoc('');
    setNewSal('');
    setNewDesc('');
    setNewSkills('');
  };

  const handleApplySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!applyingJob) return;

    const newApp: JobApplication = {
      id: `app-${Date.now()}`,
      jobId: applyingJob.id,
      jobTitle: applyingJob.title,
      candidateId: currentUser?.id || 'user',
      candidateName: currentUser?.fullName || 'Rahul Sharma',
      resumeUrl: '#',
      coverLetter: coverText,
      status: 'APPLIED',
      appliedAt: new Date().toISOString().split('T')[0]
    };

    setApplications(prev => [newApp, ...prev]);
    setCoverText('');
    setApplyingJob(null);
    setAppSubmittedMsg(true);
    setTimeout(() => setAppSubmittedMsg(false), 3000);
  };

  return (
    <div id="saas-module-9" className="space-y-6 text-slate-100">
      {/* Banner */}
      <div className="bg-slate-900/60 border border-indigo-950 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 text-left">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Briefcase className="text-indigo-400 w-5 h-5" />
            Job Board & Careers Marketplace
          </h2>
          <p className="text-slate-400 text-xs mt-1">
            Enterprise recruitment pipeline. Find full-time or contract jobs, post vacancy guidelines if you are an employer, and track application vetting workflows (Applied, Shortlisted, Offered).
          </p>
        </div>
        
        {/* Navigation Tabs */}
        <div className="flex bg-slate-950 border border-slate-850 p-1 rounded-xl">
          <button
            onClick={() => setActiveTab('FIND')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${activeTab === 'FIND' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Find Vacancies
          </button>
          <button
            onClick={() => setActiveTab('POST')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${activeTab === 'POST' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Post Job (Employer)
          </button>
          <button
            onClick={() => setActiveTab('TRACK')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1 ${activeTab === 'TRACK' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
          >
            My Applications
            <span className="text-[9px] bg-slate-900 text-slate-300 px-1.5 py-0.5 rounded-full font-mono">{applications.length}</span>
          </button>
        </div>
      </div>

      {appSubmittedMsg && (
        <div className="bg-emerald-950/40 border border-emerald-900 text-emerald-300 p-4 rounded-xl text-xs text-left font-semibold">
          🎉 Success! Your job application and simulated resume dossier have been routed to the hiring manager. Track status in "My Applications".
        </div>
      )}

      {/* Primary Tab Panels */}
      {activeTab === 'FIND' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Vacancy Index */}
          <div className="lg:col-span-8 space-y-4 text-left">
            {jobs.map(job => (
              <div key={job.id} className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 hover:border-indigo-900/50 transition flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-[9px] bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded font-bold uppercase tracking-wider">{job.type}</span>
                      <h3 className="text-base font-black text-white mt-1">{job.title}</h3>
                      <p className="text-xs text-indigo-300 font-semibold">{job.company}</p>
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">Posted: {job.postedAt}</span>
                  </div>

                  <p className="text-slate-400 text-xs mt-3 leading-relaxed">{job.description}</p>

                  {/* Skills tags */}
                  <div className="flex flex-wrap gap-1 mt-4">
                    {job.skillsRequired.map((sk, i) => (
                      <span key={i} className="bg-slate-900 border border-slate-850 text-slate-300 text-[10px] px-2.5 py-0.5 rounded">
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>

                <hr className="border-slate-900 my-4" />

                <div className="flex justify-between items-center text-xs">
                  <div className="flex gap-4 text-slate-500">
                    <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5 text-indigo-400" /> {job.location}</span>
                    <span className="flex items-center gap-1 font-mono text-emerald-400 font-semibold"><DollarSign className="w-3.5 h-3.5" /> {job.salaryRange}</span>
                  </div>
                  
                  <button
                    onClick={() => setApplyingJob(job)}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-4 py-1.5 rounded-lg transition"
                  >
                    Apply Now
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Side Info Cards */}
          <div className="lg:col-span-4 text-left space-y-4">
            <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 space-y-3">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                <Search className="w-4 h-4 text-indigo-400" /> Vetting Guidelines
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Platform applications sync with user portfolio records automatically. For top ratings, verify your Vedic math certifications in the LMS before submitting applications to high-tier agencies.
              </p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'POST' && (
        <div className="max-w-xl mx-auto bg-slate-950/40 border border-slate-900 rounded-2xl p-6 text-left">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-1.5">
            <Plus className="w-4 h-4 text-indigo-400" /> Post a Career Opportunity
          </h3>
          <form onSubmit={handlePostJob} className="space-y-4">
            <div>
              <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Job Title</label>
              <input
                type="text"
                required
                placeholder="e.g. Django Back-End Specialist"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Company Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. BrahmaVidya Labs"
                  value={newCompany}
                  onChange={(e) => setNewCompany(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Job Type</label>
                <select
                  value={newType}
                  onChange={(e) => setNewType(e.target.value as any)}
                  className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="FULL_TIME">Full-time</option>
                  <option value="PART_TIME">Part-time</option>
                  <option value="CONTRACT">Contract</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Location</label>
                <input
                  type="text"
                  placeholder="e.g. Pune, Remote, Hybrid"
                  value={newLoc}
                  onChange={(e) => setNewLoc(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Compensation package</label>
                <input
                  type="text"
                  placeholder="e.g. ₹12,00,000 - ₹15,00,000 /yr"
                  value={newSal}
                  onChange={(e) => setNewSal(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Skills required (comma separated)</label>
              <input
                type="text"
                placeholder="Django, React, Redis, Python"
                value={newSkills}
                onChange={(e) => setNewSkills(e.target.value)}
                className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Role Description</label>
              <textarea
                rows={4}
                required
                placeholder="Outline duties, deliverables, microservice stacks, and daily goals..."
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
                className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 font-sans"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold py-2 rounded-xl transition shadow-md shadow-indigo-950"
            >
              Post Career Vacancy
            </button>
          </form>
        </div>
      )}

      {activeTab === 'TRACK' && (
        <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-indigo-400" />
            Active Application status track
          </h3>
          <div className="space-y-3">
            {applications.map(app => (
              <div key={app.id} className="bg-slate-900/40 border border-slate-850 p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4 font-mono">
                <div>
                  <h4 className="text-xs font-bold text-white font-sans">{app.jobTitle}</h4>
                  <span className="block text-[9px] text-slate-500 mt-1">Applied Date: {app.appliedAt}</span>
                  <p className="text-[10px] text-slate-400 mt-2 font-sans italic">"{app.coverLetter.slice(0, 80)}..."</p>
                </div>

                <div className="text-right">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${app.status === 'APPLIED' ? 'bg-indigo-500/10 text-indigo-400' : app.status === 'SHORTLISTED' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-800 text-slate-400'}`}>
                    {app.status}
                  </span>
                  <div className="text-[9px] text-slate-500 mt-1">Simulated Resume Verified</div>
                </div>
              </div>
            ))}
            {applications.length === 0 && (
              <p className="text-xs text-slate-600">No career application submissions logged yet.</p>
            )}
          </div>
        </div>
      )}

      {/* Applying Dialog modal */}
      {applyingJob && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-slate-950 border border-slate-850 rounded-2xl w-full max-w-md p-6 text-left space-y-4 shadow-2xl">
            <div>
              <span className="text-[9px] bg-indigo-500/10 text-indigo-400 px-2.5 py-0.5 rounded font-black font-mono">APPLICATION DOSSIER</span>
              <h3 className="text-sm font-black text-white mt-1">Apply for: {applyingJob.title}</h3>
              <p className="text-xs text-slate-500 mt-0.5">{applyingJob.company}</p>
            </div>

            <form onSubmit={handleApplySubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Resume</label>
                <div className="bg-slate-900 border border-dashed border-slate-800 p-3 rounded-lg text-center text-xs text-slate-500 font-mono">
                  📂 Simulated_Resume_Academic_Portfolio.pdf auto-attached
                </div>
              </div>

              <div>
                <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Cover Letter summary</label>
                <textarea
                  rows={4}
                  required
                  placeholder="Introduce your skill highlights, certifications, and project records..."
                  value={coverText}
                  onChange={(e) => setCoverText(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500 placeholder-slate-600 font-sans"
                />
              </div>

              <div className="flex justify-end gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => setApplyingJob(null)}
                  className="bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 px-4 py-2 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-5 py-2 rounded-lg transition shadow-md shadow-indigo-950"
                >
                  Submit Application
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Module9Jobs;
