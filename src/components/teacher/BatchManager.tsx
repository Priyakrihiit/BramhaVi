/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Layers, Plus, Users, Calendar, Trash2 } from 'lucide-react';
import { Button, Input, Badge } from '../DesignSystem';

interface StudentBatch {
  id: string;
  name: string;
  courseTitle: string;
  startDate: string;
  studentCount: number;
  maxCapacity: number;
  status: 'ACTIVE' | 'UPCOMING' | 'COMPLETED';
}

export const BatchManager: React.FC = () => {
  const [batches, setBatches] = useState<StudentBatch[]>([
    { id: 'b-1', name: 'Quantum Core Group Alpha', courseTitle: 'Quantum Consciousness Mechanics', startDate: '2026-06-01', studentCount: 14, maxCapacity: 20, status: 'ACTIVE' },
    { id: 'b-2', name: 'Sanskrit Grammar Node Beta', courseTitle: 'Vedic Computational Syntax', startDate: '2026-07-20', studentCount: 8, maxCapacity: 15, status: 'UPCOMING' }
  ]);

  // Form states
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [name, setName] = useState('');
  const [courseTitle, setCourseTitle] = useState('Quantum Consciousness Mechanics');
  const [startDate, setStartDate] = useState('2026-07-25');
  const [maxCapacity, setMaxCapacity] = useState('20');
  const [status, setStatus] = useState<'ACTIVE' | 'UPCOMING'>('ACTIVE');

  const handleCreateBatch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    const newBatch: StudentBatch = {
      id: `b-${Date.now()}`,
      name,
      courseTitle,
      startDate,
      studentCount: 0,
      maxCapacity: Number(maxCapacity),
      status: status
    };

    setBatches(prev => [newBatch, ...prev]);
    setIsFormOpen(false);
    
    // reset form
    setName('');
  };

  const handleDelete = (id: string) => {
    setBatches(prev => prev.filter(b => b.id !== id));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Layers className="text-indigo-400" size={20} />
            Student Batch & Cohort Manager
          </h2>
          <p className="text-xs text-slate-400">Assemble student cohorts, set timeline dates, and monitor group capacities.</p>
        </div>

        <Button onClick={() => setIsFormOpen(true)} size="sm" variant="primary">
          <Plus size={14} /> New Student Batch
        </Button>
      </div>

      {isFormOpen && (
        <form onSubmit={handleCreateBatch} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 animate-fade-in">
          <h3 className="text-sm font-bold text-slate-200">Assemble New Academic Batch</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input label="Batch Name" placeholder="e.g. Batch Charlie" value={name} onChange={e => setName(e.target.value)} required />
            <div>
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Learning Program Link</label>
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input label="Orientation Start Date" type="date" value={startDate} onChange={e => setStartDate(e.target.value)} required />
            <Input label="Max Student Capacity" type="number" value={maxCapacity} onChange={e => setMaxCapacity(e.target.value)} required />
            <div>
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Batch Initial State</label>
              <select
                className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-2.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                value={status}
                onChange={e => setStatus(e.target.value as any)}
              >
                <option value="ACTIVE">ACTIVE</option>
                <option value="UPCOMING">UPCOMING</option>
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-2.5 pt-1 border-t border-slate-850">
            <Button type="button" variant="ghost" size="sm" onClick={() => setIsFormOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary" size="sm">Assemble Cohort</Button>
          </div>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {batches.map(b => (
          <div key={b.id} className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between hover:border-indigo-500/20 transition">
            <div className="space-y-2.5">
              <div className="flex justify-between items-start">
                <h4 className="font-bold text-white text-sm">{b.name}</h4>
                <Badge variant={b.status === 'ACTIVE' ? 'success' : b.status === 'UPCOMING' ? 'warning' : 'outline'}>
                  {b.status}
                </Badge>
              </div>
              <p className="text-xs text-slate-400 line-clamp-1">{b.courseTitle}</p>
            </div>

            <div className="border-t border-slate-800/80 mt-4 pt-3 flex justify-between items-center text-[10px] text-slate-400 font-mono">
              <span className="flex items-center gap-1.5"><Calendar size={13} className="text-slate-500" /> Starts: {b.startDate}</span>
              <span className="flex items-center gap-1.5 font-bold"><Users size={13} className="text-indigo-400" /> Size: {b.studentCount}/{b.maxCapacity}</span>
              
              <button onClick={() => handleDelete(b.id)} className="p-1 rounded bg-rose-950/10 hover:bg-rose-900 text-rose-400 transition">
                <Trash2 size={12} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
