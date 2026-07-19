/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { BarChart4, TrendingUp, Users, BookOpen, CreditCard, Sparkles, PieChartIcon } from 'lucide-react';

const ENROLLMENT_DATA = [
  { course: 'Vedic Math Basic', students: 1250, teachers: 15 },
  { course: 'Modular Algebra', students: 890, teachers: 10 },
  { course: 'SaaS Microservices', students: 1450, teachers: 22 },
  { course: 'Vedic Geometry', students: 620, teachers: 8 },
  { course: 'React & Tailwind UI', students: 1020, teachers: 14 }
];

const PLAN_SHARE_DATA = [
  { name: 'FREE Tier', value: 1400, color: '#475569' },
  { name: 'PREMIUM', value: 850, color: '#6366f1' },
  { name: 'PROFESSIONAL', value: 510, color: '#10b981' },
  { name: 'BUSINESS', value: 240, color: '#f59e0b' },
  { name: 'ENTERPRISE', value: 110, color: '#ec4899' },
  { name: 'INSTITUTION', value: 45, color: '#ef4444' }
];

export const Module13Analytics: React.FC = () => {
  const [segment, setSegment] = useState<'ADMIN_OVERVIEW' | 'STUDENT_STATS'>('ADMIN_OVERVIEW');

  return (
    <div id="saas-module-13" className="space-y-6 text-slate-100">
      {/* Page Header */}
      <div className="bg-slate-900/60 border border-indigo-950 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 text-left">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <BarChart4 className="text-indigo-400 w-5 h-5" />
            SaaS Metrics & Academic Learning Analytics
          </h2>
          <p className="text-slate-400 text-xs mt-1">
            Data insights workstation. Aggregates multi-tenant SaaS subscription splits, real-time class enrollment vectors, faculty distribution coefficients, and student learning curve histories.
          </p>
        </div>

        {/* Segment selector */}
        <div className="flex bg-slate-950 border border-slate-850 p-1 rounded-xl">
          <button
            onClick={() => setSegment('ADMIN_OVERVIEW')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${segment === 'ADMIN_OVERVIEW' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
          >
            SaaS Admin Dashboard
          </button>
          <button
            onClick={() => setSegment('STUDENT_STATS')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${segment === 'STUDENT_STATS' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
          >
            My Learning Curves
          </button>
        </div>
      </div>

      {segment === 'ADMIN_OVERVIEW' ? (
        <div className="space-y-6">
          {/* KPI deck */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-left">
            <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-4">
              <span className="text-slate-500 text-[10px] uppercase font-bold">Total Platform Members</span>
              <span className="block text-xl font-black text-white font-mono mt-2">142,850</span>
              <span className="block text-[9px] text-emerald-400 mt-1 font-bold">+12% Monthly Growth</span>
            </div>
            <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-4">
              <span className="text-slate-500 text-[10px] uppercase font-bold">Active Subscriptions</span>
              <span className="block text-xl font-black text-indigo-400 font-mono mt-2">3,155</span>
              <span className="block text-[9px] text-slate-500 mt-1">Paying Recurring Users</span>
            </div>
            <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-4">
              <span className="text-slate-500 text-[10px] uppercase font-bold">MRR (SaaS Licenses)</span>
              <span className="block text-xl font-black text-emerald-400 font-mono mt-2">₹18,45,200</span>
              <span className="block text-[9px] text-emerald-400 mt-1 font-bold">+5.4% MRR Expansion</span>
            </div>
            <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-4">
              <span className="text-slate-500 text-[10px] uppercase font-bold">Average Course Score</span>
              <span className="block text-xl font-black text-amber-400 font-mono mt-2">84.2%</span>
              <span className="block text-[9px] text-slate-500 mt-1">Verified LMS Quizzes</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Enrollment trends (Bar chart) */}
            <div className="lg:col-span-7 bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left flex flex-col justify-between">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-1.5">
                <TrendingUp className="w-4 h-4 text-indigo-400" />
                Enrollment Distribution Across Courses
              </h3>
              <div className="h-64 mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={ENROLLMENT_DATA}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="course" stroke="#475569" fontSize={11} tickLine={false} />
                    <YAxis stroke="#475569" fontSize={11} tickLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px' }} />
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                    <Bar dataKey="students" name="Students Enrolled" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="teachers" name="Assigned Teachers" fill="#10b981" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Plan Subscription Share (Pie Chart) */}
            <div className="lg:col-span-5 bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left flex flex-col justify-between">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-1.5">
                <PieChartIcon className="w-4 h-4 text-indigo-400" />
                Active SaaS subscription shares
              </h3>
              <div className="h-64 mt-2 flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={PLAN_SHARE_DATA}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {PLAN_SHARE_DATA.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px' }} />
                    <Legend wrapperStyle={{ fontSize: 10 }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-6 text-left space-y-6">
          <div className="flex justify-between items-center border-b border-slate-900 pb-4">
            <div>
              <span className="text-[9px] bg-indigo-500/10 text-indigo-400 px-2.5 py-0.5 rounded font-black font-mono">LEARNING COGNITION CARD</span>
              <h3 className="text-base font-black text-white mt-1">Rahul Sharma - Scholar Dossier</h3>
              <p className="text-xs text-slate-500">Student ID: user-student • Vedic Math Circle</p>
            </div>
            
            <div className="bg-slate-900 border border-slate-800 p-2.5 rounded-xl text-center">
              <span className="block text-slate-500 text-[8px] uppercase font-bold">Course Completion Rate</span>
              <span className="text-base font-black text-emerald-400 font-mono">88.4%</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 font-mono text-xs">
            <div className="bg-slate-900/40 border border-slate-850 p-4 rounded-xl space-y-2">
              <span className="text-[10px] text-indigo-400 font-bold uppercase tracking-wider font-sans block">Completed Deliverables</span>
              <span className="text-2xl font-black text-white font-mono">42 / 80 Hrs</span>
              <p className="text-[10px] text-slate-400 font-sans">Vedic math division internship</p>
            </div>

            <div className="bg-slate-900/40 border border-slate-850 p-4 rounded-xl space-y-2">
              <span className="text-[10px] text-indigo-400 font-bold uppercase tracking-wider font-sans block">Average Quiz Score</span>
              <span className="text-2xl font-black text-white font-mono">94.5%</span>
              <p className="text-[10px] text-slate-400 font-sans">Nikhilam & Paravartya checks</p>
            </div>

            <div className="bg-slate-900/40 border border-slate-850 p-4 rounded-xl space-y-2">
              <span className="text-[10px] text-indigo-400 font-bold uppercase tracking-wider font-sans block">Reputation Points</span>
              <span className="text-2xl font-black text-emerald-400 font-mono">120 pts</span>
              <p className="text-[10px] text-slate-400 font-sans">Peer solutions marked solved</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Module13Analytics;
