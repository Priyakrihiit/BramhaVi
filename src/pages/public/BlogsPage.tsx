/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { useLayoutStore } from '../../stores/layoutStore';
import { useAuthStore } from '../../stores/authStore';
import { Blog } from '../../types';
import { Button, Input, LoadingSpinner } from '../../components/DesignSystem';
import { ArrowLeft, Calendar, User, MessageSquare, ChevronRight, Send, Sparkles } from 'lucide-react';

export const BlogsPage: React.FC = () => {
  const { currentPath, navigateTo } = useLayoutStore();
  const { currentUser } = useAuthStore();
  const [blogs, setBlogs] = useState<Blog[]>([]);
  const [selectedBlog, setSelectedBlog] = useState<Blog | null>(null);
  const [relatedBlogs, setRelatedBlogs] = useState<Blog[]>([]);
  const [loading, setLoading] = useState(true);

  // Comments mock state
  const [commentText, setCommentText] = useState('');
  const [commentsList, setCommentsList] = useState<any[]>([
    { author: 'Rahul Sharma', text: 'This explanation of DRF permission wrappers is excellent!', date: 'July 2026' },
    { author: 'Dr. Vivek Sharma', text: 'Highly recommended guide for building secure multi-capability ecosystems.', date: 'July 2026' }
  ]);

  // Extract ID or Slug parameter virtual matching: /blogs/:id
  const match = currentPath.match(/^\/blogs\/([^/]+)/);
  const blogId = match ? match[1] : null;

  useEffect(() => {
    setLoading(true);
    if (blogId) {
      Promise.all([
        api.blogs.get(blogId),
        api.blogs.list({ isPublished: true })
      ])
        .then(([blogRes, listRes]) => {
          if (blogRes.success && blogRes.data) {
            setSelectedBlog(blogRes.data);
          }
          if (listRes.success && listRes.data) {
            setRelatedBlogs(listRes.data.filter(b => b.id !== blogId).slice(0, 2));
          }
        })
        .finally(() => setLoading(false));
    } else {
      api.blogs.list({ isPublished: true })
        .then(res => {
          if (res.success && res.data) {
            setBlogs(res.data);
          }
        })
        .finally(() => setLoading(false));
    }
  }, [blogId]);

  const handlePostComment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) {
      alert('Authentication required to post comments. Redirecting to login desk...');
      navigateTo('/auth');
      return;
    }
    if (!commentText.trim()) return;
    setCommentsList(prev => [
      ...prev,
      { author: currentUser.fullName, text: commentText, date: 'Just now' }
    ]);
    setCommentText('');
  };

  if (loading) {
    return <LoadingSpinner text="Compiling platforms blogs..." />;
  }

  // 1. ARTICLE DETAIL VIEW
  if (blogId && selectedBlog) {
    return (
      <div className="flex-1 flex flex-col bg-[#070b19]">
        {/* Breadcrumb Header */}
        <div className="bg-[#0b1329] border-b border-indigo-950/40 px-6 py-4">
          <div className="max-w-3xl mx-auto flex items-center justify-between gap-4 text-xs">
            <button 
              onClick={() => navigateTo('/blogs')}
              className="flex items-center gap-1.5 text-slate-400 hover:text-white transition font-bold"
            >
              <ArrowLeft size={13} /> Back to Blogs
            </button>
            <div className="text-slate-500 font-mono hidden sm:block">
              Home &gt; Blogs &gt; {selectedBlog.title.substring(0, 30)}...
            </div>
          </div>
        </div>

        {/* Detailed Blog Article */}
        <article className="py-12 px-6 max-w-3xl mx-auto w-full text-left space-y-8">
          <header className="space-y-4">
            <span className="px-2.5 py-0.5 rounded bg-indigo-950 text-indigo-400 font-mono text-[9px] uppercase tracking-wider font-bold">
              News & Announcements
            </span>
            <h1 className="text-2xl md:text-4xl font-black text-white leading-tight tracking-tight">{selectedBlog.title}</h1>
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 border-b border-indigo-950/40 pb-6">
              <span className="flex items-center gap-1"><User size={13} /> Author: {selectedBlog.author}</span>
              <span className="hidden md:inline">•</span>
              <span className="flex items-center gap-1"><Calendar size={13} /> Published: {selectedBlog.publishedAt || 'July 2026'}</span>
            </div>
          </header>

          {/* Body Content */}
          <div className="prose prose-invert max-w-none text-xs text-slate-350 leading-relaxed space-y-4">
            <p>{selectedBlog.content || 'Ecosystem logs and tech updates will appear here.'}</p>
          </div>

          {/* Comment Thread Section */}
          <div className="space-y-6 pt-10 border-t border-indigo-950/40">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">Comment Thread ({commentsList.length})</h4>
            
            {/* Comments Feed List */}
            <div className="space-y-4">
              {commentsList.map((comm, cIdx) => (
                <div key={cIdx} className="p-4 bg-slate-900 border border-indigo-950 rounded-xl space-y-1.5">
                  <div className="flex justify-between items-center text-[10px] text-slate-500">
                    <strong className="text-slate-350">{comm.author}</strong>
                    <span>{comm.date}</span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{comm.text}</p>
                </div>
              ))}
            </div>

            {/* Comment Form */}
            <form onSubmit={handlePostComment} className="p-4 bg-slate-900 border border-indigo-950 rounded-xl space-y-3">
              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Add Comment</label>
                <textarea
                  required
                  placeholder="Share your thoughts on this announcement..."
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  className="w-full bg-slate-950 border border-indigo-950 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 min-h-[70px]"
                />
              </div>
              <div className="flex justify-end">
                <Button type="submit" size="sm" className="flex items-center gap-1.5">
                  <Send size={11} /> Post Comment
                </Button>
              </div>
            </form>
          </div>

        </article>

        {/* Recommended Blogs Section */}
        {relatedBlogs.length > 0 && (
          <section className="py-12 border-t border-indigo-950/30 max-w-3xl mx-auto w-full px-6 text-left space-y-6">
            <div>
              <span className="text-[10px] uppercase font-bold tracking-widest text-indigo-400 font-mono flex items-center gap-1">
                <Sparkles size={11} /> Related News
              </span>
              <h3 className="text-lg font-bold text-white tracking-tight mt-0.5">Recommended Announcements</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {relatedBlogs.map((b, idx) => (
                <div key={b.id || idx} className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl flex justify-between items-center hover:border-indigo-900 transition">
                  <div className="space-y-1 pr-4">
                    <h4 className="text-xs font-bold text-white leading-snug line-clamp-1">{b.title}</h4>
                    <span className="text-[9px] text-slate-500 font-mono block mt-1">{b.publishedAt || 'July 2026'}</span>
                  </div>
                  <button 
                    onClick={() => navigateTo(`/blogs/${b.id}`)}
                    className="p-2 bg-indigo-950/40 border border-indigo-900/40 rounded-xl text-indigo-400 hover:text-white hover:bg-indigo-650 transition cursor-pointer shrink-0"
                  >
                    <ChevronRight size={14} />
                  </button>
                </div>
              ))}
            </div>
          </section>
        )}

      </div>
    );
  }

  // 2. LISTING VIEW RENDER
  return (
    <div className="flex-1 flex flex-col bg-[#070b19]">
      {/* Hero Section */}
      <section className="relative py-16 px-8 text-left border-b border-indigo-950/40">
        <div className="absolute top-1/4 left-1/4 w-[300px] h-[300px] bg-indigo-650/10 rounded-full blur-[100px] pointer-events-none"></div>
        <div className="max-w-4xl mx-auto space-y-4">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest font-mono">Galaxy Logbook</span>
          <h1 className="text-3xl font-black text-white tracking-tight">Platform Blogs & News</h1>
          <p className="text-slate-400 text-xs max-w-lg leading-relaxed">
            Read latest corporate announcements, technology disclosures, Vedic math research, and ecosystem compliance updates.
          </p>
        </div>
      </section>

      {/* Grid List of Blogs */}
      <section className="py-16 px-6 max-w-5xl mx-auto w-full">
        {blogs.length === 0 ? (
          <div className="py-12 bg-slate-900/20 border border-dashed border-indigo-950 rounded-2xl text-center text-slate-500 font-mono text-xs">
            No active announcements found in this category.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
            {blogs.map((b, idx) => (
              <div 
                key={b.id || idx}
                className="bg-slate-900 border border-indigo-950 rounded-2xl overflow-hidden hover:border-indigo-900 transition duration-200 flex flex-col justify-between"
              >
                <div className="p-5 space-y-3">
                  <span className="text-[9px] font-bold bg-indigo-950 text-indigo-400 font-mono px-2 py-0.5 rounded uppercase tracking-wider">
                    News
                  </span>
                  <h4 className="text-sm font-bold text-white line-clamp-2 leading-snug">{b.title}</h4>
                  <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                    {b.content || 'Browse technical news releases.'}
                  </p>
                </div>
                <div className="p-4 border-t border-indigo-950/40 bg-slate-900/60 flex justify-between items-center text-[10px] text-slate-500 font-mono">
                  <span>{b.publishedAt || 'July 2026'}</span>
                  <button 
                    onClick={() => navigateTo(`/blogs/${b.id}`)}
                    className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-0.5 transition cursor-pointer"
                  >
                    Read Post <ChevronRight size={13} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default BlogsPage;
