/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Button, Select } from '../DesignSystem';
import { Send, CheckCircle, RefreshCw, Sparkles, MessageSquare } from 'lucide-react';

export const InterviewPrep: React.FC = () => {
  const [interviewType, setInterviewType] = useState('technical');
  const [started, setStarted] = useState(false);
  const [chatLog, setChatLog] = useState([
    { sender: 'ai', text: 'Namaste! Welcome to your technical mock interview check. Let us review: What are deviations vichalana base offsets in Vedic Mathematics?' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [scoreReport, setScoreReport] = useState<any>(null);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const userMsg = chatInput;
    setChatLog(prev => [...prev, { sender: 'user', text: userMsg }]);
    setChatInput('');
    setLoading(true);

    setTimeout(() => {
      setChatLog(prev => [
        ...prev,
        { sender: 'ai', text: 'Thank you for your answer. Next check: How does Celery coordinate asynchronous tasks within Django?' }
      ]);
      setLoading(false);
    }, 1200);
  };

  const handleFinish = () => {
    setScoreReport({
      score: 85,
      grammar: 'Excellent structural clarity and spelling checks.',
      recommendations: 'Study mental arithmetic dev strategies and baseline deviation calculations further.'
    });
  };

  return (
    <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl text-left space-y-6">
      
      {/* Header bar controls */}
      <div className="flex justify-between items-center border-b border-indigo-950/45 pb-4">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-1.5 uppercase tracking-wider">
            <MessageSquare size={16} className="text-indigo-400" /> AI Mock Interview Prep
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">Practice behavioral, technical coding, and communications mock interviews with AI.</p>
        </div>

        {!started && (
          <div className="flex gap-2">
            <Select value={interviewType} onChange={(e) => setInterviewType(e.target.value)}>
              <option value="hr">HR Behavioral Prep</option>
              <option value="technical">Technical Programming</option>
            </Select>
            <Button size="sm" onClick={() => setStarted(true)}>Start Session</Button>
          </div>
        )}
      </div>

      {started && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Active Chats Board */}
          <div className="lg:col-span-8 flex flex-col h-[350px] bg-slate-950 border border-indigo-950 rounded-xl p-4 justify-between">
            <div className="flex-grow overflow-y-auto space-y-3 pr-1 text-xs">
              {chatLog.map((c, idx) => (
                <div key={idx} className={`p-2.5 rounded-xl ${c.sender === 'ai' ? 'bg-indigo-950/20 text-indigo-300 border border-indigo-900/30' : 'bg-slate-900 text-slate-350'}`}>
                  {c.text}
                </div>
              ))}
              {loading && <div className="text-[10px] text-slate-500 font-mono animate-pulse">AI Interviewer is writing feedback...</div>}
            </div>

            <form onSubmit={handleSendMessage} className="flex gap-2 border-t border-indigo-950/40 pt-3 mt-3">
              <input
                type="text"
                required
                placeholder="Type your response..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                className="flex-1 bg-slate-900 border border-indigo-950 rounded-xl py-2 px-3 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
              <Button type="submit" size="sm" className="px-3 shrink-0"><Send size={12} /></Button>
            </form>
          </div>

          {/* Evaluation Report sidebar */}
          <div className="lg:col-span-4 space-y-4">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block">Session Actions</span>
            <Button className="w-full text-xs py-2.5" onClick={handleFinish}>
              Finish & Evaluate Session
            </Button>

            {scoreReport && (
              <div className="p-5 bg-slate-950 border border-indigo-950 rounded-xl space-y-4 animate-fade-in">
                <div className="flex items-center gap-2 text-emerald-450 border-b border-indigo-950/45 pb-3">
                  <CheckCircle size={15} />
                  <span className="text-xs font-bold font-mono">EVALUATION METRICS</span>
                </div>
                <div className="text-xs space-y-2.5">
                  <div>
                    <span className="block text-[9px] uppercase font-bold text-slate-500 font-mono">Overall Score</span>
                    <strong className="text-sm font-bold text-emerald-400 font-mono">{scoreReport.score}% Match</strong>
                  </div>
                  <div>
                    <span className="block text-[9px] uppercase font-bold text-slate-500 font-mono">Grammar Check</span>
                    <p className="text-slate-400 leading-relaxed mt-0.5">{scoreReport.grammar}</p>
                  </div>
                  <div>
                    <span className="block text-[9px] uppercase font-bold text-slate-500 font-mono">Recommendations</span>
                    <p className="text-slate-400 leading-relaxed mt-0.5">{scoreReport.recommendations}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

        </div>
      )}

    </div>
  );
};

export default InterviewPrep;
