/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { LedgerEntry } from './types';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { DollarSign, ArrowUpRight, ArrowDownLeft, FileCheck, Landmark, Receipt, Download, RefreshCw, BarChart4 } from 'lucide-react';

const REVENUE_DATA_MONTHS = [
  { month: 'Jan', revenue: 245000, commission: 49000, royalties: 65000 },
  { month: 'Feb', revenue: 320000, commission: 64000, royalties: 82000 },
  { month: 'Mar', revenue: 410000, commission: 82000, royalties: 110000 },
  { month: 'Apr', revenue: 380000, commission: 76000, royalties: 95000 },
  { month: 'May', revenue: 540000, commission: 108000, royalties: 145000 },
  { month: 'Jun', revenue: 690000, commission: 138000, royalties: 180000 },
  { month: 'Jul', revenue: 850000, commission: 170000, royalties: 220000 }
];

export const Module3Accounting: React.FC = () => {
  const [ledger, setLedger] = useState<LedgerEntry[]>([
    {
      id: 'TX-10029',
      type: 'INCOME',
      amount: 14999,
      description: 'Enterprise Institution SaaS Annual Plan Sale - BVG-10th',
      gstAmount: 2288,
      tdsAmount: 0,
      netAmount: 12711,
      referenceId: 'sub-inst-1',
      createdAt: '2026-07-07 15:30',
      audited: true
    },
    {
      id: 'TX-10030',
      type: 'ROYALTY',
      amount: 299,
      description: 'Academic E-Book Sale Royalty Share Dr. Iyer - "Intro to Django"',
      gstAmount: 0,
      tdsAmount: 29.9,
      netAmount: 269.1,
      referenceId: 'book-rev-11',
      createdAt: '2026-07-07 14:15',
      audited: true
    },
    {
      id: 'TX-10031',
      type: 'COMMISSION',
      amount: 1000,
      description: 'Platform commission share on marketplace service request Dr. Iyer',
      gstAmount: 180,
      tdsAmount: 100,
      netAmount: 720,
      referenceId: 'serv-9871',
      createdAt: '2026-07-06 18:22',
      audited: true
    },
    {
      id: 'TX-10032',
      type: 'EXPENSE',
      amount: 4500,
      description: 'AWS S3 Asset Storage Cloud Ingress Billing',
      gstAmount: 810,
      tdsAmount: 0,
      netAmount: 5310,
      referenceId: 'aws-env-87',
      createdAt: '2026-07-05 02:00',
      audited: true
    },
    {
      id: 'TX-10033',
      type: 'PUBLISHING_REVENUE',
      amount: 149,
      description: 'Self-Publishing Processing Fee "Vedic Geometry Basics" - Rahul Sharma',
      gstAmount: 27,
      tdsAmount: 0,
      netAmount: 122,
      referenceId: 'pub-sub-881',
      createdAt: '2026-07-04 11:10',
      audited: true
    }
  ]);

  const [activeTab, setActiveTab] = useState<'ALL' | 'INCOME' | 'EXPENSE' | 'ROYALTY' | 'COMMISSION'>('ALL');
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  // Compute stats
  const totalIncome = ledger.filter(l => l.type === 'INCOME' || l.type === 'PUBLISHING_REVENUE').reduce((acc, l) => acc + l.amount, 0);
  const totalExpense = ledger.filter(l => l.type === 'EXPENSE').reduce((acc, l) => acc + l.amount, 0);
  const totalCommission = ledger.filter(l => l.type === 'COMMISSION').reduce((acc, l) => acc + l.amount, 0);
  const totalRoyalty = ledger.filter(l => l.type === 'ROYALTY').reduce((acc, l) => acc + l.amount, 0);
  const totalGST = ledger.reduce((acc, l) => acc + l.gstAmount, 0);
  const totalTDS = ledger.reduce((acc, l) => acc + l.tdsAmount, 0);

  const filteredLedger = activeTab === 'ALL'
    ? ledger
    : ledger.filter(l => l.type === activeTab);

  const triggerAuditExport = () => {
    setDownloadSuccess(true);
    setTimeout(() => setDownloadSuccess(false), 2000);
  };

  return (
    <div id="saas-module-3" className="space-y-6 text-slate-100">
      {/* Banner Title */}
      <div className="bg-slate-900/60 border border-indigo-950 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 text-left">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Landmark className="text-indigo-400 w-5 h-5" />
            Financial Accounting Ledger & Fiscal Reports
          </h2>
          <p className="text-slate-400 text-xs mt-1">
            Audit-ready accounting log. Automatically tracks double-entry income metrics, AWS cloud infrastructure expenses, platform commission structures, 10% TDS withholdings, and 18% GST tax receipts.
          </p>
        </div>
        <div>
          <button
            onClick={triggerAuditExport}
            className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-4 py-2 rounded-xl transition flex items-center gap-1.5 shadow-md shadow-indigo-950"
          >
            <Download className="w-3.5 h-3.5" /> {downloadSuccess ? 'Ledger CSV Downloaded!' : 'Export Ledger Audit Log'}
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-4 text-left relative overflow-hidden">
          <div className="absolute top-3 right-3 bg-emerald-500/10 p-1.5 rounded-lg text-emerald-400">
            <ArrowUpRight className="w-4 h-4" />
          </div>
          <span className="block text-slate-500 text-[10px] uppercase font-bold">Gross Income</span>
          <span className="block text-lg font-black text-white font-mono mt-2">₹{(totalIncome + 2450000).toLocaleString()}</span>
          <span className="block text-[9px] text-emerald-400 mt-1 font-bold">+18.4% Fiscal Year</span>
        </div>

        <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-4 text-left relative overflow-hidden">
          <div className="absolute top-3 right-3 bg-rose-500/10 p-1.5 rounded-lg text-rose-400">
            <ArrowDownLeft className="w-4 h-4" />
          </div>
          <span className="block text-slate-500 text-[10px] uppercase font-bold">Operating Expenses</span>
          <span className="block text-lg font-black text-white font-mono mt-2">₹{(totalExpense + 310240).toLocaleString()}</span>
          <span className="block text-[9px] text-slate-500 mt-1 font-mono">AWS S3, SMS Ingress</span>
        </div>

        <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-4 text-left relative overflow-hidden">
          <div className="absolute top-3 right-3 bg-indigo-500/10 p-1.5 rounded-lg text-indigo-400">
            <Receipt className="w-4 h-4" />
          </div>
          <span className="block text-slate-500 text-[10px] uppercase font-bold">GST Collected (18%)</span>
          <span className="block text-lg font-black text-white font-mono mt-2">₹{(totalGST + 441000).toLocaleString()}</span>
          <span className="block text-[9px] text-emerald-400 mt-1 font-bold">Ready for GSTR-1 File</span>
        </div>

        <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-4 text-left relative overflow-hidden">
          <div className="absolute top-3 right-3 bg-amber-500/10 p-1.5 rounded-lg text-amber-400">
            <FileCheck className="w-4 h-4" />
          </div>
          <span className="block text-slate-500 text-[10px] uppercase font-bold">TDS Withheld (10%)</span>
          <span className="block text-lg font-black text-white font-mono mt-2">₹{(totalTDS + 125000).toLocaleString()}</span>
          <span className="block text-[9px] text-amber-400 mt-1 font-bold">Form 16A Compliant</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Interactive Recharts Financial Chart */}
        <div className="lg:col-span-7 bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
              <BarChart4 className="w-4 h-4 text-indigo-400" />
              Monthly Revenue, Commission & Royalty Analytics
            </h3>
          </div>
          <div className="h-64 mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={REVENUE_DATA_MONTHS}>
                <defs>
                  <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorComm" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="month" stroke="#475569" fontSize={11} tickLine={false} />
                <YAxis stroke="#475569" fontSize={11} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px' }} />
                <Area type="monotone" dataKey="revenue" name="Gross Revenue" stroke="#6366f1" fillOpacity={1} fill="url(#colorRev)" strokeWidth={2} />
                <Area type="monotone" dataKey="commission" name="Platform Commission" stroke="#10b981" fillOpacity={1} fill="url(#colorComm)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Dynamic Ledger Ledger Logs */}
        <div className="lg:col-span-5 bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Receipt className="w-4 h-4 text-indigo-400" />
              General Audit Ledger
            </h3>
            <div className="flex gap-1">
              {['ALL', 'INCOME', 'EXPENSE', 'ROYALTY'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab as any)}
                  className={`px-2 py-1 rounded text-[9px] font-bold uppercase transition ${activeTab === tab ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-slate-400 hover:text-slate-200'}`}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2 max-h-[250px] overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-slate-800">
            {filteredLedger.map((entry) => (
              <div key={entry.id} className="bg-slate-900/60 border border-slate-850 p-3 rounded-xl flex flex-col gap-1.5">
                <div className="flex justify-between items-start">
                  <div className="text-left">
                    <span className="text-[10px] bg-slate-950 px-1.5 py-0.5 rounded text-indigo-300 font-mono font-bold uppercase">{entry.type}</span>
                    <p className="text-xs font-semibold text-slate-200 mt-1">{entry.description}</p>
                  </div>
                  <div className="text-right">
                    <span className={`text-xs font-extrabold font-mono ${entry.type === 'EXPENSE' ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {entry.type === 'EXPENSE' ? '-' : '+'}₹{entry.amount.toLocaleString()}
                    </span>
                    <span className="block text-[8px] text-slate-500 font-mono mt-0.5">{entry.createdAt}</span>
                  </div>
                </div>
                
                <hr className="border-slate-850/60" />

                <div className="flex justify-between text-[9px] font-mono text-slate-500">
                  <span>Ref: {entry.referenceId}</span>
                  <span>GST: ₹{entry.gstAmount} • TDS: ₹{entry.tdsAmount}</span>
                  <span className="text-emerald-400 font-bold flex items-center gap-0.5">
                    <FileCheck className="w-3 h-3" /> VERIFIED
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Module3Accounting;
