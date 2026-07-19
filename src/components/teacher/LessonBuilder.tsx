/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { Play, Plus, Trash2, ArrowUp, ArrowDown, AlignLeft, Video, BookOpen, Save } from 'lucide-react';
import { Button, Input } from '../DesignSystem';

interface Lesson {
  id: string;
  courseId: string;
  title: string;
  duration: string;
  videoUrl: string;
  content: string; // Markdown / description
  order: number;
}

export const LessonBuilder: React.FC = () => {
  const [courses, setCourses] = useState<any[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState('');
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(false);

  // Form states
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [duration, setDuration] = useState('30 mins');
  const [videoUrl, setVideoUrl] = useState('');
  const [content, setContent] = useState('');

  const fetchInitialData = async () => {
    try {
      const res = await fetch('/api/v1/teacher/courses/');
      if (res.ok) {
        const data = await res.json();
        setCourses(data.results || data);
        if (data.length > 0) {
          setSelectedCourseId(data[0].id);
        }
      } else {
        const mockCourses = [
          { id: 'course-1', title: 'Quantum Consciousness Mechanics' },
          { id: 'course-2', title: 'Vedic Computational Syntax' }
        ];
        setCourses(mockCourses);
        setSelectedCourseId('course-1');
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchLessons = async (courseId: string) => {
    if (!courseId) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/v1/teacher/lessons/?courseId=${courseId}`);
      if (res.ok) {
        const data = await res.json();
        setLessons(data.results || data);
      } else {
        // Fallback mocked lessons
        if (courseId === 'course-1') {
          setLessons([
            { id: 'l-1', courseId: 'course-1', title: 'The Observer Effect & Copenhagen Collapse', duration: '45 mins', videoUrl: 'https://vimeo.com/1234', content: 'In this module, we introduce the foundational observer theories.', order: 1 },
            { id: 'l-2', courseId: 'course-1', title: 'Sanskrit Syllable Resonance & Consciousness physics', duration: '50 mins', videoUrl: 'https://vimeo.com/1235', content: 'Detailed mapping of vibration frequencies to neuron nodes.', order: 2 }
          ]);
        } else {
          setLessons([
            { id: 'l-3', courseId: 'course-2', title: 'Panini’s Ashtadhyayi & Formal Languages', duration: '40 mins', videoUrl: 'https://vimeo.com/1236', content: 'Introduction to context-free grammar derivations.', order: 1 }
          ]);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (selectedCourseId) {
      fetchLessons(selectedCourseId);
    }
  }, [selectedCourseId]);

  const handleAddLesson = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    const newLesson: Lesson = {
      id: `l-${Date.now()}`,
      courseId: selectedCourseId,
      title,
      duration,
      videoUrl,
      content,
      order: lessons.length + 1
    };

    setLessons(prev => [...prev, newLesson]);
    resetForm();
  };

  const handleDelete = (id: string) => {
    setLessons(prev => prev.filter(l => l.id !== id));
  };

  const moveLesson = (index: number, direction: 'up' | 'down') => {
    if (direction === 'up' && index === 0) return;
    if (direction === 'down' && index === lessons.length - 1) return;

    const updated = [...lessons];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    const temp = updated[index];
    updated[index] = updated[targetIndex];
    updated[targetIndex] = temp;

    // Reset order
    const ordered = updated.map((l, i) => ({ ...l, order: i + 1 }));
    setLessons(ordered);
  };

  const resetForm = () => {
    setTitle('');
    setDuration('30 mins');
    setVideoUrl('');
    setContent('');
    setIsFormOpen(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Play className="text-indigo-400" size={20} />
            Interactive Lesson Builder
          </h2>
          <p className="text-xs text-slate-400">Design structural lecture milestones, link online videos, and write rich documentation.</p>
        </div>

        <div className="flex gap-3 items-center">
          <select
            className="bg-slate-900 border border-indigo-950 rounded-xl p-2.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            value={selectedCourseId}
            onChange={e => setSelectedCourseId(e.target.value)}
          >
            {courses.map(c => (
              <option key={c.id} value={c.id}>{c.title}</option>
            ))}
          </select>

          <Button onClick={() => setIsFormOpen(true)} size="sm" variant="primary">
            <Plus size={14} /> Add Lecture
          </Button>
        </div>
      </div>

      {isFormOpen && (
        <form onSubmit={handleAddLesson} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 className="text-sm font-bold text-slate-200">Register New Lecture Node</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input label="Lecture Title" placeholder="e.g. Double Slit Interference" value={title} onChange={e => setTitle(e.target.value)} required />
            <Input label="Duration" placeholder="e.g. 45 mins" value={duration} onChange={e => setDuration(e.target.value)} required />
            <Input label="Video Streaming URL" placeholder="e.g. https://vimeo.com/..." value={videoUrl} onChange={e => setVideoUrl(e.target.value)} />
          </div>

          <div>
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Lecture Content (Markdown supported)</label>
            <textarea
              className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-3.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 placeholder:text-slate-650"
              rows={4}
              placeholder="Provide lesson instructions, equations, or reading links..."
              value={content}
              onChange={e => setContent(e.target.value)}
            />
          </div>

          <div className="flex justify-end gap-2.5 pt-2">
            <Button type="button" variant="ghost" size="sm" onClick={resetForm}>Cancel</Button>
            <Button type="submit" variant="primary" size="sm">Add Milestone</Button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="text-center py-8 text-xs text-slate-500">Querying lesson milestones...</div>
      ) : lessons.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl text-slate-500 text-xs">
          No lectures added to this course curriculum yet. Select another course or add a lecture.
        </div>
      ) : (
        <div className="space-y-3">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider pl-1 select-none">
            Curriculum Sequence ({lessons.length} Lectures)
          </div>
          {lessons.map((l, index) => (
            <div key={l.id} className="bg-slate-900/45 border border-slate-850 hover:border-indigo-500/20 p-4.5 rounded-2xl flex items-center justify-between gap-4 transition">
              <div className="flex items-center gap-3.5 min-w-0">
                <div className="h-9 w-9 rounded-xl bg-indigo-500/5 border border-indigo-500/10 flex items-center justify-center text-xs text-indigo-400 font-mono font-bold select-none shrink-0">
                  {index + 1}
                </div>
                <div className="min-w-0">
                  <h4 className="font-bold text-white text-sm truncate">{l.title}</h4>
                  <div className="flex items-center gap-3 mt-1.5 text-[10px] text-slate-400 font-mono">
                    <span className="flex items-center gap-1"><AlignLeft size={10} className="text-slate-500" /> {l.duration}</span>
                    {l.videoUrl && <span className="flex items-center gap-1 text-purple-400"><Video size={10} /> Video Ready</span>}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2.5 shrink-0 select-none">
                <div className="flex flex-col gap-1">
                  <button
                    onClick={() => moveLesson(index, 'up')}
                    disabled={index === 0}
                    className="p-1 rounded bg-slate-900 border border-slate-800 text-slate-400 hover:text-white disabled:opacity-30 disabled:pointer-events-none transition"
                  >
                    <ArrowUp size={11} />
                  </button>
                  <button
                    onClick={() => moveLesson(index, 'down')}
                    disabled={index === lessons.length - 1}
                    className="p-1 rounded bg-slate-900 border border-slate-800 text-slate-400 hover:text-white disabled:opacity-30 disabled:pointer-events-none transition"
                  >
                    <ArrowDown size={11} />
                  </button>
                </div>
                <button
                  onClick={() => handleDelete(l.id)}
                  className="p-2.5 rounded-xl bg-rose-950/20 hover:bg-rose-900 border border-rose-950/10 text-rose-400 hover:text-white transition"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
