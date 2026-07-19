/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { 
  BookOpen, Layers, CheckSquare, Code, Award, Users, Bot, Search, ArrowRight, Sparkles, 
  ChevronRight, Calendar, User, Zap, Star, ShieldCheck, HelpCircle, Loader2, Play, BookOpenCheck
} from 'lucide-react';
import { NavigationMenu, CourseStructure, Certificate } from '../types';
import DynamicIcon from './DynamicIcon';
import CurriculumView from './CurriculumView';
import QuizPractice from './QuizPractice';
import CertificateVerifier from './CertificateVerifier';
import ExamArena from './ExamArena';

interface StudentPortalProps {
  menus: NavigationMenu[];
  courses: CourseStructure[];
  onSelectCourse: (course: CourseStructure) => void;
  selectedCourse: CourseStructure | null;
  structures: CourseStructure[];
}

export default function StudentPortal({ 
  menus, 
  courses, 
  onSelectCourse, 
  selectedCourse,
  structures 
}: StudentPortalProps) {
  // Navigation state
  const [activeTab, setActiveTab] = useState('courses');
  const [activeExamFilter, setActiveExamFilter] = useState<string | null>(null);
  
  // Quiz states
  const [showPractice, setShowPractice] = useState(false);
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');

  // Chat with Vidya states
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ sender: 'user' | 'vidya'; text: string }>>([
    { sender: 'vidya', text: "👋 Namaste! I'm **Vidya**, your BrahmaVidya intelligent guide. I can explain any concept, write custom syllabus outlines, test your knowledge with interactive quizzes, or resolve study blockages instantly. What shall we study today?" }
  ]);
  const [isChatting, setIsChatting] = useState(false);

  const [exams, setExams] = useState<any[]>([]);
  const [badges, setBadges] = useState<any[]>([]);
  const [activeExamForArena, setActiveExamForArena] = useState<any>(null);

  const fetchExamsAndBadges = async () => {
    try {
      const res = await fetch('/api/exams/');
      if (res.ok) {
        const data = await res.json();
        setExams(data.results || data);
      }
      const bRes = await fetch('/api/lms/user-badges/');
      if (bRes.ok) {
        const data = await bRes.json();
        setBadges(data.results || data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchExamsAndBadges();
  }, []);

  // Filter primary menus
  const primaryMenus = menus.filter(m => m.parentId === null && m.isActive);
  const subMenus = menus.filter(m => m.parentId !== null && m.isActive);

  // Handle send message to Vidya AI
  const handleSendChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;

    const userMsg = chatMessage;
    setChatHistory(prev => [...prev, { sender: 'user', text: userMsg }]);
    setChatMessage('');
    setIsChatting(true);

    try {
      const res = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
      });
      const data = await res.json();
      if (data.success) {
        setChatHistory(prev => [...prev, { sender: 'vidya', text: data.text }]);
      } else {
        setChatHistory(prev => [...prev, { sender: 'vidya', text: 'Sorry, I encountered a connection issue. Please make sure your server is online.' }]);
      }
    } catch (err) {
      console.error(err);
      setChatHistory(prev => [...prev, { sender: 'vidya', text: 'Error executing Gemini compilation.' }]);
    } finally {
      setIsChatting(false);
    }
  };

  // Filter courses based on search & exam tab selection
  const filteredCourses = courses.filter(c => {
    const matchesSearch = c.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          c.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    // Simple mock exam taxonomy check
    if (activeExamFilter) {
      if (activeExamFilter.toLowerCase() === 'neet') {
        return matchesSearch && (c.title.toLowerCase().includes('neet') || c.id === 'course-ml');
      }
      if (activeExamFilter.toLowerCase() === 'jee (main)' || activeExamFilter.toLowerCase() === 'jee (advanced)' || activeExamFilter.toLowerCase() === 'iit') {
        return matchesSearch && (c.id === 'course-python' || c.id === 'course-dsa');
      }
    }
    return matchesSearch;
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      
      {/* Dynamic Exam Submenu Strip */}
      <div className="bg-slate-900 border-b border-slate-800/80 overflow-x-auto whitespace-nowrap scrollbar-thin">
        <div className="max-w-7xl mx-auto px-6 py-2.5 flex gap-1 text-xs">
          <button 
            type="button"
            onClick={() => setActiveExamFilter(null)}
            className={`px-3 py-1 rounded-full font-medium transition-all ${
              !activeExamFilter ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            All Categories
          </button>
          {subMenus.map(sub => (
            <button
              key={sub.id}
              type="button"
              onClick={() => setActiveExamFilter(sub.title)}
              className={`px-3 py-1 rounded-full font-medium transition-all flex items-center gap-1.5 ${
                activeExamFilter === sub.title ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <DynamicIcon name={sub.icon} size={12} className="opacity-80" />
              {sub.title}
            </button>
          ))}
        </div>
      </div>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-12">
        
        {/* Interactive Hero Column */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
          
          {/* Slogan Left Grid */}
          <div className="lg:col-span-7 flex flex-col justify-between p-8 bg-gradient-to-br from-slate-900 via-slate-900/60 to-indigo-950/20 border border-slate-800/60 rounded-3xl relative overflow-hidden shadow-2xl">
            {/* Visual background gradient glow */}
            <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-500/10 rounded-full filter blur-[80px] -z-10 pointer-events-none" />
            
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-full text-xs font-semibold">
                <Sparkles size={14} className="animate-pulse text-indigo-400" />
                Accredited Multi-tier CMS & LMS Platform
              </div>
              
              <h1 className="text-4xl md:text-5xl font-black text-white leading-[1.1] tracking-tight">
                One Platform.<br />
                <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-amber-300 bg-clip-text text-transparent">
                  Unlimited Learning.
                </span>
              </h1>
              
              <p className="text-slate-400 text-sm md:text-base max-w-lg leading-relaxed">
                BrahmaVidya Galaxy is your complete digital university. Explore accredited curriculum courses, practice infinite quiz problems, design custom studies, and earn cryptographically verified credentials.
              </p>
            </div>

            <div className="mt-8 space-y-6">
              <div className="flex flex-wrap gap-4">
                <button
                  type="button"
                  onClick={() => {
                    const el = document.getElementById('courses-section');
                    if (el) el.scrollIntoView({ behavior: 'smooth' });
                  }}
                  className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-bold shadow-lg shadow-indigo-600/25 transition-all flex items-center gap-2 group"
                >
                  Explore Courses
                  <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                </button>
                <button
                  type="button"
                  onClick={() => setShowPractice(true)}
                  className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 rounded-xl text-sm font-bold transition-all"
                >
                  Start Practicing
                </button>
              </div>

              {/* Tag Features strip */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-y-3 gap-x-4 pt-6 border-t border-slate-800/60 text-slate-400 text-xs">
                <div className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-indigo-500" />
                  Expert Teachers Verified
                </div>
                <div className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-purple-500" />
                  Structured Syllabus Builder
                </div>
                <div className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                  Real-time AI Guidance
                </div>
              </div>
            </div>
          </div>

          {/* Vidya AI Bot Mascot Widget Right Grid */}
          <div className="lg:col-span-5 bg-gradient-to-b from-indigo-950/80 to-slate-900 border border-indigo-500/30 rounded-3xl p-6 shadow-2xl flex flex-col justify-between">
            <div className="flex items-center justify-between pb-4 border-b border-indigo-500/20">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-10 h-10 bg-indigo-600/20 rounded-2xl flex items-center justify-center border border-indigo-500/40">
                    <Bot className="text-indigo-400" size={20} />
                  </div>
                  <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-500 border-2 border-slate-900 rounded-full" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-sm">Vidya AI Assistant</h3>
                  <span className="text-[10px] text-emerald-400 font-semibold block">Online • Google Gemini 3.5</span>
                </div>
              </div>
              <span className="text-[10px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded-full font-bold">
                Mascot Mode
              </span>
            </div>

            {/* Chat History screen */}
            <div className="flex-1 overflow-y-auto max-h-[220px] my-4 space-y-3.5 pr-2 scrollbar-thin">
              {chatHistory.map((item, index) => (
                <div 
                  key={index} 
                  className={`flex ${item.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-xs leading-relaxed ${
                    item.sender === 'user' 
                      ? 'bg-indigo-600 text-white rounded-br-none' 
                      : 'bg-slate-950/80 border border-slate-800 text-slate-300 rounded-bl-none'
                  }`}>
                    {item.text}
                  </div>
                </div>
              ))}
              {isChatting && (
                <div className="flex justify-start">
                  <div className="bg-slate-950/80 border border-slate-800 text-slate-400 rounded-2xl rounded-bl-none px-4 py-2 text-xs flex items-center gap-2">
                    <Loader2 className="animate-spin text-indigo-400" size={12} />
                    Vidya is formulating response...
                  </div>
                </div>
              )}
            </div>

            {/* Quick Actions for Chat */}
            <div className="flex gap-1.5 pb-3 flex-wrap">
              <button 
                type="button"
                onClick={() => setChatMessage('Explain the Big-O notation for Binary Search.')}
                className="text-[10px] bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white px-2 py-1 rounded-lg border border-slate-800 transition-all"
              >
                Explain Big-O
              </button>
              <button 
                type="button"
                onClick={() => setChatMessage('Formulate a study schedule for NEET exam prep.')}
                className="text-[10px] bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white px-2 py-1 rounded-lg border border-slate-800 transition-all"
              >
                NEET Schedule
              </button>
            </div>

            {/* Input Form */}
            <form onSubmit={handleSendChat} className="flex gap-2">
              <input
                type="text"
                placeholder="Ask Vidya anything..."
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white outline-none focus:border-indigo-500"
              />
              <button
                type="submit"
                disabled={isChatting || !chatMessage.trim()}
                className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all shrink-0 disabled:opacity-50"
              >
                Send
              </button>
            </form>
          </div>
        </div>

        {/* Dynamic Horizontal Stats Strip */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            { label: 'Courses', val: '5000+', icon: BookOpen, color: 'text-indigo-400 bg-indigo-500/5 border-indigo-500/10' },
            { label: 'Tutorials', val: '100K+', icon: Layers, color: 'text-purple-400 bg-purple-500/5 border-purple-500/10' },
            { label: 'Practice Questions', val: '2M+', icon: CheckSquare, color: 'text-amber-400 bg-amber-500/5 border-amber-500/10' },
            { label: 'Active Students', val: '50K+', icon: Users, color: 'text-emerald-400 bg-emerald-500/5 border-emerald-500/10' },
            { label: 'Certificates Issued', val: '25K+', icon: Award, color: 'text-rose-400 bg-rose-500/5 border-rose-500/10' },
            { label: 'Learning Categories', val: '20+', icon: BookOpenCheck, color: 'text-teal-400 bg-teal-500/5 border-teal-500/10' }
          ].map((stat, i) => (
            <div key={i} className={`p-4 border rounded-2xl flex items-center gap-3.5 ${stat.color} hover:scale-[1.02] transition-transform`}>
              <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800">
                <stat.icon size={18} />
              </div>
              <div>
                <span className="text-xl font-bold text-white block leading-tight">{stat.val}</span>
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block mt-0.5">{stat.label}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Navigation Tabs Bar */}
        <div className="flex border-b border-slate-800/80 gap-6 text-sm font-bold text-slate-400 mb-8" id="courses-section">
          <button 
            type="button"
            onClick={() => setActiveTab('courses')}
            className={`pb-3 transition-all relative font-sans ${activeTab === 'courses' ? 'text-indigo-400' : 'hover:text-white'}`}
          >
            Courses & Syllabus
            {activeTab === 'courses' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500" />}
          </button>
          <button 
            type="button"
            onClick={() => setActiveTab('exams')}
            className={`pb-3 transition-all relative font-sans ${activeTab === 'exams' ? 'text-indigo-400' : 'hover:text-white'}`}
          >
            Exams & Assessments
            {activeTab === 'exams' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500" />}
          </button>
          <button 
            type="button"
            onClick={() => setActiveTab('badges')}
            className={`pb-3 transition-all relative font-sans ${activeTab === 'badges' ? 'text-indigo-400' : 'hover:text-white'}`}
          >
            My Badges & Credentials
            {activeTab === 'badges' && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500" />}
          </button>
        </div>

        {/* Dynamic Tab Contents */}
        {activeTab === 'courses' && (
          <div className="space-y-6">
            <div className="flex justify-between items-end">
              <div>
                <h2 className="text-2xl font-bold text-white tracking-tight">Accredited Study Programs</h2>
                <p className="text-xs text-slate-400 mt-1">Hierarchical courses managed dynamically via Control Center.</p>
              </div>
              
              {/* Live Search inside Courses */}
              <div className="relative max-w-xs w-full">
                <Search className="absolute left-3 top-2.5 text-slate-400" size={14} />
                <input
                  type="text"
                  placeholder="Filter catalog..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            {filteredCourses.length === 0 ? (
              <div className="p-16 text-center border border-dashed border-slate-800 rounded-2xl">
                <p className="text-sm text-slate-400">No courses match your active filters.</p>
                <button 
                  type="button"
                  onClick={() => { setSearchQuery(''); setActiveExamFilter(null); }}
                  className="text-xs text-indigo-400 font-bold mt-2 hover:underline"
                >
                  Clear all filters
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {filteredCourses.map(course => {
                  const courseImages: Record<string, string> = {
                    'course-python': '🐍',
                    'course-dsa': '🧱',
                    'course-fullstack': '💻',
                    'course-ml': '🧠'
                  };
                  return (
                    <div 
                      key={course.id}
                      className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden hover:border-indigo-500/50 hover:shadow-indigo-500/5 hover:shadow-xl transition-all flex flex-col group"
                    >
                      <div className="p-6 bg-slate-950/40 flex justify-between items-start border-b border-slate-800/60">
                        <div className="text-3xl">
                          {courseImages[course.id] || '📖'}
                        </div>
                        <span className="px-2 py-0.5 text-[10px] font-bold bg-indigo-500/10 text-indigo-400 rounded-full border border-indigo-500/25">
                          {course.metadata?.difficulty || 'Beginner'}
                        </span>
                      </div>

                      <div className="p-6 flex-1 flex flex-col justify-between space-y-4">
                        <div>
                          <h3 className="font-bold text-white text-base leading-snug group-hover:text-indigo-400 transition-colors">
                            {course.title}
                          </h3>
                          <p className="text-xs text-slate-400 mt-1.5 line-clamp-2 leading-relaxed">
                            {course.description}
                          </p>
                        </div>

                        <div className="space-y-3 pt-2">
                          <div className="flex justify-between items-center text-[11px] text-slate-400 border-t border-slate-800/80 pt-3">
                            <span>⏱️ {course.metadata?.duration || 'Self-paced'}</span>
                            <span>📚 {course.metadata?.lessonsCount || 8} Lectures</span>
                          </div>

                          <button
                            type="button"
                            onClick={() => onSelectCourse(course)}
                            className="w-full py-2 bg-slate-800 hover:bg-indigo-600 text-white rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5"
                          >
                            Explore Syllabus
                            <ChevronRight size={14} />
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {activeTab === 'exams' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Milestones & Certification Exams</h2>
              <p className="text-xs text-slate-400 mt-1">Test your conceptual retention to unlock cryptographically signed certifications.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {(exams && exams.length > 0 ? exams : [
                {
                  id: 'ex-quantum',
                  title: 'Quantum Advaita Metaphysics Final',
                  passing_score: 70,
                  duration_minutes: 30,
                  course_title: 'Introduction to Consciousness Physics'
                },
                {
                  id: 'ex-grammars',
                  title: 'Vedic Computational Grammars',
                  passing_score: 75,
                  duration_minutes: 45,
                  course_title: 'Sanskrit Syntax for Compiler Design'
                },
                {
                  id: 'ex-deeplearning',
                  title: 'Deep Learning Observers & Karma',
                  passing_score: 80,
                  duration_minutes: 60,
                  course_title: 'Advanced Machine Learning'
                }
              ]).map(ex => (
                <div key={ex.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between space-y-4 hover:border-indigo-500/50 transition-all">
                  <div className="space-y-2">
                    <span className="px-2 py-0.5 text-[9px] font-black uppercase bg-indigo-500/10 text-indigo-400 rounded-full border border-indigo-500/20">
                      Exam
                    </span>
                    <h3 className="font-bold text-white text-base leading-snug">{ex.title}</h3>
                    <p className="text-xs text-slate-400">{ex.course_title}</p>
                  </div>

                  <div className="border-t border-slate-800/80 pt-3 flex justify-between items-center text-[10px] text-slate-500 font-bold">
                    <span>⏱️ {ex.duration_minutes} Mins</span>
                    <span>🎯 Passing: {ex.passing_score}%</span>
                  </div>

                  <button
                    type="button"
                    onClick={() => setActiveExamForArena(ex)}
                    className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 shadow-md shadow-indigo-600/15"
                  >
                    <Play size={12} />
                    Start Certification Exam
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'badges' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">Gamified Badges & Academic Honors</h2>
              <p className="text-xs text-slate-400 mt-1">Unlock playful and professional capability tokens on the platform.</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {(badges && badges.length > 0 ? badges : [
                { id: 'b1', badge: { title: 'Knowledge Seeker', description: 'Awarded for participating in learning evaluations.', icon_url: 'https://brahmavidya.galaxy/badges/knowledge_seeker.svg' } },
                { id: 'b2', badge: { title: 'Perfect Sage', description: 'Awarded for scoring 100% on a course exam.', icon_url: 'https://brahmavidya.galaxy/badges/perfect_sage.svg' } },
                { id: 'b3', badge: { title: 'Exam Conqueror', description: 'Awarded for passing a course certification exam.', icon_url: 'https://brahmavidya.galaxy/badges/exam_conqueror.svg' } }
              ]).map((ub, idx) => (
                <div key={ub.id || idx} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center flex flex-col items-center justify-between space-y-4 hover:border-amber-500/30 transition-all">
                  <div className="h-16 w-16 rounded-full bg-slate-950 flex items-center justify-center border border-slate-800 text-3xl shadow-inner">
                    {ub.badge.title === 'Perfect Sage' ? '🌟' : ub.badge.title === 'Exam Conqueror' ? '🎓' : '📚'}
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-xs">{ub.badge.title}</h3>
                    <p className="text-[10px] text-slate-500 mt-1">{ub.badge.description}</p>
                  </div>
                  <span className="px-2 py-0.5 text-[9px] font-semibold bg-amber-500/10 text-amber-400 rounded-full border border-amber-500/20">
                    Unlocked
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Double-Grid bottom features: Exam prep & Categories */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Exam Prep List */}
          <div className="lg:col-span-6 bg-slate-900 border border-slate-800/80 rounded-3xl p-6 space-y-5">
            <div className="flex justify-between items-center border-b border-slate-800/60 pb-3">
              <h3 className="font-bold text-white text-base">Trending Exam Trackers</h3>
              <button type="button" className="text-xs text-indigo-400 hover:underline">View All</button>
            </div>

            <div className="grid grid-cols-2 gap-3">
              {[
                { title: 'NEET Practice Arena', icon: 'Activity', desc: 'Mock Tests & Diagnostics' },
                { title: 'JEE Main Preparation', icon: 'Zap', desc: 'Step-by-step math compiler' },
                { title: 'JEE Advanced Prep', icon: 'Cpu', desc: 'Advanced Physics modules' },
                { title: 'UPSC Civil Services', icon: 'Compass', desc: 'Weekly Essay Evaluations' },
                { title: 'CAT Practice Sets', icon: 'TrendingUp', desc: 'Dynamic logic puzzles' },
                { title: 'NET JRF Syllabus', icon: 'FileText', desc: 'Research thesis outlines' }
              ].map((exam, i) => (
                <div 
                  key={i} 
                  onClick={() => {
                    setActiveExamFilter(exam.title.split(' ')[0]);
                    const el = document.getElementById('courses-section');
                    if (el) el.scrollIntoView({ behavior: 'smooth' });
                  }}
                  className="p-3 bg-slate-950/40 hover:bg-indigo-500/5 border border-slate-800 hover:border-indigo-500/25 rounded-xl transition-all cursor-pointer flex gap-3"
                >
                  <div className="h-8 w-8 rounded-lg bg-slate-900 flex items-center justify-center text-indigo-400 shrink-0">
                    <Zap size={14} />
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold text-slate-200">{exam.title}</h4>
                    <span className="text-[10px] text-slate-500 block mt-0.5">{exam.desc}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Categories Grid */}
          <div className="lg:col-span-6 bg-slate-900 border border-slate-800/80 rounded-3xl p-6 space-y-5">
            <div className="flex justify-between items-center border-b border-slate-800/60 pb-3">
              <h3 className="font-bold text-white text-base">Curriculum Domains</h3>
              <button type="button" className="text-xs text-indigo-400 hover:underline">View All</button>
            </div>

            <div className="grid grid-cols-4 gap-3">
              {[
                { label: 'Engineering', emoji: '⚙️' },
                { label: 'Medical Sci', emoji: '🩺' },
                { label: 'Commerce', emoji: '📊' },
                { label: 'Programming', emoji: '💻' },
                { label: 'Design UI', emoji: '🎨' },
                { label: 'Vedic Math', emoji: '📐' },
                { label: 'Astronomy', emoji: '🌌' },
                { label: 'Yoga & Mind', emoji: '🧘' }
              ].map((cat, i) => (
                <div 
                  key={i} 
                  className="p-3 bg-slate-950/40 border border-slate-800/80 rounded-xl text-center hover:border-indigo-500/25 transition-all cursor-pointer space-y-1.5"
                >
                  <span className="text-lg block">{cat.emoji}</span>
                  <span className="text-[10px] font-medium text-slate-300 block truncate">{cat.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Dynamic Interactive Widgets Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          {/* Practice & Tests */}
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-4 flex flex-col justify-between">
            <div className="space-y-2">
              <span className="text-2xl">📝</span>
              <h4 className="font-bold text-white text-sm">Vaidya Practice & Tests</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Formulate unlimited multiple choice quizzes, mock tasks, and customized curriculum exams using Google Gemini dynamically.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setShowPractice(true)}
              className="w-full py-2 bg-indigo-600/10 hover:bg-indigo-600 text-indigo-400 hover:text-white rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5"
            >
              Start Practice Session
              <ArrowRight size={14} />
            </button>
          </div>

          {/* Certificates Engine Verification */}
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-4 flex flex-col justify-between">
            <div className="space-y-2">
              <span className="text-2xl">🏆</span>
              <h4 className="font-bold text-white text-sm">Vaidya Certified Badges</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Verify course integrity, accreditation details, and digital signatures using the secure SHA-256 hash checking module.
              </p>
            </div>
            <button
              type="button"
              onClick={() => {
                const el = document.getElementById('verifier-section');
                if (el) el.scrollIntoView({ behavior: 'smooth' });
              }}
              className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5"
            >
              Verify Certificate
              <ArrowRight size={14} />
            </button>
          </div>

          {/* Community Block */}
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-4 flex flex-col justify-between">
            <div className="space-y-2">
              <span className="text-2xl">🤝</span>
              <h4 className="font-bold text-white text-sm">Join Learning Circles</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Participate in academic discussion boards, solve assignment blockers, and share micro-credentials with classmates globally.
              </p>
            </div>
            <button
              type="button"
              onClick={() => alert('Community structures loaded dynamically! Admins can create forums via the Control Center.')}
              className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5"
            >
              Explore Circles
              <ArrowRight size={14} />
            </button>
          </div>
        </div>

        {/* Certificate Verifier Container */}
        <div id="verifier-section" className="pt-6">
          <div className="pb-4">
            <h3 className="text-xl font-bold text-white">Cryptographic Certificate Verification</h3>
            <p className="text-xs text-slate-400 mt-1">Check integrity hashes directly against our system database ledger.</p>
          </div>
          <CertificateVerifier />
        </div>

      </main>

      {activeExamForArena && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-sm">
          <div className="w-full max-w-3xl">
            <ExamArena 
              exam={activeExamForArena}
              onClose={() => setActiveExamForArena(null)}
              onFinishAttempt={() => {
                fetchExamsAndBadges();
              }}
            />
          </div>
        </div>
      )}

      {/* Course Detail Drawer Sidebar */}
      {selectedCourse && (
        <CurriculumView
          course={selectedCourse}
          structures={structures}
          onClose={() => onSelectCourse(null as any)}
        />
      )}

      {/* Quiz Dialog Modal */}
      {showPractice && (
        <QuizPractice onClose={() => setShowPractice(false)} />
      )}

      {/* Footer */}
      <footer className="bg-slate-950 border-t border-slate-900 py-8 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <span>© 2026 BrahmaVidya Galaxy Educational Platform. All rights reserved. Content-Agnostic Engine.</span>
          <div className="flex gap-4">
            <span className="hover:text-slate-400 cursor-pointer">Security Protocol</span>
            <span className="hover:text-slate-400 cursor-pointer">Accredited Nodes</span>
            <span className="hover:text-slate-400 cursor-pointer">API Ledger</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
