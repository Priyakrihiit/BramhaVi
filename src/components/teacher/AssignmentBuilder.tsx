/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { FileText, Plus, Search, Calendar, CheckSquare, Award, ExternalLink } from 'lucide-react';
import { Button, Input, Badge } from '../DesignSystem';

interface Assignment {
  id: string;
  title: string;
  courseTitle: string;
  maxPoints: number;
  dueDate: string;
  status: 'ACTIVE' | 'ARCHIVED';
  submissionsCount: number;
}

interface Submission {
  id: string;
  assignmentTitle: string;
  studentName: string;
  submittedAt: string;
  status: 'PENDING' | 'GRADED';
  grade?: string;
  feedback?: string;
}

export const AssignmentBuilder: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'assignments' | 'submissions'>('assignments');
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);

  // Form states
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [courseTitle, setCourseTitle] = useState('Quantum Consciousness Mechanics');
  const [maxPoints, setMaxPoints] = useState('100');
  const [dueDate, setDueDate] = useState('2026-08-01');

  // Grading states
  const [gradingSubmission, setGradingSubmission] = useState<Submission | null>(null);
  const [gradeInput, setGradeInput] = useState('A+');
  const [feedbackInput, setFeedbackInput] = useState('');

  const fetchAssignmentData = async () => {
    setLoading(true);
    try {
      const assRes = await fetch('/api/v1/teacher/assignments/');
      if (assRes.ok) {
        const data = await assRes.json();
        setAssignments(data.results || data);
      } else {
        setAssignments([
          { id: 'ass-1', title: 'Schrödinger Consciousness Equation Derivation', courseTitle: 'Quantum Consciousness Mechanics', maxPoints: 100, dueDate: '2026-07-25', status: 'ACTIVE', submissionsCount: 14 },
          { id: 'ass-2', title: 'Ashtadhyayi Finite Automata Parsing Tree', courseTitle: 'Vedic Computational Syntax', maxPoints: 50, dueDate: '2026-07-30', status: 'ACTIVE', submissionsCount: 8 }
        ]);
      }

      const subRes = await fetch('/api/v1/teacher/submissions/');
      if (subRes.ok) {
        const data = await subRes.json();
        setSubmissions(data.results || data);
      } else {
        setSubmissions([
          { id: 'sub-1', assignmentTitle: 'Schrödinger Consciousness Equation Derivation', studentName: 'Aditya Sharma', submittedAt: '2026-07-12 10:14', status: 'PENDING' },
          { id: 'sub-2', assignmentTitle: 'Ashtadhyayi Finite Automata Parsing Tree', studentName: 'Rohan Verma', submittedAt: '2026-07-11 16:45', status: 'GRADED', grade: 'A', feedback: 'Perfect context-free parser implementation.' }
        ]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssignmentData();
  }, []);

  const handleCreateAssignment = (e: React.FormEvent) => {
    e.preventDefault();
    const newAss: Assignment = {
      id: `ass-${Date.now()}`,
      title,
      courseTitle,
      maxPoints: Number(maxPoints),
      dueDate,
      status: 'ACTIVE',
      submissionsCount: 0
    };

    setAssignments(prev => [newAss, ...prev]);
    setIsFormOpen(false);
    setTitle('');
  };

  const handleGradeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!gradingSubmission) return;

    setSubmissions(prev => prev.map(s => s.id === gradingSubmission.id ? {
      ...s,
      status: 'GRADED',
      grade: gradeInput,
      feedback: feedbackInput
    } : s));

    setGradingSubmission(null);
    setGradeInput('A+');
    setFeedbackInput('');
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="text-indigo-400" size={20} />
            Assignment Builder
          </h2>
          <p className="text-xs text-slate-400">Deploy structural project assignments, evaluate user submissions, and record marks.</p>
        </div>

        <div className="flex border-b border-slate-800 text-xs font-bold gap-4 select-none">
          <button
            onClick={() => setActiveTab('assignments')}
            className={`pb-2.5 transition ${activeTab === 'assignments' ? 'text-indigo-400 border-b-2 border-indigo-500' : 'text-slate-400 hover:text-white'}`}
          >
            Syllabus Tasks
          </button>
          <button
            onClick={() => setActiveTab('submissions')}
            className={`pb-2.5 transition ${activeTab === 'submissions' ? 'text-indigo-400 border-b-2 border-indigo-500' : 'text-slate-400 hover:text-white'}`}
          >
            Submissions Queue
          </button>
        </div>
      </div>

      {activeTab === 'assignments' && (
        <div className="space-y-6">
          <div className="flex justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mt-2">Active Assessments</span>
            <Button onClick={() => setIsFormOpen(true)} size="sm" variant="primary">
              <Plus size={14} /> New Assignment
            </Button>
          </div>

          {isFormOpen && (
            <form onSubmit={handleCreateAssignment} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
              <h3 className="text-sm font-bold text-slate-200">Deploy Custom Task</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input label="Assignment Title" placeholder="e.g. Neuronal Energy calculations" value={title} onChange={e => setTitle(e.target.value)} required />
                <div>
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Program Outline</label>
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
                <Input label="Max Scale Points" type="number" value={maxPoints} onChange={e => setMaxPoints(e.target.value)} required />
                <Input label="Submission Deadline" type="date" value={dueDate} onChange={e => setDueDate(e.target.value)} required />
              </div>
              <div className="flex justify-end gap-2.5 pt-1">
                <Button type="button" variant="ghost" size="sm" onClick={() => setIsFormOpen(false)}>Cancel</Button>
                <Button type="submit" variant="primary" size="sm">Deploy Task</Button>
              </div>
            </form>
          )}

          <div className="grid grid-cols-1 gap-4">
            {assignments.map(ass => (
              <div key={ass.id} className="bg-slate-900/50 border border-slate-850 p-5 rounded-2xl flex flex-col md:flex-row md:items-center md:justify-between gap-4 hover:border-indigo-500/20 transition">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <h4 className="font-bold text-white text-sm">{ass.title}</h4>
                    <Badge variant="outline">{ass.status}</Badge>
                  </div>
                  <span className="text-xs text-slate-400 block">{ass.courseTitle}</span>
                </div>

                <div className="flex flex-wrap items-center gap-6 text-[11px] text-slate-400 font-mono select-none">
                  <span className="flex items-center gap-1.5"><Award size={13} className="text-amber-500" /> Max Score: {ass.maxPoints}</span>
                  <span className="flex items-center gap-1.5"><Calendar size={13} className="text-slate-500" /> Deadline: {ass.dueDate}</span>
                  <span className="flex items-center gap-1.5 text-indigo-400 font-bold"><CheckSquare size={13} /> Submissions: {ass.submissionsCount}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'submissions' && (
        <div className="space-y-4">
          {gradingSubmission && (
            <form onSubmit={handleGradeSubmit} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 animate-fade-in">
              <h3 className="text-sm font-bold text-white">Evaluate Student Submission</h3>
              <div className="p-3 bg-slate-950 rounded-xl border border-indigo-950/40 text-xs space-y-1 select-none">
                <div className="text-slate-400"><span className="font-bold text-slate-300">Student:</span> {gradingSubmission.studentName}</div>
                <div className="text-slate-400"><span className="font-bold text-slate-300">Task:</span> {gradingSubmission.assignmentTitle}</div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="md:col-span-1">
                  <Input label="Assign Grade" value={gradeInput} onChange={e => setGradeInput(e.target.value)} required />
                </div>
                <div className="md:col-span-3">
                  <Input label="Feedback" placeholder="Provide constructive criticism..." value={feedbackInput} onChange={e => setFeedbackInput(e.target.value)} required />
                </div>
              </div>
              <div className="flex justify-end gap-2.5 pt-1">
                <Button type="button" variant="ghost" size="sm" onClick={() => setGradingSubmission(null)}>Cancel</Button>
                <Button type="submit" variant="primary" size="sm">Submit Evaluation</Button>
              </div>
            </form>
          )}

          <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 border-b border-slate-800 text-[10px] uppercase font-bold text-slate-400 font-mono tracking-wider">
                <tr>
                  <th className="p-4">Student</th>
                  <th className="p-4">Task Name</th>
                  <th className="p-4">Handed In At</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Marks/Grade</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {submissions.map(s => (
                  <tr key={s.id} className="hover:bg-slate-900/40 transition">
                    <td className="p-4 font-bold text-white">{s.studentName}</td>
                    <td className="p-4">{s.assignmentTitle}</td>
                    <td className="p-4 text-slate-400 font-mono">{s.submittedAt}</td>
                    <td className="p-4">
                      <Badge variant={s.status === 'PENDING' ? 'warning' : 'success'}>
                        {s.status}
                      </Badge>
                    </td>
                    <td className="p-4 font-mono font-bold text-indigo-400">{s.grade || '—'}</td>
                    <td className="p-4 text-right">
                      {s.status === 'PENDING' ? (
                        <button
                          onClick={() => setGradingSubmission(s)}
                          className="px-2.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-[10px] tracking-wider uppercase transition flex items-center gap-1 ml-auto"
                        >
                          Grade <ExternalLink size={10} />
                        </button>
                      ) : (
                        <span className="text-[10px] text-slate-500 italic">Evaluated</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
