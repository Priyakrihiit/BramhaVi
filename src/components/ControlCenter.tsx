/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { 
  Users, UserCheck, BookOpen, Layers, CheckSquare, Award, Bot, DollarSign, HelpCircle, 
  Settings, Shield, Search, Bell, MessageSquare, Menu, FileText, LayoutGrid, Calendar, 
  Trash2, Edit, Plus, RefreshCw, Activity, ArrowRight, Check, X, Code, Globe, Play, Server, ListCollapse
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import { NavigationMenu, CourseStructure, Certificate, Role, Permission, SystemSettings, User } from '../types';
import DynamicIcon from './DynamicIcon';
import CurriculumView from './CurriculumView';
import SeoDashboard from './SeoDashboard';

interface ControlCenterProps {
  menus: NavigationMenu[];
  onAddMenu: (menu: any) => void;
  onUpdateMenu: (id: string, menu: any) => void;
  onDeleteMenu: (id: string) => void;
  courses: CourseStructure[];
  onAddCourse: (course: any) => void;
  onUpdateCourse: (id: string, course: any) => void;
  onDeleteCourse: (id: string) => void;
  roles: Role[];
  permissions: Permission[];
  onAddRole: (role: any) => void;
  onUpdateRole: (id: string, role: any) => void;
  certificates: Certificate[];
  onIssueCertificate: (cert: any) => void;
  settings: SystemSettings;
  onUpdateSettings: (settings: any) => void;
  activityLogs: Array<{ text: string; time: string }>;
  onRefreshLogs: () => void;
}

export default function ControlCenter({
  menus, onAddMenu, onUpdateMenu, onDeleteMenu,
  courses, onAddCourse, onUpdateCourse, onDeleteCourse,
  roles, permissions, onAddRole, onUpdateRole,
  certificates, onIssueCertificate,
  settings, onUpdateSettings,
  activityLogs, onRefreshLogs
}: ControlCenterProps) {
  // Navigation tabs
  const [activeAdminSubTab, setActiveAdminSubTab] = useState<'dashboard' | 'menus' | 'courses' | 'rbac' | 'certificates' | 'settings' | 'seo'>('dashboard');
  
  // Dashboard Metrics state
  const [stats, setStats] = useState<any>({
    totalStudents: { value: '12,589', change: '+12.5%' },
    totalTeachers: { value: '1,245', change: '+8.3%' },
    totalCourses: { value: '2,358', change: '+15.2%' },
    totalRevenue: { value: '₹34,75,680', change: '+18.7%' },
    activeUsers: { value: '8,975', change: '+11.3%' }
  });

  // Load backend statistics
  useEffect(() => {
    fetch('/api/stats')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setStats(data.data);
        }
      })
      .catch(err => console.error('Stats loading error', err));
  }, []);

  // --- RECHARTS MOCK DATA matching Image 1 graph ---
  const lineChartData = [
    { name: '5 May', students: 2100, teachers: 500, revenue: 1900 },
    { name: '10 May', students: 3800, teachers: 1200, revenue: 2900 },
    { name: '15 May', students: 3000, teachers: 1900, revenue: 4200 },
    { name: '20 May', students: 5100, teachers: 1500, revenue: 3800 },
    { name: '25 May', students: 4800, teachers: 2600, revenue: 5900 },
    { name: '30 May', students: 5800, teachers: 2100, revenue: 5200 },
    { name: '5 Jun', students: 7800, teachers: 3200, revenue: 8400 }
  ];

  const pieChartData = [
    { name: 'Students', value: 9856 },
    { name: 'Teachers', value: 1245 },
    { name: 'Others', value: 1488 }
  ];
  const PIE_COLORS = ['#3b82f6', '#10b981', '#f59e0b'];

  // --- MENU MANAGEMENT STATES ---
  const [newMenuTitle, setNewMenuTitle] = useState('');
  const [newMenuUrl, setNewMenuUrl] = useState('');
  const [newMenuParent, setNewMenuParent] = useState<string>('');
  const [newMenuIcon, setNewMenuIcon] = useState('BookOpen');
  const [newMenuOrder, setNewMenuOrder] = useState('1');

  const handleCreateMenu = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMenuTitle.trim() || !newMenuUrl.trim()) return;
    onAddMenu({
      title: newMenuTitle,
      url: newMenuUrl,
      parentId: newMenuParent || null,
      icon: newMenuIcon,
      displayOrder: parseInt(newMenuOrder) || 1,
      isActive: true
    });
    setNewMenuTitle('');
    setNewMenuUrl('');
    setNewMenuParent('');
  };

  // --- COURSE MANAGEMENT STATES ---
  const [newCourseTitle, setNewCourseTitle] = useState('');
  const [newCourseDesc, setNewCourseDesc] = useState('');
  const [newCourseDiff, setNewCourseDiff] = useState<'Beginner' | 'Intermediate' | 'Advanced'>('Beginner');
  const [newCourseDuration, setNewCourseDuration] = useState('40 Hours');
  const [selectedCourseForSyllabus, setSelectedCourseForSyllabus] = useState<CourseStructure | null>(null);
  const [isGeneratingSyllabus, setIsGeneratingSyllabus] = useState(false);

  const handleCreateCourse = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCourseTitle.trim()) return;
    onAddCourse({
      title: newCourseTitle,
      description: newCourseDesc,
      type: 'COURSE',
      parentId: null,
      metadata: {
        difficulty: newCourseDiff,
        duration: newCourseDuration,
        lessonsCount: 8,
        price: 0
      }
    });
    setNewCourseTitle('');
    setNewCourseDesc('');
  };

  // AI-powered syllabus outline generator call
  const generateAIOutline = async (title: string) => {
    if (!selectedCourseForSyllabus) return;
    setIsGeneratingSyllabus(true);
    try {
      const res = await fetch('/api/ai/generate-curriculum', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
      });
      const data = await res.json();
      if (data.success && Array.isArray(data.data)) {
        // Create generated modules & lessons sequentially
        for (const mod of data.data) {
          const modRes = await fetch('/api/courses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              parentId: selectedCourseForSyllabus.id,
              type: 'MODULE',
              title: mod.title,
              description: mod.description
            })
          });
          const modData = await modRes.json();
          
          if (modData.success && modData.data && Array.isArray(mod.children)) {
            for (const les of mod.children) {
              await fetch('/api/courses', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  parentId: modData.data.id,
                  type: 'LESSON',
                  title: les.title,
                  description: les.description,
                  metadata: { duration: les.duration || '20 Mins', videoUrl: 'https://www.w3schools.com/html/mov_bbb.mp4' }
                })
              });
            }
          }
        }
        onRefreshLogs(); // refresh logs/data
        alert('Vidya AI has successfully outline mapped the full course and added dynamic study modules!');
      } else {
        alert('Could not generate outline.');
      }
    } catch (e) {
      console.error(e);
      alert('Error communicating with Gemini curriculum model.');
    } finally {
      setIsGeneratingSyllabus(false);
    }
  };

  // --- CERTIFICATE STATES ---
  const [recipientName, setRecipientName] = useState('');
  const [certCourseTitle, setCertCourseTitle] = useState('');
  const [certGrade, setCertGrade] = useState('A+');

  const handleIssueCert = (e: React.FormEvent) => {
    e.preventDefault();
    if (!recipientName.trim() || !certCourseTitle.trim()) return;
    onIssueCertificate({
      recipientName,
      courseTitle: certCourseTitle,
      metadata: { grade: certGrade, accreditationCode: `BVG-CR-${Math.floor(Math.random() * 9000 + 1000)}` }
    });
    setRecipientName('');
    setCertCourseTitle('');
    alert('Cryptographic certificate successfully generated and registered on database ledger.');
  };

  // --- RBAC MANAGEMENT STATES ---
  const [newRoleName, setNewRoleName] = useState('');
  const [newRoleDesc, setNewRoleDesc] = useState('');
  const [newRolePerms, setNewRolePerms] = useState<string[]>([]);

  const togglePermission = (code: string) => {
    setNewRolePerms(prev => 
      prev.includes(code) ? prev.filter(c => c !== code) : [...prev, code]
    );
  };

  const handleCreateRole = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRoleName.trim()) return;
    onAddRole({
      name: newRoleName,
      description: newRoleDesc,
      permissions: newRolePerms
    });
    setNewRoleName('');
    setNewRoleDesc('');
    setNewRolePerms([]);
    alert('Custom dynamic security role created.');
  };

  return (
    <div className="min-h-screen bg-[#080d1a] text-[#c3cad9] flex flex-col font-sans">
      
      {/* Dynamic Dashboard content */}
      <div className="flex-1 p-6 md:p-8 space-y-8 max-w-7xl w-full mx-auto">
        
        {/* Main Administrative perspective toggle & Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h2 className="text-2xl font-black text-white tracking-tight flex items-center gap-2">
              Welcome back, Super Admin! 👋
            </h2>
            <p className="text-xs text-slate-400 mt-1">Here's what is happening in BrahmaVidya Galaxy control center today.</p>
          </div>

          {/* Quick tab filters */}
          <div className="flex gap-1.5 p-1 bg-slate-900 border border-slate-800 rounded-xl text-xs overflow-x-auto whitespace-nowrap scrollbar-none">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: LayoutGrid },
              { id: 'menus', label: 'Menu Builder', icon: Menu },
              { id: 'courses', label: 'Course Builder', icon: BookOpen },
              { id: 'rbac', label: 'Security & RBAC', icon: Shield },
              { id: 'certificates', label: 'Certificates', icon: Award },
              { id: 'settings', label: 'Platform Settings', icon: Settings },
              { id: 'seo', label: 'SEO Engine', icon: Globe }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveAdminSubTab(tab.id as any)}
                className={`px-3.5 py-2 rounded-lg font-bold transition-all flex items-center gap-2 ${
                  activeAdminSubTab === tab.id 
                    ? 'bg-indigo-600 text-white shadow-lg' 
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                <tab.icon size={13} />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* --- TAB VIEW 1: MAIN METRIC DASHBOARD --- */}
        {activeAdminSubTab === 'dashboard' && (
          <div className="space-y-8">
            
            {/* Dynamic Metric cards rows */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
              {[
                { label: 'Total Students', value: stats.totalStudents?.value || '12,589', change: stats.totalStudents?.change || '+12.5%', icon: Users, color: 'text-indigo-400 bg-indigo-500/10' },
                { label: 'Total Teachers', value: stats.totalTeachers?.value || '1,245', change: stats.totalTeachers?.change || '+8.3%', icon: UserCheck, color: 'text-emerald-400 bg-emerald-500/10' },
                { label: 'Total Courses', value: stats.totalCourses?.value || '2,358', change: stats.totalCourses?.change || '+15.2%', icon: BookOpen, color: 'text-amber-400 bg-amber-500/10' },
                { label: 'Total Revenue', value: stats.totalRevenue?.value || '₹34,75,680', change: stats.totalRevenue?.change || '+18.7%', icon: DollarSign, color: 'text-rose-400 bg-rose-500/10' },
                { label: 'Active Users', value: stats.activeUsers?.value || '8,975', change: stats.activeUsers?.change || '+11.3%', icon: Activity, color: 'text-teal-400 bg-teal-500/10' }
              ].map((card, i) => (
                <div key={i} className="bg-[#0c1326] border border-slate-800 rounded-2xl p-5 hover:border-indigo-500/30 transition-all flex items-center justify-between">
                  <div className="space-y-1">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold">{card.label}</span>
                    <span className="text-xl font-bold text-white block">{card.value}</span>
                    <span className="text-[11px] text-emerald-400 block font-semibold">{card.change} <span className="text-slate-500 font-normal">from last month</span></span>
                  </div>
                  <div className={`p-3 rounded-xl ${card.color}`}>
                    <card.icon size={20} />
                  </div>
                </div>
              ))}
            </div>

            {/* Graphs Grid Column */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
              
              {/* Platform Overview Graph */}
              <div className="lg:col-span-8 bg-[#0c1326] border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
                <div className="flex justify-between items-center pb-4 border-b border-slate-800/80">
                  <div>
                    <h3 className="font-bold text-white text-sm">Platform Overview</h3>
                    <span className="text-[10px] text-slate-400 mt-0.5 block">Dynamic analytics metrics tracker</span>
                  </div>
                  <span className="text-[11px] bg-indigo-500/15 text-indigo-400 border border-indigo-500/20 px-2.5 py-1 rounded-lg font-bold">
                    This Month
                  </span>
                </div>

                <div className="h-[280px] w-full pt-6">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={lineChartData}>
                      <defs>
                        <linearGradient id="colorStudents" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2}/>
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.2}/>
                          <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                      <YAxis stroke="#64748b" fontSize={11} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
                      <Area type="monotone" dataKey="students" name="Students Active" stroke="#3b82f6" fillOpacity={1} fill="url(#colorStudents)" strokeWidth={2} />
                      <Area type="monotone" dataKey="revenue" name="Commission Revenue (₹)" stroke="#f59e0b" fillOpacity={1} fill="url(#colorRevenue)" strokeWidth={2} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* User Registrations Pie Chart */}
              <div className="lg:col-span-4 bg-[#0c1326] border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
                <div className="flex justify-between items-center pb-4 border-b border-slate-800/80">
                  <h3 className="font-bold text-white text-sm">User Registrations</h3>
                  <span className="text-[10px] text-slate-400 block font-semibold">Active ratios</span>
                </div>

                <div className="h-[220px] w-full flex items-center justify-center pt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieChartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {pieChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div className="flex justify-around items-center pt-2 text-[11px] text-slate-400 border-t border-slate-800/60">
                  <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-blue-500" /> Students (78%)</span>
                  <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-emerald-500" /> Teachers (10%)</span>
                  <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-amber-500" /> Others (12%)</span>
                </div>
              </div>

            </div>

            {/* Quick Actions Panel and System Status Indicators */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
              
              {/* Quick Actions */}
              <div className="lg:col-span-8 bg-[#0c1326] border border-slate-800 rounded-2xl p-6 space-y-4">
                <h3 className="font-bold text-white text-sm">Quick Actions Gateways</h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {[
                    { label: 'Add Course', onClick: () => setActiveAdminSubTab('courses'), icon: BookOpen, col: 'hover:border-indigo-500/40 text-indigo-400' },
                    { label: 'Issue Certificate', onClick: () => setActiveAdminSubTab('certificates'), icon: Award, col: 'hover:border-amber-500/40 text-amber-400' },
                    { label: 'Edit Menus', onClick: () => setActiveAdminSubTab('menus'), icon: Menu, col: 'hover:border-purple-500/40 text-purple-400' },
                    { label: 'Edit RBAC Controls', onClick: () => setActiveAdminSubTab('rbac'), icon: Shield, col: 'hover:border-teal-400/40 text-teal-400' },
                    { label: 'Settings Panel', onClick: () => setActiveAdminSubTab('settings'), icon: Settings, col: 'hover:border-slate-500/40 text-slate-300' },
                    { label: 'Force Audit Refresh', onClick: onRefreshLogs, icon: RefreshCw, col: 'hover:border-rose-500/40 text-rose-400' }
                  ].map((act, idx) => (
                    <button
                      key={idx}
                      onClick={act.onClick}
                      className={`p-4 bg-[#080d1a]/50 border border-slate-800 rounded-xl text-center transition-all flex flex-col items-center justify-center gap-2 group ${act.col}`}
                    >
                      <act.icon size={22} className="group-hover:scale-110 transition-transform" />
                      <span className="text-xs font-bold text-slate-300">{act.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* System Status Indicators */}
              <div className="lg:col-span-4 bg-[#0c1326] border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
                <div>
                  <h3 className="font-bold text-white text-sm">System Health Logs</h3>
                  <p className="text-[10px] text-slate-400 mt-1">Real-time modular node diagnostics.</p>
                </div>

                <div className="space-y-2.5 my-4">
                  {[
                    { service: 'Public Site Portal', status: 'Online', ip: '10.2.0.4', color: 'bg-emerald-500 text-emerald-400' },
                    { service: 'Postgres SQL Database', status: 'Online', ip: '127.0.0.1', color: 'bg-emerald-500 text-emerald-400' },
                    { service: 'Vidya AI Integration', status: 'Online', ip: 'Gemini-3.5', color: 'bg-emerald-500 text-emerald-400' },
                    { service: 'Payment Split Ledger', status: 'Online', ip: 'SSL-V2', color: 'bg-emerald-500 text-emerald-400' },
                    { service: 'SaaS Multi-tier Server', status: 'Online', ip: 'Port 3000', color: 'bg-emerald-500 text-emerald-400' }
                  ].map((srv, idx) => (
                    <div key={idx} className="flex justify-between items-center p-2.5 bg-[#080d1a]/40 border border-slate-800/60 rounded-xl text-xs">
                      <div className="flex items-center gap-2">
                        <span className={`h-1.5 w-1.5 rounded-full ${srv.color} animate-pulse`} />
                        <span className="font-semibold text-slate-200">{srv.service}</span>
                      </div>
                      <span className="text-[10px] text-slate-500">{srv.ip}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Audit Logs activities stream */}
            <div className="bg-[#0c1326] border border-slate-800 rounded-2xl p-6">
              <div className="flex justify-between items-center border-b border-slate-800/80 pb-4">
                <div>
                  <h3 className="font-bold text-white text-sm">Live System Audit Stream</h3>
                  <p className="text-[10px] text-slate-400 mt-0.5">Sub-second administrator telemetry logs</p>
                </div>
                <button 
                  onClick={onRefreshLogs}
                  className="p-1.5 hover:bg-slate-800 text-indigo-400 hover:text-indigo-300 rounded-lg transition-all"
                  title="Force Audit Refresh"
                >
                  <RefreshCw size={15} />
                </button>
              </div>

              <div className="divide-y divide-slate-800/60 max-h-[220px] overflow-y-auto pt-3 pr-2 scrollbar-thin">
                {activityLogs.map((log, i) => (
                  <div key={i} className="py-2.5 flex justify-between items-center text-xs">
                    <span className="text-slate-300 flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-indigo-500" />
                      {log.text}
                    </span>
                    <span className="text-[10px] text-slate-500">{log.time}</span>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* --- TAB VIEW 2: DYNAMIC MENU MANAGER --- */}
        {activeAdminSubTab === 'menus' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* Create Menu Node Form */}
            <form onSubmit={handleCreateMenu} className="lg:col-span-5 bg-[#0c1326] border border-slate-800 rounded-2xl p-6 space-y-4">
              <div>
                <h3 className="font-bold text-white text-sm">Add Navigation Menu Node</h3>
                <p className="text-[11px] text-slate-400 mt-1">Append fully editable menu linkages that render in real-time.</p>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Menu Title</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Practicing Exams"
                    value={newMenuTitle}
                    onChange={(e) => setNewMenuTitle(e.target.value)}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Redirection Path URL</label>
                  <input
                    type="text"
                    required
                    placeholder="/exams/jee"
                    value={newMenuUrl}
                    onChange={(e) => setNewMenuUrl(e.target.value)}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-400 mb-1">Display Order</label>
                    <input
                      type="number"
                      required
                      placeholder="e.g. 5"
                      value={newMenuOrder}
                      onChange={(e) => setNewMenuOrder(e.target.value)}
                      className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white outline-none focus:border-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-semibold text-slate-400 mb-1">Lucide Icon name</label>
                    <select
                      value={newMenuIcon}
                      onChange={(e) => setNewMenuIcon(e.target.value)}
                      className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none focus:border-indigo-500"
                    >
                      <option value="BookOpen">BookOpen (Course)</option>
                      <option value="Layers">Layers (Tutorials)</option>
                      <option value="CheckSquare">CheckSquare (Practice)</option>
                      <option value="Code">Code (Projects)</option>
                      <option value="Award">Award (Certificates)</option>
                      <option value="Users">Users (Community)</option>
                      <option value="Bot">Bot (Vidya AI)</option>
                      <option value="Zap">Zap (Flash)</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Parent Hierarchy node</label>
                  <select
                    value={newMenuParent}
                    onChange={(e) => setNewMenuParent(e.target.value)}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  >
                    <option value="">None (Primary Root menu)</option>
                    {menus.filter(m => m.parentId === null).map(m => (
                      <option key={m.id} value={m.id}>{m.title}</option>
                    ))}
                  </select>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all"
              >
                Create Menu Node
              </button>
            </form>

            {/* Menu Nodes Tree list */}
            <div className="lg:col-span-7 bg-[#0c1326] border border-slate-800 rounded-2xl p-6 space-y-4">
              <div>
                <h3 className="font-bold text-white text-sm">Dynamic Menu Configuration Tree</h3>
                <p className="text-[11px] text-slate-400 mt-1">Review, activate/deactivate, and delete hierarchical nodes.</p>
              </div>

              <div className="space-y-4 max-h-[440px] overflow-y-auto pr-2 scrollbar-thin">
                {menus.filter(m => m.parentId === null).map(parent => {
                  const children = menus.filter(m => m.parentId === parent.id);
                  return (
                    <div key={parent.id} className="border border-slate-800 rounded-xl p-4 bg-[#080d1a]/40 space-y-3">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center gap-2.5">
                          <DynamicIcon name={parent.icon} size={15} className="text-indigo-400" />
                          <span className="font-bold text-white text-xs">{parent.title}</span>
                          <span className="text-[9px] font-mono text-slate-500">[{parent.url}]</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <button
                            type="button"
                            onClick={() => onUpdateMenu(parent.id, { isActive: !parent.isActive })}
                            className={`px-2 py-0.5 text-[9px] font-bold rounded ${
                              parent.isActive ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            }`}
                          >
                            {parent.isActive ? 'Active' : 'Disabled'}
                          </button>
                          <button
                            type="button"
                            onClick={() => onDeleteMenu(parent.id)}
                            className="p-1 hover:bg-rose-500/10 text-slate-500 hover:text-red-400 rounded-lg transition-all"
                          >
                            <Trash2 size={13} />
                          </button>
                        </div>
                      </div>

                      {/* Render Children submenus list */}
                      {children.length > 0 && (
                        <div className="pl-4 border-l border-slate-800 space-y-2">
                          {children.map(child => (
                            <div key={child.id} className="flex justify-between items-center p-2 bg-[#0c1326]/60 border border-slate-800/60 rounded-lg">
                              <span className="text-xs text-slate-300 flex items-center gap-1.5">
                                <DynamicIcon name={child.icon} size={11} className="text-slate-400" />
                                {child.title}
                                <span className="text-[9px] text-slate-500">({child.url})</span>
                              </span>
                              <div className="flex items-center gap-1">
                                <button
                                  type="button"
                                  onClick={() => onUpdateMenu(child.id, { isActive: !child.isActive })}
                                  className={`px-1.5 py-0.5 text-[8px] font-bold rounded ${
                                    child.isActive ? 'text-emerald-400' : 'text-rose-400'
                                  }`}
                                >
                                  {child.isActive ? 'On' : 'Off'}
                                </button>
                                <button
                                  type="button"
                                  onClick={() => onDeleteMenu(child.id)}
                                  className="p-0.5 text-slate-500 hover:text-red-400 rounded transition-all"
                                >
                                  <X size={11} />
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

          </div>
        )}

        {/* --- TAB VIEW 3: DYNAMIC COURSE BUILDER --- */}
        {activeAdminSubTab === 'courses' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* Create course form */}
            <form onSubmit={handleCreateCourse} className="lg:col-span-5 bg-[#0c1326] border border-slate-800 rounded-2xl p-6 space-y-4">
              <div>
                <h3 className="font-bold text-white text-sm">Design Course Curriculum</h3>
                <p className="text-[11px] text-slate-400 mt-1">Register modular study programs without coding any templates.</p>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Course Title</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Organic Chemistry Masterclass"
                    value={newCourseTitle}
                    onChange={(e) => setNewCourseTitle(e.target.value)}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Description summary</label>
                  <textarea
                    required
                    placeholder="Input detailed learning targets..."
                    value={newCourseDesc}
                    onChange={(e) => setNewCourseDesc(e.target.value)}
                    rows={3}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white outline-none focus:border-indigo-500 resize-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-400 mb-1">Target Difficulty</label>
                    <select
                      value={newCourseDiff}
                      onChange={(e) => setNewCourseDiff(e.target.value as any)}
                      className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none focus:border-indigo-500"
                    >
                      <option value="Beginner">Beginner</option>
                      <option value="Intermediate">Intermediate</option>
                      <option value="Advanced">Advanced</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-[11px] font-semibold text-slate-400 mb-1">Estimated Duration</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. 50 Hours"
                      value={newCourseDuration}
                      onChange={(e) => setNewCourseDuration(e.target.value)}
                      className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all"
              >
                Register Course
              </button>
            </form>

            {/* Courses list with expand details */}
            <div className="lg:col-span-7 bg-[#0c1326] border border-slate-800 rounded-2xl p-6 space-y-4">
              <div>
                <h3 className="font-bold text-white text-sm">SaaS Course Registry</h3>
                <p className="text-[11px] text-slate-400 mt-1">Select a course to build dynamic hierarchical modules/lessons or summon Vidya AI outline planner.</p>
              </div>

              <div className="space-y-3.5 max-h-[440px] overflow-y-auto pr-2 scrollbar-thin">
                {courses.filter(c => c.type === 'COURSE').map(course => (
                  <div key={course.id} className="border border-slate-800 rounded-xl p-4 bg-[#080d1a]/40 flex justify-between items-center gap-4 hover:border-slate-700 transition-all">
                    <div>
                      <h4 className="font-bold text-white text-xs">{course.title}</h4>
                      <p className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">{course.description}</p>
                      <div className="flex items-center gap-2 mt-1.5 text-[10px] text-indigo-400">
                        <span className="bg-indigo-500/10 px-1.5 py-0.5 rounded text-indigo-300 font-semibold">{course.metadata?.difficulty}</span>
                        <span>• ⏱️ {course.metadata?.duration}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        type="button"
                        onClick={() => setSelectedCourseForSyllabus(course)}
                        className="px-3 py-1.5 bg-indigo-600/15 text-indigo-400 border border-indigo-500/20 hover:bg-indigo-600 hover:text-white rounded-lg text-xs font-bold transition-all"
                      >
                        Syllabus Builder
                      </button>
                      <button
                        type="button"
                        onClick={() => onDeleteCourse(course.id)}
                        className="p-1.5 bg-rose-500/10 text-rose-400 hover:bg-rose-500 hover:text-white rounded-lg transition-all"
                        title="Delete course"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* --- TAB VIEW 4: SECURITY & RBAC PERMISSIONS --- */}
        {activeAdminSubTab === 'rbac' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* Create Custom Security Role */}
            <form onSubmit={handleCreateRole} className="lg:col-span-5 bg-[#0c1326] border border-slate-800 rounded-2xl p-6 space-y-4">
              <div>
                <h3 className="font-bold text-white text-sm">Add Security Role Profile</h3>
                <p className="text-[11px] text-slate-400 mt-1">Specify authorization permissions across resource endpoints dynamically.</p>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Role Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Inspector, Course Moderator"
                    value={newRoleName}
                    onChange={(e) => setNewRoleName(e.target.value)}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Profile Role Description</label>
                  <input
                    type="text"
                    required
                    placeholder="Outline access bounds..."
                    value={newRoleDesc}
                    onChange={(e) => setNewRoleDesc(e.target.value)}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1.5">Configure Dynamic Permissions</label>
                  <div className="space-y-2 max-h-[160px] overflow-y-auto border border-slate-800/80 p-2 rounded-xl bg-[#080d1a] scrollbar-thin">
                    {permissions.map(perm => (
                      <label key={perm.code} className="flex items-center gap-2.5 text-xs text-slate-300 cursor-pointer hover:text-white">
                        <input
                          type="checkbox"
                          checked={newRolePerms.includes(perm.code)}
                          onChange={() => togglePermission(perm.code)}
                          className="rounded border-slate-800 text-indigo-600 focus:ring-indigo-500 bg-slate-950"
                        />
                        <span>{perm.code} <span className="text-slate-500 text-[10px]">({perm.description})</span></span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all"
              >
                Create Security Role
              </button>
            </form>

            {/* List Roles & Permissions matrix */}
            <div className="lg:col-span-7 bg-[#0c1326] border border-slate-800 rounded-2xl p-6 space-y-4">
              <div>
                <h3 className="font-bold text-white text-sm">Dynamic RBAC Permission Matrix</h3>
                <p className="text-[11px] text-slate-400 mt-1">Review currently assigned permissions across dynamic system categories.</p>
              </div>

              <div className="space-y-4 max-h-[440px] overflow-y-auto pr-2 scrollbar-thin">
                {roles.map(role => (
                  <div key={role.id} className="border border-slate-800 rounded-xl p-4 bg-[#080d1a]/40 space-y-3">
                    <div>
                      <h4 className="font-bold text-white text-xs">{role.name}</h4>
                      <p className="text-[10px] text-slate-400 mt-0.5">{role.description}</p>
                    </div>

                    <div className="flex flex-wrap gap-1.5">
                      {role.permissions.map(code => (
                        <span key={code} className="text-[9px] bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 px-2 py-0.5 rounded-full font-bold">
                          {code}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* --- TAB VIEW 5: CERTIFICATE LEDGER & ISSUER --- */}
        {activeAdminSubTab === 'certificates' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* Certificate Form */}
            <form onSubmit={handleIssueCert} className="lg:col-span-5 bg-[#0c1326] border border-slate-800 rounded-2xl p-6 space-y-4">
              <div>
                <h3 className="font-bold text-white text-sm">Cryptographic Certificate Signer</h3>
                <p className="text-[11px] text-slate-400 mt-1">Digitally sign dynamic credentials with cryptographic hashes.</p>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Recipient Student Full Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Rahul Sharma"
                    value={recipientName}
                    onChange={(e) => setRecipientName(e.target.value)}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Course Accreditation Name</label>
                  <select
                    value={certCourseTitle}
                    onChange={(e) => setCertCourseTitle(e.target.value)}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  >
                    <option value="">Choose Course...</option>
                    {courses.filter(c => c.type === 'COURSE').map(c => (
                      <option key={c.id} value={c.title}>{c.title}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Syllabus Grade</label>
                  <select
                    value={certGrade}
                    onChange={(e) => setCertGrade(e.target.value)}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  >
                    <option value="A+">A+ (Distinction)</option>
                    <option value="A">A (Excellent)</option>
                    <option value="B">B (Satisfactory)</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all"
              >
                Sign & Issue Certificate Ledger
              </button>
            </form>

            {/* List Certificates registry */}
            <div className="lg:col-span-7 bg-[#0c1326] border border-slate-800 rounded-2xl p-6 space-y-4">
              <div>
                <h3 className="font-bold text-white text-sm">Crypto Signed Credentials Ledger</h3>
                <p className="text-[11px] text-slate-400 mt-1">Review registered certificate ledgers with timestamping.</p>
              </div>

              <div className="space-y-3.5 max-h-[440px] overflow-y-auto pr-2 scrollbar-thin">
                {certificates.map(cert => (
                  <div key={cert.id} className="border border-slate-800 rounded-xl p-4 bg-[#080d1a]/40 space-y-3">
                    <div className="flex justify-between items-start gap-4">
                      <div>
                        <h4 className="font-bold text-white text-xs">{cert.recipientName}</h4>
                        <p className="text-[11px] text-indigo-400 mt-0.5">{cert.courseTitle}</p>
                      </div>
                      <span className="px-2 py-0.5 text-[9px] font-bold bg-amber-500/10 text-amber-400 rounded-full">
                        Grade {cert.metadata?.grade}
                      </span>
                    </div>

                    <div className="pt-2 text-[9px] text-slate-500 border-t border-slate-800/60 flex justify-between items-center">
                      <span className="font-mono truncate max-w-[280px]">Hash: <span className="text-slate-400">{cert.certificateHash}</span></span>
                      <span>📅 {new Date(cert.issuedAt).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* --- TAB VIEW 6: SYSTEM METADATA SETTINGS --- */}
        {activeAdminSubTab === 'settings' && (
          <div className="bg-[#0c1326] border border-slate-800 rounded-2xl p-6 max-w-2xl mx-auto space-y-6">
            <div>
              <h3 className="font-bold text-white text-sm">Global Platform Configuration</h3>
              <p className="text-[11px] text-slate-400 mt-1">Manipulate metadata, payment commission splits, and active AI engine parameters.</p>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Platform Name</label>
                  <input
                    type="text"
                    value={settings.platformName}
                    onChange={(e) => onUpdateSettings({ platformName: e.target.value })}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Header Logo text</label>
                  <input
                    type="text"
                    value={settings.logoText}
                    onChange={(e) => onUpdateSettings({ logoText: e.target.value })}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-400 mb-1">Platform Slogan description</label>
                <input
                  type="text"
                  value={settings.platformDescription}
                  onChange={(e) => onUpdateSettings({ platformDescription: e.target.value })}
                  className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Active AI Provider Gateway</label>
                  <select
                    value={settings.activeAIProvider}
                    onChange={(e) => onUpdateSettings({ activeAIProvider: e.target.value as any })}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  >
                    <option value="gemini">Google Gemini (Default)</option>
                    <option value="openai">OpenAI GPT-4</option>
                    <option value="claude">Anthropic Claude 3.5</option>
                    <option value="local">Local DeepSeek VM</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-400 mb-1">Platform Commission rate (%)</label>
                  <input
                    type="number"
                    value={settings.commissionRate}
                    onChange={(e) => onUpdateSettings({ commissionRate: parseInt(e.target.value) || 15 })}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  />
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 flex justify-end">
              <button 
                type="button"
                onClick={() => alert('Platform Settings automatically synched with Express REST server.')}
                className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all"
              >
                Save System Parameters
              </button>
            </div>
          </div>
        )}

        {/* --- TAB VIEW 7: SEO ENGINE MANAGEMENT --- */}
        {activeAdminSubTab === 'seo' && (
          <SeoDashboard />
        )}

      </div>

      {/* Curriculum / Syllabus Builder Drawer for Admin edit */}
      {selectedCourseForSyllabus && (
        <CurriculumView
          course={selectedCourseForSyllabus}
          structures={courses}
          onClose={() => setSelectedCourseForSyllabus(null)}
          isAdmin={true}
          isGenerating={isGeneratingSyllabus}
          onGenerateSyllabus={generateAIOutline}
          onAddNode={async (node) => {
            const res = await fetch('/api/courses', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(node)
            });
            const data = await res.json();
            if (data.success) {
              onRefreshLogs(); // Refetch courses
            }
          }}
          onDeleteNode={async (nodeId) => {
            const res = await fetch(`/api/courses/${nodeId}`, {
              method: 'DELETE'
            });
            const data = await res.json();
            if (data.success) {
              onRefreshLogs();
            }
          }}
        />
      )}

    </div>
  );
}
