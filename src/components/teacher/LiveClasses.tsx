/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Video, Plus, Calendar, Clock, ExternalLink, Trash2, CheckCircle } from 'lucide-react';
import { Button, Input, Badge } from '../DesignSystem';

interface LiveClass {
  id: string;
  title: string;
  courseTitle: string;
  date: string;
  time: string;
  meetingUrl: string;
  status: 'SCHEDULED' | 'LIVE' | 'COMPLETED';
}

export const LiveClasses: React.FC = () => {
  const [classes, setClasses] = useState<LiveClass[]>([
    {
      id: 'live-1',
      title: 'Observer Intent & Wave Collapse Live Seminar',
      courseTitle: 'Quantum Consciousness Mechanics',
      date: '2026-07-15',
      time: '14:00 - 15:30 IST',
      meetingUrl: 'https://meet.google.com/abc-defg-hij',
      status: 'SCHEDULED'
    },
    {
      id: 'live-2',
      title: 'Ashtadhyayi Sandhi Parsing Rules Q&A',
      courseTitle: 'Vedic Computational Syntax',
      date: '2026-07-16',
      time: '10:00 - 11:00 IST',
      meetingUrl: 'https://meet.google.com/xyz-pqrs-tuv',
      status: 'SCHEDULED'
    }
  ]);

  // Form states
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [courseTitle, setCourseTitle] = useState('Quantum Consciousness Mechanics');
  const [date, setDate] = useState('2026-07-15');
  const [time, setTime] = useState('14:00 IST');
  const [meetingUrl, setMeetingUrl] = useState('https://meet.google.com/abc-defg-hij');

  const handleScheduleClass = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    const newClass: LiveClass = {
      id: `live-${Date.now()}`,
      title,
      courseTitle,
      date,
      time,
      meetingUrl,
      status: 'SCHEDULED'
    };

    setClasses(prev => [newClass, ...prev]);
    setIsFormOpen(false);
    setTitle('');
  };

  const handleStartLive = (id: string) => {
    setClasses(prev => prev.map(c => c.id === id ? { ...c, status: 'LIVE' } : c));
  };

  const handleDelete = (id: string) => {
    setClasses(prev => prev.filter(c => c.id !== id));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Video className="text-indigo-400" size={20} />
            Live Class Scheduler
          </h2>
          <p className="text-xs text-slate-400 font-sans">Schedule, launch, and monitor live streaming calls for academic cohorts.</p>
        </div>

        <Button onClick={() => setIsFormOpen(true)} size="sm" variant="primary">
          <Plus size={14} /> Schedule Broadcast
        </Button>
      </div>

      {isFormOpen && (
        <form onSubmit={handleScheduleClass} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 animate-fade-in">
          <h3 className="text-sm font-bold text-slate-200">Schedule New BroadCast Call</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input label="Meeting Title" placeholder="e.g. Neuronal Energy Fields Sync" value={title} onChange={e => setTitle(e.target.value)} required />
            <div>
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Program Subject</label>
              <select
                className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-2.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                value={courseTitle}
                onChange={e => setCourseTitle(e.target.value)}
              >
                <option value="Quantum Consciousness Mechanics">Quantum Consciousness Mechanics</option>
                <option value="Vedic Computational Syntax">Vedic Computational Syntax</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input label="Date" type="date" value={date} onChange={e => setDate(e.target.value)} required />
            <Input label="Time Slot (e.g. 15:00 IST)" placeholder="e.g. 15:00 - 16:00 IST" value={time} onChange={e => setTime(e.target.value)} required />
            <Input label="Broadcast Link (Google Meet/Zoom)" placeholder="e.g. https://meet.google.com/..." value={meetingUrl} onChange={e => setMeetingUrl(e.target.value)} required />
          </div>
          <div className="flex justify-end gap-2.5 pt-1 border-t border-slate-850">
            <Button type="button" variant="ghost" size="sm" onClick={() => setIsFormOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary" size="sm">Schedule Broadcast</Button>
          </div>
        </form>
      )}

      <div className="space-y-4">
        {classes.length === 0 ? (
          <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl text-slate-500 text-xs">
            No live broadcasts scheduled.
          </div>
        ) : (
          classes.map(c => (
            <div key={c.id} className="bg-slate-900/60 border border-slate-850 p-5 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-indigo-500/20 transition">
              <div className="space-y-1.5 min-w-0">
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-white text-sm truncate">{c.title}</h4>
                  <Badge variant={c.status === 'LIVE' ? 'danger' : 'outline'}>
                    {c.status}
                  </Badge>
                </div>
                <span className="text-xs text-slate-400 block truncate">{c.courseTitle}</span>
              </div>

              <div className="flex flex-wrap items-center gap-6 text-[11px] text-slate-400 font-mono shrink-0 select-none">
                <span className="flex items-center gap-1.5"><Calendar size={13} className="text-indigo-400" /> {c.date}</span>
                <span className="flex items-center gap-1.5"><Clock size={13} className="text-purple-400" /> {c.time}</span>
                
                <div className="flex gap-2 font-sans font-semibold">
                  {c.status !== 'LIVE' && (
                    <button
                      onClick={() => handleStartLive(c.id)}
                      className="px-3 py-1.5 rounded-lg bg-indigo-650 hover:bg-indigo-550 border border-indigo-600/30 text-white text-[10px] uppercase tracking-wider transition"
                    >
                      Start Call
                    </button>
                  )}
                  <a
                    href={c.meetingUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 hover:text-white text-slate-300 text-[10px] uppercase tracking-wider flex items-center gap-1 transition"
                  >
                    Join Room <ExternalLink size={10} />
                  </a>
                  <button onClick={() => handleDelete(c.id)} className="p-2 rounded bg-rose-950/20 hover:bg-rose-900 text-rose-400 hover:text-white border border-rose-950/10 transition">
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
