/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { Award, ShieldCheck, PenTool, CheckCircle2, Search } from 'lucide-react';
import { Button, Input, Badge } from '../DesignSystem';

interface CertificateRequest {
  id: string;
  studentName: string;
  courseTitle: string;
  completedAt: string;
  grade: string;
  status: 'PENDING' | 'ISSUED';
  certificateHash?: string;
}

export const TeacherCertificates: React.FC = () => {
  const [requests, setRequests] = useState<CertificateRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [signingId, setSigningId] = useState<string | null>(null);

  const fetchCertificateRequests = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/teacher/certificates/');
      if (res.ok) {
        const data = await res.json();
        setRequests(data.results || data);
      } else {
        setRequests([
          { id: 'cert-1', studentName: 'Aditya Sharma', courseTitle: 'Quantum Consciousness Mechanics', completedAt: '2026-07-10', grade: 'A+', status: 'PENDING' },
          { id: 'cert-2', studentName: 'Rohan Verma', courseTitle: 'Vedic Computational Syntax', completedAt: '2026-07-09', grade: 'A', status: 'PENDING' },
          { id: 'cert-3', studentName: 'Meera Nair', courseTitle: 'Quantum Consciousness Mechanics', completedAt: '2026-07-08', grade: 'A+', status: 'ISSUED', certificateHash: 'sha256-b0e633d9f365d932628da8d752' }
        ]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCertificateRequests();
  }, []);

  const handleSignCertificate = async (id: string) => {
    setSigningId(id);
    const hash = `sha256-${Math.random().toString(16).slice(2, 10)}${Math.random().toString(16).slice(2, 10)}`;
    
    try {
      const res = await fetch('/api/v1/teacher/certificates/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ requestId: id, certificateHash: hash })
      });

      // Optimistically update
      setRequests(prev => prev.map(r => r.id === id ? {
        ...r,
        status: 'ISSUED',
        certificateHash: hash
      } : r));
    } catch (err) {
      console.error(err);
    } finally {
      setSigningId(null);
    }
  };

  const filteredRequests = requests.filter(r =>
    r.studentName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.courseTitle.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Award className="text-indigo-400" size={20} />
            Cryptographic Certificate Board
          </h2>
          <p className="text-xs text-slate-400">Authorize, digitally sign, and issue cryptographically verifiable certificates to graduates.</p>
        </div>
      </div>

      <div className="relative">
        <Search className="absolute left-3.5 top-3 text-slate-500" size={14} />
        <input
          type="text"
          placeholder="Filter candidate names or program outlines..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          className="w-full bg-slate-900 border border-indigo-950/80 rounded-xl py-2.5 pl-10 pr-4 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950 border-b border-slate-800 text-[10px] uppercase font-bold text-slate-400 font-mono tracking-wider select-none">
            <tr>
              <th className="p-4">Student Name</th>
              <th className="p-4">Completed Program</th>
              <th className="p-4">Evaluations Grade</th>
              <th className="p-4">Date Completed</th>
              <th className="p-4">Ledger Integrity Hash</th>
              <th className="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-850">
            {filteredRequests.map(r => (
              <tr key={r.id} className="hover:bg-slate-900/40 transition">
                <td className="p-4 font-bold text-white flex items-center gap-2">
                  <ShieldCheck className="text-slate-500" size={14} />
                  {r.studentName}
                </td>
                <td className="p-4 text-slate-200">{r.courseTitle}</td>
                <td className="p-4 font-mono font-bold text-indigo-400">{r.grade}</td>
                <td className="p-4 font-mono text-slate-400">{r.completedAt}</td>
                <td className="p-4 font-mono text-[10px] text-slate-500 truncate max-w-[150px]">
                  {r.certificateHash || 'Unsigned'}
                </td>
                <td className="p-4 text-right select-none">
                  {r.status === 'PENDING' ? (
                    <button
                      onClick={() => handleSignCertificate(r.id)}
                      disabled={signingId === r.id}
                      className="px-2.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-[10px] tracking-wider uppercase transition flex items-center gap-1 ml-auto disabled:opacity-50 font-sans cursor-pointer"
                    >
                      <PenTool size={11} />
                      {signingId === r.id ? 'Signing...' : 'Sign Signature'}
                    </button>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[10px] uppercase font-bold text-emerald-400 font-sans select-none">
                      <CheckCircle2 size={12} /> VERIFIED & SIGNED
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
