/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useLayoutStore } from '../../stores/layoutStore';
import { useAuthStore } from '../../stores/authStore';
import { Button, Input } from '../../components/DesignSystem';
import { Users, MessageSquare, ArrowBigUp, Award, ChevronRight, ArrowLeft, Search, Send, Sparkles } from 'lucide-react';

export const CommunityPage: React.FC = () => {
  const { currentPath, navigateTo } = useLayoutStore();
  const { currentUser } = useAuthStore();
  const [search, setSearch] = useState('');

  // Thread Form states
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newPreview, setNewPreview] = useState('');

  // Reply states
  const [replyText, setReplyText] = useState('');

  // Extract thread parameter virtual matching: /community/:id
  const match = currentPath.match(/^\/community\/([^/]+)/);
  const threadId = match ? match[1] : null;

  const categories = [
    { id: 'cat-vedic', name: 'Vedic Math Forums', desc: 'Discuss ancient Indian calculation tricks, formulas, and educational applications.', count: '145 topics' },
    { id: 'cat-saas', name: 'SaaS Software Engineering', desc: 'Django partitioning, Celery task models, cache layers, and DRF view routers.', count: '89 topics' },
  ];

  const [threads, setThreads] = useState([
    { id: 'th-1', catId: 'cat-saas', title: 'Relational DB partitioning vs Sharding in Django PostgreSQL', author: 'Rahul Sharma', preview: 'What is the optimal threshold of rows for partitioning a table in PG?', upvotes: 42, replies: 12 },
    { id: 'th-2', catId: 'cat-vedic', title: 'Sutra for multiplying 3-digit numbers in 5 seconds flat', author: 'Dr. Vivek Sharma', preview: 'We are mapping Vedic mental math sutras to automated curriculum trees.', upvotes: 75, replies: 28 },
  ]);

  const [mockReplies, setMockReplies] = useState([
    { author: 'Dr. Ananya Iyer', text: 'Partitioning is best applied when a table exceeds 10M+ rows to maintain active indexes in memory.', date: 'Just now' },
    { author: 'Rahul Sen', text: 'Vedic math mental tools are highly compatible with automated micro-quiz generators.', date: 'Yesterday' }
  ]);

  const handlePostReply = (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) {
      alert('Authentication required to submit replies in community discussion boards. Redirecting to login desk...');
      navigateTo('/auth');
      return;
    }
    if (!replyText.trim()) return;
    setMockReplies(prev => [
      ...prev,
      { author: currentUser.fullName, text: replyText, date: 'Just now' }
    ]);
    setReplyText('');
  };

  const handleCreateThread = (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) {
      alert('Authentication required to bootstrap new forum threads. Redirecting to login desk...');
      navigateTo('/auth');
      return;
    }
    if (!newTitle.trim() || !newPreview.trim()) return;
    setThreads(prev => [
      {
        id: `th-${prev.length + 1}`,
        catId: 'cat-saas',
        title: newTitle,
        author: currentUser.fullName,
        preview: newPreview,
        upvotes: 1,
        replies: 0
      },
      ...prev
    ]);
    setIsFormOpen(false);
    setNewTitle('');
    setNewPreview('');
  };

  // 1. FORUM THREAD DETAIL VIEW
  if (threadId) {
    const selectedThread = threads.find(t => t.id === threadId) || threads[0];
    return (
      <div className="flex-1 flex flex-col bg-[#070b19]">
        {/* Breadcrumb Header */}
        <div className="bg-[#0b1329] border-b border-indigo-950/40 px-6 py-4">
          <div className="max-w-3xl mx-auto flex items-center justify-between gap-4 text-xs">
            <button 
              onClick={() => navigateTo('/community')}
              className="flex items-center gap-1.5 text-slate-400 hover:text-white transition font-bold"
            >
              <ArrowLeft size={13} /> Back to Forums
            </button>
            <div className="text-slate-500 font-mono hidden sm:block">
              Home &gt; Community &gt; {selectedThread.title.substring(0, 30)}...
            </div>
          </div>
        </div>

        {/* Detailed thread view */}
        <div className="py-12 px-6 max-w-3xl mx-auto w-full text-left space-y-6">
          <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4">
            <div className="flex justify-between items-center text-xs text-slate-500">
              <span>Author: {selectedThread.author}</span>
              <span className="flex items-center gap-1 font-mono"><ArrowBigUp size={14} className="text-indigo-400" /> {selectedThread.upvotes} Upvotes</span>
            </div>
            <h3 className="text-base font-bold text-white leading-snug">{selectedThread.title}</h3>
            <p className="text-xs text-slate-350 leading-relaxed">{selectedThread.preview}</p>
          </div>

          {/* Replies */}
          <div className="space-y-4 pt-4">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">Replies ({mockReplies.length})</h4>
            <div className="space-y-3">
              {mockReplies.map((rep, idx) => (
                <div key={idx} className="p-4 bg-slate-900 border border-indigo-950/60 rounded-xl space-y-2">
                  <div className="flex justify-between items-center text-[10px] text-slate-500">
                    <strong className="text-slate-350">{rep.author}</strong>
                    <span>{rep.date}</span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{rep.text}</p>
                </div>
              ))}
            </div>

            {/* Post Reply Form */}
            <form onSubmit={handlePostReply} className="p-4 bg-slate-900 border border-indigo-950 rounded-xl space-y-3">
              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Quick Reply</label>
                <textarea
                  required
                  placeholder="Type your response guidelines..."
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                  className="w-full bg-slate-950 border border-indigo-950 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 min-h-[70px]"
                />
              </div>
              <div className="flex justify-end">
                <Button type="submit" size="sm" className="flex items-center gap-1.5">
                  <Send size={11} /> Submit Reply
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }

  // 2. LISTING FORUMS & TOPICS VIEW
  return (
    <div className="flex-1 flex flex-col bg-[#070b19]">
      {/* Hero Header */}
      <section className="relative py-16 px-8 text-left border-b border-indigo-950/40">
        <div className="absolute top-1/4 left-1/4 w-[300px] h-[300px] bg-indigo-650/10 rounded-full blur-[100px] pointer-events-none"></div>
        <div className="max-w-4xl mx-auto space-y-4">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest font-mono">Platform Forum</span>
          <h1 className="text-3xl font-black text-white tracking-tight">Community Discussion Boards</h1>
          <p className="text-slate-400 text-xs max-w-lg leading-relaxed">
            Collaborate on research topics, share mathematical tips, debug relational database query performance, and ask guidelines.
          </p>
        </div>
      </section>

      {/* Boards list */}
      <section className="py-12 px-6 max-w-5xl mx-auto w-full text-left space-y-12">
        
        {/* Category list */}
        <div className="space-y-4">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Forums Category List</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {categories.map(cat => (
              <div key={cat.id} className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-3 relative overflow-hidden group">
                <div className="p-3 bg-indigo-950/40 text-indigo-400 rounded-xl w-fit"><Users size={18} /></div>
                <div>
                  <h4 className="text-sm font-bold text-white group-hover:text-indigo-300 transition">{cat.name}</h4>
                  <p className="text-xs text-slate-400 leading-relaxed mt-1">{cat.desc}</p>
                </div>
                <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono border-t border-indigo-950/45 pt-3">
                  <span>{cat.count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Create Thread trigger */}
        <div className="flex justify-between items-center border-t border-indigo-950/30 pt-6">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Active Threads</h3>
          <Button size="sm" variant="outline" className="text-[10px]" onClick={() => setIsFormOpen(!isFormOpen)}>
            {isFormOpen ? 'Close Panel' : 'New Thread Topic'}
          </Button>
        </div>

        {isFormOpen && (
          <form onSubmit={handleCreateThread} className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4 max-w-xl">
            <Input label="Thread Title" type="text" required placeholder="e.g. Optimized Celery queue parameters for Bulk Emails" value={newTitle} onChange={(e) => setNewTitle(e.target.value)} />
            <div className="flex flex-col gap-1.5 w-full">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Discussion Context</label>
              <textarea
                required
                placeholder="Detail your question or description..."
                value={newPreview}
                onChange={(e) => setNewPreview(e.target.value)}
                className="w-full bg-slate-950 border border-indigo-950 rounded-xl p-3 text-xs text-slate-200 focus:outline-none min-h-[90px]"
              />
            </div>
            <Button type="submit" size="sm">
              Publish Thread Topic
            </Button>
          </form>
        )}

        {/* Topics list */}
        <div className="space-y-3">
          {threads.map(th => (
            <div 
              key={th.id}
              className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:border-indigo-900 transition"
            >
              <div className="space-y-1">
                <h4 className="text-sm font-bold text-white leading-snug">{th.title}</h4>
                <p className="text-xs text-slate-400 leading-relaxed line-clamp-1">{th.preview}</p>
                <span className="block text-[10px] text-slate-500 font-mono">By: {th.author}</span>
              </div>
              <button
                onClick={() => navigateTo(`/community/${th.id}`)}
                className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-0.5 transition shrink-0 cursor-pointer"
              >
                View Thread <ChevronRight size={13} />
              </button>
            </div>
          ))}
        </div>

      </section>
    </div>
  );
};

export default CommunityPage;
