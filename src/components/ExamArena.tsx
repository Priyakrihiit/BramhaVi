import React, { useState, useEffect } from 'react';
import { 
  Clock, CheckCircle, AlertTriangle, ArrowLeft, ArrowRight, 
  BookOpen, Award, Check, RefreshCw, Star 
} from 'lucide-react';

interface Question {
  id: string;
  question_text: string;
  question_type: string;
  options: string[];
}

interface Exam {
  id: string;
  title: string;
  passing_score: number;
  duration_minutes: number;
}

interface ExamArenaProps {
  exam: Exam;
  onClose: () => void;
  onFinishAttempt: () => void;
}

export default function ExamArena({ exam, onClose, onFinishAttempt }: ExamArenaProps) {
  const [attempt, setAttempt] = useState<any>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number[]>>({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');

  // 1. Initialize and Start Exam
  useEffect(() => {
    async function startSession() {
      try {
        setIsLoading(true);
        // Hit the proxy start endpoint
        const res = await fetch(`/api/exams/${exam.id}/start/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        if (!res.ok) {
          throw new Error('Could not start exam session. Please try again.');
        }
        const attemptData = await res.json();
        setAttempt(attemptData);

        // Fetch Questions for this course/exam via Question Bank API
        const qRes = await fetch(`/api/lms/question-banks/?course=${exam.id}`, {
          method: 'GET'
        });
        let qData = [];
        if (qRes.ok) {
          const body = await qRes.json();
          qData = body.results || body;
        }

        // If no questions exist, generate some mock questions for demonstration/fallback
        if (!qData || qData.length === 0) {
          qData = [
            {
              id: 'q1',
              question_text: 'Which Upanishadic sutra describes the absolute non-dual witness (Sakshi)?',
              question_type: 'MULTIPLE_CHOICE',
              options: [
                'Tattvamasi (Chandogya Upanishad)',
                'Aham Brahmasmi (Brihadaranyaka Upanishad)',
                'Ayam Atma Brahma (Mandukya Upanishad)',
                'All of the above'
              ]
            },
            {
              id: 'q2',
              question_text: 'In quantum mechanics, what represents the observer wavefunction collapse?',
              question_type: 'MULTIPLE_CHOICE',
              options: [
                'Decoherence into multiple worlds',
                'Transition of possibility amplitudes into localized realities',
                'Superposition state elongation',
                'Schrödinger cat normalization'
              ]
            },
            {
              id: 'q3',
              question_text: 'Correlating Vedantic Prana with physical energy yields which correspondence?',
              question_type: 'MULTIPLE_CHOICE',
              options: [
                'Prana relates directly to thermodynamic entropy vectors',
                'Prana is the substrate of life force ordering physical systems',
                'Prana represents kinetic momentum transformations only',
                'None of the above'
              ]
            }
          ];
        }

        setQuestions(qData);
        setTimeLeft(exam.duration_minutes * 60);
      } catch (err: any) {
        setErrorMessage(err.message || 'Error occurred starting exam.');
      } finally {
        setIsLoading(false);
      }
    }
    startSession();
  }, [exam]);

  // 2. Timer Countdown
  useEffect(() => {
    if (isLoading || submitResult || timeLeft <= 0) return;
    const interval = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(interval);
          autoSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [isLoading, submitResult, timeLeft]);

  // 3. Choice Selection
  const handleSelectOption = (questionId: string, optionIndex: number) => {
    setSelectedAnswers(prev => {
      const current = prev[questionId] || [];
      if (current.includes(optionIndex)) {
        return { ...prev, [questionId]: current.filter(x => x !== optionIndex) };
      } else {
        // Assume single selection for this simplified multiple choice
        return { ...prev, [questionId]: [optionIndex] };
      }
    });
  };

  // 4. Submit Attempt
  const handleSubmit = async () => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    setErrorMessage('');
    try {
      const res = await fetch(`/api/exams/${exam.id}/submit/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: selectedAnswers })
      });
      if (!res.ok) {
        throw new Error('Failed to submit exam attempt.');
      }
      const data = await res.json();
      setSubmitResult(data);
    } catch (err: any) {
      setErrorMessage(err.message || 'Error submitting answers.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const autoSubmit = () => {
    handleSubmit();
  };

  // Helper: Format seconds to MM:SS
  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remaining = secs % 60;
    return `${mins.toString().padStart(2, '0')}:${remaining.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] bg-[#030712] rounded-2xl border border-slate-800 p-8 text-center">
        <RefreshCw className="animate-spin text-indigo-500 mb-4" size={40} />
        <p className="text-sm font-medium text-slate-300">Synchronizing secure session nodes with Django...</p>
      </div>
    );
  }

  if (errorMessage && !attempt) {
    return (
      <div className="bg-[#030712] rounded-2xl border border-red-900/30 p-8 text-center max-w-lg mx-auto">
        <AlertTriangle className="text-red-500 mx-auto mb-4" size={40} />
        <p className="text-sm font-semibold text-white mb-4">{errorMessage}</p>
        <button onClick={onClose} className="px-5 py-2 bg-slate-800 text-white rounded-xl text-xs font-bold hover:bg-slate-700">
          Close Arena
        </button>
      </div>
    );
  }

  // 5. Render Grading Result Screen
  if (submitResult) {
    const passed = submitResult.passed;
    return (
      <div className="bg-[#030712] rounded-2xl border border-slate-800 p-8 max-w-2xl mx-auto shadow-2xl relative overflow-hidden">
        {/* Decorative Background */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="text-center mb-8">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ${passed ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
            {passed ? <Award size={36} /> : <AlertTriangle size={36} />}
          </div>
          <h2 className="text-xl font-black text-white tracking-tight">Exam Evaluation Finalized</h2>
          <p className="text-xs text-slate-400 mt-1">{exam.title}</p>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="bg-[#090d16] border border-slate-800/80 rounded-2xl p-4 text-center">
            <span className="block text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-1">Your Score</span>
            <span className={`text-2xl font-black ${passed ? 'text-emerald-400' : 'text-red-400'}`}>{submitResult.score}%</span>
          </div>
          <div className="bg-[#090d16] border border-slate-800/80 rounded-2xl p-4 text-center">
            <span className="block text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-1">Passing Score</span>
            <span className="text-2xl font-black text-white">{exam.passing_score}%</span>
          </div>
        </div>

        <div className="bg-[#080d1a] border border-slate-800 rounded-xl p-4 mb-8">
          <h4 className="text-xs font-bold text-slate-300 mb-2 flex items-center gap-2">
            <Star size={13} className="text-amber-400" />
            Milestone Rewards & Access
          </h4>
          <ul className="text-xs text-slate-400 space-y-2">
            {passed ? (
              <>
                <li className="flex items-center gap-2 text-emerald-400">
                  <Check size={12} />
                  Dynamic Certificate Generated & Registered on blockchain signature ledger.
                </li>
                <li className="flex items-center gap-2 text-emerald-400">
                  <Check size={12} />
                  Unlocked Badge: <strong>Perfect Sage</strong> or <strong>Exam Conqueror</strong>.
                </li>
              </>
            ) : (
              <li className="flex items-center gap-2 text-rose-400">
                <AlertTriangle size={12} />
                Score is below passing rate. You may prepare and retake the exam again.
              </li>
            )}
            <li className="flex items-center gap-2">
              <Check size={12} className="text-slate-500" />
              Awarded Badge: <strong>Knowledge Seeker</strong>.
            </li>
          </ul>
        </div>

        <div className="flex gap-3 justify-end border-t border-slate-800 pt-6">
          <button 
            onClick={() => {
              onFinishAttempt();
              onClose();
            }}
            className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg"
          >
            Acknowledge & Exit
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  const totalQuestions = questions.length;

  return (
    <div className="bg-[#030712] rounded-2xl border border-slate-800 overflow-hidden shadow-2xl">
      {/* Header bar */}
      <div className="px-6 py-4 bg-[#080c16] border-b border-slate-800 flex items-center justify-between">
        <div>
          <span className="text-[10px] uppercase tracking-wider text-indigo-400 font-bold">Exam Mode</span>
          <h3 className="text-sm font-black text-white">{exam.title}</h3>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-500/10 border border-amber-500/20 text-amber-400 rounded-xl text-xs font-bold">
          <Clock size={14} className="animate-pulse" />
          <span>{formatTime(timeLeft)}</span>
        </div>
      </div>

      {/* Progress tracking */}
      <div className="h-1 bg-slate-900 w-full relative">
        <div 
          className="h-full bg-indigo-500 transition-all duration-300"
          style={{ width: `${((currentQuestionIndex + 1) / totalQuestions) * 100}%` }}
        />
      </div>

      {/* Main body */}
      <div className="p-6 md:p-8">
        {currentQuestion ? (
          <div>
            <div className="mb-6">
              <span className="text-[11px] font-bold text-slate-500 uppercase">Question {currentQuestionIndex + 1} of {totalQuestions}</span>
              <h2 className="text-base font-black text-white mt-1 leading-relaxed">
                {currentQuestion.question_text}
              </h2>
            </div>

            <div className="space-y-3 mb-8">
              {currentQuestion.options.map((option, idx) => {
                const isSelected = (selectedAnswers[currentQuestion.id] || []).includes(idx);
                return (
                  <button
                    key={idx}
                    onClick={() => handleSelectOption(currentQuestion.id, idx)}
                    className={`w-full text-left p-4 rounded-xl border text-xs font-semibold flex items-center justify-between transition-all ${
                      isSelected 
                        ? 'bg-indigo-600/10 border-indigo-500 text-white' 
                        : 'bg-[#080d16] border-slate-850 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <span>{option}</span>
                    <div className={`w-4 h-4 rounded-full border flex items-center justify-center transition-all ${
                      isSelected ? 'border-indigo-500 bg-indigo-600 text-white' : 'border-slate-750'
                    }`}>
                      {isSelected && <Check size={10} />}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="text-center p-8">
            <AlertTriangle className="text-amber-500 mx-auto mb-2" />
            <p className="text-xs text-slate-400">Questions are loading or unavailable.</p>
          </div>
        )}

        {/* Action footer */}
        <div className="flex items-center justify-between border-t border-slate-800/80 pt-6">
          <button
            onClick={() => setCurrentQuestionIndex(prev => Math.max(0, prev - 1))}
            disabled={currentQuestionIndex === 0}
            className="px-4 py-2 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-900 rounded-xl text-xs font-bold flex items-center gap-1.5 disabled:opacity-30 disabled:pointer-events-none transition-all"
          >
            <ArrowLeft size={13} />
            Previous
          </button>

          {currentQuestionIndex < totalQuestions - 1 ? (
            <button
              onClick={() => setCurrentQuestionIndex(prev => prev + 1)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-750 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all"
            >
              Next
              <ArrowRight size={13} />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-black flex items-center gap-1.5 shadow-lg shadow-emerald-900/20 disabled:opacity-40 transition-all"
            >
              {isSubmitting ? <RefreshCw className="animate-spin" size={13} /> : <CheckCircle size={13} />}
              Submit Exam
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
