import React, { useState, useEffect } from 'react';
import { Home, Users, BookOpen, Award, Bell, Play, Calendar, DollarSign, ArrowUpRight } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';
import { Button, Badge } from '../DesignSystem';
import { useAuthStore } from '../../stores/authStore';
import { teacherApi } from '../../services/teacherApi';

interface DashboardStats {
  activeStudents: number;
  totalCourses: number;
  pendingGrades: number;
  walletBalance: number;
}

export const TeacherDashboard: React.FC = () => {
  const { currentUser } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats>({
    activeStudents: 257,
    totalCourses: 3,
    pendingGrades: 3,
    walletBalance: 24500
  });

  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      const res = await teacherApi.getDashboardSummary();
      if (res.success && res.data) {
        setStats({
          activeStudents: res.data.metrics.total_students || 0,
          totalCourses: res.data.metrics.total_active_courses || 0,
          pendingGrades: res.data.metrics.pending_evaluations || 0,
          walletBalance: res.data.metrics.mtd_earnings || 0
        });
        setTimeline(res.data.schedule_timeline || []);
      }
      setLoading(false);
    };

    fetchDashboardData();
  }, []);

  // Dynamic analytic data
  const analyticData = [
    { day: 'Mon', active: 110 },
    { day: 'Tue', active: 135 },
    { day: 'Wed', active: 124 },
    { day: 'Thu', active: 145 },
    { day: 'Fri', active: 180 },
    { day: 'Sat', active: 165 },
    { day: 'Sun', active: 192 }
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden bg-gradient-to-tr from-slate-900 via-indigo-950/20 to-slate-900 border border-indigo-500/10 p-6.5 rounded-3xl text-left select-none">
        <div className="relative z-10 space-y-2.5">
          <h2 className="text-xl font-bold text-white leading-tight">Welcome back, {currentUser?.fullName || 'Dr. Priyakrih Shastri'}</h2>
          <p className="text-xs text-indigo-200/80 max-w-xl font-sans leading-relaxed">
            Your quantum consciousness curriculum has {stats.pendingGrades} student submissions waiting to be evaluated. Keep shaping intellectual synapses.
          </p>
        </div>
        <div className="absolute top-0 right-0 h-40 w-40 bg-indigo-500/5 rounded-full blur-2xl -z-0 pointer-events-none"></div>
      </div>

      {/* KPI stats strip */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 font-mono select-none">
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[9px] text-slate-500 uppercase tracking-widest block">Active Scholars</span>
            <span className="text-xl font-bold text-white block">{stats.activeStudents}</span>
          </div>
          <div className="h-9 w-9 rounded-xl bg-indigo-950 border border-indigo-500/15 flex items-center justify-center text-indigo-400">
            <Users size={16} />
          </div>
        </div>

        <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[9px] text-slate-500 uppercase tracking-widest block">Syllabus Courses</span>
            <span className="text-xl font-bold text-white block">{stats.totalCourses}</span>
          </div>
          <div className="h-9 w-9 rounded-xl bg-purple-950 border border-purple-500/15 flex items-center justify-center text-purple-400">
            <BookOpen size={16} />
          </div>
        </div>

        <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[9px] text-slate-500 uppercase tracking-widest block">Pending Grades</span>
            <span className="text-xl font-bold text-amber-400 block">{stats.pendingGrades} Tasks</span>
          </div>
          <div className="h-9 w-9 rounded-xl bg-amber-950/20 border border-amber-500/15 flex items-center justify-center text-amber-400">
            <Award size={16} />
          </div>
        </div>

        <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[9px] text-slate-500 uppercase tracking-widest block">Wallet Balance</span>
            <span className="text-xl font-bold text-emerald-400 block">₹{stats.walletBalance.toLocaleString()}</span>
          </div>
          <div className="h-9 w-9 rounded-xl bg-emerald-950/20 border border-emerald-500/15 flex items-center justify-center text-emerald-400">
            <DollarSign size={16} />
          </div>
        </div>
      </div>

      {/* Main Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left column: Analytics Area Chart */}
        <div className="lg:col-span-8 bg-slate-900 border border-slate-800 p-5 rounded-3xl flex flex-col justify-between space-y-4 select-none">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Weekly Scholar Engagement</h3>
              <p className="text-[10px] text-slate-500 mt-0.5">Evaluates daily active users inside lesson workspace nodes.</p>
            </div>
            <Badge variant="success">Online: 42</Badge>
          </div>

          <div className="h-48 text-xs font-mono">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={analyticData} margin={{ top: 5, right: 5, left: -25, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorActive" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.15}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" stroke="#475569" />
                <YAxis stroke="#475569" />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
                <Area type="monotone" dataKey="active" stroke="#6366f1" fillOpacity={1} fill="url(#colorActive)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right column: Quick Agenda list */}
        <div className="lg:col-span-4 bg-slate-900 border border-slate-800 p-5 rounded-3xl space-y-4 text-left select-none">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Calendar size={13} className="text-indigo-400" /> Agenda Milestones
          </h3>
          
          <div className="space-y-3">
            {loading ? (
              <div className="text-xs text-slate-500 italic py-4 text-center">Loading agenda...</div>
            ) : timeline.length === 0 ? (
              <div className="text-xs text-slate-500 italic py-4 text-center">No upcoming agenda tasks.</div>
            ) : (
              timeline.map((item: any, idx: number) => (
                <div key={idx} className="p-3 bg-slate-950 border border-slate-850 rounded-xl flex items-center justify-between text-xs hover:border-slate-800 transition">
                  <div className="space-y-0.5 min-w-0">
                    <span className="font-bold text-white truncate block">{item.title}</span>
                    <span className="text-[10px] text-slate-500">{item.time} ({item.duration} min)</span>
                  </div>
                  <Badge variant={item.type === 'LIVE' ? 'danger' : 'outline'}>{item.type}</Badge>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
