/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { CheckSquare, Plus, Trash2, HelpCircle, AlignLeft, Award, Save } from 'lucide-react';
import { Button, Input, Badge } from '../DesignSystem';

interface Question {
  id: string;
  text: string;
  options: string[];
  correctIndex: number;
}

interface Quiz {
  id: string;
  title: string;
  courseTitle: string;
  durationMinutes: number;
  passingScore: number;
  questionsCount: number;
}

export const QuizBuilder: React.FC = () => {
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Quiz form states
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [courseTitle, setCourseTitle] = useState('Quantum Consciousness Mechanics');
  const [duration, setDuration] = useState('30');
  const [passingScore, setPassingScore] = useState('70');
  
  // Custom Question accumulator list state
  const [questions, setQuestions] = useState<Question[]>([]);
  const [qText, setQText] = useState('');
  const [options, setOptions] = useState(['', '', '', '']);
  const [correctIndex, setCorrectIndex] = useState(0);

  const fetchQuizzes = async () => {
    setLoading(true);
    try {
      const catRes = await fetch('/api/v1/teacher/quiz/categories/');
      const res = await fetch('/api/v1/teacher/quiz/');
      if (res.ok) {
        const data = await res.json();
        setQuizzes(data.results || data);
      } else {
        setQuizzes([
          { id: 'q-1', title: 'Double Slit Resonance & Intent', courseTitle: 'Quantum Consciousness Mechanics', durationMinutes: 15, passingScore: 70, questionsCount: 5 },
          { id: 'q-2', title: 'Ashtadhyayi Sandhi Formulations', courseTitle: 'Vedic Computational Syntax', durationMinutes: 20, passingScore: 75, questionsCount: 6 }
        ]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuizzes();
  }, []);

  const handleAddQuestion = () => {
    if (!qText.trim()) return;
    const newQ: Question = {
      id: `q-${Date.now()}`,
      text: qText,
      options: [...options],
      correctIndex
    };
    setQuestions(prev => [...prev, newQ]);
    
    // Reset question form
    setQText('');
    setOptions(['', '', '', '']);
    setCorrectIndex(0);
  };

  const handleOptionChange = (idx: number, val: string) => {
    const updated = [...options];
    updated[idx] = val;
    setOptions(updated);
  };

  const handleRemoveQuestion = (id: string) => {
    setQuestions(prev => prev.filter(q => q.id !== id));
  };

  const handleSaveQuiz = (e: React.FormEvent) => {
    e.preventDefault();
    if (questions.length === 0) {
      alert('Please add at least one question to the quiz bank.');
      return;
    }

    const newQuiz: Quiz = {
      id: `quiz-${Date.now()}`,
      title,
      courseTitle,
      durationMinutes: Number(duration),
      passingScore: Number(passingScore),
      questionsCount: questions.length
    };

    setQuizzes(prev => [newQuiz, ...prev]);
    setIsFormOpen(false);
    
    // Clear whole form
    setTitle('');
    setQuestions([]);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <CheckSquare className="text-indigo-400" size={20} />
            Interactive Quiz Builder
          </h2>
          <p className="text-xs text-slate-400 font-sans">Formulate conceptual quizzes, establish passing standards, and draft multiple choice structures.</p>
        </div>

        <Button onClick={() => setIsFormOpen(true)} size="sm" variant="primary">
          <Plus size={14} /> Create Quiz
        </Button>
      </div>

      {isFormOpen && (
        <form onSubmit={handleSaveQuiz} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6 animate-fade-in">
          <h3 className="text-sm font-bold text-slate-200">Construct Dynamic Evaluation</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input label="Quiz Title" placeholder="e.g. Neuronal Quantum Spans" value={title} onChange={e => setTitle(e.target.value)} required />
            <div>
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Program Area</label>
              <select
                className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-2.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                value={courseTitle}
                onChange={e => setCourseTitle(e.target.value)}
              >
                <option value="Quantum Consciousness Mechanics">Quantum Consciousness Mechanics</option>
                <option value="Vedic Computational Syntax">Vedic Computational Syntax</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input label="Duration (Minutes)" type="number" value={duration} onChange={e => setDuration(e.target.value)} required />
            <Input label="Passing Score (%)" type="number" value={passingScore} onChange={e => setPassingScore(e.target.value)} required />
          </div>

          {/* Question addition panel */}
          <div className="bg-slate-950/60 border border-indigo-950/60 p-5 rounded-2xl space-y-4">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">Draft Question</h4>
            <Input label="Question Text" placeholder="e.g. What is the fundamental particle of neurological thought?" value={qText} onChange={e => setQText(e.target.value)} />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {options.map((opt, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <span className="text-[10px] font-mono text-slate-500 font-bold select-none">{String.fromCharCode(65 + idx)})</span>
                  <input
                    type="text"
                    placeholder={`Option ${String.fromCharCode(65 + idx)}`}
                    value={opt}
                    onChange={e => handleOptionChange(idx, e.target.value)}
                    className="flex-1 bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-slate-200 outline-none focus:border-indigo-500"
                  />
                  <input
                    type="radio"
                    name="correctIndex"
                    checked={correctIndex === idx}
                    onChange={() => setCorrectIndex(idx)}
                    className="cursor-pointer"
                  />
                </div>
              ))}
            </div>

            <button
              type="button"
              onClick={handleAddQuestion}
              className="px-4 py-2 bg-slate-900 border border-slate-800 hover:text-white rounded-xl text-xs font-bold transition flex items-center gap-1 ml-auto"
            >
              <Plus size={12} /> Add to Draft Quiz
            </button>
          </div>

          {/* Draft accumulator list */}
          {questions.length > 0 && (
            <div className="space-y-2 select-none">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Draft Questions ({questions.length})</span>
              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {questions.map((q, idx) => (
                  <div key={q.id} className="p-3 bg-slate-950 border border-slate-850 rounded-xl flex items-center justify-between text-xs">
                    <span className="truncate text-slate-300 font-medium">
                      <strong className="text-indigo-400 mr-1.5">{idx + 1}.</strong> {q.text}
                    </span>
                    <button type="button" onClick={() => handleRemoveQuestion(q.id)} className="text-rose-400 hover:text-rose-300">
                      <Trash2 size={12} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end gap-2.5 pt-2 border-t border-slate-850">
            <Button type="button" variant="ghost" size="sm" onClick={() => setIsFormOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary" size="sm">
              <Save size={14} /> Publish Quiz
            </Button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="text-center py-8 text-xs text-slate-500">Querying quiz programs...</div>
      ) : quizzes.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl text-slate-500 text-xs">
          No quizzes mapped yet. Create one above to establish active drills!
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {quizzes.map(quiz => (
            <div key={quiz.id} className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between hover:border-indigo-500/20 transition">
              <div className="space-y-2">
                <div className="flex justify-between items-start">
                  <h4 className="font-bold text-white text-sm">{quiz.title}</h4>
                  <Badge variant="outline">{quiz.questionsCount} MCQs</Badge>
                </div>
                <p className="text-xs text-slate-400">{quiz.courseTitle}</p>
              </div>

              <div className="border-t border-slate-800/80 mt-4 pt-3 flex justify-between items-center text-[10px] text-slate-500 font-mono">
                <span className="flex items-center gap-1"><AlignLeft size={10} /> ⏱️ {quiz.durationMinutes} Minutes</span>
                <span className="flex items-center gap-1"><Award size={10} className="text-amber-500" /> Passing: {quiz.passingScore}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
