/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { Layers, Plus, Search, Edit2, Trash2, Globe, Bookmark } from 'lucide-react';
import { Button, Input, Badge } from '../DesignSystem';

interface Subject {
  id: string;
  code: string;
  title: string;
  department: string;
  courseId: string;
  courseTitle: string;
  lessonsCount: number;
}

export const SubjectManager: React.FC = () => {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [courses, setCourses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Form state
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [code, setCode] = useState('');
  const [title, setTitle] = useState('');
  const [department, setDepartment] = useState('Computer Science');
  const [courseId, setCourseId] = useState('');

  const fetchInitialData = async () => {
    setLoading(true);
    try {
      // Fetch courses for the dropdown
      const courseRes = await fetch('/api/v1/teacher/courses/');
      let fetchedCourses: any[] = [];
      if (courseRes.ok) {
        fetchedCourses = await courseRes.json();
        setCourses(fetchedCourses);
      } else {
        fetchedCourses = [
          { id: 'course-1', title: 'Quantum Consciousness Mechanics' },
          { id: 'course-2', title: 'Vedic Computational Syntax' }
        ];
        setCourses(fetchedCourses);
      }

      // Fetch subjects
      const subRes = await fetch('/api/v1/teacher/subjects/');
      if (subRes.ok) {
        const data = await subRes.json();
        setSubjects(data.results || data);
      } else {
        setSubjects([
          {
            id: 'sub-1',
            code: 'PHY-401',
            title: 'Quantum Field Realization',
            department: 'Consciousness Physics',
            courseId: 'course-1',
            courseTitle: 'Quantum Consciousness Mechanics',
            lessonsCount: 8
          },
          {
            id: 'sub-2',
            code: 'SAN-302',
            title: 'Sanskrit Compiler Automata',
            department: 'Vedic Linguistics',
            courseId: 'course-2',
            courseTitle: 'Vedic Computational Syntax',
            lessonsCount: 6
          }
        ]);
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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const selectedCourseObj = courses.find(c => c.id === courseId);
    const payload = {
      code,
      title,
      department,
      courseId,
      courseTitle: selectedCourseObj ? selectedCourseObj.title : 'Unassigned Program',
      lessonsCount: 5
    };

    if (editingId) {
      setSubjects(prev => prev.map(s => s.id === editingId ? { ...s, ...payload } : s));
    } else {
      setSubjects(prev => [{ id: `sub-${Date.now()}`, ...payload }, ...prev]);
    }
    resetForm();
  };

  const handleEdit = (s: Subject) => {
    setEditingId(s.id);
    setCode(s.code);
    setTitle(s.title);
    setDepartment(s.department);
    setCourseId(s.courseId);
    setIsFormOpen(true);
  };

  const handleDelete = (id: string) => {
    setSubjects(prev => prev.filter(s => s.id !== id));
  };

  const resetForm = () => {
    setEditingId(null);
    setCode('');
    setTitle('');
    setDepartment('Computer Science');
    setCourseId('');
    setIsFormOpen(false);
  };

  const filteredSubjects = subjects.filter(s =>
    s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.department.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Layers className="text-indigo-400" size={20} />
            Subject Manager
          </h2>
          <p className="text-xs text-slate-400">Classify structural subjects and departments under academic programs.</p>
        </div>
        <Button onClick={() => setIsFormOpen(true)} size="sm" variant="primary">
          <Plus size={14} /> Add Subject
        </Button>
      </div>

      {isFormOpen && (
        <form onSubmit={handleSubmit} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 className="text-sm font-bold text-slate-200">
            {editingId ? 'Edit Subject Node' : 'Add New Subject Category'}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input label="Subject Code" placeholder="e.g. PHY-401" value={code} onChange={e => setCode(e.target.value)} required />
            <Input label="Subject Name" placeholder="e.g. Quantum Observer Dynamics" value={title} onChange={e => setTitle(e.target.value)} required />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Department</label>
              <select
                className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-2.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                value={department}
                onChange={e => setDepartment(e.target.value)}
              >
                <option value="Computer Science">Computer Science</option>
                <option value="Consciousness Physics">Consciousness Physics</option>
                <option value="Vedic Linguistics">Vedic Linguistics</option>
                <option value="Medical Sciences">Medical Sciences</option>
                <option value="Mathematics">Mathematics</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Associate Learning Program</label>
              <select
                className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-2.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                value={courseId}
                onChange={e => setCourseId(e.target.value)}
                required
              >
                <option value="">Select a Program...</option>
                {courses.map(c => (
                  <option key={c.id} value={c.id}>{c.title}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-2.5 pt-2">
            <Button type="button" variant="ghost" size="sm" onClick={resetForm}>Cancel</Button>
            <Button type="submit" variant="primary" size="sm">Register Subject</Button>
          </div>
        </form>
      )}

      <div className="relative">
        <Search className="absolute left-3.5 top-3 text-slate-500" size={14} />
        <input
          type="text"
          placeholder="Filter subject indexes..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          className="w-full bg-slate-900 border border-indigo-950/80 rounded-xl py-2.5 pl-10 pr-4 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      {loading ? (
        <div className="text-center py-8 text-xs text-slate-500">Retrieving academic categories...</div>
      ) : filteredSubjects.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-slate-800 rounded-2xl text-slate-500 text-xs">
          No subjects defined. Assign subjects to link files and syllabus nodes.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {filteredSubjects.map(s => (
            <div key={s.id} className="bg-slate-900/40 border border-slate-850 p-5 rounded-2xl space-y-4 hover:border-indigo-500/20 transition flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-[10px] font-mono text-indigo-400 font-bold tracking-wider">{s.code}</span>
                  <Badge variant="outline">{s.department}</Badge>
                </div>
                <div>
                  <h4 className="font-bold text-white text-sm leading-snug">{s.title}</h4>
                  <div className="flex items-center gap-1.5 mt-2 text-[11px] text-slate-400">
                    <Bookmark size={12} className="text-slate-500" />
                    <span className="truncate">{s.courseTitle}</span>
                  </div>
                </div>
              </div>

              <div className="border-t border-slate-850/80 pt-3 flex justify-between items-center text-[10px] text-slate-500">
                <span>📚 {s.lessonsCount} Modules linked</span>
                <div className="flex gap-1">
                  <button onClick={() => handleEdit(s)} className="p-1.5 rounded bg-slate-850 hover:bg-slate-800 text-slate-300 hover:text-white transition">
                    <Edit2 size={11} />
                  </button>
                  <button onClick={() => handleDelete(s.id)} className="p-1.5 rounded bg-rose-950/20 hover:bg-rose-900 text-rose-400 hover:text-white transition">
                    <Trash2 size={11} />
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
