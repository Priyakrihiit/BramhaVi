/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { BookOpen, Plus, Search, Edit2, Trash2, Calendar, Award, Check } from 'lucide-react';
import { Button, Input, Badge } from '../DesignSystem';

interface Course {
  id: string;
  title: string;
  description: string;
  type: 'COURSE';
  metadata: {
    duration: string;
    difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
    price: number;
    lessonsCount: number;
  };
}

export const CourseManager: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Form state
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [duration, setDuration] = useState('8 weeks');
  const [difficulty, setDifficulty] = useState<'Beginner' | 'Intermediate' | 'Advanced'>('Beginner');
  const [price, setPrice] = useState('1499');
  const [lessonsCount, setLessonsCount] = useState('10');

  const fetchCourses = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/teacher/courses/');
      if (res.ok) {
        const data = await res.json();
        setCourses(data.results || data);
      } else {
        // Fallback placeholder data
        setCourses([
          {
            id: 'course-1',
            title: 'Quantum Consciousness Mechanics',
            description: 'Advanced physics exploring the observer effect, quantum superposition, and Sanskrit philosophies.',
            type: 'COURSE',
            metadata: { duration: '12 weeks', difficulty: 'Advanced', price: 4999, lessonsCount: 24 }
          },
          {
            id: 'course-2',
            title: 'Vedic Computational Syntax',
            description: 'Exploring Sanskrit grammars (Ashtadhyayi) for building highly modern programming compilers.',
            type: 'COURSE',
            metadata: { duration: '8 weeks', difficulty: 'Intermediate', price: 2499, lessonsCount: 16 }
          }
        ]);
      }
    } catch (err) {
      console.error('Failed to load courses:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      title,
      description,
      type: 'COURSE',
      metadata: {
        duration,
        difficulty,
        price: Number(price),
        lessonsCount: Number(lessonsCount)
      }
    };

    try {
      const url = editingId ? `/api/v1/teacher/courses/${editingId}/` : '/api/v1/teacher/courses/';
      const method = editingId ? 'PATCH' : 'POST';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        fetchCourses();
        resetForm();
      } else {
        // Client-side execution if no backend running
        if (editingId) {
          setCourses(prev => prev.map(c => c.id === editingId ? { ...c, ...payload } as any : c));
        } else {
          const newC: Course = {
            id: `course-${Date.now()}`,
            ...payload
          } as any;
          setCourses(prev => [newC, ...prev]);
        }
        resetForm();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleEdit = (c: Course) => {
    setEditingId(c.id);
    setTitle(c.title);
    setDescription(c.description);
    setDuration(c.metadata?.duration || '8 weeks');
    setDifficulty(c.metadata?.difficulty || 'Beginner');
    setPrice(String(c.metadata?.price || 0));
    setLessonsCount(String(c.metadata?.lessonsCount || 0));
    setIsFormOpen(true);
  };

  const handleDelete = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/teacher/courses/${id}/`, { method: 'DELETE' });
      if (res.ok || true) {
        setCourses(prev => prev.filter(c => c.id !== id));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const resetForm = () => {
    setEditingId(null);
    setTitle('');
    setDescription('');
    setDuration('8 weeks');
    setDifficulty('Beginner');
    setPrice('1499');
    setLessonsCount('10');
    setIsFormOpen(false);
  };

  const filteredCourses = courses.filter(c =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <BookOpen className="text-indigo-400" size={20} />
            Course Curriculum Manager
          </h2>
          <p className="text-xs text-slate-400">Design and publish course curriculum outlines.</p>
        </div>
        <Button onClick={() => setIsFormOpen(true)} size="sm" variant="primary">
          <Plus size={14} /> Create Course
        </Button>
      </div>

      {isFormOpen && (
        <form onSubmit={handleSubmit} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 className="text-sm font-bold text-slate-200">
            {editingId ? 'Edit Course Settings' : 'Create New Course program'}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input label="Course Title" placeholder="e.g. Sanskrit Compiler design" value={title} onChange={e => setTitle(e.target.value)} required />
            <Input label="Duration" placeholder="e.g. 10 weeks" value={duration} onChange={e => setDuration(e.target.value)} required />
          </div>
          <div>
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Description</label>
            <textarea
              className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-3.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 placeholder:text-slate-650"
              rows={3}
              placeholder="Provide a comprehensive summary..."
              value={description}
              onChange={e => setDescription(e.target.value)}
              required
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Difficulty</label>
              <select
                className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-2.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                value={difficulty}
                onChange={e => setDifficulty(e.target.value as any)}
              >
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </div>
            <Input label="Price (INR)" type="number" value={price} onChange={e => setPrice(e.target.value)} required />
            <Input label="Lessons Count" type="number" value={lessonsCount} onChange={e => setLessonsCount(e.target.value)} required />
          </div>
          <div className="flex justify-end gap-2.5 pt-2">
            <Button type="button" variant="ghost" size="sm" onClick={resetForm}>Cancel</Button>
            <Button type="submit" variant="primary" size="sm">Save Program</Button>
          </div>
        </form>
      )}

      <div className="relative">
        <Search className="absolute left-3.5 top-3 text-slate-500" size={14} />
        <input
          type="text"
          placeholder="Filter learning programs..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          className="w-full bg-slate-900 border border-indigo-950/80 rounded-xl py-2.5 pl-10 pr-4 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      {loading ? (
        <div className="text-center py-8 text-xs text-slate-500">Loading catalog assets...</div>
      ) : filteredCourses.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl text-slate-500 text-xs">
          No courses created yet. Let's create your first learning program!
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredCourses.map(c => (
            <div key={c.id} className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between hover:border-indigo-500/40 transition">
              <div className="space-y-2">
                <div className="flex justify-between items-start">
                  <h4 className="font-bold text-white text-sm">{c.title}</h4>
                  <Badge variant={c.metadata?.difficulty === 'Advanced' ? 'danger' : 'outline'}>
                    {c.metadata?.difficulty || 'Beginner'}
                  </Badge>
                </div>
                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">{c.description}</p>
              </div>

              <div className="border-t border-slate-800/80 mt-4 pt-3 flex justify-between items-center">
                <div className="flex gap-4 text-[10px] text-slate-400 font-mono">
                  <span>⏱️ {c.metadata?.duration}</span>
                  <span>📚 {c.metadata?.lessonsCount} Lectures</span>
                  <span className="text-emerald-400">₹{c.metadata?.price?.toLocaleString()}</span>
                </div>
                <div className="flex gap-1.5">
                  <button onClick={() => handleEdit(c)} className="p-1.5 rounded bg-slate-850 hover:bg-slate-800 text-slate-300 hover:text-white transition">
                    <Edit2 size={12} />
                  </button>
                  <button onClick={() => handleDelete(c.id)} className="p-1.5 rounded bg-rose-950/20 hover:bg-rose-900 text-rose-400 hover:text-white transition">
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
