/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Button, Input } from '../DesignSystem';
import { Calendar, Video, Clock, MessageSquare, Send, CheckCircle, Paperclip } from 'lucide-react';

export const LiveClassView: React.FC = () => {
  const [selectedMeetingId, setSelectedMeetingId] = useState<string | null>(null);
  
  // Meeting schedules state
  const meetings = [
    { id: 'meet-1', title: 'Ekadhikena Sutra Live Session', time: 'Today, 4:00 PM', instructor: 'Dr. Vivek Sharma', duration: '60 Mins', link: '#/live/meet-1' },
    { id: 'meet-2', title: 'SaaS Partitioning Q&A Session', time: 'Tomorrow, 11:00 AM', instructor: 'Rahul Sharma', duration: '90 Mins', link: '#/live/meet-2' }
  ];

  // Chat message boards states
  const [chats, setChats] = useState([
    { sender: 'Ananya Iyer', text: 'Does this multiply technique cover decimal structures?', time: 'Just now' },
    { sender: 'Rahul Sen', text: 'Yes, it works identically by adjusting base factors.', time: 'Just now' }
  ]);
  const [chatInput, setChatInput] = useState('');

  const handleSendChat = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    setChats(prev => [...prev, { sender: 'You', text: chatInput, time: 'Just now' }]);
    setChatInput('');
  };

  const selectedMeeting = meetings.find(m => m.id === selectedMeetingId);

  // 1. ACTIVE LIVE CLASS ROOM RENDER
  if (selectedMeetingId && selectedMeeting) {
    return (
      <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl grid grid-cols-1 lg:grid-cols-12 gap-6 text-left">
        
        {/* Stream and Info Canvas */}
        <div className="lg:col-span-8 space-y-4">
          <button 
            onClick={() => setSelectedMeetingId(null)}
            className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 hover:text-indigo-300 transition"
          >
            ← Return to Live Schedule
          </button>
          
          <div className="aspect-video bg-slate-950 border border-indigo-950/65 rounded-2xl flex flex-col justify-between overflow-hidden relative shadow-2xl">
            <div className="p-3 bg-slate-900/80 border-b border-indigo-950/30 flex items-center justify-between text-[9px] text-slate-500 font-mono">
              <span className="flex items-center gap-1 text-rose-500">
                <span className="h-1.5 w-1.5 rounded-full bg-rose-500 animate-pulse"></span>
                LIVE TUTORIAL BROADCASTING
              </span>
              <span>INSTRUCTOR: {selectedMeeting.instructor.toUpperCase()}</span>
            </div>
            
            <div className="flex-grow flex flex-col items-center justify-center p-4">
              <div className="h-12 w-12 rounded-full bg-rose-600/20 border border-rose-500 flex items-center justify-center text-rose-400 hover:scale-105 transition duration-150 cursor-pointer shadow-lg shadow-rose-500/10">
                <Video size={24} />
              </div>
              <span className="text-[10px] text-slate-500 font-mono mt-3">Click to start streaming interactive lecture canvas</span>
            </div>

            <div className="p-3 bg-slate-900/80 border-t border-indigo-950/30 text-xs font-mono text-indigo-400">
              00:00 / {selectedMeeting.duration}
            </div>
          </div>

          <div>
            <h3 className="text-sm font-bold text-white leading-snug">{selectedMeeting.title}</h3>
            <p className="text-xs text-slate-500 mt-1 font-mono">BROADCAST PATH: {selectedMeeting.link}</p>
          </div>
        </div>

        {/* Live Chats Sidebar */}
        <div className="lg:col-span-4 flex flex-col h-[350px] lg:h-auto bg-slate-950 border border-indigo-950 rounded-2xl overflow-hidden p-4">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block border-b border-indigo-950 pb-2 mb-3">Live Session Chat</span>
          
          <div className="flex-grow overflow-y-auto space-y-3 pr-1 text-xs text-left">
            {chats.map((c, idx) => (
              <div key={idx} className="p-2.5 bg-slate-900 rounded-xl space-y-1">
                <div className="flex justify-between items-center text-[9px] text-slate-500">
                  <strong className="text-slate-350">{c.sender}</strong>
                  <span>{c.time}</span>
                </div>
                <p className="text-slate-400 leading-relaxed">{c.text}</p>
              </div>
            ))}
          </div>

          <form onSubmit={handleSendChat} className="flex gap-2 border-t border-indigo-950 pt-3 mt-3">
            <input
              type="text"
              required
              placeholder="Send message..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              className="flex-1 bg-slate-900 border border-indigo-950 rounded-xl py-2 px-3 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
            <Button type="submit" size="sm" className="px-3 py-2 shrink-0">
              <Send size={12} />
            </Button>
          </form>
        </div>

      </div>
    );
  }

  // 2. SCHEDULE LIST VIEW RENDER
  return (
    <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-6 text-left">
      <div>
        <h3 className="text-sm font-bold text-white flex items-center gap-1.5 uppercase tracking-wider">
          <Calendar size={16} className="text-indigo-400 animate-pulse" /> Scheduled Live Classes
        </h3>
        <p className="text-xs text-slate-400 mt-0.5">Participate in live interactive seminars, Q&A blocks, and attendance tracking.</p>
      </div>

      <div className="space-y-3">
        {meetings.map(m => (
          <div key={m.id} className="p-5 bg-slate-950 border border-indigo-950/60 rounded-2xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:border-indigo-900 transition">
            <div className="space-y-1">
              <span className="text-[9px] font-bold bg-indigo-950 text-indigo-400 font-mono px-2 py-0.5 rounded uppercase tracking-wider">{m.instructor}</span>
              <h4 className="text-sm font-bold text-white leading-snug pt-1">{m.title}</h4>
              <div className="flex gap-4 text-[10px] text-slate-500 font-mono">
                <span className="flex items-center gap-1"><Clock size={11} /> {m.time}</span>
                <span>•</span>
                <span>EST DURATION: {m.duration}</span>
              </div>
            </div>
            <Button size="sm" onClick={() => setSelectedMeetingId(m.id)} className="flex items-center gap-1 text-[11px] py-2 shrink-0">
              <Video size={13} /> Join Meeting Room
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LiveClassView;
