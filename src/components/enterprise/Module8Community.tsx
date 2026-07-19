/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { CommunityThread, CommunityAnswer, ForumCategory } from './types';
import { MessageSquare, ArrowBigUp, ArrowBigDown, Check, ShieldAlert, Award, Plus, Filter, Users } from 'lucide-react';

export const Module8Community: React.FC = () => {
  const { currentUser, hasCapability } = useAuthStore();
  const [categories] = useState<ForumCategory[]>([
    { id: 'cat-vedic', name: 'Vedic Math Forums', description: 'Discuss ancient Indian mathematical techniques, formulas, and modern applications.', icon: 'GraduationCap', topicsCount: 145, postsCount: 1205 },
    { id: 'cat-saas', name: 'SaaS Software Engineering', description: 'Relational DB partitioning, cache optimizations, DRF routers, and Celery setup.', icon: 'Code', topicsCount: 89, postsCount: 654 }
  ]);

  const [activeCatId, setActiveCatId] = useState('cat-vedic');

  const [threads, setThreads] = useState<CommunityThread[]>([
    {
      id: 'th-1',
      forumId: 'cat-vedic',
      title: 'Is Nikhilam Sutra efficient for larger modular prime divisors?',
      content: 'I have been experimenting with dividing multi-digit numbers by prime denominators like 97 and 103. Does Nikhilam remain optimal compared to modern synthetic division?',
      authorId: 'user-student',
      authorName: 'Rahul Sharma',
      authorAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=150',
      upvotes: 24,
      downvotes: 1,
      createdAt: '2026-07-07 10:15',
      answers: [
        {
          id: 'ans-1',
          threadId: 'th-1',
          content: 'Nikhilam handles prime divisors near bases (10^n) exceptionally. For arbitrary primes, combining Nikhilam with Anurupyena reduces remainder offsets dynamically. Synthetic division requires uniform coefficient storage, whereas Nikhilam relies purely on additive shifts.',
          authorId: 'user-teacher',
          authorName: 'Dr. Ananya Iyer',
          authorAvatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&q=80&w=150',
          upvotes: 15,
          downvotes: 0,
          isBestAnswer: true,
          createdAt: '2026-07-07 11:20'
        },
        {
          id: 'ans-2',
          threadId: 'th-1',
          content: 'I tested this in Python, Anurupyena combination is about 40% faster for bases under 1000.',
          authorId: 'user-student-2',
          authorName: 'Priyesh Pandey',
          upvotes: 3,
          downvotes: 0,
          isBestAnswer: false,
          createdAt: '2026-07-07 12:05'
        }
      ]
    }
  ]);

  // Reputation Points Tracker
  const [reputation, setReputation] = useState<Record<string, number>>({
    'user-teacher': 850,
    'user-student': 120,
    'user-student-2': 45
  });

  const [newThreadTitle, setNewThreadTitle] = useState('');
  const [newThreadBody, setNewThreadBody] = useState('');
  
  const [answerInputs, setAnswerInputs] = useState<Record<string, string>>({});

  const handleCreateThread = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newThreadTitle || !newThreadBody) return;

    const newThread: CommunityThread = {
      id: `th-${Date.now()}`,
      forumId: activeCatId,
      title: newThreadTitle,
      content: newThreadBody,
      authorId: currentUser?.id || 'user',
      authorName: currentUser?.fullName || 'Rahul Sharma',
      authorAvatar: currentUser?.avatarUrl,
      upvotes: 1,
      downvotes: 0,
      createdAt: new Date().toLocaleDateString() + ' ' + new Date().toLocaleTimeString().slice(0, 5),
      answers: []
    };

    setThreads(prev => [newThread, ...prev]);
    setNewThreadTitle('');
    setNewThreadBody('');
  };

  const handleVoteThread = (threadId: string, type: 'UP' | 'DOWN') => {
    setThreads(prev => prev.map(t => {
      if (t.id === threadId) {
        if (type === 'UP') {
          return { ...t, upvotes: t.upvotes + 1, userVote: 'UP' as const };
        } else {
          return { ...t, downvotes: t.downvotes + 1, userVote: 'DOWN' as const };
        }
      }
      return t;
    }));
  };

  const handleVoteAnswer = (threadId: string, answerId: string, type: 'UP' | 'DOWN') => {
    setThreads(prev => prev.map(t => {
      if (t.id === threadId) {
        return {
          ...t,
          answers: t.answers.map(ans => {
            if (ans.id === answerId) {
              const weight = type === 'UP' ? 1 : -1;
              return {
                ...ans,
                upvotes: type === 'UP' ? ans.upvotes + 1 : ans.upvotes,
                downvotes: type === 'DOWN' ? ans.downvotes + 1 : ans.downvotes
              };
            }
            return ans;
          })
        };
      }
      return t;
    }));
  };

  const handleSetBestAnswer = (threadId: string, answerId: string, answerAuthorId: string) => {
    setThreads(prev => prev.map(t => {
      if (t.id === threadId) {
        return {
          ...t,
          bestAnswerId: answerId,
          answers: t.answers.map(ans => ({
            ...ans,
            isBestAnswer: ans.id === answerId
          }))
        };
      }
      return t;
    }));

    // Award +15 reputation points to author of best answer
    setReputation(prev => ({
      ...prev,
      [answerAuthorId]: (prev[answerAuthorId] || 0) + 15
    }));
  };

  const handlePostAnswer = (e: React.FormEvent, threadId: string) => {
    e.preventDefault();
    const txt = answerInputs[threadId];
    if (!txt?.trim()) return;

    const newAnswer: CommunityAnswer = {
      id: `ans-${Date.now()}`,
      threadId,
      content: txt,
      authorId: currentUser?.id || 'user',
      authorName: currentUser?.fullName || 'Rahul Sharma',
      authorAvatar: currentUser?.avatarUrl,
      upvotes: 0,
      downvotes: 0,
      isBestAnswer: false,
      createdAt: 'Just now'
    };

    setThreads(prev => prev.map(t => {
      if (t.id === threadId) {
        return { ...t, answers: [...t.answers, newAnswer] };
      }
      return t;
    }));

    setAnswerInputs(prev => ({ ...prev, [threadId]: '' }));
  };

  const handleFlagThread = (threadId: string) => {
    setThreads(prev => prev.map(t => {
      if (t.id === threadId) {
        return { ...t, content: '⚠️ [This thread has been flagged by moderator and is undergoing compliance audits]' };
      }
      return t;
    }));
  };

  return (
    <div id="saas-module-8-correct" className="space-y-6 text-slate-100">
      {/* Header Banner */}
      <div className="bg-slate-900/60 border border-indigo-950 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 text-left">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <MessageSquare className="text-indigo-400 w-5 h-5" />
            Vedic Q&A Forums & Community reputation Platform
          </h2>
          <p className="text-slate-400 text-xs mt-1">
            Build collaborative wisdom. Post academic questions, cast votes, mark authoritative answers to reward community peers with dynamic reputation scores, and perform admin moderation audits.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Categories List & New Thread Creation */}
        <div className="lg:col-span-4 space-y-6 text-left">
          {/* Categories select sidebar */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 space-y-3">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Filter className="w-3.5 h-3.5 text-indigo-400" /> Forum category circles
            </h3>
            <div className="space-y-2">
              {categories.map(cat => {
                const isActive = activeCatId === cat.id;
                return (
                  <div
                    key={cat.id}
                    onClick={() => setActiveCatId(cat.id)}
                    className={`p-3 border rounded-xl cursor-pointer transition flex flex-col justify-between ${isActive ? 'bg-indigo-600/10 border-indigo-500 text-indigo-200 font-semibold' : 'hover:bg-slate-900 bg-slate-900/20 border-slate-900'}`}
                  >
                    <span className="text-xs font-bold text-slate-200">{cat.name}</span>
                    <span className="text-[10px] text-slate-500 mt-1">{cat.description}</span>
                    <span className="block text-[9px] text-slate-400 font-mono mt-2">{cat.postsCount} total comments</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* New Thread Form */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 space-y-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Plus className="w-4 h-4 text-indigo-400" /> Post New Thread Topic
            </h3>
            
            <form onSubmit={handleCreateThread} className="space-y-3">
              <div>
                <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Thread Title</label>
                <input
                  type="text"
                  required
                  placeholder="Ask clear academic question..."
                  value={newThreadTitle}
                  onChange={(e) => setNewThreadTitle(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Discussion context</label>
                <textarea
                  rows={4}
                  required
                  placeholder="Provide parameters, calculations, and screenshots details..."
                  value={newThreadBody}
                  onChange={(e) => setNewThreadBody(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 font-sans"
                />
              </div>

              <button
                type="submit"
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold py-2 rounded-xl transition shadow-md shadow-indigo-950"
              >
                Post Topic to Forum
              </button>
            </form>
          </div>
        </div>

        {/* Center/Right: Threads logs & replies */}
        <div className="lg:col-span-8 space-y-6 text-left">
          {threads.filter(t => t.forumId === activeCatId).map(th => {
            return (
              <div key={th.id} className="bg-slate-950/40 border border-slate-900 rounded-2xl p-6 space-y-5">
                {/* Author row */}
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-3">
                    {th.authorAvatar ? (
                      <img src={th.authorAvatar} alt={th.authorName} className="w-10 h-10 rounded-full object-cover" />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center font-bold text-xs">
                        {th.authorName.charAt(0)}
                      </div>
                    )}
                    <div>
                      <span className="block font-bold text-slate-200 text-sm">{th.authorName}</span>
                      <span className="block text-[10px] text-slate-500 mt-0.5">Reputation score: <strong className="text-indigo-400 font-mono font-bold">{reputation[th.authorId] || 0} pts</strong> • {th.createdAt}</span>
                    </div>
                  </div>
                  
                  {/* Moderation actions for admin */}
                  {hasCapability('ADMIN') && (
                    <button
                      onClick={() => handleFlagThread(th.id)}
                      className="text-rose-400 hover:text-rose-300 hover:bg-rose-950/30 border border-rose-900/40 text-[9px] font-bold px-2.5 py-1 rounded-lg transition font-mono flex items-center gap-1"
                    >
                      <ShieldAlert className="w-3.5 h-3.5" /> Flag Post
                    </button>
                  )}
                </div>

                {/* Content */}
                <div className="space-y-2">
                  <h4 className="text-base font-black text-white">{th.title}</h4>
                  <p className="text-slate-300 text-xs leading-relaxed">{th.content}</p>
                </div>

                {/* Voting widgets */}
                <div className="flex items-center gap-4 bg-slate-900/30 border border-slate-900 p-2 rounded-xl w-fit">
                  <button
                    onClick={() => handleVoteThread(th.id, 'UP')}
                    disabled={!!th.userVote}
                    className={`flex items-center gap-1.5 transition ${th.userVote === 'UP' ? 'text-indigo-400 scale-110' : 'text-slate-500 hover:text-slate-200'}`}
                  >
                    <ArrowBigUp className="w-5 h-5" />
                    <span className="text-xs font-bold font-mono">{th.upvotes}</span>
                  </button>
                  <span className="text-slate-700 font-mono">|</span>
                  <button
                    onClick={() => handleVoteThread(th.id, 'DOWN')}
                    disabled={!!th.userVote}
                    className={`flex items-center gap-1.5 transition ${th.userVote === 'DOWN' ? 'text-rose-400 scale-110' : 'text-slate-500 hover:text-slate-200'}`}
                  >
                    <ArrowBigDown className="w-5 h-5" />
                    <span className="text-xs font-bold font-mono">{th.downvotes}</span>
                  </button>
                </div>

                <hr className="border-slate-900" />

                {/* Answers / Replies stream */}
                <div className="space-y-4">
                  <span className="text-xs font-black text-indigo-400 uppercase tracking-wider block">Peer Answers ({th.answers.length})</span>
                  {th.answers.map(ans => {
                    return (
                      <div
                        key={ans.id}
                        className={`border rounded-xl p-4 space-y-3 relative transition duration-300 ${ans.isBestAnswer ? 'bg-indigo-950/10 border-indigo-500/50 shadow shadow-indigo-950/20' : 'bg-slate-900/20 border-slate-900'}`}
                      >
                        {ans.isBestAnswer && (
                          <span className="absolute -top-2.5 right-4 bg-indigo-500 text-white text-[9px] px-2.5 py-0.5 rounded-full font-bold flex items-center gap-0.5 uppercase tracking-wider font-mono">
                            <Award className="w-3 h-3" /> Best Certified Answer
                          </span>
                        )}

                        <div className="flex justify-between items-center">
                          <div className="flex items-center gap-2">
                            {ans.authorAvatar ? (
                              <img src={ans.authorAvatar} alt={ans.authorName} className="w-7 h-7 rounded-full object-cover" />
                            ) : (
                              <div className="w-7 h-7 rounded-full bg-emerald-600 flex items-center justify-center font-bold text-[10px]">
                                {ans.authorName.charAt(0)}
                              </div>
                            )}
                            <div>
                              <span className="block font-bold text-slate-300 text-xs">{ans.authorName}</span>
                              <span className="block text-[9px] text-slate-500 font-mono">Reputation: {reputation[ans.authorId] || 0} pts • {ans.createdAt}</span>
                            </div>
                          </div>

                          {/* Set best answer solver button */}
                          {currentUser?.id === th.authorId && !th.bestAnswerId && (
                            <button
                              onClick={() => handleSetBestAnswer(th.id, ans.id, ans.authorId)}
                              className="text-emerald-400 hover:text-white hover:bg-emerald-900/30 border border-emerald-900/40 text-[9px] font-bold px-2 py-0.5 rounded-md transition font-mono flex items-center gap-1"
                            >
                              <Check className="w-3 h-3" /> Mark Solved (+15 pts)
                            </button>
                          )}
                        </div>

                        <p className="text-slate-300 text-xs leading-relaxed">{ans.content}</p>

                        <div className="flex items-center gap-3 text-slate-500 text-[10px] font-mono">
                          <button onClick={() => handleVoteAnswer(th.id, ans.id, 'UP')} className="hover:text-indigo-400">👍 {ans.upvotes}</button>
                          <button onClick={() => handleVoteAnswer(th.id, ans.id, 'DOWN')} className="hover:text-rose-400">👎 {ans.downvotes}</button>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Post response form */}
                <form onSubmit={(e) => handlePostAnswer(e, th.id)} className="flex gap-2">
                  <input
                    type="text"
                    required
                    placeholder="Contribute your professional answer..."
                    value={answerInputs[th.id] || ''}
                    onChange={(e) => setAnswerInputs({ ...answerInputs, [th.id]: e.target.value })}
                    className="flex-1 bg-slate-900 border border-slate-850 rounded-xl px-4 py-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 font-sans"
                  />
                  <button
                    type="submit"
                    className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-4 py-2 rounded-xl transition font-sans"
                  >
                    Reply
                  </button>
                </form>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Module8Community;
