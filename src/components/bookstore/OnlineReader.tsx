/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Button } from '../DesignSystem';
import { BookOpen, Bookmark, Sun, Moon, Sparkles, X, ChevronRight } from 'lucide-react';

interface OnlineReaderProps {
  bookTitle: string;
  onClose: () => void;
}

export const OnlineReader: React.FC<OnlineReaderProps> = ({ bookTitle, onClose }) => {
  const [activeChapterIdx, setActiveChapterIdx] = useState(0);
  const [fontSize, setFontSize] = useState<'sm' | 'md' | 'lg' | 'xl'>('md');
  const [readerTheme, setReaderTheme] = useState<'light' | 'dark' | 'gold'>('dark');

  const chapters = [
    { title: 'Chapter 1: Sutra Calculations Deviations', content: 'In Vedic Mathematics, calculations rely on baseline offsets. If deviation vichalana is positive, we add; if negative, we subtract.' },
    { title: 'Chapter 2: Double-Entry Cryptographic Ledger bluepritns', content: 'Every financial entry is verified against a digital ledger key. Authors receive instant royalties settlement distributions.' }
  ];

  const fontClasses = {
    sm: 'text-xs leading-normal',
    md: 'text-sm leading-relaxed',
    lg: 'text-base leading-loose',
    xl: 'text-lg leading-loose font-serif'
  };

  const themeClasses = {
    light: 'bg-white text-slate-900 border-slate-200',
    dark: 'bg-slate-950 text-slate-100 border-indigo-950/40',
    gold: 'bg-amber-950/20 text-amber-200 border-amber-900/40'
  };

  return (
    <div className={`fixed inset-0 z-50 flex flex-col font-sans transition-colors duration-200 ${readerTheme === 'light' ? 'bg-slate-50' : 'bg-slate-950'}`}>
      
      {/* Top Controls Bar */}
      <header className={`p-4 border-b flex items-center justify-between shadow-md ${themeClasses[readerTheme]}`}>
        <div className="flex items-center gap-3">
          <BookOpen className="text-indigo-400" size={18} />
          <h2 className="text-sm font-black truncate max-w-sm">{bookTitle}</h2>
        </div>

        {/* Configurations panel */}
        <div className="flex items-center gap-4 text-xs font-mono select-none">
          {/* Theme toggles */}
          <div className="flex gap-1">
            <button onClick={() => setReaderTheme('light')} className={`p-1.5 rounded ${readerTheme === 'light' ? 'bg-indigo-650 text-white' : 'text-slate-500 hover:text-white'}`}><Sun size={12} /></button>
            <button onClick={() => setReaderTheme('dark')} className={`p-1.5 rounded ${readerTheme === 'dark' ? 'bg-indigo-650 text-white' : 'text-slate-500 hover:text-white'}`}><Moon size={12} /></button>
            <button onClick={() => setReaderTheme('gold')} className={`p-1.5 rounded ${readerTheme === 'gold' ? 'bg-indigo-650 text-amber-300 font-bold' : 'text-slate-500 hover:text-amber-300'}`}>G</button>
          </div>

          <span>|</span>

          {/* Font Sizes */}
          <div className="flex gap-1">
            {['sm', 'md', 'lg', 'xl'].map((sz) => (
              <button 
                key={sz} 
                onClick={() => setFontSize(sz as any)} 
                className={`px-2 py-0.5 rounded uppercase ${fontSize === sz ? 'bg-indigo-650 text-white font-bold' : 'text-slate-500 hover:text-white'}`}
              >
                {sz}
              </button>
            ))}
          </div>

          <button onClick={onClose} className="p-2 rounded-xl hover:bg-slate-900 text-slate-400 hover:text-white transition cursor-pointer">
            <X size={15} />
          </button>
        </div>
      </header>

      {/* Main Split Layout */}
      <div className="flex-grow grid grid-cols-1 lg:grid-cols-12 overflow-hidden">
        
        {/* Left Table of Contents */}
        <div className={`lg:col-span-3 border-r p-4 overflow-y-auto text-left ${themeClasses[readerTheme]}`}>
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block mb-4">Table of Contents</span>
          <div className="space-y-1 text-xs">
            {chapters.map((ch, idx) => (
              <button
                key={idx}
                onClick={() => setActiveChapterIdx(idx)}
                className={`w-full text-left p-3 rounded-xl border transition flex items-center justify-between cursor-pointer ${activeChapterIdx === idx ? 'bg-indigo-950/20 border-indigo-500 text-indigo-400 font-bold' : 'bg-slate-900 border-indigo-955/40 text-slate-400'}`}
              >
                <span className="truncate pr-2">{ch.title}</span>
                <ChevronRight size={12} />
              </button>
            ))}
          </div>
        </div>

        {/* Center Reading canvas */}
        <div className="lg:col-span-9 p-8 lg:p-14 overflow-y-auto text-left flex justify-center">
          <article className={`max-w-2xl w-full space-y-6 ${fontClasses[fontSize]}`}>
            <h3 className="text-xl font-black border-b border-indigo-950/20 pb-4">{chapters[activeChapterIdx].title}</h3>
            <p className="indent-8 leading-relaxed font-sans">{chapters[activeChapterIdx].content}</p>
            
            {/* Bookmark options */}
            <div className="pt-8 border-t border-indigo-950/20 flex gap-4 text-xs select-none">
              <button onClick={() => alert('Bookmark logged.')} className="text-slate-500 hover:text-indigo-400 transition flex items-center gap-1.5 cursor-pointer">
                <Bookmark size={13} /> Add bookmark
              </button>
            </div>
          </article>
        </div>

      </div>

    </div>
  );
};

export default OnlineReader;
