/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useRef, useEffect } from 'react';
import { LiveClass, LiveClassPoll, WhiteboardStroke } from './types';
import { Video, Monitor, Edit3, Trash2, Send, Vote, Users, HelpCircle, Hand, Sparkles } from 'lucide-react';

export const Module6LiveLearning: React.FC = () => {
  const [classes, setClasses] = useState<LiveClass[]>([
    {
      id: 'live-class-1',
      title: 'Vedic Mathematics - Compounded Division Speedrun',
      teacherId: 'user-teacher',
      teacherName: 'Dr. Ananya Iyer',
      scheduledAt: '2026-07-07 17:00',
      durationMins: 60,
      meetingLink: '#',
      status: 'LIVE'
    },
    {
      id: 'live-class-2',
      title: 'SaaS Microservices Scaling & API Routing',
      teacherId: 'user-teacher',
      teacherName: 'Dr. Ananya Iyer',
      scheduledAt: '2026-07-08 10:30',
      durationMins: 90,
      meetingLink: '#',
      status: 'SCHEDULED'
    }
  ]);

  const [activeClassId, setActiveClassId] = useState<string>('live-class-1');

  // Interactive Poll
  const [poll, setPoll] = useState<LiveClassPoll>({
    id: 'poll-1',
    question: 'Which method reduces Vedic modular division complexity?',
    options: ['Nikhilam Sutra', 'Paravartya Sutra', 'Anurupyena Method', 'Ekadhikena Sutra'],
    votes: [12, 8, 4, 3],
    isActive: true
  });

  const [hasVoted, setHasVoted] = useState(false);

  // Whiteboard drawing engine
  const whiteboardRef = useRef<SVGSVGElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [penColor, setPenColor] = useState('#6366f1');
  const [strokes, setStrokes] = useState<WhiteboardStroke[]>([
    // Prefilled whiteboard mock strokes
    {
      color: '#6366f1',
      points: [
        { x: 50, y: 50 }, { x: 100, y: 120 }, { x: 150, y: 50 }
      ]
    },
    {
      color: '#10b981',
      points: [
        { x: 200, y: 150 }, { x: 250, y: 50 }, { x: 300, y: 150 }
      ]
    }
  ]);
  const [currentStroke, setCurrentStroke] = useState<WhiteboardStroke | null>(null);

  // Chat
  const [liveChats, setLiveChats] = useState([
    { name: 'Rahul Sharma', text: 'Dr. Iyer, how does Nikhilam handle large prime denominators?', time: '17:05' },
    { name: 'Dr. Ananya Iyer', text: 'Excellent question Rahul. I will draw the remainder vector on the whiteboard now.', time: '17:06' }
  ]);
  const [chatInput, setChatInput] = useState('');

  // Raise Hand Queue
  const [handsRaised, setHandsRaised] = useState<string[]>(['Rahul Sharma', 'Priyesh Pandey']);
  const [myHandRaised, setMyHandRaised] = useState(false);

  // Whiteboard Draw Handlers
  const handleMouseDown = (e: React.MouseEvent<SVGSVGElement>) => {
    if (!whiteboardRef.current) return;
    const rect = whiteboardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setIsDrawing(true);
    setCurrentStroke({
      color: penColor,
      points: [{ x, y }]
    });
  };

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    if (!isDrawing || !currentStroke || !whiteboardRef.current) return;
    const rect = whiteboardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setCurrentStroke({
      ...currentStroke,
      points: [...currentStroke.points, { x, y }]
    });
  };

  const handleMouseUp = () => {
    if (isDrawing && currentStroke) {
      setStrokes(prev => [...prev, currentStroke]);
    }
    setIsDrawing(false);
    setCurrentStroke(null);
  };

  const clearWhiteboard = () => {
    setStrokes([]);
    setCurrentStroke(null);
  };

  const submitVote = (idx: number) => {
    if (hasVoted) return;
    setPoll(prev => {
      const updatedVotes = [...prev.votes];
      updatedVotes[idx] += 1;
      return { ...prev, votes: updatedVotes };
    });
    setHasVoted(true);
  };

  const handleSendChat = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    setLiveChats(prev => [...prev, { name: 'You (Student)', text: chatInput, time: '17:10' }]);
    setChatInput('');
  };

  const toggleMyHand = () => {
    if (myHandRaised) {
      setHandsRaised(prev => prev.filter(name => name !== 'You (Student)'));
    } else {
      setHandsRaised(prev => [...prev, 'You (Student)']);
    }
    setMyHandRaised(!myHandRaised);
  };

  const dismissHand = (name: string) => {
    setHandsRaised(prev => prev.filter(n => n !== name));
    if (name === 'You (Student)') setMyHandRaised(false);
  };

  return (
    <div id="saas-module-6" className="space-y-6 text-slate-100">
      {/* Page Header */}
      <div className="bg-slate-900/60 border border-indigo-950 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 text-left">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Video className="text-indigo-400 w-5 h-5" />
            Live Classroom Platform & Interaction Engine
          </h2>
          <p className="text-slate-400 text-xs mt-1">
            WebRTC learning portal. Integrates live stream feeds, interactive drawing whiteboard, instant classroom polls, multi-user chat, and a structured Raise Hand queue.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Area: Whiteboard canvas & classroom video controls */}
        <div className="lg:col-span-8 space-y-6">
          {/* Active whiteboard drawing board */}
          <div className="bg-slate-950/80 border border-slate-900 rounded-2xl overflow-hidden text-left flex flex-col justify-between">
            <div className="bg-slate-900 p-3.5 border-b border-slate-850 flex items-center justify-between">
              <span className="text-xs font-black text-slate-200 flex items-center gap-1.5 uppercase font-mono">
                <Edit3 className="w-4 h-4 text-indigo-400" /> Virtual Classroom Whiteboard
              </span>
              <div className="flex items-center gap-2">
                {/* Pen color selectors */}
                {['#6366f1', '#10b981', '#f43f5e', '#ffffff'].map((color) => (
                  <button
                    key={color}
                    onClick={() => setPenColor(color)}
                    style={{ backgroundColor: color }}
                    className={`w-4 h-4 rounded-full border transition ${penColor === color ? 'border-white scale-125' : 'border-slate-950/40 hover:scale-110'}`}
                  ></button>
                ))}
                <button
                  onClick={clearWhiteboard}
                  className="bg-rose-950/20 text-rose-400 hover:bg-rose-900 border border-rose-900/40 text-[10px] px-2.5 py-1 rounded-lg transition font-mono font-bold ml-2 flex items-center gap-1"
                >
                  <Trash2 className="w-3 h-3" /> Clear Board
                </button>
              </div>
            </div>

            {/* SVG drawing sheet */}
            <div className="relative h-96 bg-slate-950 cursor-crosshair overflow-hidden">
              <svg
                ref={whiteboardRef}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
                className="absolute inset-0 w-full h-full"
              >
                {/* Previous complete strokes */}
                {strokes.map((stroke, index) => {
                  if (stroke.points.length < 2) return null;
                  const pathData = stroke.points.reduce(
                    (acc, p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`),
                    ''
                  );
                  return (
                    <path
                      key={index}
                      d={pathData}
                      fill="none"
                      stroke={stroke.color}
                      strokeWidth={3}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  );
                })}

                {/* Active drawing stroke */}
                {currentStroke && currentStroke.points.length >= 2 && (
                  <path
                    d={currentStroke.points.reduce(
                      (acc, p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`),
                      ''
                    )}
                    fill="none"
                    stroke={currentStroke.color}
                    strokeWidth={3}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                )}
              </svg>
              
              <div className="absolute bottom-4 left-4 bg-slate-900/80 border border-slate-800 text-[10px] text-slate-400 px-2.5 py-1 rounded-lg font-mono">
                ✏️ Click & hold mouse inside black area to draw remainder vectors
              </div>
            </div>
          </div>

          {/* Active student classroom feeds & Screen-share mock toggle */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-4 text-left flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
              </span>
              <div>
                <span className="block text-xs font-bold text-white uppercase tracking-wider">WebRTC Active Call session</span>
                <span className="block text-[10px] text-slate-500 mt-0.5">Encrypted low latency streams: Pune Ingress Nodes</span>
              </div>
            </div>
            
            <div className="flex gap-2">
              <button className="bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs px-3 py-1.5 rounded-lg transition flex items-center gap-1.5 font-semibold">
                <Monitor className="w-3.5 h-3.5 text-indigo-400" /> Share Screen
              </button>
              <button
                onClick={toggleMyHand}
                className={`text-xs px-3.5 py-1.5 rounded-lg transition flex items-center gap-1.5 font-bold ${myHandRaised ? 'bg-indigo-600 text-white hover:bg-indigo-500' : 'bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300'}`}
              >
                <Hand className={`w-3.5 h-3.5 ${myHandRaised ? 'text-white' : 'text-indigo-400'}`} /> {myHandRaised ? 'Hand Raised!' : 'Raise Hand'}
              </button>
            </div>
          </div>
        </div>

        {/* Right sidebars: Polls, live chats, hands-raised queue */}
        <div className="lg:col-span-4 space-y-6">
          {/* Active Poll component */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left space-y-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Vote className="w-4 h-4 text-indigo-400" />
              Interactive Classroom Poll
            </h3>
            
            <div className="space-y-3 font-mono text-xs">
              <p className="font-sans font-bold text-slate-200">{poll.question}</p>
              
              <div className="space-y-2">
                {poll.options.map((opt, i) => {
                  const votesCount = poll.votes[i];
                  const totalVotes = poll.votes.reduce((a, b) => a + b, 0);
                  const pct = totalVotes > 0 ? Math.round((votesCount / totalVotes) * 100) : 0;

                  return (
                    <div key={i} className="flex flex-col gap-1">
                      <button
                        onClick={() => submitVote(i)}
                        disabled={hasVoted}
                        className={`w-full text-left p-2.5 rounded-lg border text-xs transition relative overflow-hidden flex justify-between items-center ${hasVoted ? 'bg-slate-900/40 border-slate-850 cursor-default' : 'hover:bg-slate-900/60 bg-slate-900/20 border-slate-850'}`}
                      >
                        {/* Fill bar */}
                        {hasVoted && (
                          <div
                            style={{ width: `${pct}%` }}
                            className="absolute top-0 left-0 bottom-0 bg-indigo-500/10 transition-all duration-500"
                          ></div>
                        )}
                        <span className="font-sans relative z-10 text-slate-200">{opt}</span>
                        {hasVoted && <span className="font-mono text-indigo-400 font-bold relative z-10">{pct}%</span>}
                      </button>
                    </div>
                  );
                })}
              </div>
              <p className="text-[9px] text-slate-500 font-sans mt-2">
                {hasVoted ? 'Vote registered successfully. Thank you!' : 'Choose one option above to register your vote instantly.'}
              </p>
            </div>
          </div>

          {/* Raise hands queue list */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Hand className="w-4 h-4 text-indigo-400" />
              Raise Hand Queue ({handsRaised.length})
            </h3>
            <div className="space-y-2">
              {handsRaised.map((name, i) => (
                <div key={i} className="bg-slate-900/40 border border-slate-850 p-2.5 rounded-xl flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs text-slate-200">
                    <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-pulse"></span>
                    <strong>{name}</strong>
                  </div>
                  <button
                    onClick={() => dismissHand(name)}
                    className="text-[9px] text-slate-500 hover:text-rose-400 font-mono font-bold"
                  >
                    DISMISS
                  </button>
                </div>
              ))}
              {handsRaised.length === 0 && (
                <span className="text-[10px] text-slate-600 block py-1">Students are quietly listening.</span>
              )}
            </div>
          </div>

          {/* Class Chat Component */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left flex flex-col justify-between h-[230px]">
            <div>
              <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Users className="w-4 h-4 text-indigo-400" />
                Classroom Feed Chat
              </h3>
              
              <div className="space-y-2 max-h-[120px] overflow-y-auto pr-1">
                {liveChats.map((c, idx) => (
                  <div key={idx} className="text-[11px]">
                    <strong className="text-indigo-400">{c.name}:</strong> <span className="text-slate-300">{c.text}</span>
                  </div>
                ))}
              </div>
            </div>

            <form onSubmit={handleSendChat} className="flex gap-1.5 mt-2 pt-2 border-t border-slate-900">
              <input
                type="text"
                required
                placeholder="Ask teacher..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-850 rounded-lg px-2.5 py-1 text-[11px] text-white focus:outline-none focus:border-indigo-500 placeholder-slate-600"
              />
              <button type="submit" className="bg-indigo-600 hover:bg-indigo-500 text-white p-1 rounded-lg transition">
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Module6LiveLearning;
