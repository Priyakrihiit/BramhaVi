/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Users, Search, ArrowUpRight, Award, TrendingUp, ShieldAlert } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { Badge } from '../DesignSystem';

interface StudentMetric {
  id: string;
  name: string;
  courseTitle: string;
  progress: number;
  avgGrade: string;
  quizzesPassed: number;
  lastActive: string;
}

export const StudentProgress: React.FC = () => {
  const [students] = useState<StudentMetric[]>([
    { id: 's-1', name: 'Aditya Sharma', courseTitle: 'Quantum Consciousness Mechanics', progress: 85, avgGrade: 'A+', quizzesPassed: 4, lastActive: '2h ago' },
    { id: 's-2', name: 'Rohan Verma', courseTitle: 'Vedic Computational Syntax', progress: 70, avgGrade: 'A', quizzesPassed: 3, lastActive: '1d ago' },
    { id: 's-3', name: 'Meera Nair', courseTitle: 'Quantum Consciousness Mechanics', progress: 92, avgGrade: 'A+', quizzesPassed: 5, lastActive: '30m ago' },
    { id: 's-4', name: 'Priya Iyer', courseTitle: 'Vedic Computational Syntax', progress: 45, avgGrade: 'B-', quizzesPassed: 1, lastActive: '3d ago' },
    { id: 's-5', name: 'Sanjay Dutt', courseTitle: 'Quantum Consciousness Mechanics', progress: 60, avgGrade: 'B', quizzesPassed: 2, lastActive: '2d ago' }
  ]);

  const [searchQuery, setSearchQuery] = useState('');

  // Recharts aggregated distribution data
  const chartData = [
    { grade: 'A+', count: 2 },
    { grade: 'A', count: 1 },
    { grade: 'B', count: 1 },
    { grade: 'B-', count: 1 },
    { grade: 'C', count: 0 }
  ];

  const filteredStudents = students.filter(s =>
    s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.courseTitle.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Users className="text-indigo-400" size={20} />
          Student Progress & Analytics
        </h2>
        <p className="text-xs text-slate-400 font-sans">Analyze syllabus completion percentage, average scoring indices, and engagement status of active student cohorts.</p>
      </div>

      {/* Grid containing analytics overview card & Recharts chart */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 select-none">
        {/* Recharts chart */}
        <div className="lg:col-span-8 bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Cohort Grade Distribution</h3>
          <div className="h-48 text-xs font-mono">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 5, right: 5, left: -25, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="grade" stroke="#64748b" />
                <YAxis stroke="#64748b" allowDecimals={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }}
                  cursor={{ fill: 'rgba(99, 102, 241, 0.05)' }}
                />
                <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Aggregate KPI */}
        <div className="lg:col-span-4 bg-slate-900 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between">
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Cohort Wellness</h3>
            <div className="text-2xl font-bold text-white font-mono flex items-center gap-1.5 mt-2">
              70.4%
              <span className="text-xs text-emerald-400 font-semibold flex items-center gap-0.5 font-sans">
                <TrendingUp size={12} /> +2.1%
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Average syllabus progress across enrolled students has grown steadily over the previous 14 calendar days.
            </p>
          </div>

          <div className="border-t border-slate-850/85 pt-3.5 flex justify-between items-center text-[10px] text-slate-500 font-mono">
            <span>Updated: Just Now</span>
            <span className="flex items-center gap-1 text-indigo-400"><Award size={10} /> 12 Certified Graduates</span>
          </div>
        </div>
      </div>

      <div className="relative">
        <Search className="absolute left-3.5 top-3 text-slate-500" size={14} />
        <input
          type="text"
          placeholder="Filter cohort students..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          className="w-full bg-slate-900 border border-indigo-950/80 rounded-xl py-2.5 pl-10 pr-4 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950 border-b border-slate-800 text-[10px] uppercase font-bold text-slate-400 font-mono tracking-wider select-none">
            <tr>
              <th className="p-4">Student</th>
              <th className="p-4">Active Course</th>
              <th className="p-4">Completion Progress</th>
              <th className="p-4">Quiz Drills Passed</th>
              <th className="p-4">Average Grade</th>
              <th className="p-4 text-right">Heartbeat Active</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-850">
            {filteredStudents.map(s => (
              <tr key={s.id} className="hover:bg-slate-900/40 transition">
                <td className="p-4 font-bold text-white flex items-center gap-2.5">
                  <div className="h-7 w-7 rounded-full bg-indigo-950 border border-indigo-500/20 flex items-center justify-center text-[10px] font-bold text-indigo-400 font-mono">
                    {s.name[0]}
                  </div>
                  {s.name}
                </td>
                <td className="p-4">{s.courseTitle}</td>
                <td className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-slate-950 h-1.5 rounded-full overflow-hidden w-24">
                      <div className="bg-indigo-550 h-1.5 rounded-full" style={{ width: `${s.progress}%` }} />
                    </div>
                    <span className="font-mono text-[10px] font-bold text-slate-400">{s.progress}%</span>
                  </div>
                </td>
                <td className="p-4 font-mono font-bold text-slate-400">{s.quizzesPassed} Quizzes</td>
                <td className="p-4">
                  <Badge variant={s.avgGrade.startsWith('A') ? 'success' : 'warning'}>
                    {s.avgGrade}
                  </Badge>
                </td>
                <td className="p-4 text-right font-mono text-slate-500">{s.lastActive}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
