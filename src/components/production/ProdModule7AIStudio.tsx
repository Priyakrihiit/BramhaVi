/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  Sparkles,
  BookOpen,
  FileText,
  Briefcase,
  Layers,
  ChevronRight,
  TrendingUp,
  Cpu,
  Copy,
  CheckCircle,
  HelpCircle,
  Clock
} from 'lucide-react';

interface AICategory {
  id: string;
  name: string;
  desc: string;
  promptPrefix: string;
  icon: any;
}

export const ProdModule7AIStudio: React.FC = () => {
  const CATEGORIES: AICategory[] = [
    { id: 'course', name: 'Academic Course', desc: 'Syllabus, modules, schedules', promptPrefix: 'Draft a comprehensive structured course curriculum and lesson plan for:', icon: BookOpen },
    { id: 'book', name: 'Book / Publication', desc: 'Chapter index, drafts, summaries', promptPrefix: 'Generate a highly structured chapter index and introductory draft for a self-published book titled:', icon: Layers },
    { id: 'assignment', name: 'LMS Assignment', desc: 'Grading rubrics & tasks', promptPrefix: 'Design a practical assignment sheet with a step-by-step task checklist and strict grading rubric for:', icon: FileText },
    { id: 'business_plan', name: 'Business Plan', desc: 'Proposals, marketing summaries', promptPrefix: 'Draft an executive business plan summary with market opportunities and revenue models for:', icon: Briefcase },
    { id: 'seo_article', name: 'SEO Optimized Article', desc: 'Keywords, headers, backlinks', promptPrefix: 'Write a high-quality SEO article formatted with meta keywords, subheadings, and link recommendations for:', icon: TrendingUp }
  ];

  const [activeCat, setActiveCat] = useState<AICategory>(CATEGORIES[0]);
  const [topic, setTopic] = useState<string>('Quantum Computing Foundations');
  const [promptValue, setPromptValue] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [generatedDraft, setGeneratedDraft] = useState<string>('');
  const [copied, setCopied] = useState<boolean>(false);

  const triggerDraftGeneration = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setPromptValue(`${activeCat.promptPrefix} "${topic}"`);

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: `${activeCat.promptPrefix} "${topic}". Provide a comprehensive, polished, structured markdown output.`
        })
      });
      const data = await response.json();
      if (data.success) {
        setGeneratedDraft(data.text);
      } else {
        setGeneratedDraft(`Error: Could not retrieve AI response. Please verify system configs.`);
      }
    } catch (err: any) {
      setGeneratedDraft(`Failed to execute API fetch: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedDraft);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div id="ai-studio-root" className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 text-left">
        {/* Left Side: Category Picker */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-slate-950/40 border border-slate-900 rounded-xl p-4">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono mb-3">AI Synthesis Category</h4>
            <div className="space-y-1.5">
              {CATEGORIES.map(cat => {
                const IconComp = cat.icon;
                return (
                  <button
                    key={cat.id}
                    onClick={() => setActiveCat(cat)}
                    className={`w-full flex items-center gap-3 p-2.5 rounded-xl transition text-left border ${activeCat.id === cat.id ? 'bg-indigo-950/60 border-indigo-900/50 text-white' : 'bg-transparent border-transparent text-slate-400 hover:bg-slate-900/40 hover:text-slate-200'}`}
                  >
                    <div className={`p-2 rounded-lg bg-slate-950 ${activeCat.id === cat.id ? 'text-indigo-400' : 'text-slate-500'}`}>
                      <IconComp className="w-4.5 h-4.5" />
                    </div>
                    <div>
                      <h5 className="text-xs font-bold">{cat.name}</h5>
                      <p className="text-[10px] text-slate-500 font-sans mt-0.5">{cat.desc}</p>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="bg-slate-950/40 border border-slate-900 rounded-xl p-4 space-y-3">
            <h4 className="text-xs font-bold text-slate-300 font-sans">Draft Parameters</h4>
            <div className="space-y-1">
              <label className="text-[10px] text-slate-500 font-mono font-bold">Subject / Topic</label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. Intro to Rust Lang"
                className="w-full bg-[#0b1329] border border-indigo-950/80 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-sans"
              />
            </div>

            <button
              onClick={triggerDraftGeneration}
              disabled={loading || !topic}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/30 text-white text-xs font-bold py-2 rounded-lg transition flex items-center justify-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              {loading ? 'Synthesizing...' : 'Generate AI Draft'}
            </button>
          </div>
        </div>

        {/* Right Side: Generation Terminal */}
        <div className="lg:col-span-8 bg-slate-950/40 border border-indigo-950/30 rounded-xl p-5 flex flex-col h-[420px] justify-between">
          <div className="flex justify-between items-center pb-3 border-b border-slate-900">
            <div className="flex items-center gap-2">
              <Cpu className="w-4.5 h-4.5 text-indigo-400" />
              <h4 className="text-xs font-black text-white uppercase tracking-wider font-mono">BrahmaVidya AI Draft Engine</h4>
            </div>

            {generatedDraft && (
              <div className="flex items-center gap-2">
                <button
                  onClick={copyToClipboard}
                  className="flex items-center gap-1 text-[10px] text-slate-400 hover:text-indigo-400 transition font-mono bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-lg"
                >
                  {copied ? <CheckCircle className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              </div>
            )}
          </div>

          <div className="flex-1 my-4 overflow-y-auto bg-slate-950 rounded-xl p-4 border border-slate-900 text-xs text-slate-300 font-mono space-y-3 leading-relaxed whitespace-pre-wrap select-text">
            {loading ? (
              <div className="flex flex-col items-center justify-center py-20 space-y-3 text-slate-500 font-sans">
                <div className="animate-spin h-5 w-5 border-2 border-indigo-500 border-t-transparent rounded-full"></div>
                <p className="text-[11px]">Executing high-concurrency model parameters via Gemini API...</p>
              </div>
            ) : generatedDraft ? (
              generatedDraft
            ) : (
              <div className="text-center py-24 text-slate-600 font-sans italic flex flex-col items-center justify-center gap-3">
                <Sparkles className="w-8 h-8 text-slate-700 animate-pulse" />
                <p>Pick a template category and click "Generate AI Draft" to begin drafting.</p>
              </div>
            )}
          </div>

          <div className="pt-3 border-t border-slate-900 flex justify-between items-center text-[10px] text-slate-500 font-mono">
            <span>MODEL: GEMINI-3.5-FLASH</span>
            <div className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-indigo-400" />
              <span>Real-time response time ~1.5s</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProdModule7AIStudio;
