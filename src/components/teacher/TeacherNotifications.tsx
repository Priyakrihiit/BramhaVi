/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Bell, Eye, Plus, Send, CheckCircle2, MessageSquare } from 'lucide-react';
import { Button, Input, Badge } from '../DesignSystem';

interface SystemNotification {
  id: string;
  senderName: string;
  category: 'SYSTEM' | 'ENROLLMENT' | 'SUBMISSION' | 'DISCUSSION';
  title: string;
  body: string;
  timestamp: string;
  isRead: boolean;
}

export const TeacherNotifications: React.FC = () => {
  const [notifications, setNotifications] = useState<SystemNotification[]>([
    {
      id: 'notif-1',
      senderName: 'System Ledger',
      category: 'SYSTEM',
      title: 'Database Sync Success',
      body: 'All course schemas and student enrollment tables have successfully committed to central nodes.',
      timestamp: '1h ago',
      isRead: false
    },
    {
      id: 'notif-2',
      senderName: 'Aditya Sharma',
      category: 'SUBMISSION',
      title: 'Assignment Submitted',
      body: 'Scholar Aditya Sharma submitted Schrödinger Consciousness Equation Derivation for grading.',
      timestamp: '2h ago',
      isRead: false
    },
    {
      id: 'notif-3',
      senderName: 'Meera Nair',
      category: 'ENROLLMENT',
      title: 'New Student Enrollment',
      body: 'Meera Nair purchased Sanskrit Compiler Design subscription.',
      timestamp: '1d ago',
      isRead: true
    }
  ]);

  // Form states for broadcasting announcements
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [announceTitle, setAnnounceTitle] = useState('');
  const [announceBody, setAnnounceBody] = useState('');
  const [broadcastTarget, setBroadcastTarget] = useState('ALL');
  const [broadcastSuccess, setBroadcastSuccess] = useState(false);

  const handleMarkRead = (id: string) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, isRead: true } : n));
  };

  const handleMarkAllRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, isRead: true })));
  };

  const handleBroadcastAnnouncement = (e: React.FormEvent) => {
    e.preventDefault();
    if (!announceTitle.trim() || !announceBody.trim()) return;

    setBroadcastSuccess(true);
    setAnnounceTitle('');
    setAnnounceBody('');
    setTimeout(() => {
      setBroadcastSuccess(false);
      setIsFormOpen(false);
    }, 3000);
  };

  const unreadCount = notifications.filter(n => !n.isRead).length;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Bell className="text-indigo-400" size={20} />
            Notifications & Broadcasts
          </h2>
          <p className="text-xs text-slate-400">Review class activities, system alerts, and publish global messages to students.</p>
        </div>

        <div className="flex gap-2 select-none">
          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllRead}
              className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-850 text-slate-400 hover:text-white border border-slate-800 text-[10px] font-bold uppercase transition"
            >
              Mark All Read
            </button>
          )}
          <Button onClick={() => setIsFormOpen(true)} size="sm" variant="primary">
            <Plus size={14} /> Send Broadcast
          </Button>
        </div>
      </div>

      {isFormOpen && (
        <form onSubmit={handleBroadcastAnnouncement} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 animate-fade-in text-left">
          <h3 className="text-sm font-bold text-slate-200">Send Cohort Announcement</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input label="Announcement Title" placeholder="e.g. Scheduled Maintenance" value={announceTitle} onChange={e => setAnnounceTitle(e.target.value)} required />
            <div>
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Broadcast Group</label>
              <select
                className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-2.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                value={broadcastTarget}
                onChange={e => setBroadcastTarget(e.target.value)}
              >
                <option value="ALL">All Enrolled Scholars</option>
                <option value="Quantum Consciousness Mechanics">Quantum Consciousness Mechanics Cohort</option>
                <option value="Vedic Computational Syntax">Vedic Computational Syntax Cohort</option>
              </select>
            </div>
          </div>
          <div>
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Message Body</label>
            <textarea
              className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-3.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 placeholder:text-slate-650"
              rows={3}
              placeholder="Provide general announcement instructions..."
              value={announceBody}
              onChange={e => setAnnounceBody(e.target.value)}
              required
            />
          </div>

          {broadcastSuccess && (
            <div className="p-3 bg-emerald-950/20 border border-emerald-500/25 text-emerald-400 text-xs rounded-xl flex items-center gap-2 select-none animate-fade-in font-sans">
              <CheckCircle2 size={14} /> Announcement successfully dispatched to all target students.
            </div>
          )}

          <div className="flex justify-end gap-2.5 pt-1">
            <Button type="button" variant="ghost" size="sm" onClick={() => setIsFormOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary" size="sm">
              <Send size={13} /> Dispatch Announcement
            </Button>
          </div>
        </form>
      )}

      {/* Notification items list */}
      <div className="space-y-3.5">
        {notifications.map(n => (
          <div key={n.id} className={`p-4.5 rounded-2xl border transition flex items-start gap-4 text-left ${n.isRead ? 'bg-slate-900/35 border-slate-900 text-slate-400' : 'bg-slate-900/60 border-indigo-550/15 text-slate-200'}`}>
            <div className={`h-8 w-8 rounded-xl flex items-center justify-center shrink-0 border ${n.isRead ? 'bg-slate-950 border-slate-900 text-slate-500' : 'bg-indigo-950/20 border-indigo-550/20 text-indigo-400'}`}>
              <Eye size={14} />
            </div>

            <div className="flex-1 space-y-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap select-none">
                <span className="text-[10px] uppercase font-bold text-slate-500 font-mono">{n.senderName}</span>
                <Badge variant={n.category === 'SYSTEM' ? 'secondary' : n.category === 'SUBMISSION' ? 'warning' : 'success'}>
                  {n.category}
                </Badge>
              </div>

              <h4 className="font-bold text-white text-xs mt-0.5">{n.title}</h4>
              <p className="text-[11px] text-slate-300 leading-relaxed pr-6">{n.body}</p>
            </div>

            <div className="flex flex-col items-end gap-2.5 shrink-0 select-none">
              <span className="font-mono text-[9px] text-slate-500">{n.timestamp}</span>
              {!n.isRead && (
                <button onClick={() => handleMarkRead(n.id)} className="text-[9px] uppercase font-bold tracking-wider text-indigo-400 hover:text-white">
                  Mark Read
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
