/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Button, Input, Textarea, Select, Badge } from '../DesignSystem';
import { BookOpen, Plus, Trash2, ShieldCheck, Settings, Save } from 'lucide-react';

export const BookEditor: React.FC = () => {
  const [activeBookTab, setActiveBookTab] = useState<'content' | 'metadata'>('content');
  
  // Ebook outline list state
  const [chapters, setChapters] = useState([
    { id: 'ch-1', title: 'Chapter 1: Deviation Formulas', content: 'Base 10 deviations vichalana calculated as...' }
  ]);
  const [selectedChId, setSelectedChId] = useState('ch-1');

  // Input states
  const [chTitle, setChTitle] = useState('');
  const [chContent, setChContent] = useState('');

  // Book metadata details
  const [bookTitle, setBookTitle] = useState('Introduction to Mental Vedic Arithmetic');
  const [isbn, setIsbn] = useState('978-3-16-148410-0');
  const [pricing, setPricing] = useState('999');

  const handleAddChapter = () => {
    if (!chTitle.trim()) return;
    const newId = `ch-${chapters.length + 1}`;
    setChapters(prev => [...prev, { id: newId, title: chTitle, content: chContent }]);
    setChTitle('');
    setChContent('');
    alert('Ebook chapter outlines appended.');
  };

  const selectedCh = chapters.find(c => c.id === selectedChId);

  return (
    <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-6 text-left">
      
      {/* Header controls */}
      <div className="flex justify-between items-center border-b border-indigo-950/45 pb-4">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-1.5 uppercase tracking-wider">
            <BookOpen size={16} className="text-indigo-400" /> Self-Publishing Book Editor
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">Write ebook drafts, upload covers, and configure royalty ISBN parameters.</p>
        </div>

        {/* Action tabs */}
        <div className="flex gap-2 text-xs font-mono select-none">
          <button onClick={() => setActiveBookTab('content')} className={`px-3 py-1 rounded-lg border ${activeBookTab === 'content' ? 'bg-indigo-650 border-indigo-500 text-white font-bold' : 'border-indigo-950 text-slate-500 hover:text-slate-350'}`}>Writing Editor</button>
          <button onClick={() => setActiveBookTab('metadata')} className={`px-3 py-1 rounded-lg border ${activeBookTab === 'metadata' ? 'bg-indigo-650 border-indigo-500 text-white font-bold' : 'border-indigo-950 text-slate-500 hover:text-slate-350'}`}>Book Metadata</button>
        </div>
      </div>

      {/* WRITING CANVAS */}
      {activeBookTab === 'content' && (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          
          {/* Chapter Outline list */}
          <div className="md:col-span-4 space-y-4 border-r border-indigo-950/45 pr-4">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block">Chapter Nodes</span>
            <div className="space-y-2">
              {chapters.map(ch => (
                <button
                  key={ch.id}
                  onClick={() => setSelectedChId(ch.id)}
                  className={`w-full text-left p-3 rounded-xl border transition flex items-center justify-between text-xs cursor-pointer ${selectedChId === ch.id ? 'bg-indigo-950/20 border-indigo-500 text-indigo-400 font-bold' : 'bg-slate-950 border-indigo-955/80 text-slate-450'}`}
                >
                  <span className="truncate pr-2">{ch.title}</span>
                  <Badge variant="primary" className="text-[8px]">DRAFT</Badge>
                </button>
              ))}
            </div>

            {/* Quick Appender */}
            <div className="p-4 bg-slate-950 rounded-xl space-y-3">
              <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">Add Chapter</span>
              <Input placeholder="Chapter Title" value={chTitle} onChange={(e) => setChTitle(e.target.value)} />
              <Button size="sm" onClick={handleAddChapter} className="w-full text-[10px]">Append Chapter</Button>
            </div>
          </div>

          {/* Chapter Details editor text box */}
          <div className="md:col-span-8 space-y-4">
            {selectedCh ? (
              <div className="space-y-4">
                <div className="border-b border-indigo-950/45 pb-3 flex justify-between items-center">
                  <h4 className="text-sm font-bold text-white">{selectedCh.title}</h4>
                  <Button size="sm" className="flex items-center gap-1 text-[10px] py-1.5" onClick={() => alert('Draft saved on memory cache.')}>
                    <Save size={12} /> Save Draft
                  </Button>
                </div>
                <Textarea 
                  label="Chapter rich content paragraphs" 
                  value={chContent} 
                  onChange={(e) => setChContent(e.target.value)}
                  placeholder="Start writing the contents of this chapter guidelines..."
                />
              </div>
            ) : (
              <div className="text-center py-12 text-slate-500 text-xs italic">Select a chapter outline node to begin drafting contents.</div>
            )}
          </div>

        </div>
      )}

      {/* EBOOK METADATA DETAILS */}
      {activeBookTab === 'metadata' && (
        <div className="max-w-xl space-y-4">
          <Input label="Book Publication Title" value={bookTitle} onChange={(e) => setBookTitle(e.target.value)} />
          <div className="grid grid-cols-2 gap-4">
            <Input label="ISBN Code Number" value={isbn} onChange={(e) => setIsbn(e.target.value)} />
            <Input label="Retail Payout Price (INR)" value={pricing} onChange={(e) => setPricing(e.target.value)} />
          </div>
          <Select label="Ebook Category Type">
            <option value="cs">Computer Science & Cryptography</option>
            <option value="math">Vedic Math shortcuts</option>
          </Select>
          <Button onClick={() => alert('Publication submitted for publisher review queue.')}>
            Submit Ebook for Publication Review
          </Button>
        </div>
      )}

    </div>
  );
};

export default BookEditor;
