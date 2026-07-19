/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Calendar, Clock, BookOpen, Plus, FileText, Video } from 'lucide-react';
import { Button, Badge } from '../DesignSystem';

interface CalendarEvent {
  id: string;
  title: string;
  type: 'LIVE_CLASS' | 'ASSIGNMENT_DUE' | 'QUIZ_OPEN';
  date: string;
  timeSlot: string;
  courseTitle: string;
}

export const TeacherCalendar: React.FC = () => {
  const [events, setEvents] = useState<CalendarEvent[]>([
    {
      id: 'e-1',
      title: 'Observer Intent Live Seminar',
      type: 'LIVE_CLASS',
      date: '2026-07-15',
      timeSlot: '14:00 - 15:30 IST',
      courseTitle: 'Quantum Consciousness Mechanics'
    },
    {
      id: 'e-2',
      title: 'Schrödinger Derivation Assignment Deadline',
      type: 'ASSIGNMENT_DUE',
      date: '2026-07-25',
      timeSlot: '23:59 IST',
      courseTitle: 'Quantum Consciousness Mechanics'
    },
    {
      id: 'e-3',
      title: 'Ashtadhyayi Sandhi Formulations Q&A',
      type: 'LIVE_CLASS',
      date: '2026-07-16',
      timeSlot: '10:00 - 11:00 IST',
      courseTitle: 'Vedic Computational Syntax'
    },
    {
      id: 'e-4',
      title: 'Ashtadhyayi Sandhi Parsing Test',
      type: 'QUIZ_OPEN',
      date: '2026-07-30',
      timeSlot: '09:00 IST',
      courseTitle: 'Vedic Computational Syntax'
    }
  ]);

  const [filterType, setFilterType] = useState<string>('ALL');

  const filteredEvents = events.filter(e => filterType === 'ALL' || e.type === filterType);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Calendar className="text-indigo-400" size={20} />
            Academic Agenda Calendar
          </h2>
          <p className="text-xs text-slate-400">View upcoming webinars, homework milestones, and quiz schedules.</p>
        </div>

        <div className="flex gap-2 text-xs select-none">
          {['ALL', 'LIVE_CLASS', 'ASSIGNMENT_DUE', 'QUIZ_OPEN'].map(t => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={`px-3 py-1.5 rounded-lg border text-[10px] uppercase font-bold tracking-wider font-mono transition ${
                filterType === t 
                  ? 'bg-indigo-650 border-indigo-550 text-white' 
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {t.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 select-none">
        {/* Right Agenda timeline panel (12 cols for simplicity, let's make it look like an elegant bento list) */}
        <div className="md:col-span-12 space-y-4">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest pl-1">Agenda Chronological List</span>
          
          <div className="space-y-3.5">
            {filteredEvents.map(event => (
              <div key={event.id} className="bg-slate-900/50 border border-slate-850 p-4.5 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-indigo-500/10 transition">
                <div className="flex items-center gap-4 min-w-0">
                  <div className={`h-10 w-10 rounded-xl flex items-center justify-center shrink-0 border ${
                    event.type === 'LIVE_CLASS'
                      ? 'bg-rose-950/15 border-rose-550/10 text-rose-400'
                      : event.type === 'ASSIGNMENT_DUE'
                      ? 'bg-emerald-950/15 border-emerald-550/10 text-emerald-400'
                      : 'bg-purple-950/15 border-purple-550/10 text-purple-400'
                  }`}>
                    {event.type === 'LIVE_CLASS' ? <Video size={16} /> : event.type === 'ASSIGNMENT_DUE' ? <FileText size={16} /> : <BookOpen size={16} />}
                  </div>

                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h4 className="font-bold text-white text-sm truncate">{event.title}</h4>
                      <Badge variant={event.type === 'LIVE_CLASS' ? 'danger' : event.type === 'ASSIGNMENT_DUE' ? 'success' : 'warning'}>
                        {event.type.replace('_', ' ')}
                      </Badge>
                    </div>
                    <span className="text-[11px] text-slate-400 mt-1 block truncate">{event.courseTitle}</span>
                  </div>
                </div>

                <div className="flex items-center gap-5 text-xs text-slate-400 font-mono shrink-0">
                  <span className="flex items-center gap-1.5"><Calendar size={13} className="text-slate-500" /> {event.date}</span>
                  <span className="flex items-center gap-1.5"><Clock size={13} className="text-slate-500" /> {event.timeSlot}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
