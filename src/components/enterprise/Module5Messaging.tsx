/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { ChatMessage } from './types';
import { MessageSquare, Send, Image, FileText, Mic, Check, CheckCheck, Smile, Paperclip, Play, Pause } from 'lucide-react';

interface ChatChannel {
  id: string;
  name: string;
  avatar: string;
  type: 'TEACHER_USER' | 'USER_USER' | 'ADMIN_TEACHER';
  role: string;
  unreadCount: number;
  typing?: boolean;
}

export const Module5Messaging: React.FC = () => {
  const { currentUser } = useAuthStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [channels, setChannels] = useState<ChatChannel[]>([
    { id: 'ch-teacher', name: 'Dr. Ananya Iyer', avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&q=80&w=150', type: 'TEACHER_USER', role: 'Data Sciences Faculty', unreadCount: 2 },
    { id: 'ch-student', name: 'Rahul Sharma (Student)', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=150', type: 'USER_USER', role: 'Vedic Math Scholar', unreadCount: 0 },
    { id: 'ch-admin', name: 'Super Admin Core', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&q=80&w=150', type: 'ADMIN_TEACHER', role: 'Platform Registrar', unreadCount: 0 }
  ]);

  const [activeChannelId, setActiveChannelId] = useState('ch-teacher');

  const [chatHistories, setChatHistories] = useState<Record<string, ChatMessage[]>>({
    'ch-teacher': [
      {
        id: 'msg-1',
        senderId: 'user-teacher',
        receiverId: currentUser?.id || 'user-student',
        text: 'Hello! I reviewed your custom curriculum proposal for Vedic mathematics in SaaS.',
        createdAt: '5 mins ago',
        readStatus: 'READ'
      },
      {
        id: 'msg-2',
        senderId: 'user-teacher',
        receiverId: currentUser?.id || 'user-student',
        text: 'I attached the lecture notes regarding algebraic algorithms. Let me know if you need any adjustments.',
        createdAt: '4 mins ago',
        readStatus: 'READ',
        attachment: {
          type: 'DOCUMENT',
          name: 'Syllabus_Vedic_Algebra_V1.pdf',
          url: '#'
        }
      }
    ],
    'ch-student': [
      {
        id: 'msg-3',
        senderId: currentUser?.id || 'user-student',
        receiverId: 'user-student-2',
        text: 'Hey Rahul, are you joining the Vedic Mathematics live class today at 5:00 PM?',
        createdAt: '2 hours ago',
        readStatus: 'READ'
      }
    ],
    'ch-admin': [
      {
        id: 'msg-4',
        senderId: 'user-admin',
        receiverId: currentUser?.id || 'user-teacher',
        text: 'Greetings. Your self-publishing submission royalty payout is ready to be audited.',
        createdAt: 'Yesterday',
        readStatus: 'READ'
      }
    ]
  });

  const [textInput, setTextInput] = useState('');
  const [voicePlayingId, setVoicePlayingId] = useState<string | null>(null);

  const activeChannel = channels.find(c => c.id === activeChannelId);
  const activeMessages = chatHistories[activeChannelId] || [];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [activeMessages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!textInput.trim() || !activeChannel) return;

    const newMsg: ChatMessage = {
      id: `msg-sent-${Date.now()}`,
      senderId: currentUser?.id || 'user',
      receiverId: activeChannel.id === 'ch-teacher' ? 'user-teacher' : activeChannel.id === 'ch-student' ? 'user-student-2' : 'user-admin',
      text: textInput,
      createdAt: 'Just now',
      readStatus: 'SENT'
    };

    setChatHistories(prev => ({
      ...prev,
      [activeChannelId]: [...(prev[activeChannelId] || []), newMsg]
    }));
    setTextInput('');

    // Mark sent as delivered quickly
    setTimeout(() => {
      setChatHistories(prev => ({
        ...prev,
        [activeChannelId]: prev[activeChannelId].map(m => m.id === newMsg.id ? { ...m, readStatus: 'DELIVERED' as const } : m)
      }));
    }, 1000);

    // Simulate an automatic smart reply with a typing indicator
    setTimeout(() => {
      setChannels(prev => prev.map(c => c.id === activeChannelId ? { ...c, typing: true } : c));
    }, 2000);

    setTimeout(() => {
      const autoreply: ChatMessage = {
        id: `msg-recv-${Date.now()}`,
        senderId: activeChannel.id === 'ch-teacher' ? 'user-teacher' : activeChannel.id === 'ch-student' ? 'user-student-2' : 'user-admin',
        receiverId: currentUser?.id || 'user',
        text: `Thanks for your message! This is a secure, encrypted real-time chat sync response regarding "${textInput.slice(0, 30)}". Let's sync this live during learning schedules.`,
        createdAt: 'Just now',
        readStatus: 'READ'
      };

      setChannels(prev => prev.map(c => c.id === activeChannelId ? { ...c, typing: false, unreadCount: 0 } : c));
      setChatHistories(prev => ({
        ...prev,
        [activeChannelId]: [...(prev[activeChannelId] || []), autoreply]
      }));

      // Mark user message as read
      setChatHistories(prev => ({
        ...prev,
        [activeChannelId]: prev[activeChannelId].map(m => m.senderId === (currentUser?.id || 'user') ? { ...m, readStatus: 'READ' as const } : m)
      }));
    }, 4500);
  };

  const simulateAttachment = (type: 'IMAGE' | 'DOCUMENT' | 'VOICE') => {
    if (!activeChannel) return;
    
    let attachmentDetail = { type, name: '', url: '#' };
    let text = '';
    
    if (type === 'IMAGE') {
      attachmentDetail.name = 'screenshot_portfolio_issue.png';
      attachmentDetail.url = 'https://images.unsplash.com/photo-1531403009284-440f080d1e12?auto=format&fit=crop&q=80&w=400';
      text = 'Uploaded a screenshot of my new website portfolio mockup.';
    } else if (type === 'DOCUMENT') {
      attachmentDetail.name = 'Vedic_Math_Assignment_Final.pdf';
      text = 'Submitted my solved Vedic Mathematics assignments file.';
    } else {
      attachmentDetail.name = 'Voice note (0:14)';
      text = 'Sent a voice recording';
    }

    const newMsg: ChatMessage = {
      id: `msg-sent-${Date.now()}`,
      senderId: currentUser?.id || 'user',
      receiverId: activeChannel.id === 'ch-teacher' ? 'user-teacher' : activeChannel.id === 'ch-student' ? 'user-student-2' : 'user-admin',
      text,
      createdAt: 'Just now',
      readStatus: 'SENT',
      attachment: attachmentDetail
    };

    setChatHistories(prev => ({
      ...prev,
      [activeChannelId]: [...(prev[activeChannelId] || []), newMsg]
    }));
  };

  const handleChannelSwitch = (channelId: string) => {
    setActiveChannelId(channelId);
    setChannels(prev => prev.map(c => c.id === channelId ? { ...c, unreadCount: 0 } : c));
  };

  return (
    <div id="saas-module-5" className="bg-slate-950/60 border border-slate-900 rounded-2xl overflow-hidden h-[500px] flex text-slate-100">
      {/* Sidebar Channels List */}
      <div className="w-64 border-r border-slate-900 bg-slate-950 flex flex-col justify-between shrink-0">
        <div>
          <div className="p-4 border-b border-slate-900 text-left">
            <h3 className="text-xs font-black text-white uppercase tracking-wider flex items-center gap-1.5">
              <MessageSquare className="w-4 h-4 text-indigo-400" />
              Messaging Channels
            </h3>
          </div>
          
          <div className="p-2 space-y-1 overflow-y-auto max-h-[350px]">
            {channels.map((chan) => {
              const isSelected = activeChannelId === chan.id;
              return (
                <div
                  key={chan.id}
                  onClick={() => handleChannelSwitch(chan.id)}
                  className={`flex items-center gap-3 p-2.5 rounded-xl cursor-pointer transition text-left ${isSelected ? 'bg-indigo-600/10 border border-indigo-950 text-indigo-200' : 'hover:bg-slate-900 text-slate-400'}`}
                >
                  <div className="relative shrink-0">
                    <img src={chan.avatar} alt={chan.name} className="w-9 h-9 rounded-full object-cover" />
                    <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-500 rounded-full border-2 border-slate-950"></span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <span className="block font-bold text-slate-200 text-xs truncate">{chan.name}</span>
                    <span className="block text-[9px] text-slate-500 truncate mt-0.5">{chan.role}</span>
                  </div>
                  {chan.unreadCount > 0 && (
                    <span className="bg-indigo-600 text-white text-[9px] font-black px-1.5 py-0.5 rounded-full shrink-0 font-mono">
                      {chan.unreadCount}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Messaging footer info */}
        <div className="p-3 border-t border-slate-900 bg-slate-950/40 text-[9px] text-slate-500 font-mono text-left">
          🔐 Encrypted Peer Tunnel Synced
        </div>
      </div>

      {/* Primary Chat Windows Pane */}
      {activeChannel ? (
        <div className="flex-1 flex flex-col justify-between bg-slate-900/20 relative">
          {/* Header */}
          <div className="p-3 border-b border-slate-900 bg-slate-950/80 flex items-center justify-between">
            <div className="flex items-center gap-2.5 text-left">
              <img src={activeChannel.avatar} alt={activeChannel.name} className="w-8 h-8 rounded-full object-cover" />
              <div>
                <span className="block text-xs font-bold text-white">{activeChannel.name}</span>
                <span className="block text-[9px] text-emerald-400 font-medium">Online</span>
              </div>
            </div>
            {activeChannel.typing && (
              <span className="text-[10px] text-indigo-400 animate-pulse font-mono font-medium">typing...</span>
            )}
          </div>

          {/* Messages Stream */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 max-h-[350px] scrollbar-thin scrollbar-thumb-slate-800">
            {activeMessages.map((msg) => {
              const isMe = msg.senderId === (currentUser?.id || 'user-student');
              return (
                <div key={msg.id} className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}>
                  <div className={`p-3 rounded-2xl max-w-sm text-left text-xs ${isMe ? 'bg-indigo-600 text-white rounded-tr-none shadow-md shadow-indigo-950/20' : 'bg-slate-900/90 text-slate-200 rounded-tl-none border border-slate-800'}`}>
                    
                    {/* Optional Attachments render */}
                    {msg.attachment && (
                      <div className="mb-2.5 p-2 bg-black/20 rounded-xl border border-white/5 space-y-2">
                        {msg.attachment.type === 'IMAGE' && (
                          <div className="rounded-lg overflow-hidden max-h-40">
                            <img src={msg.attachment.url} alt="attached asset" className="w-full object-cover" />
                          </div>
                        )}
                        
                        {msg.attachment.type === 'DOCUMENT' && (
                          <div className="flex items-center gap-2 text-xs font-mono">
                            <FileText className="w-5 h-5 text-indigo-300" />
                            <div className="min-w-0">
                              <span className="block font-bold text-slate-100 truncate text-[11px]">{msg.attachment.name}</span>
                              <span className="block text-[9px] text-slate-400">PDF Document • 1.4 MB</span>
                            </div>
                          </div>
                        )}

                        {msg.attachment.type === 'VOICE' && (
                          <div className="flex items-center gap-2 text-xs">
                            <button
                              onClick={() => setVoicePlayingId(voicePlayingId === msg.id ? null : msg.id)}
                              className="bg-indigo-500/20 text-indigo-300 p-1.5 rounded-full hover:bg-indigo-500/40 transition shrink-0"
                            >
                              {voicePlayingId === msg.id ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                            </button>
                            <div className="w-32 h-4 bg-slate-800 rounded flex items-center overflow-hidden shrink-0 relative px-1">
                              {/* Mock waveform animation */}
                              <div className="flex items-end gap-0.5 h-full pt-1.5">
                                {[3,5,2,6,8,5,2,4,6,7,4,2,3,5,7,3,1,4,6,3,2,5].map((h, i) => (
                                  <span
                                    key={i}
                                    style={{ height: `${h * 10}%` }}
                                    className={`w-0.5 rounded-full transition-all duration-300 ${voicePlayingId === msg.id ? 'bg-indigo-400 animate-pulse' : 'bg-slate-500'}`}
                                  ></span>
                                ))}
                              </div>
                            </div>
                            <span className="text-[10px] font-mono text-slate-400">0:14</span>
                          </div>
                        )}
                      </div>
                    )}

                    <p>{msg.text}</p>
                    
                    <div className="flex justify-end items-center gap-1 mt-1 text-[9px] opacity-60 font-mono">
                      <span>{msg.createdAt}</span>
                      {isMe && (
                        <span>
                          {msg.readStatus === 'SENT' ? (
                            <Check className="w-3 h-3 text-slate-400" />
                          ) : msg.readStatus === 'DELIVERED' ? (
                            <CheckCheck className="w-3 h-3 text-slate-400" />
                          ) : (
                            <CheckCheck className="w-3 h-3 text-sky-400" />
                          )}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>

          {/* Typing/Controls Dock Footer */}
          <div className="p-3 bg-slate-950/80 border-t border-slate-900 flex flex-col gap-2">
            {/* Attachment Simulators Bar */}
            <div className="flex gap-2 text-xs">
              <button
                onClick={() => simulateAttachment('IMAGE')}
                className="flex items-center gap-1 text-[10px] bg-slate-900 text-slate-400 hover:text-white px-2.5 py-1 rounded-lg border border-slate-850"
              >
                <Image className="w-3.5 h-3.5 text-indigo-400" /> Add Photo
              </button>
              <button
                onClick={() => simulateAttachment('DOCUMENT')}
                className="flex items-center gap-1 text-[10px] bg-slate-900 text-slate-400 hover:text-white px-2.5 py-1 rounded-lg border border-slate-850"
              >
                <FileText className="w-3.5 h-3.5 text-emerald-400" /> Attach PDF
              </button>
              <button
                onClick={() => simulateAttachment('VOICE')}
                className="flex items-center gap-1 text-[10px] bg-slate-900 text-slate-400 hover:text-white px-2.5 py-1 rounded-lg border border-slate-850"
              >
                <Mic className="w-3.5 h-3.5 text-rose-400" /> Record Voice
              </button>
            </div>

            {/* Input form */}
            <form onSubmit={handleSendMessage} className="flex gap-2">
              <input
                type="text"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Type your message securely..."
                className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
              />
              <button
                type="submit"
                className="bg-indigo-600 hover:bg-indigo-500 text-white p-2.5 rounded-xl transition shadow-md shadow-indigo-950"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      ) : (
        <div className="flex-1 h-full flex flex-col items-center justify-center text-slate-600">
          <MessageSquare className="w-12 h-12 stroke-[1.5] text-slate-800 mb-2 animate-pulse" />
          <p className="text-xs">No active chat channel selected.</p>
        </div>
      )}
    </div>
  );
};

export default Module5Messaging;
