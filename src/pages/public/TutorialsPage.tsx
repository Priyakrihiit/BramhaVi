/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { useLayoutStore } from '../../stores/layoutStore';
import { Tutorial } from '../../types';
import { Input, Button, SkeletonCard, LoadingSpinner } from '../../components/DesignSystem';
import { BookOpen, User, Calendar, Tag, ChevronRight, ArrowLeft, Download, Paperclip, Search } from 'lucide-react';

export const TutorialsPage: React.FC = () => {
  const { currentPath, navigateTo } = useLayoutStore();
  const [tutorials, setTutorials] = useState<Tutorial[]>([]);
  const [selectedTutorial, setSelectedTutorial] = useState<Tutorial | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Search & Filter state
  const [search, setSearch] = useState('');
  const [activeTag, setActiveTag] = useState('All');

  // Parse path parameters virtual matching: /tutorials/:id
  const match = currentPath.match(/^\/tutorials\/([^/]+)/);
  const tutorialId = match ? match[1] : null;

  useEffect(() => {
    setLoading(true);
    if (tutorialId) {
      // Load specific tutorial details
      api.tutorials.get(tutorialId)
        .then(res => {
          if (res.success && res.data) {
            setSelectedTutorial(res.data);
          }
        })
        .finally(() => setLoading(false));
    } else {
      // Load all tutorials list
      api.tutorials.list({ isPublished: true })
        .then(res => {
          if (res.success && res.data) {
            setTutorials(res.data);
          }
        })
        .finally(() => setLoading(false));
    }
  }, [tutorialId]);

  const tags = ['All', 'React', 'TypeScript', 'Tailwind', 'Vite', 'Django', 'Celery', 'PostgreSQL'];

  const filteredTutorials = tutorials.filter(tut => {
    const matchesSearch = tut.title.toLowerCase().includes(search.toLowerCase()) || 
                          (tut.content && tut.content.toLowerCase().includes(search.toLowerCase()));
    
    // In our type `Tutorial`, we can extract tags or category
    const matchesTag = activeTag === 'All' || 
                       (tut.title.toLowerCase().includes(activeTag.toLowerCase())) ||
                       (tut.content && tut.content.toLowerCase().includes(activeTag.toLowerCase()));
    return matchesSearch && matchesTag;
  });

  if (loading) {
    return <LoadingSpinner text="Compiling technical tutorials..." />;
  }

  // 1. DETAIL VIEW RENDER
  if (tutorialId && selectedTutorial) {
    return (
      <div className="flex-1 flex flex-col bg-[#070b19]">
        {/* Breadcrumb Header */}
        <div className="bg-[#0b1329] border-b border-indigo-950/40 px-6 py-4">
          <div className="max-w-4xl mx-auto flex items-center justify-between gap-4 text-xs">
            <button 
              onClick={() => navigateTo('/tutorials')}
              className="flex items-center gap-1.5 text-slate-400 hover:text-white transition font-bold"
            >
              <ArrowLeft size={13} /> Back to Tutorials
            </button>
            <div className="text-slate-500 font-mono hidden sm:block">
              Home &gt; Tutorials &gt; {selectedTutorial.title.substring(0, 30)}...
            </div>
          </div>
        </div>

        {/* Detailed article layout */}
        <article className="py-12 px-6 max-w-4xl mx-auto w-full text-left space-y-8">
          <header className="space-y-4">
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded bg-indigo-950 text-indigo-400 font-mono text-[9px] uppercase tracking-wider font-bold">
              <Tag size={10} /> TECHNICAL GUIDE
            </span>
            <h1 className="text-2xl md:text-4xl font-black text-white leading-tight tracking-tight">{selectedTutorial.title}</h1>
            
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 border-b border-indigo-950/40 pb-6">
              <span className="flex items-center gap-1"><User size={13} /> Author ID: {selectedTutorial.author}</span>
              <span className="hidden md:inline">•</span>
              <span className="flex items-center gap-1"><Calendar size={13} /> Published: {selectedTutorial.publishedAt || 'July 2026'}</span>
            </div>
          </header>

          {/* Core Content Box (Simulated Markdown/Written tutorial rendering) */}
          <div className="prose prose-invert max-w-none text-xs text-slate-350 space-y-4 leading-relaxed bg-slate-900/20 border border-indigo-950 p-6 rounded-2xl">
            <p>
              {selectedTutorial.content || 'Here is the detailed step-by-step instruction log configured for this topic. Use code snippets and schemas below to establish connections.'}
            </p>
            <h3 className="text-sm font-bold text-white mt-6 uppercase tracking-wider">Example Blueprint Configuration</h3>
            <pre className="p-4 bg-slate-950 border border-indigo-950 rounded-xl overflow-x-auto text-[11px] font-mono text-indigo-300">
{`# BrahmaVidya Galaxy - Tech Tutorial Hook
import os

def check_identity(user_id, active_capabilities):
    if "ADMIN" in active_capabilities:
        return True
    return False

# Initialize check
print(check_identity("USR-9042", ["LEARNING", "TEACHING"]))`}
            </pre>
          </div>

          {/* Attachments Section */}
          <div className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl space-y-3">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Paperclip size={14} className="text-indigo-400" /> Attached Resources
            </h4>
            <div className="flex flex-wrap gap-3">
              <Button size="sm" variant="secondary" className="text-[10px]" onClick={() => alert('Downloading technical schematics PDF...')}>
                <Download size={12} /> download_schematics.pdf
              </Button>
              <Button size="sm" variant="secondary" className="text-[10px]" onClick={() => alert('Copying blueprint source code...')}>
                <Download size={12} /> setup_hooks.py
              </Button>
            </div>
          </div>
        </article>
      </div>
    );
  }

  // 2. LISTING VIEW RENDER
  return (
    <div className="flex-1 flex flex-col bg-[#070b19]">
      {/* Hero Header */}
      <section className="relative py-16 px-8 text-left border-b border-indigo-950/40">
        <div className="absolute top-1/4 left-1/4 w-[300px] h-[300px] bg-indigo-650/10 rounded-full blur-[100px] pointer-events-none"></div>
        <div className="max-w-4xl mx-auto space-y-4">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest font-mono">Platform Documentation</span>
          <h1 className="text-3xl font-black text-white tracking-tight">Written Tutorials Hub</h1>
          <p className="text-slate-400 text-xs max-w-lg leading-relaxed">
            Access exhaustive, step-by-step guides, code blocks, blueprints, and download resources compiled by certified teachers and professionals.
          </p>
        </div>
      </section>

      {/* Filter and Search Bar */}
      <section className="py-6 px-6 max-w-5xl mx-auto w-full flex flex-col sm:flex-row gap-4 items-center justify-between border-b border-indigo-950/20 text-xs">
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-2.5 text-slate-500" size={14} />
          <input
            type="text"
            placeholder="Search guides..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-900 border border-indigo-950 rounded-xl py-2 pl-9 pr-4 text-xs text-slate-300 focus:outline-none"
          />
        </div>
        
        <div className="flex flex-wrap gap-1.5 w-full sm:w-auto justify-start sm:justify-end">
          {tags.map(t => (
            <button
              key={t}
              onClick={() => setActiveTag(t)}
              className={`px-3 py-1 rounded-xl text-[10px] font-semibold transition border ${activeTag === t ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-slate-900 border-indigo-950 text-slate-450 hover:text-white'}`}
            >
              {t}
            </button>
          ))}
        </div>
      </section>

      {/* Grid of Tutorial Cards */}
      <section className="py-12 px-6 max-w-5xl mx-auto w-full">
        {filteredTutorials.length === 0 ? (
          <div className="py-12 bg-slate-900/20 border border-dashed border-indigo-950 rounded-2xl text-center py-20 text-slate-500 font-mono text-xs">
            No matching technical guides found in this catalog.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
            {filteredTutorials.map((tut, idx) => (
              <div 
                key={tut.id || idx} 
                className="bg-slate-900 border border-indigo-950 rounded-2xl flex flex-col justify-between overflow-hidden hover:border-indigo-900 transition duration-200"
              >
                <div className="p-5 space-y-3">
                  <div className="flex items-center gap-1.5 text-[9px] text-indigo-400 font-mono font-bold uppercase">
                    <BookOpen size={11} /> Technical guide
                  </div>
                  <h4 className="text-sm font-bold text-white leading-snug line-clamp-2">{tut.title}</h4>
                  <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                    {tut.content || 'Browse technical instructions and blueprints.'}
                  </p>
                </div>
                <div className="p-4 border-t border-indigo-950/40 bg-slate-900/60 flex justify-between items-center text-[10px] text-slate-500 font-mono">
                  <span>Author ID: {tut.author}</span>
                  <button 
                    onClick={() => navigateTo(`/tutorials/${tut.id}`)}
                    className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-0.5 transition cursor-pointer"
                  >
                    Read Guide <ChevronRight size={13} />
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

export default TutorialsPage;
