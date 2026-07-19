/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { CourseStructure } from '../../types';
import { useLayoutStore } from '../../stores/layoutStore';
import { useThemeStore } from '../../stores/themeStore';
import { Button, LoadingSpinner, Badge, Input, Select } from '../../components/DesignSystem';
import { 
  BookOpen, Video, HelpCircle, Sparkles, CheckCircle, ChevronRight, 
  ArrowLeft, Award, Star, MessageSquare, ShieldAlert, Send, Plus, 
  Trash2, FileText, Download 
} from 'lucide-react';

export const CoursesShell: React.FC = () => {
  const {
    selectedCourse,
    setSelectedCourse,
    activeLesson,
    setActiveLesson,
    activeQuiz,
    setActiveQuiz,
    currentPath,
    navigateTo,
  } = useLayoutStore();

  const { theme } = useThemeStore();
  const [courses, setCourses] = useState<CourseStructure[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Public catalog filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<'ALL' | 'MATH' | 'SaaS' | 'PREP'>('ALL');
  const [selectedPriceType, setSelectedPriceType] = useState<'ALL' | 'FREE' | 'PAID'>('ALL');
  const [isEnrolled, setIsEnrolled] = useState(false);

  // Lesson quiz states
  const [isGenerating, setIsGenerating] = useState(false);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [score, setScore] = useState<number | null>(null);

  // Vidya AI assistant sidebar
  const [isAiOpen, setIsAiOpen] = useState(true);
  const [aiInput, setAiInput] = useState('');
  const [aiLog, setAiLog] = useState([
    { sender: 'ai', text: 'Namaste! I am Vidya AI, your academic tutor. Ask me to explain base bases, formulas, or draft code examples.' }
  ]);
  const [aiLoading, setAiLoading] = useState(false);

  // Course Details Tabs
  const [detailTab, setDetailTab] = useState<'curriculum' | 'instructor' | 'reviews'>('curriculum');

  // Parse route parameters virtual matching: /courses/:id
  const match = currentPath.match(/^\/courses\/([^/]+)/);
  const courseId = match ? match[1] : null;

  useEffect(() => {
    api.courses.list()
      .then(res => {
        if (res.success && res.data) {
          setCourses(res.data);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  // Synchronize route parameter with layout store state to prevent routing loops
  useEffect(() => {
    if (!loading && courses.length > 0) {
      if (courseId) {
        if (!selectedCourse || selectedCourse.id !== courseId) {
          const found = courses.find(c => c.id === courseId);
          if (found) {
            setSelectedCourse(found);
          }
        }
      } else {
        if (selectedCourse) {
          setSelectedCourse(null);
        }
      }
    }
  }, [courseId, courses, loading, selectedCourse, setSelectedCourse]);

  const handleGenerateQuiz = async () => {
    if (!activeLesson) return;
    setIsGenerating(true);
    setScore(null);
    setAnswers({});
    try {
      const res = await api.ai.generateQuiz(activeLesson.title);
      if (res.success && res.data) {
        setActiveQuiz(res.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsGenerating(false);
    }
  };

  const submitQuiz = () => {
    if (!activeQuiz) return;
    let correct = 0;
    activeQuiz.forEach((q, idx) => {
      if (answers[idx] === q.answer) correct++;
    });
    setScore(correct);
  };

  const handleSendAiMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!aiInput.trim()) return;
    const userMsg = aiInput;
    setAiLog(prev => [...prev, { sender: 'user', text: userMsg }]);
    setAiInput('');
    setAiLoading(true);

    setTimeout(() => {
      setAiLog(prev => [
        ...prev, 
        { sender: 'ai', text: `Here is the explanation for your query: "${userMsg}". In Vedic Math, base operations rely on deviations (Vichalana) from powers of 10. Let me know if you would like a step-by-step example.` }
      ]);
      setAiLoading(false);
    }, 1200);
  };

  if (loading) {
    return <LoadingSpinner text="Parsing academic programs..." />;
  }

  // 1. DYNAMIC LESSON WORKSPACE RENDER (If enrolled AND inside study mode)
  if (selectedCourse && isEnrolled && activeLesson) {
    const modulesList = courses.filter(c => c.parentId === selectedCourse.id && c.type === 'PROGRAM');
    return (
      <div className="flex-grow grid grid-cols-1 lg:grid-cols-12 bg-slate-950 min-h-[calc(100vh-200px)]">
        
        {/* Left Lesson Navigator Sidebar */}
        <div className="lg:col-span-3 border-r border-indigo-950/40 bg-[#0b1329]/90 p-4 text-left overflow-y-auto flex flex-col justify-between">
          <div>
            <button
              onClick={() => setIsEnrolled(false)}
              className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 hover:text-indigo-300 mb-6 flex items-center gap-1.5 transition cursor-pointer"
            >
              <ArrowLeft size={13} /> Exit Classroom
            </button>
            
            <span className="text-[9px] uppercase font-bold tracking-widest text-slate-500 block">Course Outline</span>
            <h2 className="text-sm font-extrabold text-white mt-1 mb-6 leading-snug">{selectedCourse.title}</h2>

            <div className="space-y-4">
              {modulesList.map(mod => (
                <div key={mod.id} className="space-y-1">
                  <div className="p-2.5 rounded bg-slate-900 border border-indigo-950">
                    <span className="block text-[8px] uppercase font-bold text-indigo-400 tracking-wider">Module</span>
                    <h4 className="text-xs font-bold text-slate-200 mt-0.5 leading-snug">{mod.title}</h4>
                  </div>
                  <div className="pl-3.5 space-y-1 pt-1">
                    {courses.filter(c => c.parentId === mod.id && c.type === 'MODULE').map(les => (
                      <button
                        key={les.id}
                        onClick={() => setActiveLesson(les)}
                        className={`w-full text-left py-1.5 px-2 rounded-lg transition flex items-center justify-between text-xs cursor-pointer ${activeLesson?.id === les.id ? 'bg-indigo-950/40 text-indigo-350 font-bold border border-indigo-900/30' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/40'}`}
                      >
                        <span className="truncate pr-2 flex items-center gap-1.5">
                          <Video size={12} className="text-indigo-400 shrink-0" />
                          {les.title}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-8 p-4 bg-indigo-950/20 border border-indigo-900/40 rounded-xl space-y-3">
            <span className="text-[8px] font-bold bg-indigo-900/50 border border-indigo-500/20 text-indigo-300 font-mono px-2 py-0.5 rounded uppercase">Accredited Exam</span>
            <p className="text-[10px] text-slate-400 leading-relaxed">Ready to verify study modules? Take the proctored exam to earn secure diplomas.</p>
            <Button size="sm" variant="primary" className="w-full text-[10px] py-2" onClick={() => alert('Verification exam loading...')}>
              <Award size={12} /> Start Exam
            </Button>
          </div>
        </div>

        {/* Center Main Lesson Viewer */}
        <div className={`p-8 text-left space-y-6 overflow-y-auto ${isAiOpen ? 'lg:col-span-6' : 'lg:col-span-9'}`}>
          <div className="flex justify-between items-center">
            <div className="text-[10px] text-slate-500 font-mono">
              Programs &gt; {selectedCourse.title} &gt; {activeLesson.title}
            </div>
            <button 
              onClick={() => setIsAiOpen(!isAiOpen)} 
              className="text-[10px] font-bold text-indigo-400 hover:underline uppercase font-mono cursor-pointer"
            >
              {isAiOpen ? 'Close AI Panel' : 'Open Vidya AI'}
            </button>
          </div>

          <div className="max-w-3xl space-y-6">
            <div>
              <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Lesson study node</span>
              <h1 className="text-2xl font-extrabold text-white tracking-tight mt-0.5 leading-snug">{activeLesson.title}</h1>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">{activeLesson.description}</p>
            </div>

            {/* Video Player or Written article text box */}
            <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4">
              <span className="text-[10px] font-bold text-indigo-400 uppercase font-mono block">Written Lecture notes</span>
              <div className="text-xs text-slate-350 space-y-4 leading-relaxed font-sans">
                <p>In this lesson, we cover factor divisions using baseline methods. Base 10 calculations require identifying deviations from base values.</p>
                <div className="p-3 bg-slate-950 rounded-xl border border-indigo-950/80 font-mono text-indigo-300">
                  Deviation = Number - Base Base
                </div>
                <p>For example, deviation for 12 with base 10 is +2, while for 8 deviation is -2.</p>
              </div>

              {/* Attachments downloads */}
              <div className="pt-4 border-t border-indigo-950/45 flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center gap-1.5"><FileText size={13} /> lecture_deviations.pdf</span>
                <Button size="sm" variant="ghost" className="text-indigo-400 flex items-center gap-1 hover:underline text-[10px]" onClick={() => alert('Downloading attachments...')}>
                  <Download size={11} /> Download PDF
                </Button>
              </div>
            </div>

            {/* AI Practice Quiz compiler */}
            <div className="bg-slate-900 border border-indigo-950 rounded-2xl p-5 shadow-xl relative overflow-hidden">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4 border-b border-indigo-950/45 pb-4">
                <div>
                  <h3 className="text-xs font-extrabold text-white flex items-center gap-1.5 uppercase tracking-wider">
                    <Sparkles className="text-indigo-400 animate-pulse" size={14} />
                    Gemini AI Practice Checkpoint
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">Let Gemini compile a smart quiz instantly using this lesson's technical metrics.</p>
                </div>
                <Button onClick={handleGenerateQuiz} isLoading={isGenerating} size="sm" variant="outline" className="shrink-0 text-[10px] py-1.5">
                  Construct AI Quiz
                </Button>
              </div>

              {activeQuiz ? (
                <div className="space-y-4 pt-2">
                  {activeQuiz.map((q, idx) => (
                    <div key={idx} className="space-y-2 text-left">
                      <h4 className="text-xs font-bold text-slate-200">Q{idx + 1}: {q.question}</h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {q.options.map((opt: string) => {
                          const selected = answers[idx] === opt;
                          return (
                            <button
                              key={opt}
                              onClick={() => setAnswers(prev => ({ ...prev, [idx]: opt }))}
                              className={`p-2.5 rounded-xl text-left text-xs transition border cursor-pointer ${selected ? 'bg-indigo-950/40 border-indigo-500 text-indigo-300 font-semibold' : 'bg-slate-950 border-indigo-950/40 hover:bg-slate-850 text-slate-400'}`}
                            >
                              {opt}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}

                  <div className="pt-4 border-t border-indigo-950/45 flex items-center justify-between">
                    <Button onClick={submitQuiz} size="sm">Verify Answers</Button>
                    {score !== null && (
                      <div className="text-xs font-semibold flex items-center gap-1.5">
                        <CheckCircle className="text-emerald-500" size={14} />
                        <span>Score: <strong className="text-emerald-400 font-mono">{score} / {activeQuiz.length}</strong></span>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-4 text-xs text-slate-500 italic">Checkpoint standby. Generate above.</div>
              )}
            </div>
          </div>
        </div>

        {/* Right Vidya AI Assistant Chat Panel */}
        {isAiOpen && (
          <div className="lg:col-span-3 border-l border-indigo-950/40 bg-[#0b1329]/95 flex flex-col justify-between p-4 h-[350px] lg:h-auto">
            <div>
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block border-b border-indigo-950/40 pb-2 mb-3">Vidya AI Assistant</span>
              <div className="space-y-3 overflow-y-auto max-h-[70vh] pr-1 text-xs text-left">
                {aiLog.map((log, idx) => (
                  <div key={idx} className={`p-2.5 rounded-xl ${log.sender === 'ai' ? 'bg-indigo-950/20 text-indigo-300 border border-indigo-900/30' : 'bg-slate-900 text-slate-350'}`}>
                    {log.text}
                  </div>
                ))}
                {aiLoading && <div className="text-[10px] text-slate-500 font-mono animate-pulse">Vidya AI is compiling answers...</div>}
              </div>
            </div>

            <form onSubmit={handleSendAiMessage} className="flex gap-2 border-t border-indigo-950/40 pt-3">
              <input
                type="text"
                required
                placeholder="Ask Vidya AI..."
                value={aiInput}
                onChange={(e) => setAiInput(e.target.value)}
                className="flex-1 bg-slate-900 border border-indigo-950 rounded-xl py-2 px-3 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
              <Button type="submit" size="sm" className="px-3 shrink-0"><Send size={12} /></Button>
            </form>
          </div>
        )}

      </div>
    );
  }

  // 2. PUBLIC COURSE DETAIL PAGE (If selected but NOT inside classrooms study mode)
  if (selectedCourse && !isEnrolled) {
    const modulesList = courses.filter(c => c.parentId === selectedCourse.id && c.type === 'PROGRAM');
    return (
      <div className="flex-1 bg-[#070b19]">
        
        {/* Detail Hero Section */}
        <section className="py-16 px-8 text-left bg-gradient-to-b from-[#0b1329] to-[#070b19] border-b border-indigo-950/40">
          <div className="max-w-6xl mx-auto flex flex-col lg:flex-row justify-between items-start lg:items-center gap-8">
            <div className="space-y-4 max-w-2xl">
              <button 
                onClick={() => setSelectedCourse(null)}
                className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 hover:text-indigo-300 mb-2 flex items-center gap-1.5 transition cursor-pointer"
              >
                <ArrowLeft size={13} /> Back to Catalog
              </button>
              <h1 className="text-3xl font-black text-white tracking-tight">{selectedCourse.title}</h1>
              <p className="text-slate-400 text-xs leading-relaxed">{selectedCourse.description || 'Master this program curriculum structured with proctored exams and ledger credentials.'}</p>
              
              <div className="flex flex-wrap gap-4 text-xs font-mono text-slate-500">
                <span className="flex items-center gap-1.5 text-indigo-400"><Star size={13} /> 4.9 Reviews</span>
                <span>•</span>
                <span>Level: {selectedCourse.metadata?.difficulty || 'All Levels'}</span>
              </div>
            </div>

            {/* Buying / Enrollment checklist card */}
            <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl w-full lg:w-80 space-y-4 shadow-2xl">
              <div className="flex justify-between items-baseline">
                <strong className="text-xl font-black text-white font-mono">₹4,999</strong>
                <span className="text-[10px] text-emerald-450 font-bold uppercase">Includes Certifications</span>
              </div>
              <Button onClick={() => setIsEnrolled(true)} className="w-full">
                Enroll In Course
              </Button>
              <Button variant="outline" onClick={() => navigateTo('/bookstore')} className="w-full text-xs py-2.5">
                Purchase eBook Copy
              </Button>
            </div>
          </div>
        </section>

        {/* Tabs and detailed outline cards */}
        <section className="py-12 px-8 max-w-4xl mx-auto text-left space-y-8">
          <div className="flex border-b border-indigo-950/40 gap-6 text-xs font-semibold select-none">
            <button onClick={() => setDetailTab('curriculum')} className={`py-3 relative cursor-pointer ${detailTab === 'curriculum' ? 'text-indigo-400 font-extrabold' : 'text-slate-500'}`}>Syllabus Outlines</button>
            <button onClick={() => setDetailTab('instructor')} className={`py-3 relative cursor-pointer ${detailTab === 'instructor' ? 'text-indigo-400 font-extrabold' : 'text-slate-500'}`}>Teachers Profile</button>
          </div>

          {detailTab === 'curriculum' && (
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Curriculum Outline</h3>
              {modulesList.map(mod => (
                <div key={mod.id} className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl space-y-3">
                  <h4 className="text-xs font-bold text-white leading-snug">{mod.title}</h4>
                  <ul className="pl-4 space-y-2 text-xs text-slate-400">
                    {courses.filter(c => c.parentId === mod.id && c.type === 'MODULE').map(les => (
                      <li key={les.id} className="flex items-center gap-2">
                        <Video size={12} className="text-indigo-400" />
                        {les.title}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}

          {detailTab === 'instructor' && (
            <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl flex items-center gap-4">
              <div className="h-14 w-14 rounded-full bg-indigo-950 text-indigo-400 font-black text-lg flex items-center justify-center border border-indigo-900/60 shrink-0 select-none">
                VS
              </div>
              <div className="text-xs">
                <strong className="block text-sm text-white">Dr. Vivek Sharma</strong>
                <span className="text-[10px] text-slate-500 font-mono">Senior Academic Vedic Instructor</span>
                <p className="text-slate-400 leading-relaxed mt-2">Specialist in mathematical baseline deviations with years of credential auditing experience.</p>
              </div>
            </div>
          )}
        </section>

      </div>
    );
  }

  // 3. PUBLIC CATALOG LISTING VIEW
  const filteredCourses = courses.filter(c => {
    if (c.parentId || c.type !== 'COURSE') return false;
    if (searchQuery.trim()) {
      const matchQuery = c.title.toLowerCase().includes(searchQuery.toLowerCase());
      if (!matchQuery) return false;
    }
    if (selectedCategory === 'MATH' && !c.title.includes('Vedic')) return false;
    if (selectedCategory === 'SaaS' && !c.title.includes('Performance')) return false;
    return true;
  });

  return (
    <div className="flex-grow flex flex-col bg-[#070b19]">
      
      {/* Search Header Banner */}
      <section className="relative py-16 px-8 text-left border-b border-indigo-950/40">
        <div className="max-w-4xl mx-auto space-y-4">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest font-mono">Education Galaxy</span>
          <h1 className="text-3xl font-black text-white tracking-tight">Structured Programs & Course Catalog</h1>
          <p className="text-slate-400 text-xs max-w-lg leading-relaxed">
            Query across verified written lessons, video programs, and interactive quizzes. Enroll to activate digital ledger credential trackers.
          </p>

          {/* Search boxes filters */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4 max-w-2xl">
            <div className="relative flex-1">
              <input
                type="text"
                placeholder="Search programs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-900 border border-indigo-950 rounded-xl py-3 pl-4 pr-4 text-xs focus:outline-none text-slate-200"
              />
            </div>
            <div className="flex gap-2">
              <Select value={selectedCategory} onChange={(e: any) => setSelectedCategory(e.target.value)}>
                <option value="ALL">All Categories</option>
                <option value="MATH">Vedic Mathematics</option>
                <option value="SaaS">SaaS Performance</option>
              </Select>
            </div>
          </div>
        </div>
      </section>

      {/* Results grid */}
      <section className="py-12 px-8 max-w-5xl mx-auto w-full text-left">
        {filteredCourses.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredCourses.map(course => (
              <button
                key={course.id}
                onClick={() => setSelectedCourse(course)}
                className="p-6 bg-slate-900 hover:bg-slate-850 border border-indigo-950/60 hover:border-indigo-500/50 rounded-2xl transition text-left space-y-4 group cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div className="p-3 bg-indigo-950/50 text-indigo-400 rounded-xl">
                    <BookOpen size={20} />
                  </div>
                  <ChevronRight className="text-slate-650 group-hover:text-indigo-450 transition" size={16} />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white group-hover:text-indigo-300 transition">{course.title}</h4>
                  <p className="text-xs text-slate-400 leading-relaxed mt-1.5 line-clamp-2">{course.description || 'Complete syllabus guidelines covering modular lessons.'}</p>
                </div>
                <div className="pt-2 flex items-center gap-4 text-[9px] text-slate-500 font-mono border-t border-indigo-950/40">
                  <span>DURATION: {course.metadata?.duration || '15 Hours'}</span>
                  <span>LEVEL: {course.metadata?.difficulty || 'Intermediate'}</span>
                </div>
              </button>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-slate-500 font-mono text-xs italic">No matching academic courses indexed.</div>
        )}
      </section>

    </div>
  );
};

export default CoursesShell;
