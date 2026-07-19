/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { UnifiedSearchResult, SearchCategory } from './types';
import { Search, Filter, BookOpen, BookText, Briefcase, MessageSquare, ExternalLink, Sparkles } from 'lucide-react';

const SEARCH_MOCK_DATABASE: UnifiedSearchResult[] = [
  {
    id: 'res-1',
    title: 'Nikhilam Sutra & Modular Remainder Bounds',
    description: 'Advance your division speed using Vedic mathematics techniques. Complete with video tutorials, screen-share lectures, and certification tests.',
    category: 'COURSES',
    matchType: 'Keyword Title Match',
    url: '#courses',
    relevanceScore: 98
  },
  {
    id: 'res-2',
    title: 'Introduction to Django REST Framework & SaaS Architecture',
    description: 'E-Book detailing microservices, Postgres double-entry ledgers, Celery tasks, and JWT multi-tenant schemas.',
    category: 'BOOKS',
    matchType: 'Fuzzy Title Match',
    url: '#bookstore',
    relevanceScore: 92
  },
  {
    id: 'res-3',
    title: 'Senior Full Stack Django Architect Needed',
    description: 'Full-time career opportunity with compensation up to ₹18,00,000 per annum. Apply now with simulated resume portfolios.',
    category: 'CAREERS',
    matchType: 'Description Skill Match',
    url: '#careers',
    relevanceScore: 84
  },
  {
    id: 'res-4',
    title: 'Is Nikhilam Sutra efficient for larger modular prime divisors?',
    description: 'Community forum Q&A thread with certified solutions. Reviewed and validated by Dr. Ananya Iyer.',
    category: 'DISCUSSIONS',
    matchType: 'Forum Thread Match',
    url: '#community',
    relevanceScore: 89
  },
  {
    id: 'res-5',
    title: 'Vedic Geometry Course - Sulba Sutras Basic Calculations',
    description: 'Learn ancient geometric construction methods, Vedic trigonometry scales, and modern CAD integration layouts.',
    category: 'COURSES',
    matchType: 'Keyword Title Match',
    url: '#courses',
    relevanceScore: 78
  }
];

export const Module12Search: React.FC = () => {
  const [query, setQuery] = useState('');
  const [selectedCat, setSelectedCat] = useState<'ALL' | SearchCategory>('ALL');

  const filteredResults = SEARCH_MOCK_DATABASE.filter(item => {
    // Filter by Category first
    const catMatches = selectedCat === 'ALL' || item.category === selectedCat;
    
    // Filter by text search
    if (!query.trim()) return catMatches;
    const txt = query.toLowerCase();
    const titleMatches = item.title.toLowerCase().includes(txt);
    const descMatches = item.description.toLowerCase().includes(txt);
    
    return catMatches && (titleMatches || descMatches);
  }).sort((a,b) => b.relevanceScore - a.relevanceScore);

  return (
    <div id="saas-module-12" className="space-y-6 text-slate-100">
      {/* Page Header */}
      <div className="bg-slate-900/60 border border-indigo-950 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 text-left">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Search className="text-indigo-400 w-5 h-5" />
            Elastic Global Search & Full-Text Vector Query Index
          </h2>
          <p className="text-slate-400 text-xs mt-1">
            Unified query portal. Executes sub-second indexed search scans across courses, academic e-books, active community Q&A, organization tenants, and employer vacancies simultaneously.
          </p>
        </div>
      </div>

      {/* Global Search Inputs */}
      <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 space-y-4 text-left">
        <div className="flex gap-2">
          <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 flex items-center gap-3 focus-within:border-indigo-500 transition">
            <Search className="w-5 h-5 text-slate-500 shrink-0" />
            <input
              type="text"
              placeholder="Search across LMS, Bookstore, Jobs, Discussions, and Portals..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="bg-transparent border-none text-xs text-white placeholder-slate-500 focus:outline-none flex-1 font-sans"
            />
          </div>
        </div>

        {/* Categories Pills Filters */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <span className="text-slate-500 text-[10px] uppercase font-bold mr-2 flex items-center gap-1"><Filter className="w-3.5 h-3.5" /> Filter Matrix:</span>
          {['ALL', 'COURSES', 'BOOKS', 'DISCUSSIONS', 'CAREERS'].map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCat(cat as any)}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition ${selectedCat === cat ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-slate-400 hover:text-slate-200'}`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Search results stack */}
      <div className="space-y-4 text-left">
        <span className="text-xs font-bold text-slate-500 uppercase tracking-widest block font-mono">Found {filteredResults.length} indexed search matches:</span>
        <div className="space-y-3">
          {filteredResults.map(res => {
            return (
              <div
                key={res.id}
                className="bg-slate-950/40 border border-slate-900 hover:border-indigo-900/50 rounded-2xl p-5 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 transition duration-300"
              >
                <div className="space-y-1.5 flex-1 text-left">
                  <div className="flex flex-wrap items-center gap-2">
                    {/* Category specific icons */}
                    {res.category === 'COURSES' && <span className="bg-indigo-500/10 text-indigo-400 p-1 rounded"><BookOpen className="w-3.5 h-3.5" /></span>}
                    {res.category === 'BOOKS' && <span className="bg-emerald-500/10 text-emerald-400 p-1 rounded"><BookText className="w-3.5 h-3.5" /></span>}
                    {res.category === 'DISCUSSIONS' && <span className="bg-amber-500/10 text-amber-400 p-1 rounded"><MessageSquare className="w-3.5 h-3.5" /></span>}
                    {res.category === 'CAREERS' && <span className="bg-rose-500/10 text-rose-400 p-1 rounded"><Briefcase className="w-3.5 h-3.5" /></span>}

                    <span className="text-[10px] text-slate-500 uppercase font-bold font-mono">{res.category}</span>
                    <span className="text-slate-600 text-[10px] font-mono">•</span>
                    <span className="text-slate-500 text-[10px] font-mono">{res.matchType}</span>
                  </div>

                  <h3 className="text-sm font-extrabold text-white">{res.title}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed font-sans">{res.description}</p>
                </div>

                {/* Score badge & Anchor redirect button */}
                <div className="flex items-center gap-4 shrink-0 font-mono text-xs w-full md:w-auto justify-between md:justify-end">
                  <div className="flex items-center gap-1 bg-slate-900 border border-slate-850 px-2.5 py-1 rounded-lg">
                    <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                    <span className="text-slate-300">Relevance: <strong className="text-indigo-400">{res.relevanceScore}%</strong></span>
                  </div>
                  
                  <a
                    href={res.url}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-4 py-2 rounded-xl transition flex items-center gap-1"
                  >
                    Go To <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            );
          })}
          {filteredResults.length === 0 && (
            <div className="bg-slate-950/40 border border-slate-900 rounded-2xl h-48 flex flex-col items-center justify-center text-slate-600">
              <Search className="w-10 h-10 mb-2 stroke-[1.5]" />
              <p className="text-xs">No indexed database objects match your search parameters. Try expanding filters.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Module12Search;
