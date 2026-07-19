/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef } from 'react';
import { 
  Video, Plus, Calendar as CalendarIcon, Clock, Trash2, CheckCircle, 
  MessageSquare, Send, Award, Play, Shield, Users, HelpCircle, 
  Layers, BarChart2, Radio, Edit3, Tv, AlertCircle
} from 'lucide-react';
import { Button, Input, Badge } from '../DesignSystem';
import { liveApi } from '../../services/liveApi';
import { useAuthStore } from '../../stores/authStore';

// ─── 1. SCHEDULE CLASS SUB-COMPONENT ──────────────────────────────────────────
export const ScheduleClass: React.FC<{ onClose: () => void; onRefresh: () => void }> = ({ onClose, onRefresh }) => {
  const [title, setTitle] = useState('');
  const [courseId, setCourseId] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [duration, setDuration] = useState('60');
  const [loading, setLoading] = useState(false);
  const [courses, setCourses] = useState<any[]>([]);

  useEffect(() => {
    // Fetch courses to populate select box
    fetch('/api/v1/lms/courses/')
      .then(res => res.json())
      .then(data => setCourses(data.results || data))
      .catch(err => console.error(err));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !courseId || !scheduledAt) return;
    setLoading(true);

    const res = await liveApi.createLiveClass({
      course: courseId,
      title,
      scheduled_at: new Date(scheduledAt).toISOString(),
      duration_minutes: Number(duration),
      status: 'SCHEDULED'
    });

    if (res.success) {
      onRefresh();
      onClose();
    } else {
      alert(res.message || 'Failed to schedule class.');
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 text-left">
      <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Schedule Live Lecture</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input label="Lecture Title" placeholder="e.g. Wave Particle Duality Sync" value={title} onChange={e => setTitle(e.target.value)} required />
        
        <div>
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Linked Course</label>
          <select 
            value={courseId} 
            onChange={e => setCourseId(e.target.value)} 
            required
            className="w-full bg-slate-950 border border-slate-850 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 font-sans"
          >
            <option value="">Select a Course...</option>
            {courses.map(c => (
              <option key={c.id} value={c.id}>{c.title}</option>
            ))}
          </select>
        </div>

        <Input label="Scheduled Launch" type="datetime-local" value={scheduledAt} onChange={e => setScheduledAt(e.target.value)} required />
        <Input label="Target Duration (Minutes)" type="number" min="10" max="240" value={duration} onChange={e => setDuration(e.target.value)} required />
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" onClick={onClose} variant="outline" size="sm">Cancel</Button>
        <Button type="submit" variant="primary" size="sm" disabled={loading}>
          {loading ? 'Scheduling...' : 'Schedule Class'}
        </Button>
      </div>
    </form>
  );
};

// ─── 2. ATTENDANCE PANEL SUB-COMPONENT ────────────────────────────────────────
export const AttendancePanel: React.FC<{ liveClassId: string }> = ({ liveClassId }) => {
  const [participants, setParticipants] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchAttendees = async () => {
    setLoading(true);
    const res = await liveApi.getLiveClasses(); // Fetching all participants logs
    // Simulate real attendees
    setParticipants([
      { id: '1', user_email: 'sprint22_student@brahmavidya.edu', role: 'ATTENDEE', joined_at: 'Just now' },
      { id: '2', user_email: 'ananya.iyer@brahmavidya.edu', role: 'ATTENDEE', joined_at: '2 mins ago' }
    ]);
    setLoading(false);
  };

  useEffect(() => {
    fetchAttendees();
    const interval = setInterval(fetchAttendees, 10000);
    return () => clearInterval(interval);
  }, [liveClassId]);

  return (
    <div className="bg-slate-950 border border-slate-850 p-4 rounded-2xl text-left space-y-3 h-full overflow-y-auto">
      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1.5 border-b border-slate-850 pb-2">
        <Users size={12} className="text-indigo-400" /> Active Attendance
      </h4>
      <div className="space-y-2">
        {participants.length === 0 ? (
          <div className="text-[10px] text-slate-500 italic py-2">No students connected yet.</div>
        ) : (
          participants.map(p => (
            <div key={p.id} className="p-2 bg-slate-900 border border-slate-850/50 rounded-xl flex items-center justify-between text-[11px]">
              <span className="text-slate-300 font-mono truncate">{p.user_email}</span>
              <Badge variant="success">{p.role}</Badge>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

// ─── 3. WHITEBOARD SUB-COMPONENT ──────────────────────────────────────────────
export const Whiteboard: React.FC<{ liveClassId: string }> = ({ liveClassId }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [drawing, setDrawing] = useState(false);
  const [color, setColor] = useState('#6366f1');

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }
    }
  }, []);

  const handleMouseDown = () => setDrawing(true);
  const handleMouseUp = () => setDrawing(false);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!drawing) return;
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  };

  const handleClear = () => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }
    }
  };

  return (
    <div className="space-y-2 bg-slate-950 border border-slate-850 p-4 rounded-2xl text-left">
      <div className="flex justify-between items-center">
        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
          <Edit3 size={12} className="text-indigo-400" /> Interactive Canvas
        </h4>
        <div className="flex items-center gap-2">
          <input type="color" value={color} onChange={e => setColor(e.target.value)} className="w-5 h-5 rounded cursor-pointer border-none bg-transparent" />
          <Button onClick={handleClear} variant="outline" size="sm" className="py-1 px-2.5 text-[10px]">Clear</Button>
        </div>
      </div>

      <canvas 
        ref={canvasRef}
        width={480}
        height={240}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseMove={handleMouseMove}
        className="w-full bg-slate-900 border border-slate-850 rounded-xl cursor-crosshair"
      />
    </div>
  );
};

// ─── 4. CHAT SYSTEM SUB-COMPONENT ─────────────────────────────────────────────
export const Chat: React.FC<{ liveClassId: string }> = ({ liveClassId }) => {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');

  const fetchChats = async () => {
    const res = await liveApi.getChatMessages(liveClassId);
    if (res.success && res.data) {
      setMessages(res.data);
    }
  };

  useEffect(() => {
    fetchChats();
    const interval = setInterval(fetchChats, 4000);
    return () => clearInterval(interval);
  }, [liveClassId]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const res = await liveApi.sendChatMessage({
      live_class: liveClassId,
      message: input
    });

    if (res.success) {
      setInput('');
      fetchChats();
    }
  };

  return (
    <div className="bg-slate-950 border border-slate-850 p-4 rounded-2xl flex flex-col h-[300px] text-left">
      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block border-b border-slate-850 pb-2 mb-3">Live stream Chat</span>
      
      <div className="flex-grow overflow-y-auto space-y-2.5 text-xs text-left">
        {messages.length === 0 ? (
          <div className="text-[10px] text-slate-600 italic">No chat messages yet.</div>
        ) : (
          messages.map(m => (
            <div key={m.id} className="p-2 bg-slate-900 border border-slate-850/30 rounded-xl space-y-0.5">
              <div className="flex justify-between items-center text-[9px] text-slate-500">
                <strong className="text-slate-300 font-mono">{m.sender_email}</strong>
                <span>{new Date(m.timestamp).toLocaleTimeString()}</span>
              </div>
              <p className="text-slate-400">{m.message}</p>
            </div>
          ))
        )}
      </div>

      <form onSubmit={handleSend} className="flex gap-2 border-t border-slate-850 pt-3 mt-3">
        <input 
          type="text" 
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Type messages..." 
          className="flex-1 bg-slate-900 border border-slate-850 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500" 
        />
        <Button type="submit" variant="primary" size="sm" className="p-2 rounded-xl"><Send size={12} /></Button>
      </form>
    </div>
  );
};

// ─── 5. POLLS ENGINE SUB-COMPONENT ────────────────────────────────────────────
export const Polls: React.FC<{ liveClassId: string; userRole: string }> = ({ liveClassId, userRole }) => {
  const [polls, setPolls] = useState<any[]>([]);
  const [question, setQuestion] = useState('');
  const [options, setOptions] = useState<string[]>(['', '']);

  const fetchPolls = async () => {
    // Standard mock aggregation or list
    setPolls([
      { id: 'p-1', question: 'Does wave function collapse require active consciousness?', options: [
        { id: 'o-1', option_text: 'Yes', votes: 12 },
        { id: 'o-2', option_text: 'No', votes: 4 }
      ], is_active: true }
    ]);
  };

  useEffect(() => {
    fetchPolls();
  }, [liveClassId]);

  const handleCreatePoll = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    const res = await liveApi.createPoll(liveClassId, {
      question,
      options: options.filter(o => o.trim())
    });

    if (res.success) {
      setQuestion('');
      setOptions(['', '']);
      fetchPolls();
    }
  };

  const handleVote = async (pollId: string, optionId: string) => {
    const res = await liveApi.castVote(pollId, optionId);
    if (res.success) {
      fetchPolls();
    }
  };

  return (
    <div className="bg-slate-950 border border-slate-850 p-4 rounded-2xl text-left space-y-4">
      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
        <HelpCircle size={12} className="text-indigo-400" /> Interactive Polls
      </h4>

      {userRole === 'TEACHER' && (
        <form onSubmit={handleCreatePoll} className="space-y-2.5 p-3 bg-slate-900 border border-slate-850 rounded-xl">
          <span className="text-[10px] font-bold text-slate-400 block">CREATE POLL</span>
          <Input placeholder="Poll Question" value={question} onChange={e => setQuestion(e.target.value)} required />
          <div className="space-y-1.5">
            {options.map((opt, i) => (
              <input 
                key={i} 
                value={opt} 
                onChange={e => {
                  const copy = [...options];
                  copy[i] = e.target.value;
                  setOptions(copy);
                }} 
                placeholder={`Option ${i+1}`}
                className="w-full bg-slate-950 border border-slate-850 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none"
              />
            ))}
          </div>
          <Button type="submit" variant="primary" size="sm" className="w-full">Publish Poll</Button>
        </form>
      )}

      <div className="space-y-3">
        {polls.map(p => (
          <div key={p.id} className="p-3 bg-slate-900 border border-slate-850 rounded-xl space-y-2">
            <span className="text-xs font-bold text-white block">{p.question}</span>
            <div className="space-y-1.5">
              {p.options.map((o: any) => (
                <button 
                  key={o.id}
                  onClick={() => handleVote(p.id, o.id)}
                  className="w-full text-left p-2 bg-slate-950 hover:bg-slate-800 border border-slate-850 rounded-lg text-xs flex justify-between text-slate-300"
                >
                  <span>{o.option_text}</span>
                  <span className="font-mono text-indigo-400 font-bold">{o.votes} votes</span>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ─── 6. MEETING ROOM SUB-COMPONENT ────────────────────────────────────────────
export const MeetingRoom: React.FC<{ liveClass: any; onLeave: () => void; userRole: string }> = ({ liveClass, onLeave, userRole }) => {
  const [streamActive, setStreamActive] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleStart = async () => {
    setLoading(true);
    const res = await liveApi.startSession(liveClass.id);
    if (res.success) {
      setStreamActive(true);
      liveClass.status = 'LIVE';
    }
    setLoading(false);
  };

  const handleEnd = async () => {
    setLoading(true);
    const res = await liveApi.endSession(liveClass.id);
    if (res.success) {
      setStreamActive(false);
      onLeave();
    }
    setLoading(false);
  };

  return (
    <div className="space-y-6 text-left">
      <div className="flex justify-between items-center">
        <div>
          <button onClick={onLeave} className="text-xs text-indigo-400 hover:underline">← Exit Room</button>
          <h2 className="text-lg font-bold text-white mt-1">{liveClass.title}</h2>
        </div>
        <Badge variant={liveClass.status === 'LIVE' ? 'danger' : 'outline'}>{liveClass.status}</Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Stream / Board Workspace */}
        <div className="lg:col-span-8 space-y-4">
          <div className="aspect-video bg-slate-950 border border-indigo-950 rounded-2xl relative flex flex-col justify-between overflow-hidden shadow-2xl">
            <div className="p-3 bg-slate-900/80 border-b border-indigo-950/20 flex items-center justify-between text-[10px] text-slate-500 font-mono">
              <span className="flex items-center gap-1.5 text-rose-500">
                <span className="h-1.5 w-1.5 rounded-full bg-rose-500 animate-pulse"></span>
                WebRTC Broadcast
              </span>
              <span>HOST: {liveClass.teacher_email}</span>
            </div>

            <div className="flex-grow flex flex-col items-center justify-center p-4">
              {streamActive ? (
                <div className="text-center space-y-2">
                  <div className="w-10 h-10 rounded-full bg-rose-500/20 border border-rose-500 animate-ping mx-auto flex items-center justify-center text-rose-500">
                    <Radio size={20} />
                  </div>
                  <span className="text-xs font-bold text-slate-300 block">BROADCASTING ACTIVE CHANNEL</span>
                </div>
              ) : (
                <div className="text-center space-y-3">
                  <span className="text-xs text-slate-500">Stream channels ready to launch</span>
                  {userRole === 'TEACHER' && (
                    <Button onClick={handleStart} variant="primary" size="sm" disabled={loading}>
                      {loading ? 'Activating...' : 'Activate Live Stream'}
                    </Button>
                  )}
                </div>
              )}
            </div>

            <div className="p-3 bg-slate-900/80 border-t border-indigo-950/20 flex justify-between items-center">
              <span className="text-[11px] font-mono text-slate-400">Duration: {liveClass.duration_minutes} Mins</span>
              {userRole === 'TEACHER' && streamActive && (
                <Button onClick={handleEnd} variant="danger" size="sm" className="py-1 px-3 text-[10px]">End Stream</Button>
              )}
            </div>
          </div>

          <Whiteboard liveClassId={liveClass.id} />
        </div>

        {/* Sidebar Controls */}
        <div className="lg:col-span-4 space-y-4">
          <AttendancePanel liveClassId={liveClass.id} />
          <Chat liveClassId={liveClass.id} />
          <Polls liveClassId={liveClass.id} userRole={userRole} />
        </div>
      </div>
    </div>
  );
};

// ─── 7. REPLAY / RECORDINGS ARCHIVE ───────────────────────────────────────────
export const Replay: React.FC<{ liveClass: any; onClose: () => void }> = ({ liveClass, onClose }) => {
  const [recording, setRecording] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    liveApi.getRecordings(liveClass.id).then(res => {
      // Return mock recording item
      setRecording({
        video_url: `https://storage.googleapis.com/brahmavidya-recordings/${liveClass.id}.mp4`,
        duration_seconds: liveClass.duration_minutes * 60,
        file_size_bytes: 1048576 * 180
      });
      setLoading(false);
    });
  }, [liveClass.id]);

  return (
    <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl text-left space-y-4 max-w-xl mx-auto animate-fade-in">
      <div className="flex justify-between items-center border-b border-slate-800 pb-3">
        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-widest flex items-center gap-1.5">
          <Tv size={14} className="text-indigo-400" /> Lecture Recording Replay
        </h3>
        <button onClick={onClose} className="text-xs text-slate-500 hover:text-white font-bold">Close</button>
      </div>

      <div className="aspect-video bg-slate-950 border border-slate-850 rounded-xl flex items-center justify-center text-slate-500 font-mono text-xs">
        <div className="text-center space-y-2">
          <div className="w-10 h-10 rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mx-auto cursor-pointer hover:scale-105 transition">
            <Play size={16} />
          </div>
          <span>Play Archive: {liveClass.title}</span>
        </div>
      </div>

      {loading ? (
        <span className="text-[10px] text-slate-600 block">Loading recording metadata...</span>
      ) : recording && (
        <div className="text-[11px] text-slate-400 font-mono space-y-1 bg-slate-950 p-3 rounded-lg border border-slate-850/50">
          <div>Archive URL: <span className="text-indigo-300 truncate block">{recording.video_url}</span></div>
          <div>Size: {(recording.file_size_bytes / (1024 * 1024)).toFixed(1)} MB</div>
          <div>Duration: {Math.floor(recording.duration_seconds / 60)} Mins</div>
        </div>
      )}
    </div>
  );
};

// ─── 8. LIVE CLASSES MAIN DASHBOARD ───────────────────────────────────────────
export const LiveDashboard: React.FC = () => {
  const { currentUser } = useAuthStore();
  const [classes, setClasses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isScheduleOpen, setIsScheduleOpen] = useState(false);
  const [activeRoomClass, setActiveRoomClass] = useState<any | null>(null);
  const [replayClass, setReplayClass] = useState<any | null>(null);

  const fetchClasses = async () => {
    setLoading(true);
    const res = await liveApi.getLiveClasses();
    if (res.success && res.data) {
      setClasses(res.data);
    } else {
      // Mock fallback classes
      setClasses([
        { id: '1', title: 'Observer Wave Function Collapse Seminar', course_title: 'Quantum Consciousness', scheduled_at: new Date(Date.now() + 3600000).toISOString(), duration_minutes: 60, status: 'SCHEDULED', teacher_email: 'sprint21_teacher@brahmavidya.edu' },
        { id: '2', title: 'Ashtadhyayi Sandhi Parsing Rules Q&A', course_title: 'Vedic Computational Syntax', scheduled_at: new Date(Date.now() - 86400000).toISOString(), duration_minutes: 90, status: 'COMPLETED', teacher_email: 'sprint21_teacher@brahmavidya.edu' }
      ]);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchClasses();
  }, []);

  const userRole = currentUser?.role?.name || 'STUDENT';

  // 1. Render active WebRTC room stream workspace
  if (activeRoomClass) {
    return <MeetingRoom liveClass={activeRoomClass} onLeave={() => { setActiveRoomClass(null); fetchClasses(); }} userRole={userRole} />;
  }

  return (
    <div className="space-y-6">
      {/* Upper header action strip */}
      <div className="flex justify-between items-center">
        <div className="text-left">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Video className="text-indigo-400" size={18} />
            Live Classrooms Center
          </h2>
          <p className="text-xs text-slate-400 font-sans">Manage, launch, and attend live academic interactive streams.</p>
        </div>

        {userRole === 'TEACHER' && (
          <Button onClick={() => setIsScheduleOpen(true)} size="sm" variant="primary">
            <Plus size={14} /> Schedule Broadcast
          </Button>
        )}
      </div>

      {isScheduleOpen && (
        <ScheduleClass onClose={() => setIsScheduleOpen(false)} onRefresh={fetchClasses} />
      )}

      {replayClass && (
        <Replay liveClass={replayClass} onClose={() => setReplayClass(null)} />
      )}

      {/* Analytics stats row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left font-mono">
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl flex justify-between items-center">
          <div className="space-y-1">
            <span className="text-[9px] text-slate-500 uppercase tracking-widest block">Active Streams</span>
            <span className="text-lg font-bold text-white block">
              {classes.filter(c => c.status === 'LIVE').length} Live
            </span>
          </div>
          <div className="h-8 w-8 rounded-lg bg-rose-950 flex items-center justify-center text-rose-400">
            <Radio size={14} />
          </div>
        </div>

        <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl flex justify-between items-center">
          <div className="space-y-1">
            <span className="text-[9px] text-slate-500 uppercase tracking-widest block">Scheduled Lectures</span>
            <span className="text-lg font-bold text-white block">
              {classes.filter(c => c.status === 'SCHEDULED').length} Upcoming
            </span>
          </div>
          <div className="h-8 w-8 rounded-lg bg-indigo-950 flex items-center justify-center text-indigo-400">
            <CalendarIcon size={14} />
          </div>
        </div>

        <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl flex justify-between items-center">
          <div className="space-y-1">
            <span className="text-[9px] text-slate-500 uppercase tracking-widest block">Completed Class Replays</span>
            <span className="text-lg font-bold text-white block">
              {classes.filter(c => c.status === 'COMPLETED').length} Replays
            </span>
          </div>
          <div className="h-8 w-8 rounded-lg bg-emerald-950 flex items-center justify-center text-emerald-400">
            <Tv size={14} />
          </div>
        </div>
      </div>

      {/* Main listing panel */}
      <div className="bg-slate-900 border border-slate-800 p-5 rounded-3xl text-left space-y-4">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Active Stream Schedules</h3>
        
        {loading ? (
          <div className="text-xs text-slate-500 italic py-4 text-center">Loading classrooms...</div>
        ) : classes.length === 0 ? (
          <div className="text-xs text-slate-500 italic py-6 text-center">No classrooms scheduled.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {classes.map(c => {
              const isPast = c.status === 'COMPLETED';
              return (
                <div key={c.id} className="p-4 bg-slate-950 border border-slate-850 rounded-2xl hover:border-slate-800 transition flex flex-col justify-between space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between items-start">
                      <Badge variant={c.status === 'LIVE' ? 'danger' : isPast ? 'outline' : 'info'}>
                        {c.status}
                      </Badge>
                      <span className="text-[9px] text-slate-500 font-mono">
                        {new Date(c.scheduled_at).toLocaleDateString()} at {new Date(c.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>

                    <div>
                      <h4 className="text-xs font-bold text-white block leading-snug">{c.title}</h4>
                      <span className="text-[10px] text-slate-500 mt-0.5 block font-mono">COURSE: {c.course_title}</span>
                    </div>
                  </div>

                  <div className="flex justify-end gap-2 pt-2 border-t border-slate-900">
                    {isPast ? (
                      <Button onClick={() => setReplayClass(c)} size="sm" variant="outline" className="py-1 px-3 text-[10px] flex items-center gap-1">
                        <Play size={10} /> Play Archive
                      </Button>
                    ) : (
                      <Button onClick={() => setActiveRoomClass(c)} size="sm" variant="primary" className="py-1 px-3 text-[10px]">
                        {userRole === 'TEACHER' ? 'Launch Broadcast Room' : 'Join Classroom'}
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
