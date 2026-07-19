/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { FileText, Download, CheckCircle2, TrendingUp, RefreshCw, Calendar } from 'lucide-react';
import { Button, Badge } from '../DesignSystem';

interface AcademicReport {
  id: string;
  name: string;
  type: 'ENROLLMENT' | 'ATTENDANCE' | 'REVENUE' | 'GRADUATES';
  generatedAt: string;
  fileSize: string;
}

export const TeacherReports: React.FC = () => {
  const [reports, setReports] = useState<AcademicReport[]>([
    { id: 'rep-1', name: 'Quantum Core Group Attendance Sheet', type: 'ATTENDANCE', generatedAt: '2026-07-10 14:00', fileSize: '14 KB' },
    { id: 'rep-2', name: 'June 2026 Revenue & Fee Invoice Statement', type: 'REVENUE', generatedAt: '2026-07-01 00:00', fileSize: '28 KB' },
    { id: 'rep-3', name: 'Syllabus Enrollment Metrics Log', type: 'ENROLLMENT', generatedAt: '2026-06-15 18:22', fileSize: '35 KB' }
  ]);

  const [generatingType, setGeneratingType] = useState<string | null>(null);
  const [generateSuccess, setGenerateSuccess] = useState(false);

  const handleGenerateReport = (type: 'ENROLLMENT' | 'ATTENDANCE' | 'REVENUE' | 'GRADUATES') => {
    setGeneratingType(type);
    setGenerateSuccess(false);

    setTimeout(() => {
      const names = {
        ENROLLMENT: 'Scholar Enrollment Demographic Ledger',
        ATTENDANCE: 'Monthly Attendance Roster Breakdown',
        REVENUE: 'Royalty & BV Galaxy Fee Settlement Invoice',
        GRADUATES: 'Accredited Cryptographic Certificate Signatures Registry'
      };

      const newRep: AcademicReport = {
        id: `rep-${Date.now()}`,
        name: names[type],
        type,
        generatedAt: new Date().toISOString().replace('T', ' ').slice(0, 16),
        fileSize: `${Math.floor(Math.random() * 40) + 10} KB`
      };

      setReports(prev => [newRep, ...prev]);
      setGeneratingType(null);
      setGenerateSuccess(true);
    }, 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <FileText className="text-indigo-400" size={20} />
          Academic Reports Engine
        </h2>
        <p className="text-xs text-slate-400">Generate, compile, and download physical spreadsheet audits for classes and royalties.</p>
      </div>

      {generateSuccess && (
        <div className="p-3 bg-emerald-950/20 border border-emerald-500/25 text-emerald-400 text-xs rounded-xl flex items-center gap-2 select-none animate-fade-in font-sans">
          <CheckCircle2 size={14} /> Report compiled and cached successfully. Download link is ready below.
        </div>
      )}

      {/* Grid of Report compilation cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 select-none">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between space-y-4">
          <div className="space-y-1">
            <span className="text-[9px] text-indigo-400 font-mono uppercase font-black tracking-wider">Demographics</span>
            <h3 className="text-xs font-bold text-white">Enrollment Logs</h3>
            <p className="text-[10px] text-slate-400">Lists students, join dates, and syllabus access levels.</p>
          </div>
          <button
            onClick={() => handleGenerateReport('ENROLLMENT')}
            disabled={generatingType !== null}
            className="w-full py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-[10px] uppercase font-bold tracking-wider transition font-mono flex items-center justify-center gap-1.5"
          >
            {generatingType === 'ENROLLMENT' ? <RefreshCw size={11} className="animate-spin" /> : <RefreshCw size={11} />}
            {generatingType === 'ENROLLMENT' ? 'Compiling...' : 'Generate Spreadsheet'}
          </button>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between space-y-4">
          <div className="space-y-1">
            <span className="text-[9px] text-rose-400 font-mono uppercase font-black tracking-wider">Auditing</span>
            <h3 className="text-xs font-bold text-white">Attendance Sheets</h3>
            <p className="text-[10px] text-slate-400">Presents daily present/absent markers for compliance.</p>
          </div>
          <button
            onClick={() => handleGenerateReport('ATTENDANCE')}
            disabled={generatingType !== null}
            className="w-full py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-[10px] uppercase font-bold tracking-wider transition font-mono flex items-center justify-center gap-1.5"
          >
            {generatingType === 'ATTENDANCE' ? <RefreshCw size={11} className="animate-spin" /> : <RefreshCw size={11} />}
            {generatingType === 'ATTENDANCE' ? 'Compiling...' : 'Generate Spreadsheet'}
          </button>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between space-y-4">
          <div className="space-y-1">
            <span className="text-[9px] text-emerald-400 font-mono uppercase font-black tracking-wider">Financials</span>
            <h3 className="text-xs font-bold text-white">Revenue & Fee Audits</h3>
            <p className="text-[10px] text-slate-400">Details settlement accounts, invoice fee ratios.</p>
          </div>
          <button
            onClick={() => handleGenerateReport('REVENUE')}
            disabled={generatingType !== null}
            className="w-full py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-[10px] uppercase font-bold tracking-wider transition font-mono flex items-center justify-center gap-1.5"
          >
            {generatingType === 'REVENUE' ? <RefreshCw size={11} className="animate-spin" /> : <RefreshCw size={11} />}
            {generatingType === 'REVENUE' ? 'Compiling...' : 'Generate Spreadsheet'}
          </button>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between space-y-4">
          <div className="space-y-1">
            <span className="text-[9px] text-purple-400 font-mono uppercase font-black tracking-wider">Accreditation</span>
            <h3 className="text-xs font-bold text-white">Graduates Ledger</h3>
            <p className="text-[10px] text-slate-400">Includes secure hashes of signed student completions.</p>
          </div>
          <button
            onClick={() => handleGenerateReport('GRADUATES')}
            disabled={generatingType !== null}
            className="w-full py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-[10px] uppercase font-bold tracking-wider transition font-mono flex items-center justify-center gap-1.5"
          >
            {generatingType === 'GRADUATES' ? <RefreshCw size={11} className="animate-spin" /> : <RefreshCw size={11} />}
            {generatingType === 'GRADUATES' ? 'Compiling...' : 'Generate Spreadsheet'}
          </button>
        </div>
      </div>

      {/* Generated Sheets library table */}
      <div className="space-y-3 select-none">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider pl-1">Generated Spreadsheet Library</h3>
        
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
          <table className="w-full text-left text-xs text-slate-350">
            <thead className="bg-slate-950 border-b border-slate-800 text-[10px] uppercase font-bold text-slate-400 font-mono tracking-wider">
              <tr>
                <th className="p-4">Report Description File</th>
                <th className="p-4">Categorization</th>
                <th className="p-4">File Size</th>
                <th className="p-4">Compiled Timestamp</th>
                <th className="p-4 text-right">Download</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850">
              {reports.map(rep => (
                <tr key={rep.id} className="hover:bg-slate-900/30 transition">
                  <td className="p-4 font-bold text-white flex items-center gap-2">
                    <FileText size={14} className="text-indigo-400" />
                    {rep.name}
                  </td>
                  <td className="p-4">
                    <Badge variant={rep.type === 'REVENUE' ? 'success' : rep.type === 'ATTENDANCE' ? 'warning' : 'outline'}>
                      {rep.type}
                    </Badge>
                  </td>
                  <td className="p-4 font-mono">{rep.fileSize}</td>
                  <td className="p-4 font-mono text-slate-400">{rep.generatedAt}</td>
                  <td className="p-4 text-right">
                    <button
                      className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 hover:text-white transition flex items-center gap-1 ml-auto"
                      title="Download spreadsheet"
                    >
                      <Download size={12} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
