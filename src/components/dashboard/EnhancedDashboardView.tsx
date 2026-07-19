/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { useLayoutStore } from '../../stores/layoutStore';
import { useThemeStore } from '../../stores/themeStore';
import { api } from '../../services/api';
import { 
  User, CourseStructure, Book, Order, Invoice, Transaction, 
  RoyaltyStatement, WithdrawalRequest, ServiceRequest, Product 
} from '../../types';
import { 
  Button, Input, Textarea, Select, Checkbox, Dialog, StatsCard, 
  ChartsWrapper, DataTable, Badge, Avatar, LoadingSpinner 
} from '../DesignSystem';
import { 
  Sparkles, Award, Wallet, Bell, Globe, BookOpen, Layers, 
  MessageSquare, Briefcase, Plus, Trash2, Calendar, ShieldCheck, 
  Clock, CheckCircle, Video, Heart, Bookmark, Eye, Download, FileText 
} from 'lucide-react';
import { CourseBuilder } from '../education/CourseBuilder';
import { LiveClassView } from '../education/LiveClassView';
import { CourseReviewDesk } from '../education/CourseReviewDesk';
import { BookEditor } from '../bookstore/BookEditor';
import { PublisherWorkspace } from '../bookstore/PublisherWorkspace';
import { CareerDashboard } from '../career/CareerDashboard';
import { ResumeBuilder } from '../career/ResumeBuilder';
import { JobMarketplace } from '../career/JobMarketplace';
import { InterviewPrep } from '../career/InterviewPrep';
import { RecruiterWorkspace } from '../career/RecruiterWorkspace';

// Teacher Portal Components
import { TeacherDashboard } from '../teacher/TeacherDashboard';
import { CourseManager } from '../teacher/CourseManager';
import { SubjectManager } from '../teacher/SubjectManager';
import { LessonBuilder } from '../teacher/LessonBuilder';
import { AssignmentBuilder } from '../teacher/AssignmentBuilder';
import { QuizBuilder } from '../teacher/QuizBuilder';
import { QuestionBank } from '../teacher/QuestionBank';
import { Attendance } from '../teacher/Attendance';
import { LiveDashboard as LiveClasses } from '../live/LiveDashboard';
import { StudentProgress } from '../teacher/StudentProgress';
import { BatchManager } from '../teacher/BatchManager';
import { TeacherWallet } from '../teacher/TeacherWallet';
import { TeacherCertificates } from '../teacher/TeacherCertificates';
import { TeacherAnalytics } from '../teacher/TeacherAnalytics';
import { TeacherProfile } from '../teacher/TeacherProfile';
import { TeacherSettings } from '../teacher/TeacherSettings';
import { TeacherCalendar } from '../teacher/TeacherCalendar';
import { TeacherNotifications } from '../teacher/TeacherNotifications';
import { TeacherReports } from '../teacher/TeacherReports';

interface EnhancedDashboardViewProps {
  currentUser: any;
  onRefreshWallet: () => void;
}

export const EnhancedDashboardView: React.FC<EnhancedDashboardViewProps> = ({ currentUser, onRefreshWallet }) => {
  const { navigateTo } = useLayoutStore();
  const { login } = useAuthStore();
  const [loading, setLoading] = useState(false);

  // Tab states
  const [activeWorkspaceTab, setActiveWorkspaceTab] = useState<'overview' | 'content' | 'career' | 'capabilities' | 'profile' | 'common'>('overview');
  const [teachingSubTab, setTeachingSubTab] = useState<'analytics' | 'builder' | 'live'>('analytics');
  const [selectedTeacherTab, setSelectedTeacherTab] = useState<string>('dashboard');
  const [adminSubTab, setAdminSubTab] = useState<'moderation' | 'ledger'>('moderation');
  const [careerSubTab, setCareerSubTab] = useState<'dashboard' | 'resume' | 'marketplace' | 'mock'>('dashboard');

  // Dynamic Workspace Data states
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [courses, setCourses] = useState<CourseStructure[]>([]);
  const [services, setServices] = useState<Product[]>([]);

  // Profile Form states
  const [fullName, setFullName] = useState(currentUser?.fullName || '');
  const [avatarUrl, setAvatarUrl] = useState(currentUser?.avatarUrl || '');
  const [bio, setBio] = useState('Senior SaaS Software Engineer and Mathematics enthusiast.');
  const [education, setEducation] = useState([
    { degree: 'M.Tech Computer Science', school: 'IIT Bombay', year: '2022' }
  ]);
  const [experience, setExperience] = useState([
    { role: 'Backend Lead', company: 'BVG Networks', duration: '2 Years' }
  ]);
  const [newDegree, setNewDegree] = useState('');
  const [newSchool, setNewSchool] = useState('');
  const [newYear, setNewYear] = useState('');
  const [newRole, setNewRole] = useState('');
  const [newCompany, setNewCompany] = useState('');
  const [newDuration, setNewDuration] = useState('');

  // Capabilities lists
  const [capabilityApplications, setCapabilityApplications] = useState([
    { id: 'app-1', capabilityCode: 'TEACHING', status: 'APPROVED', notes: 'Academic qualifications audited.' },
    { id: 'app-2', capabilityCode: 'AUTHORING', status: 'PENDING', notes: 'Ebook draft sample review queue.' }
  ]);

  useEffect(() => {
    if (currentUser) {
      setFullName(currentUser.fullName);
      setAvatarUrl(currentUser.avatarUrl || '');
      fetchWorkspaceData();
    }
  }, [currentUser]);

  const fetchWorkspaceData = async () => {
    setLoading(true);
    try {
      const [txRes, ordRes, invRes, bkRes, crRes, svRes] = await Promise.all([
        api.finance.listTransactions(currentUser?.id),
        api.marketplace.listOrders(currentUser?.id),
        api.marketplace.listInvoices(currentUser?.id),
        api.books.list(),
        api.courses.list(),
        api.marketplace.listProducts({ type: 'SERVICE' })
      ]);

      if (txRes.success && txRes.data) setTransactions(txRes.data);
      if (ordRes.success && ordRes.data) setOrders(ordRes.data);
      if (invRes.success && invRes.data) setInvoices(invRes.data);
      if (bkRes.success && bkRes.data) setBooks(bkRes.data);
      if (crRes.success && crRes.data) setCourses(crRes.data);
      if (svRes.success && svRes.data) setServices(svRes.data);
    } catch (err) {
      console.error('Failed to load workspace datasets:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = (e: React.FormEvent) => {
    e.preventDefault();
    alert('Personal information profile nodes updated on memory ledger!');
  };

  const handleAddEducation = () => {
    if (!newDegree || !newSchool || !newYear) return;
    setEducation(prev => [...prev, { degree: newDegree, school: newSchool, year: newYear }]);
    setNewDegree('');
    setNewSchool('');
    setNewYear('');
  };

  const handleAddExperience = () => {
    if (!newRole || !newCompany || !newDuration) return;
    setExperience(prev => [...prev, { role: newRole, company: newCompany, duration: newDuration }]);
    setNewRole('');
    setNewCompany('');
    setNewDuration('');
  };

  const handleApplyCapability = (code: string) => {
    setCapabilityApplications(prev => [
      ...prev,
      { id: `app-${prev.length + 1}`, capabilityCode: code, status: 'PENDING', notes: 'Submitted via capability center.' }
    ]);
    alert(`Capability request for ${code} logged securely.`);
  };

  // Get active capabilities list
  const activeCapabilities = currentUser?.capabilities 
    ? currentUser.capabilities.filter((c: any) => c.status === 'ACTIVE').map((c: any) => c.capabilityCode)
    : (currentUser?.roleId === 'role-super-admin' ? ['ADMIN', 'TEACHING', 'AUTHORING', 'LEARNING', 'SERVICES'] 
       : currentUser?.roleId === 'role-teacher' ? ['TEACHING', 'LEARNING']
       : currentUser?.roleId === 'role-student' ? ['LEARNING'] : []);

  if (loading) {
    return <LoadingSpinner text="Mapping workspace database cells..." />;
  }

  return (
    <div id="bvg-workspace-dashboard" className="flex-grow flex flex-col bg-[#070b19]">
      
      {/* 1. WORKSPACE HEADER */}
      <section className="bg-[#0b1329] border-b border-indigo-950/80 py-10 px-8 text-left">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="flex items-center gap-4">
            <Avatar src={avatarUrl} name={fullName} size="lg" className="border-2 border-indigo-500" />
            <div className="space-y-1.5">
              <h2 className="text-xl font-black text-white">Welcome back, {fullName}!</h2>
              <div className="flex flex-wrap gap-1.5 items-center">
                {activeCapabilities.map((cap: string) => (
                  <Badge key={cap} variant="primary">{cap}</Badge>
                ))}
              </div>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="p-4 bg-slate-900 border border-indigo-950 rounded-2xl flex items-center gap-3">
              <div className="p-2.5 bg-indigo-950 text-indigo-400 rounded-xl"><Wallet size={16} /></div>
              <div>
                <span className="block text-[8px] uppercase font-bold text-slate-500 font-mono">Ledger balance</span>
                <strong className="text-sm font-black text-white font-mono">₹{currentUser?.walletBalance.toLocaleString() || '0'}</strong>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. TABBED VIEW COORDINATORS */}
      <section className="border-b border-indigo-950/40 bg-slate-950/50">
        <div className="max-w-6xl mx-auto px-8 flex gap-6 text-[10px] font-bold uppercase tracking-widest font-mono select-none">
          <button 
            onClick={() => setActiveWorkspaceTab('overview')} 
            className={`py-4 transition border-b-2 cursor-pointer ${activeWorkspaceTab === 'overview' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-500 hover:text-slate-350'}`}
          >
            Overview
          </button>
          <button 
            onClick={() => setActiveWorkspaceTab('content')} 
            className={`py-4 transition border-b-2 cursor-pointer ${activeWorkspaceTab === 'content' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-500 hover:text-slate-350'}`}
          >
            My Content
          </button>
          <button 
            onClick={() => setActiveWorkspaceTab('career')} 
            className={`py-4 transition border-b-2 cursor-pointer ${activeWorkspaceTab === 'career' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-500 hover:text-slate-350'}`}
          >
            Career Galaxy
          </button>
          <button 
            onClick={() => setActiveWorkspaceTab('capabilities')} 
            className={`py-4 transition border-b-2 cursor-pointer ${activeWorkspaceTab === 'capabilities' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-500 hover:text-slate-350'}`}
          >
            Capability Center
          </button>
          <button 
            onClick={() => setActiveWorkspaceTab('profile')} 
            className={`py-4 transition border-b-2 cursor-pointer ${activeWorkspaceTab === 'profile' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-500 hover:text-slate-350'}`}
          >
            Profile Editor
          </button>
          <button 
            onClick={() => setActiveWorkspaceTab('common')} 
            className={`py-4 transition border-b-2 cursor-pointer ${activeWorkspaceTab === 'common' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-500 hover:text-slate-350'}`}
          >
            Common Hub
          </button>
        </div>
      </section>

      {/* 3. DYNAMIC CONTENT RENDERS */}
      <section className="py-12 px-8 max-w-6xl mx-auto w-full text-left">
        
        {/* A. OVERVIEW WORKSPACE TAB */}
        {activeWorkspaceTab === 'overview' && (
          <div className="space-y-10">
            {/* Quick Actions Grid */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Quick Actions</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button onClick={() => navigateTo('/courses')} className="p-4 bg-slate-900 border border-indigo-950 hover:border-indigo-900 rounded-2xl text-left space-y-2 group transition">
                  <div className="p-2.5 bg-indigo-950/60 text-indigo-400 rounded-xl w-fit"><BookOpen size={16} /></div>
                  <h4 className="text-xs font-bold text-white group-hover:text-indigo-300 transition">Continue Learning</h4>
                </button>
                <button onClick={() => navigateTo('/become-teacher')} className="p-4 bg-slate-900 border border-indigo-950 hover:border-indigo-900 rounded-2xl text-left space-y-2 group transition">
                  <div className="p-2.5 bg-indigo-950/60 text-indigo-400 rounded-xl w-fit"><Sparkles size={16} /></div>
                  <h4 className="text-xs font-bold text-white group-hover:text-indigo-300 transition">Create Course</h4>
                </button>
                <button onClick={() => navigateTo('/become-author')} className="p-4 bg-slate-900 border border-indigo-950 hover:border-indigo-900 rounded-2xl text-left space-y-2 group transition">
                  <div className="p-2.5 bg-indigo-950/60 text-indigo-400 rounded-xl w-fit"><Award size={16} /></div>
                  <h4 className="text-xs font-bold text-white group-hover:text-indigo-300 transition">Write Ebook</h4>
                </button>
                <button onClick={() => navigateTo('/portfolio')} className="p-4 bg-slate-900 border border-indigo-950 hover:border-indigo-900 rounded-2xl text-left space-y-2 group transition">
                  <div className="p-2.5 bg-indigo-950/60 text-indigo-400 rounded-xl w-fit"><Layers size={16} /></div>
                  <h4 className="text-xs font-bold text-white group-hover:text-indigo-300 transition">Build Portfolio</h4>
                </button>
              </div>
            </div>

            {/* Statistics Row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <StatsCard label="Courses Enrolled" value="3 Active" change="20% Month" />
              <StatsCard label="Books Purchased" value="2 eBooks" />
              <StatsCard label="Services Active" value="1 Project" change="On Schedule" />
              <StatsCard label="Certificates Earned" value="5 Hashes" isPositive={true} />
            </div>

            {/* Main dashboard columns */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
              {/* Timeline Column */}
              <div className="md:col-span-8 space-y-4">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Activity Timeline</h3>
                <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-6">
                  <div className="flex gap-4">
                    <div className="p-2 bg-indigo-950 text-indigo-400 rounded-full h-fit"><CheckCircle size={14} /></div>
                    <div>
                      <span className="block text-[10px] text-slate-500 font-mono font-bold">10 MINUTES AGO</span>
                      <p className="text-xs text-white leading-relaxed font-semibold mt-0.5">Lesson "Multiplying via Ekadhikena Sutra" completed successfully.</p>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="p-2 bg-indigo-950 text-indigo-400 rounded-full h-fit"><Wallet size={14} /></div>
                    <div>
                      <span className="block text-[10px] text-slate-500 font-mono font-bold">2 HOURS AGO</span>
                      <p className="text-xs text-white leading-relaxed font-semibold mt-0.5">Wallet payouts statement for Ebook June royalties updated.</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recommendations Column */}
              <div className="md:col-span-4 space-y-4">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Recommendations</h3>
                <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4">
                  <div className="flex items-center gap-3 border-b border-indigo-950/45 pb-3">
                    <div className="p-2 bg-indigo-950 text-indigo-400 rounded-lg"><BookOpen size={14} /></div>
                    <div className="text-xs">
                      <strong className="block text-white leading-tight">Advanced Celery tasks in Django</strong>
                      <span className="text-[10px] text-slate-500 font-mono">90% match for you</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-950 text-indigo-400 rounded-lg"><Sparkles size={14} /></div>
                    <div className="text-xs">
                      <strong className="block text-white leading-tight">Vedic mental division guides</strong>
                      <span className="text-[10px] text-slate-500 font-mono">Popular this week</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* B. MY CONTENT TAB (Changes based on active capabilities) */}
        {activeWorkspaceTab === 'content' && (
          <div className="space-y-8">
            <div className="border-b border-indigo-950/30 pb-4 mb-6">
              <h3 className="text-sm font-bold text-white tracking-tight">Active Capabilities Content</h3>
              <p className="text-xs text-slate-400 mt-1">This section adapters dynamically to display tools for your approved capabilities.</p>
            </div>

            {/* Dynamic tabs based on user capabilities */}
            {/* Dynamic tabs based on user capabilities */}
            {activeCapabilities.includes('ADMIN') && (
              <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-6 text-left">
                <h4 className="text-xs font-bold text-rose-450 uppercase tracking-wider flex items-center gap-1.5">
                  <ShieldCheck size={14} /> System Administrator Portal
                </h4>
                <div className="flex gap-2 text-xs font-mono select-none mb-4">
                  <button onClick={() => setAdminSubTab('moderation')} className={`px-3 py-1 rounded-lg border ${adminSubTab === 'moderation' ? 'bg-indigo-650 border-indigo-500 text-white' : 'border-indigo-950 text-slate-500 hover:text-slate-350'}`}>Course Moderation Approvals</button>
                </div>
                {adminSubTab === 'moderation' ? <CourseReviewDesk /> : (
                  <div className="text-xs text-slate-450 italic">System security audits ledger checks.</div>
                )}
              </div>
            )}

            {activeCapabilities.includes('TEACHING') && (
              <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-6 text-left">
                <div className="flex justify-between items-center border-b border-indigo-950/40 pb-4 mb-4 select-none">
                  <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                    <BookOpen size={14} /> Teacher Portal Cockpit
                  </h4>
                  <Badge variant="success">Capability Approved</Badge>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                  {/* Left Workspace Sidebar */}
                  <div className="lg:col-span-3 space-y-6 select-none border-r border-indigo-950/30 pr-2">
                    {[
                      {
                        group: 'Core Cockpit',
                        items: [
                          { id: 'dashboard', label: 'Dashboard' },
                          { id: 'analytics', label: 'Analytics Center' },
                          { id: 'notifications', label: 'Alerts & Messages' },
                          { id: 'reports', label: 'Reports compilation' },
                          { id: 'settings', label: 'Portal Settings' }
                        ]
                      },
                      {
                        group: 'Curriculum Planning',
                        items: [
                          { id: 'course-manager', label: 'Course Manager' },
                          { id: 'subject-manager', label: 'Subject Manager' },
                          { id: 'lesson-builder', label: 'Lesson Builder' },
                          { id: 'question-bank', label: 'Question Bank' },
                          { id: 'quiz-builder', label: 'Quiz Builder' },
                          { id: 'assignment-builder', label: 'Assignment Builder' }
                        ]
                      },
                      {
                        group: 'Operations & Classes',
                        items: [
                          { id: 'live', label: 'Live Broadcasts' },
                          { id: 'attendance', label: 'Attendance logs' },
                          { id: 'batches', label: 'Batch Manager' },
                          { id: 'progress', label: 'Student Progress' },
                          { id: 'calendar', label: 'Agenda Calendar' }
                        ]
                      },
                      {
                        group: 'Wallet & Credentials',
                        items: [
                          { id: 'wallet', label: 'Ledger Wallet' },
                          { id: 'certificates', label: 'Certificates board' },
                          { id: 'profile', label: 'Academic Profile' }
                        ]
                      }
                    ].map((group, gIdx) => (
                      <div key={gIdx} className="space-y-2">
                        <span className="text-[10px] uppercase font-bold text-slate-500 font-mono tracking-widest block pl-2">{group.group}</span>
                        <div className="space-y-1">
                          {group.items.map((tab) => {
                            const isActive = selectedTeacherTab === tab.id;
                            return (
                              <button
                                key={tab.id}
                                onClick={() => setSelectedTeacherTab(tab.id)}
                                className={`w-full text-left py-2 px-3.5 rounded-xl text-xs font-semibold transition ${
                                  isActive
                                    ? 'bg-indigo-600 text-white'
                                    : 'text-slate-450 hover:bg-slate-950/40 hover:text-white'
                                }`}
                              >
                                {tab.label}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Right main workspace workspace */}
                  <div className="lg:col-span-9 bg-[#0b1329] border border-indigo-950/60 p-6 rounded-3xl min-h-[500px]">
                    {(() => {
                      switch (selectedTeacherTab) {
                        case 'dashboard':
                          return <TeacherDashboard />;
                        case 'course-manager':
                          return <CourseManager />;
                        case 'subject-manager':
                          return <SubjectManager />;
                        case 'lesson-builder':
                          return <LessonBuilder />;
                        case 'assignment-builder':
                          return <AssignmentBuilder />;
                        case 'quiz-builder':
                          return <QuizBuilder />;
                        case 'question-bank':
                          return <QuestionBank />;
                        case 'attendance':
                          return <Attendance />;
                        case 'live':
                          return <LiveClasses />;
                        case 'progress':
                          return <StudentProgress />;
                        case 'batches':
                          return <BatchManager />;
                        case 'wallet':
                          return <TeacherWallet />;
                        case 'certificates':
                          return <TeacherCertificates />;
                        case 'analytics':
                          return <TeacherAnalytics />;
                        case 'profile':
                          return <TeacherProfile />;
                        case 'settings':
                          return <TeacherSettings />;
                        case 'calendar':
                          return <TeacherCalendar />;
                        case 'notifications':
                          return <TeacherNotifications />;
                        case 'reports':
                          return <TeacherReports />;
                        default:
                          return <TeacherDashboard />;
                      }
                    })()}
                  </div>
                </div>
              </div>
            )}

            {activeCapabilities.includes('AUTHORING') && (
              <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-6 text-left">
                <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                  <BookOpen size={14} /> Self-Publishing Authoring Suite
                </h4>
                <BookEditor />
              </div>
            )}

            {activeCapabilities.includes('PUBLISHING') && (
              <div className="p-6 bg-[#0b1329] border border-indigo-950 rounded-2xl space-y-6 text-left">
                <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                  <ShieldCheck size={14} /> Publisher Management Console
                </h4>
                <PublisherWorkspace />
              </div>
            )}

            {activeCapabilities.includes('SERVICES') && (
              <div className="p-6 bg-[#0b1329] border border-indigo-950 rounded-2xl space-y-6 text-left">
                <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Briefcase size={14} /> Freelance Agency Operations
                </h4>
                <DataTable 
                  headers={['Client', 'Project Task', 'Milestone Settle', 'Estimated budget']} 
                  rows={[
                    ['Acme Tech', 'Django DB partitions setup', 'IN PROGRESS', '₹75,000'],
                    ['IIT Bombay Co-op', 'Vedic math quizzes setup', 'COMPLETED', '₹35,000']
                  ]}
                />
              </div>
            )}

            {activeCapabilities.length === 0 && (
              <div className="py-12 bg-slate-900/10 border border-dashed border-indigo-950 rounded-2xl text-center text-slate-500 font-mono text-xs italic">
                No advanced creator content dashboards active. Request Teacher or Provider capabilities to unlock options.
              </div>
            )}
          </div>
        )}

        {/* C. CAPABILITY CENTER TAB */}
        {activeWorkspaceTab === 'capabilities' && (
          <div className="space-y-8">
            <div className="border-b border-indigo-950/30 pb-4 mb-6">
              <h3 className="text-sm font-bold text-white tracking-tight">Capability Authorization Center</h3>
              <p className="text-xs text-slate-400 mt-1">Request new capability approvals or deactivate active roles instantly under a single identity.</p>
            </div>

            {/* Current Active List */}
            <div className="space-y-4 text-left">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Active Capabilities</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {activeCapabilities.map((cap: string) => (
                  <div key={cap} className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl flex justify-between items-center">
                    <div>
                      <strong className="block text-xs text-white uppercase tracking-wider">{cap}</strong>
                      <span className="text-[10px] text-emerald-450 font-mono font-bold mt-1 block">STATUS: ACTIVE</span>
                    </div>
                    <Button size="sm" variant="ghost" className="text-rose-500 text-[10px]" onClick={() => alert('Capability deactivation requested.')}>
                      Deactivate
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            {/* Applications List */}
            <div className="space-y-4 text-left pt-6 border-t border-indigo-950/40">
              <div className="flex justify-between items-center">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Application History</h4>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" className="text-[10px]" onClick={() => handleApplyCapability('TEACHING')}>
                    Apply Teacher
                  </Button>
                  <Button size="sm" variant="outline" className="text-[10px]" onClick={() => handleApplyCapability('SERVICES')}>
                    Apply Service Provider
                  </Button>
                </div>
              </div>
              <DataTable 
                headers={['Capability requested', 'Review status', 'Admin notes']} 
                rows={capabilityApplications.map(app => [
                  app.capabilityCode,
                  <Badge variant={app.status === 'APPROVED' ? 'success' : 'warning'}>{app.status}</Badge>,
                  app.notes
                ])}
              />
            </div>
          </div>
        )}

        {/* D. PROFILE EDITOR TAB */}
        {activeWorkspaceTab === 'profile' && (
          <div className="space-y-8 max-w-2xl">
            <div className="border-b border-indigo-950/30 pb-4 mb-6">
              <h3 className="text-sm font-bold text-white tracking-tight">Profile Settings Node</h3>
              <p className="text-xs text-slate-400 mt-1">Configure profile photos, resume education arrays, experience logs, and security credentials.</p>
            </div>

            <form onSubmit={handleUpdateProfile} className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4 shadow-xl">
              <Input label="Full Name" type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
              <Input label="Avatar Image URL" type="url" value={avatarUrl} onChange={(e) => setAvatarUrl(e.target.value)} />
              <Textarea label="Biography" value={bio} onChange={(e) => setBio(e.target.value)} />
              <Button type="submit">
                Save Personal Information
              </Button>
            </form>

            {/* Education lists editor */}
            <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4 text-left">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">Education Credentials</h4>
              <div className="space-y-3">
                {education.map((edu, idx) => (
                  <div key={idx} className="flex justify-between items-center p-3 bg-slate-950 border border-indigo-950 rounded-xl text-xs">
                    <div>
                      <strong className="text-white">{edu.degree}</strong>
                      <span className="block text-[10px] text-slate-500">{edu.school} ({edu.year})</span>
                    </div>
                    <button 
                      onClick={() => setEducation(prev => prev.filter((_, i) => i !== idx))}
                      className="text-rose-500 hover:text-rose-455 transition"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 border-t border-indigo-950/40">
                <Input placeholder="Degree" value={newDegree} onChange={(e) => setNewDegree(e.target.value)} />
                <Input placeholder="University" value={newSchool} onChange={(e) => setNewSchool(e.target.value)} />
                <div className="flex gap-2">
                  <Input placeholder="Year" value={newYear} onChange={(e) => setNewYear(e.target.value)} />
                  <Button size="sm" onClick={handleAddEducation} className="shrink-0"><Plus size={14} /></Button>
                </div>
              </div>
            </div>

            {/* Active Devices / Security Session list */}
            <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4 text-left">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">Active Device Sessions</h4>
              <div className="space-y-3 text-xs">
                <div className="p-3 bg-slate-950 border border-indigo-950 rounded-xl flex justify-between items-center">
                  <div>
                    <strong className="text-white">Windows 11 // Chrome Browser</strong>
                    <span className="block text-[10px] text-emerald-450 font-mono">IP: 192.168.1.1 (CURRENT SESSION)</span>
                  </div>
                </div>
                <div className="p-3 bg-slate-950 border border-indigo-950 rounded-xl flex justify-between items-center text-slate-400">
                  <div>
                    <strong>iPhone 15 // Safari Browser</strong>
                    <span className="block text-[10px] text-slate-500 font-mono">IP: 103.82.90.1 (Logged in July 2026)</span>
                  </div>
                  <Button size="sm" variant="ghost" className="text-rose-500 text-[10px]" onClick={() => alert('Device session revoked.')}>
                    Revoke Device
                  </Button>
                </div>
              </div>
            </div>

          </div>
        )}

        {/* E. COMMON SECTIONS HUB */}
        {activeWorkspaceTab === 'common' && (
          <div className="space-y-8">
            <div className="border-b border-indigo-950/30 pb-4 mb-6">
              <h3 className="text-sm font-bold text-white tracking-tight">Common Academic Vault</h3>
              <p className="text-xs text-slate-400 mt-1">Review bookmarks, download certificates, review purchase invoices, or submit support tickets.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-left">
              {/* Bookmark & Wishlists */}
              <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4">
                <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                  <Bookmark size={14} className="text-indigo-400" /> Bookmarked Topics & Wishlist
                </h4>
                <div className="space-y-2 text-xs">
                  <div className="p-3 bg-slate-950 border border-indigo-950 rounded-xl flex justify-between items-center">
                    <span>Sutra Division Shortcuts (Vedic Math)</span>
                    <button onClick={() => navigateTo('/courses')} className="text-indigo-400 hover:underline">Open</button>
                  </div>
                  <div className="p-3 bg-slate-950 border border-indigo-950 rounded-xl flex justify-between items-center text-slate-400">
                    <span>Double-Entry ledger blueprints (Book)</span>
                    <button onClick={() => navigateTo('/bookstore')} className="text-indigo-400 hover:underline">Preview</button>
                  </div>
                </div>
              </div>

              {/* Purchase invoices history */}
              <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4">
                <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                  <FileText size={14} className="text-indigo-400" /> Purchase History Invoices
                </h4>
                {invoices.length > 0 ? (
                  <div className="space-y-2">
                    {invoices.map((inv, idx) => (
                      <div key={inv.id || idx} className="p-3 bg-slate-950 border border-indigo-950 rounded-xl flex justify-between items-center text-xs">
                        <div>
                          <strong className="text-white">Invoice ID: {inv.invoiceNumber}</strong>
                          <span className="block text-[9px] text-slate-500">Amount paid: ₹{inv.amount.toLocaleString()}</span>
                        </div>
                        <Badge variant="success">PAID</Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4 text-xs text-slate-500 italic">No invoice registers logged.</div>
                )}
              </div>
            </div>
          </div>
        )}

      </section>

    </div>
  );
};

export default EnhancedDashboardView;
