/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { HelpCircle, CheckCircle, XCircle, ArrowRight, Loader2, Bot, Sparkles, Award } from 'lucide-react';

interface QuizQuestion {
  question: string;
  options: string[];
  answer: string;
}

interface QuizPracticeProps {
  onClose: () => void;
}

export default function QuizPractice({ onClose }: QuizPracticeProps) {
  const [topic, setTopic] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selectedAns, setSelectedAns] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [score, setScore] = useState(0);
  const [completed, setCompleted] = useState(false);

  const startQuizGeneration = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setIsGenerating(true);
    setQuestions([]);
    setCurrentIdx(0);
    setSelectedAns(null);
    setIsSubmitted(false);
    setScore(0);
    setCompleted(false);

    try {
      const res = await fetch('/api/ai/generate-quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic })
      });
      const data = await res.json();
      if (data.success && Array.isArray(data.data)) {
        setQuestions(data.data);
      } else {
        alert('Could not formulate quiz nodes. Please try again.');
      }
    } catch (err) {
      console.error(err);
      alert('Error communicating with AI Quiz compiler.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSubmitAnswer = () => {
    if (!selectedAns) return;
    setIsSubmitted(true);
    const correct = selectedAns === questions[currentIdx].answer;
    if (correct) {
      setScore(prev => prev + 1);
    }
  };

  const handleNext = () => {
    if (currentIdx + 1 < questions.length) {
      setCurrentIdx(currentIdx + 1);
      setSelectedAns(null);
      setIsSubmitted(false);
    } else {
      setCompleted(true);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-xl shadow-2xl overflow-hidden text-slate-100 flex flex-col">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex justify-between items-center bg-slate-950/40">
          <div className="flex items-center gap-2">
            <Sparkles className="text-amber-400" size={18} />
            <h3 className="font-bold text-white text-base">Vidya AI Smart Practice Arena</h3>
          </div>
          <button 
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-all text-sm font-bold"
          >
            ✕
          </button>
        </div>

        <div className="p-6 flex-1 overflow-y-auto space-y-6">
          {questions.length === 0 ? (
            <div className="space-y-4">
              <div className="text-center py-6">
                <Bot className="text-indigo-400 mx-auto mb-3" size={48} />
                <h4 className="text-lg font-bold text-white">Dynamic Quiz Compiler</h4>
                <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                  Input any academic topic (e.g. "Linear Algebra", "Python Loops", "Organic Chemistry") and let Vidya compile a customized practice assessment.
                </p>
              </div>

              <form onSubmit={startQuizGeneration} className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1.5">Enter Study Topic</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. NEET Biology Photosynthesis, Dynamic Programming"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white outline-none focus:border-indigo-500"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isGenerating}
                  className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 shadow-lg disabled:opacity-50"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="animate-spin" size={14} />
                      Compiling Interactive Questions...
                    </>
                  ) : (
                    <>
                      Generate Custom Practice Quiz
                    </>
                  )}
                </button>
              </form>
            </div>
          ) : completed ? (
            <div className="text-center py-8 space-y-4">
              <Award className="text-amber-400 mx-auto animate-bounce" size={56} />
              <div>
                <h4 className="text-xl font-bold text-white">Practice Set Completed!</h4>
                <p className="text-sm text-indigo-400 mt-1 font-semibold">
                  Result Score: {score} of {questions.length} ({Math.round((score / questions.length) * 100)}%)
                </p>
                <p className="text-xs text-slate-400 mt-2">
                  Excellent focus. Your learning statistics have been routed to the analytics dashboard.
                </p>
              </div>

              <div className="flex gap-3 justify-center pt-2">
                <button
                  type="button"
                  onClick={() => setQuestions([])}
                  className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-semibold transition-all"
                >
                  Try Another Topic
                </button>
                <button
                  type="button"
                  onClick={onClose}
                  className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-all"
                >
                  Finish Practice
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-5">
              {/* Progress Indicator */}
              <div className="flex justify-between items-center text-xs text-slate-400">
                <span>Question {currentIdx + 1} of {questions.length}</span>
                <span>Score: {score} Correct</span>
              </div>

              {/* Question */}
              <div className="p-4 bg-slate-950/40 rounded-xl border border-slate-800/80">
                <h4 className="text-sm font-semibold text-white leading-relaxed">
                  {questions[currentIdx].question}
                </h4>
              </div>

              {/* Options */}
              <div className="space-y-2.5">
                {questions[currentIdx].options.map((opt, idx) => {
                  const isSelected = selectedAns === opt;
                  const isCorrectAnswer = opt === questions[currentIdx].answer;
                  
                  let optionClass = "border-slate-800 hover:border-slate-700 hover:bg-slate-800/20";
                  if (isSelected && !isSubmitted) optionClass = "border-indigo-500 bg-indigo-500/5 text-white";
                  if (isSubmitted) {
                    if (isCorrectAnswer) {
                      optionClass = "border-emerald-500/50 bg-emerald-500/10 text-emerald-400 font-medium";
                    } else if (isSelected) {
                      optionClass = "border-rose-500/50 bg-rose-500/10 text-rose-400";
                    } else {
                      optionClass = "border-slate-800/40 opacity-60";
                    }
                  }

                  return (
                    <button
                      key={idx}
                      disabled={isSubmitted}
                      type="button"
                      onClick={() => setSelectedAns(opt)}
                      className={`w-full text-left p-3.5 border rounded-xl text-xs transition-all flex justify-between items-center ${optionClass}`}
                    >
                      <span>{opt}</span>
                      {isSubmitted && isCorrectAnswer && <CheckCircle size={14} className="text-emerald-400 shrink-0" />}
                      {isSubmitted && isSelected && !isCorrectAnswer && <XCircle size={14} className="text-rose-400 shrink-0" />}
                    </button>
                  );
                })}
              </div>

              {/* Action Button */}
              <div className="pt-2">
                {!isSubmitted ? (
                  <button
                    type="button"
                    onClick={handleSubmitAnswer}
                    disabled={!selectedAns}
                    className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all disabled:opacity-50 disabled:hover:bg-indigo-600"
                  >
                    Submit Answer
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleNext}
                    className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5"
                  >
                    Next Question
                    <ArrowRight size={14} />
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
