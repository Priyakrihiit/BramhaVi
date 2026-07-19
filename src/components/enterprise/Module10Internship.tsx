/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { InternshipOpportunity, InternshipDeliverable } from './types';
import { BookOpen, GraduationCap, Clock, Plus, ClipboardCheck, MessageSquare, Award, CheckCircle2 } from 'lucide-react';

export const Module10Internship: React.FC = () => {
  const { currentUser } = useAuthStore();
  const [internships, setInternships] = useState<InternshipOpportunity[]>([
    {
      id: 'intern-1',
      title: 'Vedic Algorithm Optimization Internship',
      department: 'Astrophysics & Mathematics',
      mentorName: 'Dr. Ananya Iyer',
      mentorEmail: 'teacher@brahmavidya.edu',
      durationMonths: 3,
      stipendAmount: 5000,
      targetHours: 80,
      loggedHours: 42,
      status: 'ACTIVE'
    }
  ]);

  const [deliverables, setDeliverables] = useState<InternshipDeliverable[]>([
    {
      id: 'del-1',
      internshipId: 'intern-1',
      weekNumber: 1,
      tasksCompleted: 'Coded speed math division simulations utilizing Paravartya Sutras. Documented memory profiles.',
      hoursLogged: 15,
      feedback: 'Outstanding algorithmic correctness. Time complexity parameters are accurate.',
      status: 'APPROVED',
      createdAt: '2026-06-20'
    },
    {
      id: 'del-2',
      internshipId: 'intern-1',
      weekNumber: 2,
      tasksCompleted: 'Integrated Nikhilam sutras with secondary division remainder matrices. Added Python bench markers.',
      hoursLogged: 12,
      feedback: 'Good work, try benchmarking against floating point operations for larger bounds.',
      status: 'APPROVED',
      createdAt: '2026-06-27'
    },
    {
      id: 'del-3',
      internshipId: 'intern-1',
      weekNumber: 3,
      tasksCompleted: 'Debugging multi-digit subtraction bottlenecks on local Node engines.',
      hoursLogged: 15,
      status: 'PENDING',
      createdAt: '2026-07-04'
    }
  ]);

  const [activeInternId, setActiveInternId] = useState<string>('intern-1');

  // New log submission state
  const [newWeek, setNewWeek] = useState(4);
  const [newTasks, setNewTasks] = useState('');
  const [newHours, setNewHours] = useState(10);
  const [successMsg, setSuccessMsg] = useState(false);

  const activeIntern = internships.find(i => i.id === activeInternId) || internships[0];

  const handleLogDeliverable = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTasks) return;

    const newDel: InternshipDeliverable = {
      id: `del-${Date.now()}`,
      internshipId: activeIntern.id,
      weekNumber: newWeek,
      tasksCompleted: newTasks,
      hoursLogged: newHours,
      status: 'PENDING',
      createdAt: new Date().toISOString().split('T')[0]
    };

    setDeliverables(prev => [newDel, ...prev]);
    
    // Update logged hours count
    setInternships(prev => prev.map(intern => {
      if (intern.id === activeIntern.id) {
        return {
          ...intern,
          loggedHours: intern.loggedHours + newHours
        };
      }
      return intern;
    }));

    setSuccessMsg(true);
    setNewWeek(prev => prev + 1);
    setNewTasks('');
    setTimeout(() => setSuccessMsg(false), 3000);
  };

  const pct = Math.min(100, Math.round((activeIntern.loggedHours / activeIntern.targetHours) * 100));

  return (
    <div id="saas-module-10" className="space-y-6 text-slate-100">
      {/* Page Banner */}
      <div className="bg-slate-900/60 border border-indigo-950 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 text-left">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <GraduationCap className="text-indigo-400 w-5 h-5" />
            Co-op Internships & Weekly Deliverables Log
          </h2>
          <p className="text-slate-400 text-xs mt-1">
            Accelerated real-world learning. Complete structured work deliverables assigned by academic faculty mentors, record your hours, receive formal feedback reviews, and earn certifications.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left pane: Active Internship details & Weekly log submission */}
        <div className="lg:col-span-5 space-y-6 text-left">
          {/* Active Internship Profile Metadata */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 space-y-4">
            <div>
              <span className="text-[9px] bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded font-bold uppercase tracking-wider">{activeIntern.status} INTERNSHIP</span>
              <h3 className="text-base font-black text-white mt-1">{activeIntern.title}</h3>
              <p className="text-xs text-slate-400">{activeIntern.department}</p>
            </div>

            <hr className="border-slate-900" />

            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-500">Academic Mentor:</span>
                <span className="font-bold text-white">{activeIntern.mentorName} ({activeIntern.mentorEmail})</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Stipend Amount:</span>
                <span className="font-bold text-emerald-400 font-mono">₹{activeIntern.stipendAmount.toLocaleString()} /mo</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Duration Period:</span>
                <span className="font-bold text-white">{activeIntern.durationMonths} Months</span>
              </div>
            </div>

            <hr className="border-slate-900" />

            {/* Certification Hour Progress Gauge */}
            <div className="space-y-1.5 font-mono text-xs">
              <div className="flex justify-between items-center text-slate-300">
                <span className="font-sans font-bold flex items-center gap-1"><Clock className="w-3.5 h-3.5 text-indigo-400" /> Hourly Progress</span>
                <span className="font-bold text-indigo-400">{activeIntern.loggedHours} / {activeIntern.targetHours} Hrs ({pct}%)</span>
              </div>
              <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                <div style={{ width: `${pct}%` }} className="h-full bg-indigo-500 transition-all duration-500"></div>
              </div>
              {pct >= 100 ? (
                <span className="text-[10px] text-emerald-400 font-bold flex items-center gap-1 pt-1 font-sans">
                  <Award className="w-4 h-4" /> Goal Met! Vedic Math Dev Intern Certificate claim enabled.
                </span>
              ) : (
                <span className="text-[9px] text-slate-500 block pt-0.5">Need {activeIntern.targetHours - activeIntern.loggedHours} more approved hours to claim completion credentials.</span>
              )}
            </div>
          </div>

          {/* Log Deliverable Form */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 space-y-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Plus className="w-4 h-4 text-indigo-400" /> Record Weekly deliverables Log
            </h3>
            {successMsg && (
              <span className="text-[11px] text-emerald-400 font-semibold block">
                Deliverable log registered. Awaiting mentor evaluation feedback.
              </span>
            )}
            <form onSubmit={handleLogDeliverable} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Week Number</label>
                  <input
                    type="number"
                    required
                    min={1}
                    value={newWeek}
                    onChange={(e) => setNewWeek(parseInt(e.target.value))}
                    className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Hours Spent</label>
                  <input
                    type="number"
                    required
                    min={1}
                    value={newHours}
                    onChange={(e) => setNewHours(parseInt(e.target.value))}
                    className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Tasks Completed Description</label>
                <textarea
                  rows={4}
                  required
                  placeholder="Outline the mathematical algorithms, code profiles, or visual syllabus blueprints designed this week..."
                  value={newTasks}
                  onChange={(e) => setNewTasks(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none placeholder-slate-600 font-sans"
                />
              </div>

              <button
                type="submit"
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold py-2 rounded-xl transition shadow-md shadow-indigo-950 flex items-center justify-center gap-1.5"
              >
                <Plus className="w-3.5 h-3.5" /> Append Internship Log
              </button>
            </form>
          </div>
        </div>

        {/* Right pane: Approved deliverables ledger history */}
        <div className="lg:col-span-7 space-y-4 text-left">
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-1.5">
              <ClipboardCheck className="w-4 h-4 text-indigo-400" />
              Weekly Evaluation Logs Ledger
            </h3>

            <div className="space-y-3">
              {deliverables.map(del => (
                <div key={del.id} className="bg-slate-900/40 border border-slate-850 p-4 rounded-xl space-y-3">
                  <div className="flex justify-between items-start">
                    <span className="text-xs font-bold text-white">Week {del.weekNumber} Deliverables</span>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] bg-slate-950 text-indigo-400 px-2 py-0.5 rounded font-mono font-bold">{del.hoursLogged} Hours logged</span>
                      <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full ${del.status === 'APPROVED' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'}`}>
                        {del.status}
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed font-sans">{del.tasksCompleted}</p>

                  {/* Mentor Feedback section */}
                  {del.feedback ? (
                    <div className="p-2.5 bg-black/20 border-l-2 border-indigo-500 rounded-r-lg space-y-1">
                      <span className="text-[9px] text-indigo-400 uppercase font-black font-mono flex items-center gap-1"><MessageSquare className="w-3 h-3" /> Mentor feedback</span>
                      <p className="text-[11px] text-slate-400 leading-relaxed font-sans">"{del.feedback}"</p>
                    </div>
                  ) : (
                    <div className="text-[10px] text-slate-500 italic font-mono">
                      ⏳ Pending faculty review.
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Module10Internship;
