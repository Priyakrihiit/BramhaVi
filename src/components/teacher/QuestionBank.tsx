/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { HelpCircle, Search, Plus, Filter, BookOpen, Trash2 } from 'lucide-react';
import { Button, Input, Badge } from '../DesignSystem';

interface BankQuestion {
  id: string;
  text: string;
  domain: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  options: string[];
  correctIndex: number;
}

export const QuestionBank: React.FC = () => {
  const [questions, setQuestions] = useState<BankQuestion[]>([
    {
      id: 'qb-1',
      text: 'What neurological state correlates with the Planck length consciousness limit?',
      domain: 'Quantum Consciousness Mechanics',
      difficulty: 'Hard',
      options: ['Alpha brain waves synchronization', 'Microtubules super-coherence', 'Cerebellum core synapse decay', 'Hippocampus temporal fold'],
      correctIndex: 1
    },
    {
      id: 'qb-2',
      text: 'Which Paninian Sutra controls the rules of vowel Sandhi formulations?',
      domain: 'Vedic Computational Syntax',
      difficulty: 'Medium',
      options: ['Ikoyanaci', 'Adengunah', 'Vriddhireci', 'Halantyam'],
      correctIndex: 0
    },
    {
      id: 'qb-3',
      text: 'In standard double-slit models, what happens to the interference waveform during observer intent measurements?',
      domain: 'Quantum Consciousness Mechanics',
      difficulty: 'Hard',
      options: ['Wavelength doubles', 'Waveform collapses to localized particles', 'Infinite diffraction paths emerge', 'Signal amplification occurs'],
      correctIndex: 1
    }
  ]);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('All');
  
  // Question Builder Form states
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [text, setText] = useState('');
  const [domain, setDomain] = useState('Quantum Consciousness Mechanics');
  const [difficulty, setDifficulty] = useState<'Easy' | 'Medium' | 'Hard'>('Medium');
  const [options, setOptions] = useState(['', '', '', '']);
  const [correctIndex, setCorrectIndex] = useState(0);

  const handleAddQuestion = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;

    const newQ: BankQuestion = {
      id: `qb-${Date.now()}`,
      text,
      domain,
      difficulty,
      options: [...options],
      correctIndex
    };

    setQuestions(prev => [newQ, ...prev]);
    resetForm();
  };

  const handleOptionChange = (idx: number, val: string) => {
    const updated = [...options];
    updated[idx] = val;
    setOptions(updated);
  };

  const handleDelete = (id: string) => {
    setQuestions(prev => prev.filter(q => q.id !== id));
  };

  const resetForm = () => {
    setText('');
    setOptions(['', '', '', '']);
    setCorrectIndex(0);
    setIsFormOpen(false);
  };

  const filteredQuestions = questions.filter(q => {
    const matchesSearch = q.text.toLowerCase().includes(searchQuery.toLowerCase()) || q.domain.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDifficulty = selectedDifficulty === 'All' || q.difficulty === selectedDifficulty;
    return matchesSearch && matchesDifficulty;
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <HelpCircle className="text-indigo-400" size={20} />
            Centralized Question Bank
          </h2>
          <p className="text-xs text-slate-400">Add, organize, and inspect atomic exam questions for cognitive assessments.</p>
        </div>

        <Button onClick={() => setIsFormOpen(true)} size="sm" variant="primary">
          <Plus size={14} /> Add Question
        </Button>
      </div>

      {isFormOpen && (
        <form onSubmit={handleAddQuestion} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 animate-fade-in">
          <h3 className="text-sm font-bold text-slate-200">Register Atomic Question Node</h3>
          
          <Input label="Question Core Text" placeholder="Enter question formulation..." value={text} onChange={e => setText(e.target.value)} required />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Syllabus Domain</label>
              <select
                className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-2.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                value={domain}
                onChange={e => setDomain(e.target.value)}
              >
                <option value="Quantum Consciousness Mechanics">Quantum Consciousness Mechanics</option>
                <option value="Vedic Computational Syntax">Vedic Computational Syntax</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Difficulty Weight</label>
              <select
                className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-2.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                value={difficulty}
                onChange={e => setDifficulty(e.target.value as any)}
              >
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </div>
          </div>

          <div className="space-y-3">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block select-none">Formulate Choices & Flag Key Answer</label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {options.map((opt, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-slate-500">{String.fromCharCode(65 + idx)})</span>
                  <input
                    type="text"
                    placeholder={`Choice ${String.fromCharCode(65 + idx)}`}
                    value={opt}
                    onChange={e => handleOptionChange(idx, e.target.value)}
                    required
                    className="flex-1 bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-250 outline-none focus:border-indigo-500"
                  />
                  <input
                    type="radio"
                    name="bankCorrect"
                    checked={correctIndex === idx}
                    onChange={() => setCorrectIndex(idx)}
                    className="cursor-pointer"
                  />
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-2.5 pt-2 border-t border-slate-850">
            <Button type="button" variant="ghost" size="sm" onClick={resetForm}>Cancel</Button>
            <Button type="submit" variant="primary" size="sm">Register Node</Button>
          </div>
        </form>
      )}

      {/* Filter strip */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-3 text-slate-500" size={14} />
          <input
            type="text"
            placeholder="Search questions or keywords..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900 border border-indigo-950/80 rounded-xl py-2.5 pl-10 pr-4 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div className="flex gap-2 text-xs">
          {['All', 'Easy', 'Medium', 'Hard'].map(d => (
            <button
              key={d}
              onClick={() => setSelectedDifficulty(d)}
              className={`px-4 py-2.5 rounded-xl font-bold border transition ${selectedDifficulty === d ? 'bg-indigo-650 border-indigo-550 text-white' : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'}`}
            >
              {d}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        {filteredQuestions.length === 0 ? (
          <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl text-slate-500 text-xs">
            No question entries match your filters.
          </div>
        ) : (
          filteredQuestions.map(q => (
            <div key={q.id} className="bg-slate-900/40 border border-slate-850 p-5 rounded-2xl space-y-4 hover:border-indigo-500/20 transition flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex justify-between items-start">
                  <span className="text-[10px] bg-slate-950/60 border border-slate-800 px-2.5 py-1 text-slate-400 rounded-full flex items-center gap-1">
                    <BookOpen size={10} className="text-slate-500" />
                    {q.domain}
                  </span>
                  <Badge variant={q.difficulty === 'Hard' ? 'danger' : q.difficulty === 'Medium' ? 'warning' : 'success'}>
                    {q.difficulty}
                  </Badge>
                </div>

                <h4 className="font-bold text-white text-sm leading-relaxed">{q.text}</h4>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2 select-none">
                  {q.options.map((opt, oIdx) => (
                    <div key={oIdx} className={`p-2.5 rounded-lg border text-xs flex items-center gap-2 ${q.correctIndex === oIdx ? 'bg-indigo-950/25 border-indigo-500/35 text-indigo-300 font-medium' : 'bg-slate-950/30 border-slate-850 text-slate-400'}`}>
                      <span className="font-mono text-[10px] font-bold text-slate-500">{String.fromCharCode(65 + oIdx)})</span>
                      <span className="truncate">{opt}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="border-t border-slate-850/80 pt-3 flex justify-end">
                <button onClick={() => handleDelete(q.id)} className="p-1.5 rounded bg-rose-950/20 hover:bg-rose-900 text-rose-400 hover:text-white transition">
                  <Trash2 size={12} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
