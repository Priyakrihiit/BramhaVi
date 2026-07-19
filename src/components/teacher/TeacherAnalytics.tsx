/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { TrendingUp, Users, DollarSign, BookOpen, RefreshCw, Award } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { Button } from '../DesignSystem';

interface CourseStat {
  courseTitle: string;
  enrolled: number;
  revenue: number;
  completionRate: number;
}

export const TeacherAnalytics: React.FC = () => {
  const [courseStats, setCourseStats] = useState<CourseStat[]>([]);
  const [loading, setLoading] = useState(false);

  // Growth trajectory historical dataset
  const growthData = [
    { month: 'Jan', enrollments: 40, revenue: 45000 },
    { month: 'Feb', enrollments: 65, revenue: 75000 },
    { month: 'Mar', enrollments: 80, revenue: 95000 },
    { month: 'Apr', enrollments: 120, revenue: 145000 },
    { month: 'May', enrollments: 155, revenue: 195000 },
    { month: 'Jun', enrollments: 210, revenue: 265000 }
  ];

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/teacher/analytics/course-performance/');
      if (res.ok) {
        const data = await res.json();
        setCourseStats(data.results || data);
      } else {
        setCourseStats([
          { courseTitle: 'Quantum Consciousness Mechanics', enrolled: 124, revenue: 312000, completionRate: 85 },
          { courseTitle: 'Vedic Computational Syntax', enrolled: 88, revenue: 220000, completionRate: 72 },
          { courseTitle: 'Double Slit Interference 101', enrolled: 45, revenue: 67500, completionRate: 90 }
        ]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="text-indigo-400" size={20} />
            Academic KPI & Analytics Center
          </h2>
          <p className="text-xs text-slate-400">Recompute system metrics, audit course performance levels, and check revenue streams.</p>
        </div>

        <Button onClick={fetchAnalytics} size="sm" variant="secondary" className="gap-1.5 font-mono text-[10px]">
          <RefreshCw size={11} className={loading ? 'animate-spin' : ''} /> RECOMPUTE LEDGER
        </Button>
      </div>

      {/* Quick Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono select-none">
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-400 uppercase tracking-widest block">Accumulated Students</span>
            <Users className="text-indigo-400" size={14} />
          </div>
          <span className="text-xl font-bold text-white block mt-1">257 Active</span>
        </div>
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-400 uppercase tracking-widest block">Gross Revenue Ledger</span>
            <DollarSign className="text-emerald-400" size={14} />
          </div>
          <span className="text-xl font-bold text-emerald-400 block mt-1">₹599,500</span>
        </div>
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-400 uppercase tracking-widest block">Average Grad Rate</span>
            <Award className="text-purple-400" size={14} />
          </div>
          <span className="text-xl font-bold text-white block mt-1">82.3% Completed</span>
        </div>
      </div>

      {/* Graphs workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 select-none font-mono text-xs">
        {/* Trajectory Growth Area Chart */}
        <div className="bg-slate-900 border border-slate-805 p-5 rounded-2xl">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Enrollment Growth Trajectory</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={growthData} margin={{ top: 5, right: 5, left: -25, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorEnrollments" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="month" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
                <Area type="monotone" dataKey="enrollments" stroke="#6366f1" fillOpacity={1} fill="url(#colorEnrollments)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Revenue streams chart */}
        <div className="bg-slate-900 border border-slate-805 p-5 rounded-2xl">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Course-wise Revenue Generation</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={courseStats} margin={{ top: 5, right: 5, left: -10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="courseTitle" stroke="#64748b" tick={false} />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
                <Bar dataKey="revenue" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Course stats audit list */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden select-none">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950 border-b border-slate-800 text-[10px] uppercase font-bold text-slate-400 font-mono tracking-wider">
            <tr>
              <th className="p-4">Active Course Syllabus Name</th>
              <th className="p-4">Total Students</th>
              <th className="p-4">Completion Rate</th>
              <th className="p-4 text-right">Gross Income Yield</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-850">
            {courseStats.map((cs, idx) => (
              <tr key={idx} className="hover:bg-slate-900/40 transition">
                <td className="p-4 font-bold text-white flex items-center gap-2">
                  <BookOpen className="text-slate-500" size={14} />
                  {cs.courseTitle}
                </td>
                <td className="p-4 font-mono">{cs.enrolled} Enrolled</td>
                <td className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-slate-950 h-1.5 rounded-full overflow-hidden w-24">
                      <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: `${cs.completionRate}%` }} />
                    </div>
                    <span className="font-mono text-[10px] text-slate-400 font-bold">{cs.completionRate}%</span>
                  </div>
                </td>
                <td className="p-4 text-right font-mono font-bold text-emerald-400">₹{cs.revenue.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
