import React, { useState, useEffect } from 'react';
import {
  Sparkles, MessageSquare, BookOpen, FileText, CheckSquare, Layers,
  Compass, Award, Cpu, Brain, ChevronRight, Play, CheckCircle2,
  AlertTriangle, RefreshCw, Send, Trash2, HelpCircle, Plus, BookMarked,
  Code, Briefcase, Bookmark, Settings
} from 'lucide-react';
import { Badge, Button, Input, Textarea } from '../DesignSystem';

interface Prompt {
  id: string;
  title: string;
  description: string;
  category: string;
  prompt_text: string;
}

interface Conversation {
  id: string;
  title: string;
  created_at: string;
}

interface Message {
  id: string;
  sender_role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

interface Flashcard {
  id: string;
  front: string;
  back: string;
  hint: string;
}

interface FlashcardDeck {
  id: string;
  title: string;
  topic: string;
  card_count: number;
  cards?: Flashcard[];
}

interface QuizQuestion {
  id: string;
  question_number: number;
  question: string;
  options: string[];
  correct_answer: string;
  explanation: string;
}

interface Quiz {
  id: string;
  quiz_title: string;
  topic: string;
  questions: QuizQuestion[];
}

export const StudentAiPortal: React.FC = () => {
  const [activeTab, setActiveTab] = useState<
    'dashboard' | 'chat' | 'notes' | 'quiz' | 'flashcards' | 'roadmap' | 'assignment' | 'prompts'
  >('dashboard');

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Conversations
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConv, setActiveConv] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [agentType, setAgentType] = useState('tutor');

  // Prompts
  const [prompts, setPrompts] = useState<Prompt[]>([]);

  // Features input/outputs
  const [explainInput, setExplainInput] = useState('');
  const [explainOutput, setExplainOutput] = useState('');
  
  const [notesInput, setNotesInput] = useState('');
  const [notesFormat, setNotesFormat] = useState('SUMMARY');
  const [notesOutput, setNotesOutput] = useState('');

  const [roadmapInput, setRoadmapInput] = useState('');
  const [roadmapOutput, setRoadmapOutput] = useState('');

  const [assignmentInput, setAssignmentInput] = useState('');
  const [assignmentDifficulty, setAssignmentDifficulty] = useState('medium');
  const [assignmentOutput, setAssignmentOutput] = useState('');

  // Flashcards state
  const [fcTopic, setFcTopic] = useState('');
  const [fcCount, setFcCount] = useState(5);
  const [decks, setDecks] = useState<FlashcardDeck[]>([]);
  const [activeDeck, setActiveDeck] = useState<FlashcardDeck | null>(null);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showFcAnswer, setShowFcAnswer] = useState(false);

  // Quiz state
  const [quizTopic, setQuizTopic] = useState('');
  const [quizDifficulty, setQuizDifficulty] = useState('medium');
  const [quizCount, setQuizCount] = useState(5);
  const [activeQuiz, setActiveQuiz] = useState<Quiz | null>(null);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [showQuizResults, setShowQuizResults] = useState(false);

  useEffect(() => {
    fetchConversations();
    fetchPrompts();
    fetchDecks();
  }, []);

  const fetchConversations = async () => {
    try {
      const res = await fetch('/api/v1/ai/conversations/');
      if (res.ok) {
        const data = await res.json();
        setConversations(data.results || data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchPrompts = async () => {
    try {
      const res = await fetch('/api/v1/ai/prompts/');
      if (res.ok) {
        const data = await res.json();
        setPrompts(data.results || data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchDecks = async () => {
    try {
      const res = await fetch('/api/v1/ai/flashcards/decks/');
      if (res.ok) {
        const data = await res.json();
        setDecks(data.results || data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const createConversation = async (title = 'New Session') => {
    try {
      const res = await fetch('/api/v1/ai/conversations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
      });
      if (res.ok) {
        const newConv = await res.json();
        setConversations([newConv, ...conversations]);
        selectConversation(newConv);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const selectConversation = async (conv: Conversation) => {
    setActiveConv(conv);
    try {
      const res = await fetch(`/api/v1/ai/conversations/${conv.id}/messages/`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.results || data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const deleteConversation = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/ai/conversations/${id}/`, {
        method: 'DELETE',
      });
      if (res.ok) {
        setConversations(conversations.filter(c => c.id !== id));
        if (activeConv?.id === id) {
          setActiveConv(null);
          setMessages([]);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim() || !activeConv) return;
    const userMsg = { id: Math.random().toString(), sender_role: 'user' as const, content: chatInput, created_at: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    const promptToSend = chatInput;
    setChatInput('');
    setLoading(true);

    try {
      const res = await fetch(`/api/v1/ai/conversations/${activeConv.id}/messages/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: promptToSend, agent_type: agentType }),
      });
      if (res.ok) {
        const data = await res.json();
        // Force refresh conversation message list to sync properly
        selectConversation(activeConv);
      } else {
        const errData = await res.json();
        setErrorMsg(errData.detail || 'Failed to fetch AI reply');
      }
    } catch (err) {
      setErrorMsg('Network error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const handleExplain = async () => {
    if (!explainInput.trim()) return;
    setLoading(true);
    setExplainOutput('');
    try {
      const res = await fetch('/api/v1/ai/features/explain/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: explainInput }),
      });
      if (res.ok) {
        const data = await res.json();
        setExplainOutput(data.explanation);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateNotes = async () => {
    if (!notesInput.trim()) return;
    setLoading(true);
    setNotesOutput('');
    try {
      const res = await fetch('/api/v1/ai/features/notes/generate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: notesInput, format: notesFormat }),
      });
      if (res.ok) {
        const data = await res.json();
        setNotesOutput(data.notes);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateRoadmap = async () => {
    if (!roadmapInput.trim()) return;
    setLoading(true);
    setRoadmapOutput('');
    try {
      const res = await fetch('/api/v1/ai/features/roadmap/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: roadmapInput }),
      });
      if (res.ok) {
        const data = await res.json();
        setRoadmapOutput(data.roadmap);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateAssignment = async () => {
    if (!assignmentInput.trim()) return;
    setLoading(true);
    setAssignmentOutput('');
    try {
      const res = await fetch('/api/v1/ai/features/assignment/generate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: assignmentInput, difficulty: assignmentDifficulty }),
      });
      if (res.ok) {
        const data = await res.json();
        setAssignmentOutput(data.assignment);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateFlashcards = async () => {
    if (!fcTopic.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('/api/v1/ai/flashcards/decks/generate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: fcTopic, card_count: fcCount }),
      });
      if (res.ok) {
        const data = await res.json();
        setDecks([data, ...decks]);
        selectDeck(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectDeck = async (deck: FlashcardDeck) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/v1/ai/flashcards/decks/${deck.id}/`);
      if (res.ok) {
        const data = await res.json();
        setActiveDeck(data);
        setCurrentCardIndex(0);
        setShowFcAnswer(false);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const submitFlashcardReview = async (correct: boolean) => {
    if (!activeDeck || !activeDeck.cards) return;
    const card = activeDeck.cards[currentCardIndex];
    try {
      await fetch(`/api/v1/ai/flashcards/${card.id}/review/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correct }),
      });
    } catch (err) {
      console.error(err);
    }

    if (currentCardIndex < activeDeck.cards.length - 1) {
      setCurrentCardIndex(currentCardIndex + 1);
      setShowFcAnswer(false);
    } else {
      alert('Deck completed!');
      setActiveDeck(null);
      fetchDecks();
    }
  };

  const handleGenerateQuiz = async () => {
    if (!quizTopic.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('/api/v1/ai/quizzes/generate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: quizTopic, difficulty: quizDifficulty, question_count: quizCount }),
      });
      if (res.ok) {
        const data = await res.json();
        setActiveQuiz(data);
        setSelectedAnswers({});
        setShowQuizResults(false);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-950 border border-indigo-950/60 rounded-3xl p-6 text-left space-y-6">
      {/* HEADER SECTION */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-indigo-950/40 pb-5 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="text-indigo-400 animate-pulse" size={20} />
            <h1 className="text-lg font-black text-white">Vidya AI Portal Studio</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">Deploy, generate, and orchestrate educational AI models to accelerate study progress.</p>
        </div>
        <div className="flex flex-wrap gap-1 bg-slate-900 border border-indigo-950/80 p-1 rounded-2xl">
          {['dashboard', 'chat', 'notes', 'quiz', 'flashcards', 'roadmap', 'assignment', 'prompts'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`px-3 py-1.5 rounded-xl text-[10px] font-bold uppercase tracking-wider transition ${activeTab === tab ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-slate-950'}`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* DASHBOARD TAB */}
      {activeTab === 'dashboard' && (
        <div className="space-y-6 animate-fade-in">
          {/* QUICK SUMMARY CARDS */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl flex items-center gap-4">
              <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl"><Brain size={20} /></div>
              <div>
                <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider">AI Tutor</span>
                <span className="text-sm font-black text-white">Active Explainer</span>
              </div>
            </div>
            <div className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl flex items-center gap-4">
              <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-xl"><Layers size={20} /></div>
              <div>
                <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider">Flashcard Decks</span>
                <span className="text-sm font-black text-white">{decks.length} Decks</span>
              </div>
            </div>
            <div className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl flex items-center gap-4">
              <div className="p-3 bg-amber-500/10 text-amber-400 rounded-xl"><CheckSquare size={20} /></div>
              <div>
                <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider">Active Chat Sessions</span>
                <span className="text-sm font-black text-white">{conversations.length} Sessions</span>
              </div>
            </div>
            <div className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl flex items-center gap-4">
              <div className="p-3 bg-rose-500/10 text-rose-400 rounded-xl"><Compass size={20} /></div>
              <div>
                <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider">Knowledge Base</span>
                <span className="text-sm font-black text-white">RAG Grounded</span>
              </div>
            </div>
          </div>

          {/* QUICK ACTIONS PANEL */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* LESSON EXPLAINER */}
            <div className="bg-slate-900 border border-indigo-950 p-5 rounded-2xl space-y-4">
              <div className="flex items-center gap-2 border-b border-indigo-950/40 pb-3">
                <BookOpen size={16} className="text-indigo-400" />
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">AI Lesson Explainer</h3>
              </div>
              <div className="space-y-3">
                <Textarea
                  placeholder="Paste complex textbook paragraphs or academic concepts here..."
                  value={explainInput}
                  onChange={e => setExplainInput(e.target.value)}
                  rows={3}
                />
                <Button variant="primary" className="w-full text-xs font-bold" onClick={handleExplain} disabled={loading}>
                  {loading ? 'Synthesizing Explanation...' : 'Explain in Simple Words'}
                </Button>
                {explainOutput && (
                  <div className="p-4 bg-slate-950 border border-indigo-950 rounded-xl text-slate-300 text-xs font-sans whitespace-pre-wrap leading-relaxed">
                    {explainOutput}
                  </div>
                )}
              </div>
            </div>

            {/* QUICK PRESETS & SERVICES */}
            <div className="bg-slate-900 border border-indigo-950 p-5 rounded-2xl space-y-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 border-b border-indigo-950/40 pb-3 mb-4">
                  <Sparkles size={16} className="text-indigo-400" />
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider">Academic Micro-Tools</h3>
                </div>
                <p className="text-xs text-slate-400">Jump directly into specialized workspace tools to build learning objects.</p>
              </div>
              <div className="grid grid-cols-2 gap-3 mt-4">
                <button onClick={() => setActiveTab('chat')} className="p-3 bg-slate-950 border border-indigo-950 hover:bg-indigo-950/20 hover:border-indigo-900/50 rounded-xl text-left space-y-1 transition text-xs font-bold text-slate-200">
                  <MessageSquare size={16} className="text-indigo-400" />
                  <span>AI Tutor Chat</span>
                </button>
                <button onClick={() => setActiveTab('quiz')} className="p-3 bg-slate-950 border border-indigo-950 hover:bg-indigo-950/20 hover:border-indigo-900/50 rounded-xl text-left space-y-1 transition text-xs font-bold text-slate-200">
                  <CheckSquare size={16} className="text-emerald-400" />
                  <span>Quiz Builder</span>
                </button>
                <button onClick={() => setActiveTab('flashcards')} className="p-3 bg-slate-950 border border-indigo-950 hover:bg-indigo-950/20 hover:border-indigo-900/50 rounded-xl text-left space-y-1 transition text-xs font-bold text-slate-200">
                  <Layers size={16} className="text-amber-400" />
                  <span>Flashcards Spaced</span>
                </button>
                <button onClick={() => setActiveTab('roadmap')} className="p-3 bg-slate-950 border border-indigo-950 hover:bg-indigo-950/20 hover:border-indigo-900/50 rounded-xl text-left space-y-1 transition text-xs font-bold text-slate-200">
                  <Compass size={16} className="text-indigo-400" />
                  <span>Roadmaps</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI CHAT TAB */}
      {activeTab === 'chat' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-fade-in">
          {/* SIDEBAR: CONVERSATION LIST */}
          <div className="lg:col-span-4 bg-slate-900 border border-indigo-950 rounded-2xl p-4 space-y-4 max-h-[500px] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-indigo-950/40 pb-2">
              <span className="text-xs font-bold text-white uppercase tracking-wider">Conversations</span>
              <button onClick={() => createConversation()} className="p-1 bg-indigo-600/10 hover:bg-indigo-600 text-indigo-400 hover:text-white rounded-lg transition">
                <Plus size={14} />
              </button>
            </div>
            <div className="space-y-1.5">
              {conversations.map(conv => (
                <div
                  key={conv.id}
                  className={`flex items-center justify-between p-2.5 rounded-xl transition text-left cursor-pointer border ${activeConv?.id === conv.id ? 'bg-indigo-950/40 border-indigo-900/50 text-white' : 'border-transparent text-slate-400 hover:bg-slate-950 hover:text-slate-200'}`}
                  onClick={() => selectConversation(conv)}
                >
                  <div className="flex items-center gap-2 overflow-hidden">
                    <MessageSquare size={14} className={activeConv?.id === conv.id ? 'text-indigo-400' : 'text-slate-500'} />
                    <span className="text-xs font-bold truncate max-w-[140px]">{conv.title}</span>
                  </div>
                  <button onClick={(e) => { e.stopPropagation(); deleteConversation(conv.id); }} className="p-1 text-slate-500 hover:text-rose-400 rounded transition">
                    <Trash2 size={12} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* CHAT DISPLAY */}
          <div className="lg:col-span-8 bg-slate-900 border border-indigo-950 rounded-2xl p-5 flex flex-col justify-between h-[500px]">
            {activeConv ? (
              <React.Fragment>
                {/* SETTINGS BAR */}
                <div className="flex items-center justify-between border-b border-indigo-950/40 pb-2.5 mb-3 text-xs">
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-white">{activeConv.title}</span>
                    <select
                      className="bg-slate-950 border border-indigo-950/60 rounded px-2 py-0.5 text-[10px] text-slate-350 outline-none font-bold"
                      value={agentType}
                      onChange={e => setAgentType(e.target.value)}
                    >
                      <option value="tutor">🎓 AI Tutor</option>
                      <option value="explainer">💡 Lesson Explainer</option>
                      <option value="code">💻 Coding Assistant</option>
                      <option value="interview">💼 Interview Practice</option>
                    </select>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">ID: {activeConv.id.substring(0, 8)}</span>
                </div>

                {/* MESSAGES */}
                <div className="flex-1 overflow-y-auto space-y-3.5 pr-2 mb-4 scrollbar-thin">
                  {messages.map(msg => (
                    <div key={msg.id} className={`flex ${msg.sender_role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[85%] p-3.5 rounded-2xl text-xs font-sans leading-relaxed ${msg.sender_role === 'user' ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-slate-950 border border-indigo-950/80 text-slate-300 rounded-bl-none'}`}>
                        {msg.content}
                      </div>
                    </div>
                  ))}
                  {loading && (
                    <div className="flex justify-start">
                      <div className="bg-slate-950 border border-indigo-950/80 text-slate-400 p-3.5 rounded-2xl rounded-bl-none text-xs flex items-center gap-2">
                        <RefreshCw className="animate-spin text-indigo-400" size={14} />
                        <span>AI Assistant is writing...</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* CHAT INPUT */}
                <div className="flex gap-2">
                  <Input
                    placeholder="Ask anything or request guidance on topics..."
                    value={chatInput}
                    onChange={e => setChatInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && sendChatMessage()}
                  />
                  <Button variant="primary" onClick={sendChatMessage} disabled={loading}>
                    <Send size={14} />
                  </Button>
                </div>
              </React.Fragment>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
                <MessageSquare className="text-slate-600" size={40} />
                <div className="space-y-1">
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider">No Active Session</h3>
                  <p className="text-[11px] text-slate-400">Select an existing chat session or start a new prompt conversation.</p>
                </div>
                <Button variant="primary" className="text-xs font-bold" onClick={() => createConversation()}>
                  Start New AI Session
                </Button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* AI NOTES TAB */}
      {activeTab === 'notes' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-fade-in">
          <div className="lg:col-span-5 bg-slate-900 border border-indigo-950 p-5 rounded-2xl space-y-4">
            <div className="flex items-center gap-2 border-b border-indigo-950/40 pb-2">
              <FileText size={16} className="text-indigo-400" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">Generate Organized Study Notes</h3>
            </div>
            <div className="space-y-4">
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Format Note Style</span>
                <select
                  value={notesFormat}
                  onChange={e => setNotesFormat(e.target.value)}
                  className="w-full bg-slate-950 border border-indigo-950 rounded-xl p-2.5 text-xs text-white outline-none font-bold"
                >
                  <option value="SUMMARY">Standard Summary Summary</option>
                  <option value="CORNELL">Cornell Study System</option>
                  <option value="OUTLINE">Outline Structured List</option>
                  <option value="MINDMAP">Mindmap Nodes Representation</option>
                  <option value="BULLETS">Bullets Point Takeaways</option>
                </select>
              </div>
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Source Content</span>
                <Textarea
                  placeholder="Paste video transcripts, study logs or textbook contents here..."
                  value={notesInput}
                  onChange={e => setNotesInput(e.target.value)}
                  rows={8}
                />
              </div>
              <Button variant="primary" className="w-full text-xs font-bold" onClick={handleGenerateNotes} disabled={loading}>
                {loading ? 'Formatting Notes...' : 'Compile Notes with AI'}
              </Button>
            </div>
          </div>
          <div className="lg:col-span-7 bg-slate-900 border border-indigo-950 p-5 rounded-2xl flex flex-col">
            <div className="flex items-center justify-between border-b border-indigo-950/40 pb-2 mb-3">
              <span className="text-xs font-bold text-white uppercase tracking-wider">Notes Output ({notesFormat})</span>
            </div>
            <div className="flex-1 p-4 bg-slate-950 border border-indigo-950 rounded-xl text-slate-300 text-xs font-sans whitespace-pre-wrap leading-relaxed min-h-[300px] overflow-y-auto">
              {notesOutput || 'Output notes will appear here.'}
            </div>
          </div>
        </div>
      )}

      {/* AI QUIZ TAB */}
      {activeTab === 'quiz' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-fade-in">
          <div className="lg:col-span-5 bg-slate-900 border border-indigo-950 p-5 rounded-2xl space-y-4">
            <div className="flex items-center gap-2 border-b border-indigo-950/40 pb-2">
              <CheckSquare size={16} className="text-indigo-400" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">Build AI Generated Quizzes</h3>
            </div>
            <div className="space-y-4">
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Topic</span>
                <Input placeholder="Vedic fast division, Python threads..." value={quizTopic} onChange={e => setQuizTopic(e.target.value)} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Difficulty</span>
                  <select value={quizDifficulty} onChange={e => setQuizDifficulty(e.target.value)} className="w-full bg-slate-950 border border-indigo-950 rounded-xl p-2.5 text-xs text-white outline-none font-bold">
                    <option value="easy">Easy Mode</option>
                    <option value="medium">Medium Mode</option>
                    <option value="hard">Hard Mode</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Question Count</span>
                  <Input type="number" min={3} max={20} value={quizCount} onChange={e => setQuizCount(parseInt(e.target.value) || 5)} />
                </div>
              </div>
              <Button variant="primary" className="w-full text-xs font-bold" onClick={handleGenerateQuiz} disabled={loading}>
                {loading ? 'Synthesizing Quiz...' : 'Generate New Quiz'}
              </Button>
            </div>
          </div>

          <div className="lg:col-span-7 bg-slate-900 border border-indigo-950 p-5 rounded-2xl flex flex-col">
            {activeQuiz ? (
              <div className="space-y-5">
                <div className="border-b border-indigo-950/40 pb-3 flex justify-between items-center">
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider">{activeQuiz.quiz_title}</h3>
                  <span className="text-[10px] text-indigo-400 font-bold">{activeQuiz.topic}</span>
                </div>
                <div className="space-y-4 max-h-[350px] overflow-y-auto pr-2 scrollbar-thin">
                  {activeQuiz.questions.map(q => (
                    <div key={q.id} className="space-y-2 border-b border-indigo-950/30 pb-3 last:border-b-0">
                      <p className="text-xs font-bold text-slate-200">{q.question_number}. {q.question}</p>
                      <div className="grid grid-cols-1 gap-2 pl-3">
                        {q.options.map((opt, oIdx) => (
                          <button
                            key={oIdx}
                            onClick={() => {
                              if (!showQuizResults) setSelectedAnswers({ ...selectedAnswers, [q.question_number]: opt });
                            }}
                            className={`p-2 rounded-xl text-xs text-left transition border ${selectedAnswers[q.question_number] === opt ? 'bg-indigo-650 border-indigo-500 text-white font-bold' : 'bg-slate-950 border-indigo-950/60 text-slate-400 hover:text-slate-200'}`}
                          >
                            {opt}
                          </button>
                        ))}
                      </div>
                      {showQuizResults && (
                        <div className="p-3 bg-slate-950 border border-indigo-950 rounded-xl space-y-1 mt-2 text-[10px]">
                          <div className="flex items-center gap-1.5 font-bold">
                            {selectedAnswers[q.question_number] === q.correct_answer ? (
                              <span className="text-emerald-400">✓ Correct</span>
                            ) : (
                              <span className="text-rose-400">✗ Incorrect (Answer: {q.correct_answer})</span>
                            )}
                          </div>
                          <p className="text-slate-400 leading-relaxed font-sans">{q.explanation}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                {!showQuizResults ? (
                  <Button variant="primary" className="w-full text-xs font-bold" onClick={() => setShowQuizResults(true)}>
                    Submit Answers & Show Explanations
                  </Button>
                ) : (
                  <Button variant="secondary" className="w-full text-xs font-bold" onClick={() => setActiveQuiz(null)}>
                    Clear Quiz View
                  </Button>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-4 py-8">
                <CheckSquare className="text-slate-600" size={40} />
                <p className="text-[11px] text-slate-400">Topic quiz has not been generated yet.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* AI FLASHCARDS TAB */}
      {activeTab === 'flashcards' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-fade-in">
          {/* DECK BUILDER / SELECTOR */}
          <div className="lg:col-span-5 bg-slate-900 border border-indigo-950 p-5 rounded-2xl space-y-4">
            <div className="flex items-center gap-2 border-b border-indigo-950/40 pb-2">
              <Layers size={16} className="text-indigo-400" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">Leitner Flashcard Decks</h3>
            </div>
            <div className="space-y-4">
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Generate Deck Topic</span>
                <Input placeholder="Enter study topic..." value={fcTopic} onChange={e => setFcTopic(e.target.value)} />
              </div>
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Card Count</span>
                <Input type="number" min={5} max={50} value={fcCount} onChange={e => setFcCount(parseInt(e.target.value) || 10)} />
              </div>
              <Button variant="primary" className="w-full text-xs font-bold" onClick={handleGenerateFlashcards} disabled={loading}>
                {loading ? 'Synthesizing Deck...' : 'Generate New Deck'}
              </Button>
            </div>

            <div className="border-t border-indigo-950/40 pt-4 space-y-2">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Available Decks</span>
              <div className="space-y-1 max-h-[180px] overflow-y-auto scrollbar-thin">
                {decks.map(d => (
                  <button
                    key={d.id}
                    onClick={() => selectDeck(d)}
                    className="w-full flex items-center justify-between p-2 bg-slate-950 border border-indigo-950/60 rounded-xl hover:border-indigo-900 text-left text-xs transition"
                  >
                    <span className="font-bold text-slate-200 truncate max-w-[200px]">{d.title}</span>
                    <Badge variant="primary" className="text-[9px]">{d.card_count} Cards</Badge>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* ACTIVE FLASHCARD REVIEW */}
          <div className="lg:col-span-7 bg-slate-900 border border-indigo-950 p-5 rounded-2xl flex flex-col justify-between min-h-[300px]">
            {activeDeck && activeDeck.cards && activeDeck.cards.length > 0 ? (
              <React.Fragment>
                <div className="flex justify-between items-center border-b border-indigo-950/40 pb-2">
                  <span className="text-xs font-bold text-white uppercase tracking-wider">{activeDeck.title}</span>
                  <span className="text-[10px] text-indigo-400 font-bold font-mono">Card {currentCardIndex + 1} of {activeDeck.cards.length}</span>
                </div>

                <div
                  className="flex-1 my-6 flex items-center justify-center p-6 bg-slate-950 border border-indigo-950/60 rounded-2xl min-h-[160px] text-center cursor-pointer hover:border-indigo-900 transition"
                  onClick={() => setShowFcAnswer(!showFcAnswer)}
                >
                  <div className="space-y-2">
                    {!showFcAnswer ? (
                      <React.Fragment>
                        <h4 className="text-sm font-bold text-white">{activeDeck.cards[currentCardIndex].front}</h4>
                        <span className="text-[10px] text-indigo-400 font-semibold block animate-pulse">Click card to reveal answer</span>
                      </React.Fragment>
                    ) : (
                      <React.Fragment>
                        <h4 className="text-sm font-bold text-emerald-400">{activeDeck.cards[currentCardIndex].back}</h4>
                        {activeDeck.cards[currentCardIndex].hint && (
                          <p className="text-[10px] text-slate-500 italic">Hint: {activeDeck.cards[currentCardIndex].hint}</p>
                        )}
                      </React.Fragment>
                    )}
                  </div>
                </div>

                {showFcAnswer ? (
                  <div className="grid grid-cols-2 gap-3">
                    <Button variant="danger" className="text-xs font-bold" onClick={() => submitFlashcardReview(false)}>
                      Incorrect (Reset Box 1)
                    </Button>
                    <Button variant="success" className="text-xs font-bold" onClick={() => submitFlashcardReview(true)}>
                      Correct (Advance Box)
                    </Button>
                  </div>
                ) : (
                  <Button variant="secondary" className="w-full text-xs font-bold" onClick={() => setShowFcAnswer(true)}>
                    Reveal Answer
                  </Button>
                )}
              </React.Fragment>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-4 py-8">
                <Layers className="text-slate-600" size={40} />
                <p className="text-[11px] text-slate-400">No active card deck review. Select or generate a deck from the list.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ROADMAPS TAB */}
      {activeTab === 'roadmap' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-fade-in">
          <div className="lg:col-span-5 bg-slate-900 border border-indigo-950 p-5 rounded-2xl space-y-4">
            <div className="flex items-center gap-2 border-b border-indigo-950/40 pb-2">
              <Compass size={16} className="text-indigo-400" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">Generate Academic Roadmaps</h3>
            </div>
            <div className="space-y-4">
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Target Domain Topic</span>
                <Input placeholder="Fullstack React, Corporate Law Basics..." value={roadmapInput} onChange={e => setRoadmapInput(e.target.value)} />
              </div>
              <Button variant="primary" className="w-full text-xs font-bold" onClick={handleGenerateRoadmap} disabled={loading}>
                {loading ? 'Designing Roadmap...' : 'Construct Roadmap'}
              </Button>
            </div>
          </div>
          <div className="lg:col-span-7 bg-slate-900 border border-indigo-950 p-5 rounded-2xl flex flex-col">
            <div className="flex items-center justify-between border-b border-indigo-950/40 pb-2 mb-3">
              <span className="text-xs font-bold text-white uppercase tracking-wider">Roadmap Steps Layout</span>
            </div>
            <div className="flex-1 p-4 bg-slate-950 border border-indigo-950 rounded-xl text-slate-350 text-xs font-sans whitespace-pre-wrap leading-relaxed min-h-[300px] overflow-y-auto">
              {roadmapOutput || 'Generated roadmaps will be displayed here.'}
            </div>
          </div>
        </div>
      )}

      {/* ASSIGNMENT TAB */}
      {activeTab === 'assignment' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-fade-in">
          <div className="lg:col-span-5 bg-slate-900 border border-indigo-950 p-5 rounded-2xl space-y-4">
            <div className="flex items-center gap-2 border-b border-indigo-950/40 pb-2">
              <FileText size={16} className="text-indigo-400" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">Build Assignment Templates</h3>
            </div>
            <div className="space-y-4">
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Assignment Topic</span>
                <Input placeholder="Vedic multiplication, Balance sheets balancing..." value={assignmentInput} onChange={e => setAssignmentInput(e.target.value)} />
              </div>
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Difficulty Target</span>
                <select value={assignmentDifficulty} onChange={e => setAssignmentDifficulty(e.target.value)} className="w-full bg-slate-950 border border-indigo-950 rounded-xl p-2.5 text-xs text-white outline-none font-bold">
                  <option value="easy">Easy Level</option>
                  <option value="medium">Medium Level</option>
                  <option value="hard">Hard Level</option>
                </select>
              </div>
              <Button variant="primary" className="w-full text-xs font-bold" onClick={handleGenerateAssignment} disabled={loading}>
                {loading ? 'Synthesizing Assignment Template...' : 'Design Assignment Rubrics'}
              </Button>
            </div>
          </div>
          <div className="lg:col-span-7 bg-slate-900 border border-indigo-950 p-5 rounded-2xl flex flex-col">
            <div className="flex items-center justify-between border-b border-indigo-950/40 pb-2 mb-3">
              <span className="text-xs font-bold text-white uppercase tracking-wider">Assignment Specsheet</span>
            </div>
            <div className="flex-1 p-4 bg-slate-950 border border-indigo-950 rounded-xl text-slate-350 text-xs font-sans whitespace-pre-wrap leading-relaxed min-h-[300px] overflow-y-auto">
              {assignmentOutput || 'Generated assignment rubrics will be shown here.'}
            </div>
          </div>
        </div>
      )}

      {/* PROMPT LIBRARY TAB */}
      {activeTab === 'prompts' && (
        <div className="space-y-4 animate-fade-in">
          <div className="border-b border-indigo-950/40 pb-2">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">Prompt Templates Library</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {prompts.map(p => (
              <div key={p.id} className="p-4 bg-slate-900 border border-indigo-950 rounded-xl flex flex-col justify-between hover:border-indigo-900 transition">
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <strong className="text-xs font-bold text-white">{p.title}</strong>
                    <Badge variant="primary" className="text-[8px] uppercase tracking-wider">{p.category}</Badge>
                  </div>
                  <p className="text-[10px] text-slate-400 leading-relaxed">{p.description || 'No description provided.'}</p>
                </div>
                <div className="mt-3.5 pt-3 border-t border-indigo-950/40 flex justify-end">
                  <Button
                    variant="secondary"
                    className="text-[9px] font-bold py-1 px-2.5 rounded-lg"
                    onClick={() => {
                      setActiveTab('chat');
                      setChatInput(p.prompt_text);
                    }}
                  >
                    Inject into Chat
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
