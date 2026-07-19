/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef } from 'react';
import { 
  BookOpen, Bookmark, FileText, Calendar, Award, Zap, Clock, Plus, Trash2, 
  Search, Pin, ChevronRight, Play, Pause, Square, CheckCircle, RefreshCw, 
  Settings, Volume2, VolumeX, BarChart2, CheckSquare, Target, Bell, Sparkles, 
  ArrowLeft, List, CalendarDays, ExternalLink, Moon, Sun, AwardIcon
} from 'lucide-react';
import { useThemeStore } from '../../stores/themeStore';
import { useLayoutStore } from '../../stores/layoutStore';
import { 
  studentApi, Bookmark as BookmarkType, StudentNote, StudyGoal, 
  StudySession, StudyCalendarEvent, LearningStreak
} from '../../services/studentApi';
import { Badge, Button, Input, Textarea, Avatar } from '../DesignSystem';
import { StudentAiPortal } from './StudentAiPortal';

interface StudentDashboardProps {
  currentUser: any;
}

export const StudentDashboard: React.FC<StudentDashboardProps> = ({ currentUser }) => {
  const { theme, toggleTheme } = useThemeStore();
  const { navigateTo } = useLayoutStore();

  // Navigation Subsections inside the Student Portal
  const [activeSubTab, setActiveSubTab] = useState<'home' | 'courses' | 'bookmarks' | 'notes' | 'goals' | 'calendar' | 'achievements' | 'ai'>('home');

  // --- STATE WITH ROBUST PERSISTENCE / FALLBACK ---
  const [streak, setStreak] = useState<LearningStreak>({
    id: 'streak-1',
    current_streak: 5,
    longest_streak: 12,
    last_active_date: new Date().toISOString().split('T')[0],
    total_xp: 350,
    current_level: 3,
  });

  const [continueLearning, setContinueLearning] = useState<any[]>([
    { id: 'cl-1', course_id: 'course-1', course_title: 'Vedic Mathematics Masterclass', last_node_title: 'Sutra division shortcuts (Ekadhikena)', progress: 65, duration: '12 min left' },
    { id: 'cl-2', course_id: 'course-2', course_title: 'Double-Entry Ledger Bookkeeping', last_node_title: 'Balance sheets balancing principles', progress: 40, duration: '25 min left' },
    { id: 'cl-3', course_id: 'course-3', course_title: 'Advanced Django Custom Middlewares', last_node_title: 'Middleware chaining & trace ID context', progress: 85, duration: '8 min left' }
  ]);

  const [bookmarks, setBookmarks] = useState<BookmarkType[]>([]);
  const [notes, setNotes] = useState<StudentNote[]>([]);
  const [goals, setGoals] = useState<StudyGoal[]>([]);
  const [sessions, setSessions] = useState<StudySession[]>([]);
  const [calendarEvents, setCalendarEvents] = useState<StudyCalendarEvent[]>([]);

  // Search filter states
  const [bookmarkSearch, setBookmarkSearch] = useState('');
  const [noteSearch, setNoteSearch] = useState('');
  const [goalFilter, setGoalFilter] = useState<'ALL' | 'PENDING' | 'IN_PROGRESS' | 'COMPLETED'>('ALL');

  // Interactive Form States
  const [newGoalTitle, setNewGoalTitle] = useState('');
  const [newGoalDesc, setNewGoalDesc] = useState('');
  const [newGoalTarget, setNewGoalTarget] = useState(new Date().toISOString().split('T')[0]);

  const [newNoteTitle, setNewNoteTitle] = useState('');
  const [newNoteNode, setNewNoteNode] = useState('Vedic Mathematics');
  const [newNoteContent, setNewNoteContent] = useState('');
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);

  const [newBookmarkTitle, setNewBookmarkTitle] = useState('');
  const [newBookmarkUrl, setNewBookmarkUrl] = useState('');
  const [newBookmarkCategory, setNewBookmarkCategory] = useState('LMS Course');

  const [newCalendarTitle, setNewCalendarTitle] = useState('');
  const [newCalendarDesc, setNewCalendarDesc] = useState('');
  const [newCalendarDate, setNewCalendarDate] = useState(new Date().toISOString().split('T')[0]);
  const [newCalendarTime, setNewCalendarTime] = useState('10:00');

  // Study Timer States
  const [timerActive, setTimerActive] = useState(false);
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [timerSubject, setTimerSubject] = useState('General Learning');
  const [xpGainedNotification, setXpGainedNotification] = useState<string | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Audio state
  const [soundEnabled, setSoundEnabled] = useState(false);

  // Loading indicator
  const [loading, setLoading] = useState(false);

  // Load datasets from REST or Local Storage
  const loadData = async () => {
    setLoading(true);
    try {
      // 1. Fetch from Django REST API endpoints via studentApi client
      const [
        streakRes,
        historyRes,
        bookmarksRes,
        notesRes,
        goalsRes,
        calendarRes
      ] = await Promise.all([
        studentApi.getStreak(),
        studentApi.listContinueLearning(),
        studentApi.listBookmarks(),
        studentApi.listNotes(),
        studentApi.listGoals(),
        studentApi.listCalendarEvents(),
      ]);

      // If APIs are online, load them
      if (streakRes.success && streakRes.data) setStreak(streakRes.data);
      if (bookmarksRes.success && bookmarksRes.data) setBookmarks(bookmarksRes.data);
      if (notesRes.success && notesRes.data) setNotes(notesRes.data);
      if (goalsRes.success && goalsRes.data) setGoals(goalsRes.data);
      if (calendarRes.success && calendarRes.data) setCalendarEvents(calendarRes.data);

    } catch (err) {
      console.warn('REST APIs not fully populated, relying on integrated localStorage layer.', err);
    }

    // 2. Local fallback sync logic (always synchronized to ensure instant fidelity)
    const localStreak = localStorage.getItem('bv_streak');
    const localBookmarks = localStorage.getItem('bv_bookmarks');
    const localNotes = localStorage.getItem('bv_notes');
    const localGoals = localStorage.getItem('bv_goals');
    const localCalendar = localStorage.getItem('bv_calendar');

    if (localStreak) setStreak(JSON.parse(localStreak));
    if (localBookmarks) {
      setBookmarks(JSON.parse(localBookmarks));
    } else {
      const defaultB = [
        { id: 'b-1', student: 'current', content_type: 'LMS', content_id: 'c1', title: 'Ekadhikena Division Sutra Cheat-sheet', source_name: 'Vedic Math', url_path: '/courses', created_at: new Date().toISOString() },
        { id: 'b-2', student: 'current', content_type: 'EBOOK', content_id: 'b1', title: 'Double Entry Ledger System blueprints', source_name: 'eBook Library', url_path: '/bookstore', created_at: new Date().toISOString() }
      ];
      setBookmarks(defaultB);
      localStorage.setItem('bv_bookmarks', JSON.stringify(defaultB));
    }

    if (localNotes) {
      setNotes(JSON.parse(localNotes));
    } else {
      const defaultN = [
        { id: 'n-1', student: 'current', node: 'Vedic Math', node_title: 'Intro', title: 'Ekadhikena Purvena Sutra', content: 'Notes: This sutra translates to "By one more than the previous". Extremely useful for mental squaring of numbers ending in 5. Example: 35^2 = (3 * 4) | 25 = 1225.', is_pinned: true, created_at: new Date().toISOString(), updated_at: new Date().toISOString() },
        { id: 'n-2', student: 'current', node: 'Django Backend', node_title: 'Middleware', title: 'Custom Request Interceptors', content: 'Always append request_id trace to the thread context to ensure elastic search can group log indices securely.', is_pinned: false, created_at: new Date().toISOString(), updated_at: new Date().toISOString() }
      ];
      setNotes(defaultN);
      localStorage.setItem('bv_notes', JSON.stringify(defaultN));
    }

    if (localGoals) {
      setGoals(JSON.parse(localGoals));
    } else {
      const defaultG: StudyGoal[] = [
        { id: 'g-1', student: 'current', title: 'Complete Vedic Maths Chapter 3 Quizzes', description: 'Resolve mental division exercises and unlock high speed mental math badge.', target_date: new Date(Date.now() + 86400000 * 2).toISOString().split('T')[0], progress_percentage: 45, status: 'IN_PROGRESS' },
        { id: 'g-2', student: 'current', title: 'Read Chapter 1 of Double Entry Ledgers', description: 'Fully audit matching principles and ledger balance charts.', target_date: new Date(Date.now() + 86400000 * 5).toISOString().split('T')[0], progress_percentage: 100, status: 'COMPLETED' },
        { id: 'g-3', student: 'current', title: 'Implement Django JWT Blacklist Pipeline', description: 'Create token rotation verification tests under apps/users/tests.', target_date: new Date(Date.now() + 86400000 * 8).toISOString().split('T')[0], progress_percentage: 10, status: 'PENDING' }
      ];
      setGoals(defaultG);
      localStorage.setItem('bv_goals', JSON.stringify(defaultG));
    }

    if (localCalendar) {
      setCalendarEvents(JSON.parse(localCalendar));
    } else {
      const defaultC = [
        { id: 'cal-1', student: 'current', title: 'Vedic Division Live Interactive Seminar', description: 'Attend the online webinar with Dr. Shastri.', starts_at: new Date().toISOString().split('T')[0] + 'T14:00:00', ends_at: new Date().toISOString().split('T')[0] + 'T15:30:00' },
        { id: 'cal-2', student: 'current', title: 'IIT JEE Mock Exam Arena Trial', description: 'Compete in the national math practice dashboard tournament.', starts_at: new Date(Date.now() + 86400000).toISOString().split('T')[0] + 'T09:00:00', ends_at: new Date(Date.now() + 86400000).toISOString().split('T')[0] + 'T12:00:00' }
      ];
      setCalendarEvents(defaultC);
      localStorage.setItem('bv_calendar', JSON.stringify(defaultC));
    }

    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  // Sync to local storage wrapper
  const saveStateToLocal = (key: string, data: any) => {
    localStorage.setItem(key, JSON.stringify(data));
  };

  // --- STUDY TIMER CONTROLS ---
  useEffect(() => {
    if (timerActive) {
      timerRef.current = setInterval(() => {
        setTimerSeconds(prev => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [timerActive]);

  const handleStartTimer = async (subjectName: string) => {
    setTimerSubject(subjectName);
    setTimerSeconds(0);
    setTimerActive(true);

    try {
      const res = await studentApi.startSession({ node: subjectName });
      if (res.success && res.data) {
        setActiveSessionId(res.data.id);
      }
    } catch (e) {
      console.warn(e);
    }

    if (soundEnabled) {
      try {
        const audio = new Audio('https://assets.mixkit.co/active_storage/sfx/2568/2568-84.wav');
        audio.volume = 0.2;
        audio.play();
      } catch (err) {}
    }
  };

  const handlePauseTimer = () => {
    setTimerActive(prev => !prev);
  };

  const handleStopTimer = async () => {
    setTimerActive(false);
    const completedSeconds = timerSeconds;
    setTimerSeconds(0);

    if (completedSeconds < 5) {
      return; // Too short to record
    }

    // Award XP
    const earnedXp = Math.ceil(completedSeconds / 6) || 1; // 10 XP per minute
    const updatedStreak = {
      ...streak,
      total_xp: streak.total_xp + earnedXp,
      current_level: Math.floor((streak.total_xp + earnedXp) / 150) + 1
    };
    setStreak(updatedStreak);
    saveStateToLocal('bv_streak', updatedStreak);

    // Save Study session in mock history
    const newSession: StudySession = {
      id: `session-${Date.now()}`,
      student: 'current',
      node_title: timerSubject,
      started_at: new Date(Date.now() - completedSeconds * 1000).toISOString(),
      ended_at: new Date().toISOString(),
      duration_seconds: completedSeconds,
      is_active: false
    };

    const updatedSessions = [newSession, ...sessions];
    setSessions(updatedSessions);
    saveStateToLocal('bv_sessions', updatedSessions);

    // Dynamic notification trigger
    setXpGainedNotification(`🔥 Bravo! You study-logged ${Math.floor(completedSeconds / 60)}m ${completedSeconds % 60}s of "${timerSubject}" and gained +${earnedXp} XP!`);
    setTimeout(() => {
      setXpGainedNotification(null);
    }, 5500);

    // Call REST endpoint
    if (activeSessionId) {
      try {
        await studentApi.endSession(activeSessionId);
      } catch (e) {
        console.warn(e);
      }
    }

    // Alert Sound
    if (soundEnabled) {
      try {
        const audio = new Audio('https://assets.mixkit.co/active_storage/sfx/1435/1435-84.wav');
        audio.volume = 0.3;
        audio.play();
      } catch (err) {}
    }
  };

  // --- BOOKMARKS ACTIONS ---
  const handleAddBookmark = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newBookmarkTitle) return;

    const newB: BookmarkType = {
      id: `b-${Date.now()}`,
      student: 'current',
      content_type: newBookmarkCategory,
      content_id: `id-${Date.now()}`,
      title: newBookmarkTitle,
      source_name: newBookmarkCategory,
      url_path: newBookmarkUrl || '/courses',
      created_at: new Date().toISOString()
    };

    const updated = [newB, ...bookmarks];
    setBookmarks(updated);
    saveStateToLocal('bv_bookmarks', updated);

    // Reset inputs
    setNewBookmarkTitle('');
    setNewBookmarkUrl('');

    // Call API
    try {
      await studentApi.toggleBookmark({
        content_type: newB.content_type,
        content_id: newB.content_id,
        title: newB.title,
        url_path: newB.url_path
      });
    } catch (err) {}
  };

  const handleRemoveBookmark = (id: string) => {
    const updated = bookmarks.filter(b => b.id !== id);
    setBookmarks(updated);
    saveStateToLocal('bv_bookmarks', updated);
  };

  // --- GOAL ACTIONS ---
  const handleAddGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newGoalTitle) return;

    const newG: StudyGoal = {
      id: `g-${Date.now()}`,
      student: 'current',
      title: newGoalTitle,
      description: newGoalDesc,
      target_date: newGoalTarget,
      progress_percentage: 0,
      status: 'PENDING'
    };

    const updated = [newG, ...goals];
    setGoals(updated);
    saveStateToLocal('bv_goals', updated);

    // Reset inputs
    setNewGoalTitle('');
    setNewGoalDesc('');

    // REST api call
    try {
      await studentApi.createGoal({
        title: newG.title,
        description: newG.description,
        target_date: newG.target_date
      });
    } catch (e) {}
  };

  const handleToggleGoalComplete = (id: string) => {
    const updated = goals.map(g => {
      if (g.id === id) {
        const nextStatus = g.status === 'COMPLETED' ? 'IN_PROGRESS' : 'COMPLETED';
        const nextPercent = nextStatus === 'COMPLETED' ? 100 : 50;
        return { ...g, status: nextStatus, progress_percentage: nextPercent };
      }
      return g;
    });
    setGoals(updated);
    saveStateToLocal('bv_goals', updated);
  };

  const handleUpdateGoalSlider = (id: string, value: number) => {
    const updated = goals.map(g => {
      if (g.id === id) {
        const nextStatus = value === 100 ? 'COMPLETED' : value > 0 ? 'IN_PROGRESS' : 'PENDING';
        return { ...g, progress_percentage: value, status: nextStatus };
      }
      return g;
    });
    setGoals(updated);
    saveStateToLocal('bv_goals', updated);
  };

  const handleDeleteGoal = (id: string) => {
    const updated = goals.filter(g => g.id !== id);
    setGoals(updated);
    saveStateToLocal('bv_goals', updated);
  };

  // --- NOTES ACTIONS ---
  const handleSaveNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNoteTitle || !newNoteContent) return;

    if (editingNoteId) {
      // Update existing
      const updated = notes.map(n => {
        if (n.id === editingNoteId) {
          return {
            ...n,
            title: newNoteTitle,
            node: newNoteNode,
            content: newNoteContent,
            updated_at: new Date().toISOString()
          };
        }
        return n;
      });
      setNotes(updated);
      saveStateToLocal('bv_notes', updated);
      setEditingNoteId(null);
    } else {
      // Create new
      const newN: StudentNote = {
        id: `n-${Date.now()}`,
        student: 'current',
        node: newNoteNode,
        node_title: newNoteNode,
        title: newNoteTitle,
        content: newNoteContent,
        is_pinned: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      const updated = [newN, ...notes];
      setNotes(updated);
      saveStateToLocal('bv_notes', updated);
    }

    setNewNoteTitle('');
    setNewNoteContent('');
  };

  const handleTogglePinNote = (id: string) => {
    const updated = notes.map(n => {
      if (n.id === id) {
        return { ...n, is_pinned: !n.is_pinned };
      }
      return n;
    });
    setNotes(updated);
    saveStateToLocal('bv_notes', updated);
  };

  const handleDeleteNote = (id: string) => {
    const updated = notes.filter(n => n.id !== id);
    setNotes(updated);
    saveStateToLocal('bv_notes', updated);
  };

  const handleEditNote = (note: StudentNote) => {
    setEditingNoteId(note.id);
    setNewNoteTitle(note.title);
    setNewNoteNode(note.node || 'General Learning');
    setNewNoteContent(note.content);
  };

  // --- CALENDAR ACTIONS ---
  const handleAddCalendarEvent = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCalendarTitle) return;

    const newEvent: StudyCalendarEvent = {
      id: `cal-${Date.now()}`,
      student: 'current',
      title: newCalendarTitle,
      description: newCalendarDesc,
      starts_at: `${newCalendarDate}T${newCalendarTime}:00`,
      ends_at: `${newCalendarDate}T23:59:00`
    };

    const updated = [...calendarEvents, newEvent];
    setCalendarEvents(updated);
    saveStateToLocal('bv_calendar', updated);

    setNewCalendarTitle('');
    setNewCalendarDesc('');
  };

  // --- CHART METRICS (STATIC BACKING DATA + CALCULATIONS) ---
  const weeklyStudyHours = [3.2, 4.5, 2.8, 5.0, 3.8, 6.2, 4.0]; // Hours from Mon-Sun
  const weeklyLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  const monthlyStudyHours = [12, 18, 24, 29, 36, 42]; // Spline metrics last 6 months
  const monthlyLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];

  const totalWeeklyHours = weeklyStudyHours.reduce((a, b) => a + b, 0);
  const averageDailyMinutes = Math.round((totalWeeklyHours * 60) / 7);

  // Filter lists
  const filteredBookmarks = bookmarks.filter(b => 
    b.title.toLowerCase().includes(bookmarkSearch.toLowerCase()) || 
    b.source_name.toLowerCase().includes(bookmarkSearch.toLowerCase())
  );

  const filteredNotes = notes.filter(n => 
    n.title.toLowerCase().includes(noteSearch.toLowerCase()) || 
    n.content.toLowerCase().includes(noteSearch.toLowerCase())
  );

  const filteredGoals = goals.filter(g => {
    if (goalFilter === 'ALL') return true;
    return g.status === goalFilter;
  });

  return (
    <div id="student-portal-viewport" className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans transition-colors duration-300">
      
      {/* 1. BRAND TOP BAR */}
      <header className="bg-slate-900 border-b border-indigo-950/80 px-6 py-4 flex flex-wrap justify-between items-center gap-4 sticky top-0 z-50 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-600/20 text-indigo-400 rounded-xl border border-indigo-500/30">
            <Sparkles size={20} className="animate-pulse" />
          </div>
          <div>
            <h1 className="text-base font-black text-white tracking-tight flex items-center gap-1.5">
              BrahmaVidya Student Space
              <span className="text-[10px] bg-indigo-900/60 text-indigo-300 font-mono px-2 py-0.5 rounded-full border border-indigo-500/30">LEVEL {streak.current_level}</span>
            </h1>
            <p className="text-[10px] text-slate-400 font-mono">Continuous learning & telemetry suite</p>
          </div>
        </div>

        {/* STUDY TIMER WIDGET AT HEAD */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2 px-4 py-2 bg-slate-950 border border-indigo-950 rounded-full">
            <span className={`h-2.5 w-2.5 rounded-full ${timerActive ? 'bg-emerald-500 animate-ping' : 'bg-slate-600'}`}></span>
            <span className="text-xs font-mono font-bold text-slate-300">{timerSubject}:</span>
            <strong className="text-sm font-mono font-black text-indigo-400">
              {Math.floor(timerSeconds / 3600).toString().padStart(2, '0')}:
              {Math.floor((timerSeconds % 3600) / 60).toString().padStart(2, '0')}:
              {(timerSeconds % 60).toString().padStart(2, '0')}
            </strong>

            <div className="flex items-center gap-1 border-l border-slate-800 pl-2 ml-1">
              {!timerActive && timerSeconds === 0 ? (
                <button 
                  onClick={() => handleStartTimer('Vedic Math')} 
                  title="Start study timer" 
                  className="p-1.5 hover:bg-slate-900 text-emerald-400 rounded-full transition cursor-pointer"
                >
                  <Play size={14} fill="currentColor" />
                </button>
              ) : (
                <React.Fragment>
                  <button 
                    onClick={handlePauseTimer} 
                    title={timerActive ? "Pause study timer" : "Resume timer"} 
                    className="p-1.5 hover:bg-slate-900 text-yellow-400 rounded-full transition cursor-pointer"
                  >
                    {timerActive ? <Pause size={14} /> : <Play size={14} fill="currentColor" />}
                  </button>
                  <button 
                    onClick={handleStopTimer} 
                    title="Stop study timer and save" 
                    className="p-1.5 hover:bg-slate-900 text-rose-500 rounded-full transition cursor-pointer"
                  >
                    <Square size={14} fill="currentColor" />
                  </button>
                </React.Fragment>
              )}
            </div>
          </div>

          {/* Sound trigger */}
          <button 
            onClick={() => setSoundEnabled(!soundEnabled)} 
            className="p-2 bg-slate-850 hover:bg-slate-800 rounded-xl text-slate-400 transition"
            title={soundEnabled ? "Mute audio alarms" : "Enable sound effects"}
          >
            {soundEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
          </button>

          {/* Light/Dark mode */}
          <button 
            onClick={toggleTheme} 
            className="p-2 bg-slate-850 hover:bg-slate-800 rounded-xl text-slate-400 transition"
            title="Toggle Visual Theme Theme"
          >
            {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
          </button>
        </div>
      </header>

      {/* XP EARNED FLOAT NOTIFICATION */}
      {xpGainedNotification && (
        <div className="fixed bottom-6 right-6 z-50 max-w-sm bg-indigo-950 border-2 border-indigo-500 text-white p-4 rounded-2xl shadow-2xl animate-bounce flex items-start gap-3">
          <div className="p-2 bg-indigo-500 text-white rounded-xl"><Award size={20} className="animate-spin" /></div>
          <div>
            <h4 className="font-bold text-xs">Learning Verified!</h4>
            <p className="text-[11px] text-slate-200 mt-1">{xpGainedNotification}</p>
          </div>
        </div>
      )}

      {/* MAIN CONTAINER LAYOUT */}
      <div className="flex-grow flex flex-col md:flex-row w-full max-w-7xl mx-auto">
        
        {/* SIDEBAR NAVIGATION */}
        <aside className="w-full md:w-64 border-b md:border-b-0 md:border-r border-indigo-950/40 bg-slate-950/40 p-6 flex flex-col gap-6">
          <div className="flex items-center gap-3 bg-indigo-950/40 p-3 rounded-2xl border border-indigo-950">
            <Avatar name={currentUser?.fullName || 'Student'} size="md" className="border border-indigo-500" />
            <div>
              <strong className="block text-xs text-white truncate">{currentUser?.fullName || 'Vedic Learner'}</strong>
              <span className="text-[9px] font-mono text-emerald-400 block mt-0.5">CBAC verified active</span>
            </div>
          </div>

          <nav className="flex flex-col gap-1.5 select-none text-left">
            <button 
              onClick={() => setActiveSubTab('home')} 
              className={`flex items-center justify-between px-4 py-3 rounded-xl text-xs font-semibold tracking-wide transition cursor-pointer ${activeSubTab === 'home' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-900/60'}`}
            >
              <div className="flex items-center gap-2.5">
                <BarChart2 size={16} /> <span>Home Workspace</span>
              </div>
              <ChevronRight size={12} className="opacity-60" />
            </button>

            <button 
              onClick={() => setActiveSubTab('courses')} 
              className={`flex items-center justify-between px-4 py-3 rounded-xl text-xs font-semibold tracking-wide transition cursor-pointer ${activeSubTab === 'courses' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-900/60'}`}
            >
              <div className="flex items-center gap-2.5">
                <BookOpen size={16} /> <span>Resume Courses</span>
              </div>
              <ChevronRight size={12} className="opacity-60" />
            </button>

            <button 
              onClick={() => setActiveSubTab('bookmarks')} 
              className={`flex items-center justify-between px-4 py-3 rounded-xl text-xs font-semibold tracking-wide transition cursor-pointer ${activeSubTab === 'bookmarks' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-900/60'}`}
            >
              <div className="flex items-center gap-2.5">
                <Bookmark size={16} /> <span>Topics Bookmarks</span>
              </div>
              <Badge variant="primary" className="text-[9px]">{bookmarks.length}</Badge>
            </button>

            <button 
              onClick={() => setActiveSubTab('notes')} 
              className={`flex items-center justify-between px-4 py-3 rounded-xl text-xs font-semibold tracking-wide transition cursor-pointer ${activeSubTab === 'notes' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-900/60'}`}
            >
              <div className="flex items-center gap-2.5">
                <FileText size={16} /> <span>Lesson Notes</span>
              </div>
              <Badge variant="primary" className="text-[9px]">{notes.length}</Badge>
            </button>

            <button 
              onClick={() => setActiveSubTab('goals')} 
              className={`flex items-center justify-between px-4 py-3 rounded-xl text-xs font-semibold tracking-wide transition cursor-pointer ${activeSubTab === 'goals' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-900/60'}`}
            >
              <div className="flex items-center gap-2.5">
                <CheckSquare size={16} /> <span>Study Goals</span>
              </div>
              <ChevronRight size={12} className="opacity-60" />
            </button>

            <button 
              onClick={() => setActiveSubTab('calendar')} 
              className={`flex items-center justify-between px-4 py-3 rounded-xl text-xs font-semibold tracking-wide transition cursor-pointer ${activeSubTab === 'calendar' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-900/60'}`}
            >
              <div className="flex items-center gap-2.5">
                <Calendar size={16} /> <span>Study Schedule</span>
              </div>
              <ChevronRight size={12} className="opacity-60" />
            </button>

            <button 
              onClick={() => setActiveSubTab('achievements')} 
              className={`flex items-center justify-between px-4 py-3 rounded-xl text-xs font-semibold tracking-wide transition cursor-pointer ${activeSubTab === 'achievements' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-900/60'}`}
            >
              <div className="flex items-center gap-2.5">
                <Award size={16} /> <span>Achievements Vault</span>
              </div>
              <ChevronRight size={12} className="opacity-60" />
            </button>

            <button 
              onClick={() => setActiveSubTab('ai')} 
              className={`flex items-center justify-between px-4 py-3 rounded-xl text-xs font-semibold tracking-wide transition cursor-pointer ${activeSubTab === 'ai' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-900/60'}`}
            >
              <div className="flex items-center gap-2.5">
                <Sparkles size={16} className="text-indigo-400 animate-pulse" /> <span>AI Portal Studio</span>
              </div>
              <ChevronRight size={12} className="opacity-60" />
            </button>
          </nav>

          <div className="mt-auto pt-6 border-t border-indigo-950/40 text-left">
            <span className="text-[9px] font-mono text-slate-500 uppercase tracking-widest font-bold block mb-2">Back to main</span>
            <button 
              onClick={() => navigateTo('/dashboard')}
              className="w-full flex items-center gap-2 p-2 bg-slate-900 border border-indigo-950 hover:bg-slate-850 rounded-xl text-[11px] font-bold text-indigo-400 transition cursor-pointer"
            >
              <ArrowLeft size={12} /> Leave Student Space
            </button>
          </div>
        </aside>

        {/* WORKSPACE MAIN VIEW AREA */}
        <main className="flex-grow p-6 md:p-8 overflow-y-auto text-left">
          
          {/* A. HOME VIEW (BENTO WIDGETS + CHARTS GRID) */}
          {activeSubTab === 'home' && (
            <div className="space-y-8 animate-fade-in">
              
              {/* STREAK & WELCOME BANNER */}
              <div className="p-6 bg-gradient-to-r from-[#0b1329] to-[#0f244a] border border-indigo-950 rounded-3xl flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="p-1 bg-yellow-500/10 text-yellow-500 rounded-lg"><Zap size={14} className="fill-current animate-bounce" /></span>
                    <span className="text-[10px] font-mono font-black text-indigo-300 uppercase tracking-widest">Active Study streak</span>
                  </div>
                  <h2 className="text-xl md:text-2xl font-black text-white leading-tight">You are on a {streak.current_streak}-Day Study Streak!</h2>
                  <p className="text-xs text-slate-350 leading-relaxed max-w-lg">Keep studying daily to expand your mind, earn extra `$VIDYA` points, and verify your certification on the immutable memory ledger.</p>
                </div>

                <div className="flex gap-4 items-center">
                  <div className="px-5 py-4 bg-slate-950/80 border border-indigo-900/60 rounded-2xl text-center">
                    <strong className="block text-xl font-mono font-black text-white">{streak.current_streak}</strong>
                    <span className="text-[9px] uppercase font-bold text-slate-500 font-mono">Current days</span>
                  </div>
                  <div className="px-5 py-4 bg-slate-950/80 border border-indigo-900/60 rounded-2xl text-center">
                    <strong className="block text-xl font-mono font-black text-indigo-400">{streak.longest_streak}</strong>
                    <span className="text-[9px] uppercase font-bold text-slate-500 font-mono">Longest record</span>
                  </div>
                  <div className="px-5 py-4 bg-slate-950/80 border border-indigo-900/60 rounded-2xl text-center">
                    <strong className="block text-xl font-mono font-black text-emerald-400">{streak.total_xp}</strong>
                    <span className="text-[9px] uppercase font-bold text-slate-500 font-mono">Total XP</span>
                  </div>
                </div>
              </div>

              {/* BENTO GRID ROW 1: CORE TELEMETRY STATISTICS & STUDY TIMER */}
              <section className="grid grid-cols-1 md:grid-cols-12 gap-6">
                
                {/* 1. WEEKLY HOURS CHART (SVG-based bar graph) */}
                <div className="md:col-span-6 p-6 space-y-4 bg-slate-900 border border-indigo-950 rounded-2xl">
                  <div className="flex justify-between items-center border-b border-indigo-950/40 pb-3">
                    <div>
                      <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Weekly Study Activity</h3>
                      <p className="text-[10px] text-slate-500 mt-0.5">Hours logged per day last week</p>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-black font-mono text-indigo-400">{totalWeeklyHours.toFixed(1)} hrs</span>
                      <span className="block text-[8px] uppercase font-mono font-bold text-slate-500">Weekly Total</span>
                    </div>
                  </div>

                  {/* SVG Bar Chart */}
                  <div className="h-44 flex items-end justify-between pt-4 gap-2">
                    {weeklyStudyHours.map((hours, idx) => {
                      const maxHours = Math.max(...weeklyStudyHours);
                      const heightPercent = (hours / maxHours) * 80;
                      return (
                        <div key={idx} className="flex-grow flex flex-col items-center gap-2 group cursor-pointer">
                          <span className="text-[9px] font-mono text-indigo-300 opacity-0 group-hover:opacity-100 transition duration-200">
                            {hours}h
                          </span>
                          <div 
                            className="w-full bg-indigo-950 hover:bg-indigo-600 border border-indigo-800/40 hover:border-indigo-400 rounded-t-lg transition-all duration-300 relative group"
                            style={{ height: `${Math.max(heightPercent, 5)}%` }}
                          >
                            <div className="absolute inset-x-0 top-0 h-1 bg-white/20 rounded-t-lg"></div>
                          </div>
                          <span className="text-[9px] font-mono text-slate-450 font-bold">
                            {weeklyLabels[idx]}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* 2. MONTHLY ACTIVITY SPLINE CHART (SVG-based area graph) */}
                <div className="md:col-span-6 p-6 space-y-4 bg-slate-900 border border-indigo-950 rounded-2xl">
                  <div className="flex justify-between items-center border-b border-indigo-950/40 pb-3">
                    <div>
                      <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Study Duration Spline Curve</h3>
                      <p className="text-[10px] text-slate-500 mt-0.5">Continuous months accumulation (Hours)</p>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-black font-mono text-indigo-400">{averageDailyMinutes}m</span>
                      <span className="block text-[8px] uppercase font-mono font-bold text-slate-500">Daily average</span>
                    </div>
                  </div>

                  {/* SVG Area Spline */}
                  <div className="h-44 pt-4 relative">
                    <svg className="w-full h-full" viewBox="0 0 100 40" preserveAspectRatio="none">
                      <defs>
                        <linearGradient id="spline-gradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#4f46e5" stopOpacity="0.4" />
                          <stop offset="100%" stopColor="#4f46e5" stopOpacity="0.0" />
                        </linearGradient>
                      </defs>
                      
                      {/* Area Node */}
                      <path 
                        d="M 0 40 L 0 32 L 20 28 L 40 24 L 60 20 L 80 15 L 100 10 L 100 40 Z" 
                        fill="url(#spline-gradient)"
                      />

                      {/* Stroke Node */}
                      <path 
                        d="M 0 32 L 20 28 L 40 24 L 60 20 L 80 15 L 100 10" 
                        fill="none" 
                        stroke="#6366f1" 
                        strokeWidth="1.5"
                        strokeLinecap="round"
                      />

                      {/* Dots */}
                      <circle cx="0" cy="32" r="1.5" fill="#ffffff" stroke="#6366f1" strokeWidth="0.8" />
                      <circle cx="20" cy="28" r="1.5" fill="#ffffff" stroke="#6366f1" strokeWidth="0.8" />
                      <circle cx="40" cy="24" r="1.5" fill="#ffffff" stroke="#6366f1" strokeWidth="0.8" />
                      <circle cx="60" cy="20" r="1.5" fill="#ffffff" stroke="#6366f1" strokeWidth="0.8" />
                      <circle cx="80" cy="15" r="1.5" fill="#ffffff" stroke="#6366f1" strokeWidth="0.8" />
                      <circle cx="100" cy="10" r="1.5" fill="#ffffff" stroke="#6366f1" strokeWidth="0.8" />
                    </svg>

                    <div className="absolute inset-x-0 bottom-0 flex justify-between px-2">
                      {monthlyLabels.map((lbl, idx) => (
                        <span key={idx} className="text-[9px] font-mono text-slate-450 font-bold mt-1">
                          {lbl}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

              </section>

              {/* BENTO GRID ROW 2: PROGRESS RADIALS, CONTINUE CARDS, QUICK ACTIONS */}
              <section className="grid grid-cols-1 md:grid-cols-12 gap-6">
                
                {/* 1. CONTINUE LEARNING LIST */}
                <div className="md:col-span-8 space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                      <BookOpen size={14} className="text-indigo-400" /> Continue Learning
                    </h3>
                    <button onClick={() => setActiveSubTab('courses')} className="text-[10px] text-indigo-400 hover:underline font-bold font-mono">View All</button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {continueLearning.map(item => (
                      <div key={item.id} className="p-4 bg-slate-900 border border-indigo-950 hover:border-indigo-850 rounded-2xl flex flex-col justify-between gap-3 group transition shadow-sm">
                        <div className="space-y-1.5">
                          <strong className="block text-[11px] font-black text-white group-hover:text-indigo-300 transition line-clamp-1">{item.course_title}</strong>
                          <span className="block text-[9px] text-slate-500 font-mono truncate">{item.last_node_title}</span>
                        </div>

                        <div className="space-y-2">
                          <div className="flex justify-between items-center text-[8px] font-mono font-bold text-slate-400">
                            <span>{item.progress}% DONE</span>
                            <span>{item.duration}</span>
                          </div>
                          
                          <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden">
                            <div className="bg-indigo-500 h-full rounded-full transition-all" style={{ width: `${item.progress}%` }}></div>
                          </div>
                        </div>

                        <button 
                          onClick={() => handleStartTimer(item.course_title)}
                          className="w-full mt-1 flex items-center justify-center gap-1 py-1.5 bg-indigo-950 text-indigo-300 hover:bg-indigo-600 hover:text-white rounded-xl text-[10px] font-mono font-bold transition cursor-pointer"
                        >
                          <Play size={10} fill="currentColor" /> Resume study session
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 2. RECENT STUDY GOAL PROGRESS CARDS */}
                <div className="md:col-span-4 space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                      <Target size={14} className="text-indigo-400" /> Study Goal Checklist
                    </h3>
                    <button onClick={() => setActiveSubTab('goals')} className="text-[10px] text-indigo-400 hover:underline font-bold font-mono">Manage</button>
                  </div>

                  <div className="p-4 bg-slate-900 border border-indigo-950 rounded-2xl space-y-3 shadow-md">
                    {goals.slice(0, 3).map(goal => (
                      <div key={goal.id} className="flex gap-3 items-start border-b border-indigo-950/40 pb-2.5 last:border-0 last:pb-0">
                        <button 
                          onClick={() => handleToggleGoalComplete(goal.id)}
                          className={`mt-0.5 p-0.5 border rounded cursor-pointer ${goal.status === 'COMPLETED' ? 'bg-indigo-600 border-indigo-500 text-white' : 'border-indigo-950 text-transparent hover:text-indigo-400'}`}
                        >
                          <CheckCircle size={12} fill="currentColor" />
                        </button>
                        <div className="flex-grow space-y-0.5 text-xs">
                          <strong className={`block font-semibold ${goal.status === 'COMPLETED' ? 'text-slate-500 line-through' : 'text-white'}`}>
                            {goal.title}
                          </strong>
                          <span className="block text-[8px] font-mono text-slate-500">Target: {goal.target_date} // {goal.progress_percentage}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </section>

              {/* BENTO GRID ROW 3: BOOKMARKS & NOTES PREVIEWS */}
              <section className="grid grid-cols-1 md:grid-cols-12 gap-6">
                
                {/* 1. RECENT BOOKMARKS */}
                <div className="md:col-span-6 space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                      <Bookmark size={14} className="text-indigo-400" /> Recent Saved Bookmarks
                    </h3>
                    <button onClick={() => setActiveSubTab('bookmarks')} className="text-[10px] text-indigo-400 hover:underline font-bold font-mono">View All</button>
                  </div>

                  <div className="p-4 bg-slate-900 border border-indigo-950 rounded-2xl space-y-2">
                    {bookmarks.slice(0, 3).map(bk => (
                      <div key={bk.id} className="p-2.5 bg-slate-950 border border-indigo-950/60 rounded-xl flex justify-between items-center text-xs group hover:border-indigo-900 transition">
                        <div>
                          <strong className="block text-white group-hover:text-indigo-400 transition">{bk.title}</strong>
                          <span className="text-[8px] font-mono text-slate-500 uppercase font-bold">{bk.source_name}</span>
                        </div>
                        <button 
                          onClick={() => navigateTo(bk.url_path)}
                          className="p-1.5 bg-indigo-950/60 text-indigo-400 hover:bg-indigo-600 hover:text-white rounded-lg transition"
                          title="Open course url"
                        >
                          <ExternalLink size={12} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 2. RECENT PINNED NOTES */}
                <div className="md:col-span-6 space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                      <FileText size={14} className="text-indigo-400" /> Pinned Study Notes
                    </h3>
                    <button onClick={() => setActiveSubTab('notes')} className="text-[10px] text-indigo-400 hover:underline font-bold font-mono">Open Notepad</button>
                  </div>

                  <div className="p-4 bg-slate-900 border border-indigo-950 rounded-2xl space-y-2">
                    {notes.filter(n => n.is_pinned).slice(0, 2).map(note => (
                      <div key={note.id} className="p-3 bg-slate-950 border border-indigo-950/60 rounded-xl space-y-1.5">
                        <div className="flex justify-between items-center">
                          <strong className="text-xs text-indigo-300 font-bold">{note.title}</strong>
                          <span className="text-[8px] bg-indigo-900/40 text-indigo-300 font-mono px-2 py-0.5 rounded border border-indigo-900/60">{note.node}</span>
                        </div>
                        <p className="text-[11px] text-slate-400 leading-relaxed line-clamp-2">{note.content}</p>
                      </div>
                    ))}
                    {notes.filter(n => n.is_pinned).length === 0 && (
                      <div className="py-6 text-center text-xs text-slate-500 italic">No pinned notes yet. Pin notes for easy retrieval!</div>
                    )}
                  </div>
                </div>

              </section>

            </div>
          )}

          {/* B. COURSES / RESUME LEARNING */}
          {activeSubTab === 'courses' && (
            <div className="space-y-6 animate-fade-in">
              <div className="border-b border-indigo-950/30 pb-4">
                <h2 className="text-base font-black text-white">Resume In-Progress Course Enrollments</h2>
                <p className="text-xs text-slate-450 mt-1">Pick up right where you left off. Starting a module activates your telemetry study tracking timer.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {continueLearning.map(course => (
                  <div key={course.id} className="p-6 bg-slate-900 border border-indigo-950 hover:border-indigo-900 rounded-3xl space-y-4 transition shadow-md flex flex-col justify-between">
                    <div className="space-y-2">
                      <div className="flex justify-between items-start gap-4">
                        <h3 className="text-sm font-black text-white">{course.course_title}</h3>
                        <Badge variant="primary" className="text-[9px] uppercase font-mono font-bold tracking-wider">{course.duration}</Badge>
                      </div>
                      <p className="text-xs text-slate-400">Current Chapter Topic: <strong className="text-slate-300">{course.last_node_title}</strong></p>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between items-center text-[10px] font-mono font-bold text-slate-400">
                        <span>Course Completion status</span>
                        <span>{course.progress}%</span>
                      </div>
                      <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden">
                        <div className="bg-indigo-500 h-full rounded-full transition-all" style={{ width: `${course.progress}%` }}></div>
                      </div>
                    </div>

                    <div className="flex gap-2.5 pt-2">
                      <button 
                        onClick={() => handleStartTimer(course.course_title)}
                        className="flex-grow flex items-center justify-center gap-2 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-2xl text-xs font-bold transition cursor-pointer"
                      >
                        <Play size={12} fill="currentColor" /> Resume Video Lesson
                      </button>
                      <button 
                        onClick={() => navigateTo('/courses')}
                        className="p-2.5 bg-slate-950 hover:bg-slate-850 text-slate-300 border border-indigo-950 rounded-2xl transition cursor-pointer"
                        title="View Course Syllabus"
                      >
                        <List size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* C. TOPIC BOOKMARKS */}
          {activeSubTab === 'bookmarks' && (
            <div className="space-y-6 animate-fade-in">
              <div className="border-b border-indigo-950/30 pb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                  <h2 className="text-base font-black text-white">Syllabus & Material Bookmarks</h2>
                  <p className="text-xs text-slate-450 mt-1">Your saved library bookmarks on educational modules and ebooks.</p>
                </div>
                
                <div className="relative w-full sm:w-64">
                  <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500"><Search size={14} /></span>
                  <input 
                    type="text" 
                    placeholder="Search bookmarks..." 
                    value={bookmarkSearch}
                    onChange={(e) => setBookmarkSearch(e.target.value)}
                    className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-indigo-950 text-xs rounded-xl focus:border-indigo-600 outline-none transition"
                  />
                </div>
              </div>

              {/* BOOKMARK NEW FORM */}
              <form onSubmit={handleAddBookmark} className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl grid grid-cols-1 sm:grid-cols-4 gap-3 items-end">
                <div className="sm:col-span-2">
                  <label className="block text-[10px] font-mono font-bold text-slate-400 uppercase mb-1.5">Topic Bookmark Title</label>
                  <input 
                    type="text" 
                    required
                    placeholder="e.g. Sutra Division Rules" 
                    value={newBookmarkTitle} 
                    onChange={(e) => setNewBookmarkTitle(e.target.value)}
                    className="w-full bg-slate-950 border border-indigo-950 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-600 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-mono font-bold text-slate-400 uppercase mb-1.5">Category</label>
                  <select 
                    value={newBookmarkCategory} 
                    onChange={(e) => setNewBookmarkCategory(e.target.value)}
                    className="w-full bg-slate-950 border border-indigo-950 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-600 outline-none"
                  >
                    <option value="LMS Course">LMS Course</option>
                    <option value="eBook chapter">eBook Chapter</option>
                    <option value="Cheat-sheet">Cheat-sheet</option>
                    <option value="Custom note">Custom note</option>
                  </select>
                </div>
                <Button type="submit" className="w-full py-2.5">
                  <Plus size={14} /> Add Bookmark
                </Button>
              </form>

              {/* LIST OF BOOKMARKS */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {filteredBookmarks.map(b => (
                  <div key={b.id} className="p-4 bg-slate-900 border border-indigo-950 hover:border-indigo-850 rounded-2xl flex justify-between items-center transition group shadow-sm">
                    <div className="space-y-1 text-left">
                      <strong className="block text-xs text-white group-hover:text-indigo-400 transition">{b.title}</strong>
                      <div className="flex gap-2 text-[9px] font-mono text-slate-500 font-bold items-center">
                        <span className="uppercase text-indigo-400">{b.source_name}</span>
                        <span>•</span>
                        <span>Saved: {new Date(b.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>

                    <div className="flex gap-1.5">
                      <button 
                        onClick={() => navigateTo(b.url_path)}
                        className="p-2 bg-indigo-950/60 text-indigo-400 hover:bg-indigo-600 hover:text-white rounded-xl transition cursor-pointer"
                        title="Browse bookmarked node"
                      >
                        <ExternalLink size={12} />
                      </button>
                      <button 
                        onClick={() => handleRemoveBookmark(b.id)}
                        className="p-2 bg-slate-950 text-slate-500 hover:text-rose-500 rounded-xl transition cursor-pointer"
                        title="Delete bookmark"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </div>
                ))}
                {filteredBookmarks.length === 0 && (
                  <div className="sm:col-span-2 py-12 text-center text-xs text-slate-500 italic">No bookmarks matches current filters.</div>
                )}
              </div>
            </div>
          )}

          {/* D. LESSON STUDY NOTES */}
          {activeSubTab === 'notes' && (
            <div className="space-y-6 animate-fade-in">
              <div className="border-b border-indigo-950/30 pb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                  <h2 className="text-base font-black text-white">Markdown In-Lesson Notepad</h2>
                  <p className="text-xs text-slate-450 mt-1">Draft notes while learning chapters. Pin essential templates to your core homepage widget feed.</p>
                </div>
                
                <div className="relative w-full sm:w-64">
                  <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-slate-500"><Search size={14} /></span>
                  <input 
                    type="text" 
                    placeholder="Search notes content..." 
                    value={noteSearch}
                    onChange={(e) => setNoteSearch(e.target.value)}
                    className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-indigo-950 text-xs rounded-xl focus:border-indigo-600 outline-none transition"
                  />
                </div>
              </div>

              {/* DUAL COLUMN NOTEPAD */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
                
                {/* NEW / EDIT FORM (7 columns) */}
                <form onSubmit={handleSaveNote} className="md:col-span-7 p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4 text-left shadow-lg">
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                    {editingNoteId ? '✏️ Edit Study Note' : '📝 Create New Chapter Note'}
                  </h3>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[9px] font-mono font-bold text-slate-450 uppercase mb-1">Chapter / Subject Node</label>
                      <input 
                        type="text" 
                        required
                        value={newNoteNode}
                        onChange={(e) => setNewNoteNode(e.target.value)}
                        placeholder="e.g. Vedic Division"
                        className="w-full bg-slate-950 border border-indigo-950 rounded-xl px-3 py-1.5 text-xs text-white focus:border-indigo-600 outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-[9px] font-mono font-bold text-slate-450 uppercase mb-1">Note Heading</label>
                      <input 
                        type="text" 
                        required
                        value={newNoteTitle}
                        onChange={(e) => setNewNoteTitle(e.target.value)}
                        placeholder="e.g. Balancing rule variables"
                        className="w-full bg-slate-950 border border-indigo-950 rounded-xl px-3 py-1.5 text-xs text-white focus:border-indigo-600 outline-none"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-[9px] font-mono font-bold text-slate-450 uppercase mb-1">Markdown Body content</label>
                    <textarea 
                      required
                      value={newNoteContent}
                      onChange={(e) => setNewNoteContent(e.target.value)}
                      rows={6}
                      placeholder="Markdown notes, code samples, or sutras blueprints..."
                      className="w-full bg-slate-950 border border-indigo-950 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-600 outline-none font-mono"
                    ></textarea>
                  </div>

                  <div className="flex gap-2">
                    <Button type="submit" className="flex-grow py-2.5">
                      {editingNoteId ? 'Update Ledger Note' : 'Log Note'}
                    </Button>
                    {editingNoteId && (
                      <Button 
                        type="button" 
                        variant="outline" 
                        onClick={() => {
                          setEditingNoteId(null);
                          setNewNoteTitle('');
                          setNewNoteContent('');
                        }}
                      >
                        Cancel
                      </Button>
                    )}
                  </div>
                </form>

                {/* NOTE LOGS CATALOG (5 columns) */}
                <div className="md:col-span-5 space-y-4 text-left">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Note Registers</h3>
                  <div className="space-y-3 max-h-[350px] overflow-y-auto scrollbar-thin">
                    {filteredNotes.map(note => (
                      <div key={note.id} className="p-4 bg-slate-900 border border-indigo-950 rounded-2xl space-y-2.5 hover:border-indigo-900 transition">
                        <div className="flex justify-between items-start gap-4">
                          <div>
                            <span className="text-[8px] bg-indigo-950 text-indigo-400 font-mono px-2 py-0.5 rounded border border-indigo-900">{note.node}</span>
                            <strong className="block text-xs text-white font-semibold mt-1.5">{note.title}</strong>
                          </div>

                          <div className="flex gap-1">
                            <button 
                              onClick={() => handleTogglePinNote(note.id)}
                              className={`p-1.5 rounded-lg border transition cursor-pointer ${note.is_pinned ? 'bg-indigo-600 border-indigo-500 text-white' : 'border-indigo-950/80 text-slate-500 hover:text-white'}`}
                              title={note.is_pinned ? "Unpin note from dashboard" : "Pin note to dashboard"}
                            >
                              <Pin size={10} />
                            </button>
                            <button 
                              onClick={() => handleEditNote(note)}
                              className="p-1.5 bg-slate-950 border border-indigo-950 text-indigo-400 hover:bg-indigo-600 hover:text-white rounded-lg transition cursor-pointer"
                              title="Edit note"
                            >
                              ✏️
                            </button>
                            <button 
                              onClick={() => handleDeleteNote(note.id)}
                              className="p-1.5 bg-slate-950 border border-indigo-950 text-slate-500 hover:text-rose-500 rounded-lg transition cursor-pointer"
                              title="Delete note"
                            >
                              <Trash2 size={10} />
                            </button>
                          </div>
                        </div>

                        <p className="text-[11px] text-slate-400 font-mono leading-relaxed bg-slate-950/50 p-2.5 rounded-xl border border-indigo-950/40 truncate">
                          {note.content}
                        </p>
                      </div>
                    ))}
                    {filteredNotes.length === 0 && (
                      <div className="py-12 text-center text-xs text-slate-500 italic">No active notes logged.</div>
                    )}
                  </div>
                </div>

              </div>
            </div>
          )}

          {/* E. STUDY GOALS */}
          {activeSubTab === 'goals' && (
            <div className="space-y-6 animate-fade-in">
              <div className="border-b border-indigo-950/30 pb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                  <h2 className="text-base font-black text-white">Personal Study Targets & Goals</h2>
                  <p className="text-xs text-slate-450 mt-1">Configure weekly milestones, adjust task sliders, and view progress tickers.</p>
                </div>

                <div className="flex gap-1.5 bg-slate-900 border border-indigo-950 p-1 rounded-xl text-[10px] font-mono font-bold select-none">
                  {(['ALL', 'PENDING', 'IN_PROGRESS', 'COMPLETED'] as const).map(f => (
                    <button 
                      key={f}
                      onClick={() => setGoalFilter(f)}
                      className={`px-3 py-1 rounded-lg transition cursor-pointer ${goalFilter === f ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'}`}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>

              {/* GOAL GENERATION GRID */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
                
                {/* NEW GOAL FORM (5 columns) */}
                <form onSubmit={handleAddGoal} className="md:col-span-5 p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4 text-left shadow-lg">
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                    <Target size={14} className="text-indigo-400" /> Spawn New Study Target
                  </h3>

                  <div>
                    <label className="block text-[9px] font-mono font-bold text-slate-450 uppercase mb-1">Target Milestone Title</label>
                    <input 
                      type="text" 
                      required
                      placeholder="e.g. Finish Jee (main) physics syllabus" 
                      value={newGoalTitle} 
                      onChange={(e) => setNewGoalTitle(e.target.value)}
                      className="w-full bg-slate-950 border border-indigo-950 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-600 outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-[9px] font-mono font-bold text-slate-450 uppercase mb-1">Target Description / Actions</label>
                    <textarea 
                      placeholder="Outline exercises, chapters, or specific videos to finalize..." 
                      value={newGoalDesc} 
                      onChange={(e) => setNewGoalDesc(e.target.value)}
                      rows={3}
                      className="w-full bg-slate-950 border border-indigo-950 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-600 outline-none"
                    ></textarea>
                  </div>

                  <div>
                    <label className="block text-[9px] font-mono font-bold text-slate-450 uppercase mb-1">Target Date</label>
                    <input 
                      type="date" 
                      required
                      value={newGoalTarget} 
                      onChange={(e) => setNewGoalTarget(e.target.value)}
                      className="w-full bg-slate-950 border border-indigo-950 rounded-xl px-3 py-1.5 text-xs text-white focus:border-indigo-600 outline-none"
                    />
                  </div>

                  <Button type="submit" className="w-full py-2.5">
                    <Plus size={14} /> Establish Milestone Target
                  </Button>
                </form>

                {/* ACTIVE CHECKLIST (7 columns) */}
                <div className="md:col-span-7 space-y-4 text-left">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Milestone Progress checklist</h3>

                  <div className="space-y-4 max-h-[380px] overflow-y-auto scrollbar-thin pr-1">
                    {filteredGoals.map(g => (
                      <div key={g.id} className="p-4 bg-slate-900 border border-indigo-950 rounded-2xl space-y-3 shadow-md hover:border-indigo-900 transition">
                        <div className="flex justify-between items-start gap-4">
                          <div className="flex gap-3 items-start">
                            <button 
                              onClick={() => handleToggleGoalComplete(g.id)}
                              className={`mt-0.5 p-0.5 border rounded cursor-pointer ${g.status === 'COMPLETED' ? 'bg-indigo-600 border-indigo-500 text-white' : 'border-indigo-950 text-transparent hover:text-indigo-400'}`}
                            >
                              <CheckCircle size={14} fill="currentColor" />
                            </button>
                            <div className="space-y-1">
                              <strong className={`block text-xs font-black ${g.status === 'COMPLETED' ? 'text-slate-500 line-through' : 'text-white'}`}>
                                {g.title}
                              </strong>
                              {g.description && <p className="text-[10px] text-slate-450 leading-relaxed">{g.description}</p>}
                            </div>
                          </div>

                          <div className="flex items-center gap-1.5">
                            <Badge variant={g.status === 'COMPLETED' ? 'success' : g.status === 'IN_PROGRESS' ? 'primary' : 'warning'}>
                              {g.status}
                            </Badge>
                            <button 
                              onClick={() => handleDeleteGoal(g.id)}
                              className="p-1 hover:bg-slate-950 text-slate-500 hover:text-rose-500 rounded transition cursor-pointer"
                              title="Delete goal"
                            >
                              <Trash2 size={12} />
                            </button>
                          </div>
                        </div>

                        {/* SLIDER CONTROLS */}
                        <div className="space-y-1.5 pt-2 border-t border-indigo-950/40">
                          <div className="flex justify-between items-center text-[9px] font-mono font-bold text-slate-400">
                            <span>ADJUST PROGRESS RATIO:</span>
                            <span className="text-indigo-400">{g.progress_percentage}%</span>
                          </div>

                          <div className="flex items-center gap-3">
                            <input 
                              type="range" 
                              min="0" 
                              max="100" 
                              value={g.progress_percentage}
                              onChange={(e) => handleUpdateGoalSlider(g.id, parseInt(e.target.value))}
                              className="flex-grow h-1 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                    {filteredGoals.length === 0 && (
                      <div className="py-12 text-center text-xs text-slate-500 italic">No study targets matches this filter category.</div>
                    )}
                  </div>
                </div>

              </div>
            </div>
          )}

          {/* F. STUDY CALENDAR */}
          {activeSubTab === 'calendar' && (
            <div className="space-y-6 animate-fade-in">
              <div className="border-b border-indigo-950/30 pb-4">
                <h2 className="text-base font-black text-white">Unified Learning Study Schedule</h2>
                <p className="text-xs text-slate-450 mt-1">LMS Exam sessions dates, scheduled Live seminar classes, and personalized study reminders.</p>
              </div>

              {/* CALENDAR COLUMN SPLIT */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
                
                {/* 1. INTERACTIVE STUDY EVENT CREATION (5 columns) */}
                <form onSubmit={handleAddCalendarEvent} className="md:col-span-5 p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4 text-left shadow-lg">
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                    <CalendarDays size={14} className="text-indigo-400" /> Log Custom Reminder
                  </h3>

                  <div>
                    <label className="block text-[9px] font-mono font-bold text-slate-450 uppercase mb-1">Event Topic</label>
                    <input 
                      type="text" 
                      required
                      placeholder="e.g. Physics chapter mock test" 
                      value={newCalendarTitle} 
                      onChange={(e) => setNewCalendarTitle(e.target.value)}
                      className="w-full bg-slate-950 border border-indigo-950 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-600 outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-[9px] font-mono font-bold text-slate-450 uppercase mb-1">Brief Description</label>
                    <textarea 
                      placeholder="Provide additional details regarding syllabus links or preparation material..." 
                      value={newCalendarDesc} 
                      onChange={(e) => setNewCalendarDesc(e.target.value)}
                      rows={2}
                      className="w-full bg-slate-950 border border-indigo-950 rounded-xl px-3 py-2 text-xs text-white focus:border-indigo-600 outline-none"
                    ></textarea>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-[9px] font-mono font-bold text-slate-450 uppercase mb-1">Reminder Date</label>
                      <input 
                        type="date" 
                        required
                        value={newCalendarDate} 
                        onChange={(e) => setNewCalendarDate(e.target.value)}
                        className="w-full bg-slate-950 border border-indigo-950 rounded-xl px-3 py-1.5 text-xs text-white focus:border-indigo-600 outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-[9px] font-mono font-bold text-slate-450 uppercase mb-1">Hour Time</label>
                      <input 
                        type="time" 
                        required
                        value={newCalendarTime} 
                        onChange={(e) => setNewCalendarTime(e.target.value)}
                        className="w-full bg-slate-950 border border-indigo-950 rounded-xl px-3 py-1.5 text-xs text-white focus:border-indigo-600 outline-none"
                      />
                    </div>
                  </div>

                  <Button type="submit" className="w-full py-2.5">
                    <Plus size={14} /> Schedule Event
                  </Button>
                </form>

                {/* 2. AGENDA CALENDAR SCHEDULE (7 columns) */}
                <div className="md:col-span-7 space-y-4 text-left">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Upcoming Calendar Events</h3>

                  <div className="space-y-4 max-h-[380px] overflow-y-auto scrollbar-thin pr-1">
                    {calendarEvents.map(ev => {
                      const eventDateTime = new Date(ev.starts_at);
                      return (
                        <div key={ev.id} className="p-4 bg-slate-900 border border-indigo-950 rounded-2xl flex gap-4 shadow-sm">
                          <div className="px-3.5 py-3 bg-indigo-950 border border-indigo-900/60 text-center rounded-xl flex flex-col justify-center select-none shrink-0 h-fit">
                            <span className="block text-[8px] uppercase font-mono font-bold text-indigo-400">
                              {eventDateTime.toLocaleString('default', { month: 'short' })}
                            </span>
                            <strong className="block text-sm font-mono font-black text-white mt-0.5">
                              {eventDateTime.getDate()}
                            </strong>
                          </div>

                          <div className="flex-grow space-y-1.5 text-xs">
                            <div className="flex justify-between items-start gap-4">
                              <strong className="text-white font-bold">{ev.title}</strong>
                              <span className="text-[9px] font-mono text-indigo-400 bg-indigo-950 px-2 py-0.5 rounded border border-indigo-900">
                                {eventDateTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </span>
                            </div>
                            {ev.description && <p className="text-[11px] text-slate-450 leading-relaxed">{ev.description}</p>}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

              </div>
            </div>
          )}

          {/* G. ACHIEVEMENTS VAULT */}
          {activeSubTab === 'achievements' && (
            <div className="space-y-6 animate-fade-in">
              <div className="border-b border-indigo-950/30 pb-4">
                <h2 className="text-base font-black text-white">Gamified Achievements & Credentials Vault</h2>
                <p className="text-xs text-slate-455 mt-1">View unlocked achievement badges, platform titles, and cumulative study targets milestones.</p>
              </div>

              {/* ACHIEVEMENTS GRID */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                
                <div className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl text-center space-y-3 relative overflow-hidden group">
                  <div className="absolute top-2 right-2 text-[9px] font-mono text-emerald-400 font-bold bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-900/60">UNLOCKED</div>
                  <div className="p-4 bg-yellow-500/10 text-yellow-500 rounded-full w-fit mx-auto border border-yellow-500/20 group-hover:scale-110 transition duration-300">
                    <Zap size={24} className="fill-current" />
                  </div>
                  <div className="space-y-1">
                    <strong className="block text-xs text-white">Vedic Fast Calculator</strong>
                    <p className="text-[10px] text-slate-400 leading-relaxed">Completed 5 consecutive math shortcut division lesson modules.</p>
                  </div>
                  <div className="text-[9px] text-slate-500 font-mono font-bold bg-slate-950 py-1 rounded-lg">AWARD: +150 XP</div>
                </div>

                <div className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl text-center space-y-3 relative overflow-hidden group">
                  <div className="absolute top-2 right-2 text-[9px] font-mono text-emerald-400 font-bold bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-900/60">UNLOCKED</div>
                  <div className="p-4 bg-indigo-500/10 text-indigo-400 rounded-full w-fit mx-auto border border-indigo-500/20 group-hover:scale-110 transition duration-300">
                    <Award size={24} />
                  </div>
                  <div className="space-y-1">
                    <strong className="block text-xs text-white">Dedicated Scholar</strong>
                    <p className="text-[10px] text-slate-400 leading-relaxed">Logged more than 300 minutes of authenticated study sessions telemetry.</p>
                  </div>
                  <div className="text-[9px] text-slate-500 font-mono font-bold bg-slate-950 py-1 rounded-lg">AWARD: +300 XP</div>
                </div>

                <div className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl text-center space-y-3 relative overflow-hidden opacity-60 group">
                  <div className="absolute top-2 right-2 text-[9px] font-mono text-slate-400 font-bold bg-slate-950 px-2 py-0.5 rounded border border-indigo-950">LOCKED</div>
                  <div className="p-4 bg-slate-950 text-slate-500 rounded-full w-fit mx-auto border border-slate-900">
                    <CheckSquare size={24} />
                  </div>
                  <div className="space-y-1">
                    <strong className="block text-xs text-white">Continuous Streak Master</strong>
                    <p className="text-[10px] text-slate-400 leading-relaxed">Acquire a continuous study active streak of 15 calendar days.</p>
                  </div>
                  <div className="text-[9px] text-slate-500 font-mono font-bold bg-slate-950 py-1 rounded-lg">AWARD: +500 XP</div>
                </div>

              </div>
            </div>
          )}

          {activeSubTab === 'ai' && (
            <div className="animate-fade-in">
              <StudentAiPortal />
            </div>
          )}

        </main>
      </div>

    </div>
  );
};

export default StudentDashboard;
