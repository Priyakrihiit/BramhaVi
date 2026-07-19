/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { SaaSNotification, NotificationChannel, NotificationCategory } from './types';
import { Bell, Mail, MessageSquare, Phone, Send, Trash2, ShieldAlert, CheckCircle2 } from 'lucide-react';

export const Module11Notifications: React.FC = () => {
  const { currentUser } = useAuthStore();
  const [logs, setLogs] = useState<SaaSNotification[]>([
    {
      id: 'notif-101',
      title: 'Vedic Algebra Course Syllabus Approved',
      message: 'Greetings Rahul, your requested Vedic Algebra curriculum proposal has been marked as APPROVED by Dr. Ananya Iyer.',
      category: 'ACADEMIC',
      channels: ['IN_APP', 'EMAIL'],
      createdAt: '10 mins ago',
      read: false
    },
    {
      id: 'notif-102',
      title: 'Subscription Invoice INV-1092 Settlement',
      message: 'Transaction Success. ₹14,999 has been debited for Institution SaaS Annual access tier.',
      category: 'TRANSACTIONAL',
      channels: ['IN_APP', 'EMAIL', 'SMS'],
      createdAt: '1 hour ago',
      read: true
    },
    {
      id: 'notif-103',
      title: 'Security Verification Login Alert',
      message: 'Your account logged in successfully from secure IP Pune 103.88.22.',
      category: 'SECURITY',
      channels: ['IN_APP'],
      createdAt: 'Yesterday',
      read: true
    }
  ]);

  // Form states
  const [newTitle, setNewTitle] = useState('');
  const [newMessage, setNewMessage] = useState('');
  const [newCat, setNewCat] = useState<NotificationCategory>('ACADEMIC');
  
  // Multi-select channels
  const [selInApp, setSelInApp] = useState(true);
  const [selEmail, setSelEmail] = useState(false);
  const [selSMS, setSelSMS] = useState(false);
  const [selPush, setSelPush] = useState(false);

  const [successMsg, setSuccessMsg] = useState(false);

  const handleDispatchNotification = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle || !newMessage) return;

    const channelsToDispatch: NotificationChannel[] = [];
    if (selInApp) channelsToDispatch.push('IN_APP');
    if (selEmail) channelsToDispatch.push('EMAIL');
    if (selSMS) channelsToDispatch.push('SMS');
    if (selPush) channelsToDispatch.push('PUSH');

    const newNotification: SaaSNotification = {
      id: `notif-${Date.now()}`,
      title: newTitle,
      message: newMessage,
      category: newCat,
      channels: channelsToDispatch,
      createdAt: 'Just now',
      read: false
    };

    setLogs(prev => [newNotification, ...prev]);
    setSuccessMsg(true);

    // Reset fields
    setNewTitle('');
    setNewMessage('');
    setTimeout(() => setSuccessMsg(false), 2500);
  };

  const handleMarkAllRead = () => {
    setLogs(prev => prev.map(l => ({ ...l, read: true })));
  };

  const handleClearAll = () => {
    setLogs([]);
  };

  const handleMarkRead = (id: string) => {
    setLogs(prev => prev.map(l => l.id === id ? { ...l, read: true } : l));
  };

  return (
    <div id="saas-module-11" className="space-y-6 text-slate-100">
      {/* Page Header */}
      <div className="bg-slate-900/60 border border-indigo-950 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 text-left">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Bell className="text-indigo-400 w-5 h-5 animate-bounce" />
            Notification Dispatcher & Multi-Channel Alert Engine
          </h2>
          <p className="text-slate-400 text-xs mt-1">
            Simulate real-time messaging pipeline. Distribute notifications across In-App, Email (SendGrid), SMS (Twilio), and Webpush configurations simultaneously using uniform dispatch queues.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Admin notification dispatch simulator */}
        <div className="lg:col-span-5 space-y-6 text-left">
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 space-y-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Send className="w-4 h-4 text-indigo-400" /> Dispatch System Notification
            </h3>
            {successMsg && (
              <span className="text-[11px] text-emerald-400 font-bold block">
                Notification successfully pushed to selected delivery channels!
              </span>
            )}
            <form onSubmit={handleDispatchNotification} className="space-y-4">
              <div>
                <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Alert Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Scheduled Live Stream Class Starting"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none placeholder-slate-600"
                />
              </div>

              <div>
                <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Target Category</label>
                <select
                  value={newCat}
                  onChange={(e) => setNewCat(e.target.value as NotificationCategory)}
                  className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none"
                >
                  <option value="ACADEMIC">Academic Bulletin</option>
                  <option value="TRANSACTIONAL">Transactional Invoice Receipt</option>
                  <option value="COMMUNITY">Community Discussion Activity</option>
                  <option value="SECURITY">Security / 2FA / Login Warning</option>
                </select>
              </div>

              {/* Multi-select channels checkbox row */}
              <div className="space-y-2">
                <label className="block text-[10px] text-slate-400 uppercase font-bold">Select Active Delivery Channels</label>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <label className="flex items-center gap-2 bg-slate-900 border border-slate-850 p-2 rounded-lg cursor-pointer">
                    <input type="checkbox" checked={selInApp} onChange={(e) => setSelInApp(e.target.checked)} className="accent-indigo-500" />
                    <span className="flex items-center gap-1"><Bell className="w-3.5 h-3.5 text-indigo-400" /> In-App Feed</span>
                  </label>
                  <label className="flex items-center gap-2 bg-slate-900 border border-slate-850 p-2 rounded-lg cursor-pointer">
                    <input type="checkbox" checked={selEmail} onChange={(e) => setSelEmail(e.target.checked)} className="accent-indigo-500" />
                    <span className="flex items-center gap-1"><Mail className="w-3.5 h-3.5 text-emerald-400" /> Email (SendGrid)</span>
                  </label>
                  <label className="flex items-center gap-2 bg-slate-900 border border-slate-850 p-2 rounded-lg cursor-pointer">
                    <input type="checkbox" checked={selSMS} onChange={(e) => setSelSMS(e.target.checked)} className="accent-indigo-500" />
                    <span className="flex items-center gap-1"><Phone className="w-3.5 h-3.5 text-sky-400" /> SMS (Twilio)</span>
                  </label>
                  <label className="flex items-center gap-2 bg-slate-900 border border-slate-850 p-2 rounded-lg cursor-pointer">
                    <input type="checkbox" checked={selPush} onChange={(e) => setSelPush(e.target.checked)} className="accent-indigo-500" />
                    <span className="flex items-center gap-1"><MessageSquare className="w-3.5 h-3.5 text-rose-400" /> Push Web Notification</span>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Notification Body text</label>
                <textarea
                  rows={4}
                  required
                  placeholder="Draft clear message body..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none placeholder-slate-600 font-sans"
                />
              </div>

              <button
                type="submit"
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold py-2 rounded-xl transition shadow-md shadow-indigo-950 flex items-center justify-center gap-1.5"
              >
                <Send className="w-3.5 h-3.5" /> Dispatch Alert Queue
              </button>
            </form>
          </div>
        </div>

        {/* Right column: Notification history log ledger */}
        <div className="lg:col-span-7 space-y-4 text-left">
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 flex flex-col justify-between h-[510px]">
            <div>
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                  <Bell className="w-4 h-4 text-indigo-400" />
                  Active Notification feed ({logs.filter(l => !l.read).length} Unread)
                </h3>
                <div className="flex gap-2">
                  <button onClick={handleMarkAllRead} className="text-[10px] text-slate-500 hover:text-indigo-400 font-bold font-mono">MARK READ</button>
                  <button onClick={handleClearAll} className="text-[10px] text-slate-500 hover:text-rose-400 font-bold font-mono flex items-center gap-0.5">
                    <Trash2 className="w-3 h-3" /> CLEAR ALL
                  </button>
                </div>
              </div>

              <div className="space-y-2 max-h-[410px] overflow-y-auto pr-1">
                {logs.map(log => (
                  <div
                    key={log.id}
                    className={`p-3.5 rounded-xl border flex flex-col gap-2 transition duration-300 ${log.read ? 'bg-slate-900/30 border-slate-900/60 opacity-60' : 'bg-slate-900/80 border-indigo-950 shadow shadow-indigo-950/20'}`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="text-left">
                        <span className="text-[8px] font-mono bg-slate-950 px-1.5 py-0.5 rounded text-indigo-400 font-bold uppercase">{log.category}</span>
                        <h4 className="text-xs font-bold text-slate-200 mt-1">{log.title}</h4>
                      </div>
                      <span className="text-[9px] text-slate-500 font-mono shrink-0">{log.createdAt}</span>
                    </div>

                    <p className="text-[11px] text-slate-400 font-sans leading-relaxed">{log.message}</p>

                    <hr className="border-slate-850/40" />

                    <div className="flex justify-between items-center text-[9px] font-mono text-slate-500">
                      {/* Delivery channels indicators */}
                      <div className="flex gap-1.5">
                        {log.channels.map((ch, idx) => (
                          <span key={idx} className="bg-slate-950 border border-slate-900 px-1 py-0.2 rounded font-extrabold uppercase text-[8px] text-slate-400">
                            {ch}
                          </span>
                        ))}
                      </div>

                      {!log.read ? (
                        <button
                          onClick={() => handleMarkRead(log.id)}
                          className="text-indigo-400 hover:underline font-bold"
                        >
                          Mark as read
                        </button>
                      ) : (
                        <span className="text-slate-600">READ</span>
                      )}
                    </div>
                  </div>
                ))}
                {logs.length === 0 && (
                  <div className="h-48 flex flex-col items-center justify-center text-slate-600">
                    <Bell className="w-10 h-10 mb-2 stroke-[1.5]" />
                    <p className="text-xs">No notifications are logged in this session feed.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Module11Notifications;
