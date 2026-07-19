/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  DollarSign,
  Briefcase,
  Users,
  Percent,
  BookOpen,
  ArrowUpRight,
  TrendingUp,
  FileSpreadsheet,
  CheckCircle,
  Clock,
  ShieldCheck,
  Download
} from 'lucide-react';

interface SettlementRecord {
  id: string;
  payeeName: string;
  role: 'TEACHER' | 'AUTHOR' | 'AFFILIATE' | 'ORGANIZATION';
  grossSales: number;
  royaltyRate: number;
  payoutAmount: number;
  gstDeduction: number;
  tdsDeduction: number;
  netSettled: number;
  status: 'SETTLED' | 'PENDING' | 'HELD';
}

export const ProdModule3Settlement: React.FC = () => {
  const [records, setRecords] = useState<SettlementRecord[]>([
    { id: 'SET-9901', payeeName: 'Dr. Ramesh Sharma', role: 'TEACHER', grossSales: 12000, royaltyRate: 70, payoutAmount: 8400, gstDeduction: 1512, tdsDeduction: 840, netSettled: 6048, status: 'PENDING' },
    { id: 'SET-9902', payeeName: 'Prof. Sarah Lin', role: 'TEACHER', grossSales: 24500, royaltyRate: 70, payoutAmount: 17150, gstDeduction: 3087, tdsDeduction: 1715, netSettled: 12348, status: 'PENDING' },
    { id: 'SET-9903', payeeName: 'Arvind Gupta (Publishing)', role: 'AUTHOR', grossSales: 6800, royaltyRate: 50, payoutAmount: 3400, gstDeduction: 612, tdsDeduction: 340, netSettled: 2448, status: 'PENDING' },
    { id: 'SET-9904', payeeName: 'Riya Patel (Academic Pro)', role: 'AFFILIATE', grossSales: 4200, royaltyRate: 15, payoutAmount: 630, gstDeduction: 113, tdsDeduction: 63, netSettled: 454, status: 'PENDING' },
    { id: 'SET-9905', payeeName: 'Mumbai Tech Institute', role: 'ORGANIZATION', grossSales: 54000, royaltyRate: 85, payoutAmount: 45900, gstDeduction: 8262, tdsDeduction: 4590, netSettled: 33048, status: 'SETTLED' }
  ]);

  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const triggerSettlement = () => {
    setRecords(records.map(r => ({ ...r, status: r.status === 'PENDING' ? 'SETTLED' : r.status })));
    showToast('Success: All pending settlement ledgers automatically distributed & recorded in AWS S3.');
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  const totalSales = records.reduce((sum, r) => sum + r.grossSales, 0);
  const totalNet = records.reduce((sum, r) => sum + r.netSettled, 0);
  const totalGST = records.reduce((sum, r) => sum + r.gstDeduction, 0);
  const totalTDS = records.reduce((sum, r) => sum + r.tdsDeduction, 0);

  const exportCSV = () => {
    // Generate simulated CSV and trigger download
    const headers = ['Settlement ID', 'Payee', 'Role', 'Gross Sales', 'Commission %', 'Net Settled', 'Status'];
    const rows = records.map(r => [r.id, r.payeeName, r.role, r.grossSales, r.royaltyRate, r.netSettled, r.status]);
    const content = [headers, ...rows].map(e => e.join(',')).join('\n');
    
    const blob = new Blob([content], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('href', url);
    a.setAttribute('download', `financial-settlements-${new Date().toISOString().split('T')[0]}.csv`);
    a.click();
    showToast('Export Completed: Settlement CSV report downloaded.');
  };

  return (
    <div id="settlement-engine-root" className="space-y-6">
      {/* Financial Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 text-left">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">Total Platform Sales</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-xl font-black text-white mt-1 font-mono">₹{totalSales.toLocaleString('en-IN')}</p>
          <span className="text-[9px] text-slate-500 font-sans mt-1 block">Cumulative gross receipts</span>
        </div>

        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 text-left">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">Net Settled Payouts</span>
            <ArrowUpRight className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-xl font-black text-white mt-1 font-mono">₹{totalNet.toLocaleString('en-IN')}</p>
          <span className="text-[9px] text-slate-500 font-sans mt-1 block">Disbursed to partners</span>
        </div>

        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 text-left">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">GST Deducted (18%)</span>
            <Percent className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-xl font-black text-white mt-1 font-mono">₹{totalGST.toLocaleString('en-IN')}</p>
          <span className="text-[9px] text-slate-500 font-sans mt-1 block">Withheld tax matching</span>
        </div>

        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 text-left">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">TDS Deducted (10%)</span>
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-xl font-black text-white mt-1 font-mono">₹{totalTDS.toLocaleString('en-IN')}</p>
          <span className="text-[9px] text-slate-500 font-sans mt-1 block">Form-16A compliance rules</span>
        </div>
      </div>

      {toastMessage && (
        <div className="bg-indigo-950/50 border border-indigo-900/60 p-3 rounded-lg text-xs text-indigo-300 text-left animate-fadeIn">
          {toastMessage}
        </div>
      )}

      {/* Main Ledger Table */}
      <div className="bg-[#050914] border border-slate-900 rounded-xl p-4 text-left">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-900 mb-4">
          <div>
            <h4 className="text-sm font-black text-white">Monthly Revenue Splits & TDS Ledger</h4>
            <p className="text-[11px] text-slate-500">Validation of double-entry commercial distributions.</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={exportCSV}
              className="bg-slate-950 border border-slate-900 text-xs text-slate-300 hover:text-white hover:bg-slate-900 px-3 py-1.5 rounded-lg transition font-mono flex items-center gap-1.5"
            >
              <FileSpreadsheet className="w-3.5 h-3.5" /> Export Report
            </button>
            <button
              onClick={triggerSettlement}
              className="bg-indigo-600 hover:bg-indigo-500 text-white border border-indigo-500/20 text-xs font-bold font-sans px-3.5 py-1.5 rounded-lg transition flex items-center gap-1.5"
            >
              <CheckCircle className="w-3.5 h-3.5" /> Auto Settled Pending
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-900 text-[10px] text-slate-500 uppercase tracking-wider font-mono">
                <th className="py-2.5">Settlement ID</th>
                <th className="py-2.5">Beneficiary Partner</th>
                <th className="py-2.5">Category</th>
                <th className="py-2.5">Gross Sales</th>
                <th className="py-2.5">Rev Split</th>
                <th className="py-2.5">Tax Withholding</th>
                <th className="py-2.5">Net Payout</th>
                <th className="py-2.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-900/40 text-xs font-mono">
              {records.map((rec) => (
                <tr key={rec.id} className="hover:bg-slate-950/20">
                  <td className="py-3 text-slate-400 font-bold">{rec.id}</td>
                  <td className="py-3 font-sans">
                    <div className="font-bold text-slate-200">{rec.payeeName}</div>
                  </td>
                  <td className="py-3">
                    <span className="text-[9px] bg-slate-900 border border-indigo-950 text-indigo-400 px-2 py-0.5 rounded uppercase">
                      {rec.role}
                    </span>
                  </td>
                  <td className="py-3 text-slate-300">₹{rec.grossSales.toLocaleString('en-IN')}</td>
                  <td className="py-3 text-slate-400">{rec.royaltyRate}%</td>
                  <td className="py-3 text-[10px] text-slate-500 leading-tight">
                    <div>GST: ₹{rec.gstDeduction}</div>
                    <div>TDS: ₹{rec.tdsDeduction}</div>
                  </td>
                  <td className="py-3 text-emerald-400 font-bold">₹{rec.netSettled.toLocaleString('en-IN')}</td>
                  <td className="py-3">
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border uppercase ${
                      rec.status === 'SETTLED'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-950'
                        : 'bg-amber-500/10 text-amber-400 border-amber-950'
                    }`}>
                      {rec.status}
                    </span>
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

export default ProdModule3Settlement;
