/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Award, ShieldCheck, Search, Loader2, Calendar, Check, ExternalLink, QrCode } from 'lucide-react';
import { Certificate } from '../types';

export default function CertificateVerifier() {
  const [hash, setHash] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [result, setResult] = useState<Certificate | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!hash.trim()) return;

    setIsVerifying(true);
    setResult(null);
    setError(null);

    try {
      const res = await fetch(`/api/certificates/verify/${hash.trim()}`);
      const data = await res.json();
      if (data.success && data.data) {
        setResult(data.data);
      } else {
        setError(data.message || 'Verification failed: Hash is not signed on our digital educational ledger.');
      }
    } catch (err) {
      console.error(err);
      setError('A system communication error occurred during ledger synchronization.');
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6 text-slate-100">
      
      <div className="flex items-start gap-4">
        <div className="p-3 bg-amber-500/10 text-amber-400 rounded-xl">
          <ShieldCheck size={28} />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-1.5">
            Credential Integrity Engine
          </h3>
          <p className="text-xs text-slate-400 mt-1 max-w-lg">
            Verify any digital micro-credential or certificate issued by the BrahmaVidya Galaxy control center. Our ledger hash guarantees authenticity, timestamping, and accreditation standards.
          </p>
        </div>
      </div>

      <form onSubmit={handleVerify} className="flex gap-2.5">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-3 text-slate-400" size={16} />
          <input
            type="text"
            required
            placeholder="Enter unique SHA-256 certificate hash..."
            value={hash}
            onChange={(e) => setHash(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white outline-none focus:border-indigo-500"
          />
        </div>
        <button
          type="submit"
          disabled={isVerifying}
          className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shadow-lg shrink-0 disabled:opacity-50"
        >
          {isVerifying ? (
            <>
              <Loader2 className="animate-spin" size={14} />
              Securing...
            </>
          ) : (
            'Verify Hash'
          )}
        </button>
      </form>

      {/* Verify Result Card */}
      {result && (
        <div className="border border-emerald-500/30 bg-emerald-500/5 rounded-xl p-5 space-y-4 animate-fade-in">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs uppercase tracking-widest">
            <Check size={14} className="p-0.5 bg-emerald-500 text-slate-950 rounded-full" />
            Verification Successful: Active Ledger Record Signed
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2 text-xs border-t border-slate-800">
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Recipient Name</span>
              <span className="font-semibold text-white block mt-0.5">{result.recipientName}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Course Curriculum</span>
              <span className="font-semibold text-white block mt-0.5">{result.courseTitle}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Issued Date</span>
              <span className="font-semibold text-white block mt-0.5">
                {new Date(result.issuedAt).toLocaleDateString()}
              </span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] uppercase">Grade / Code</span>
              <span className="font-semibold text-amber-400 block mt-0.5">
                {result.metadata?.grade || 'A'} ({result.metadata?.accreditationCode || 'BVG-LDR'})
              </span>
            </div>
          </div>

          <div className="pt-2 flex justify-between items-center text-[10px] text-slate-400 border-t border-slate-800">
            <span className="truncate max-w-md">Ledger Hash: <code className="text-indigo-400">{result.certificateHash}</code></span>
            <span className="flex items-center gap-1">
              Secured on Blockchain ledger
              <QrCode size={12} className="text-slate-400" />
            </span>
          </div>
        </div>
      )}

      {error && (
        <div className="border border-red-500/30 bg-red-500/5 rounded-xl p-4 text-xs text-rose-400 animate-fade-in">
          {error}
        </div>
      )}

      {/* Default Verification Helper */}
      {!result && !error && (
        <div className="p-3 bg-slate-950/40 rounded-xl border border-slate-800/80 flex justify-between items-center text-[11px] text-slate-400">
          <span>
            💡 Try this signed mock hash from active ledger: 
            <code className="bg-slate-900 border border-slate-800 px-1.5 py-0.5 text-indigo-400 font-mono ml-1.5">
              ea0f885f8c85350c37bb1a1820b22a013f9f9dcd87239cc841203582ba93d7cb
            </code>
          </span>
          <button
            type="button"
            onClick={() => setHash('ea0f885f8c85350c37bb1a1820b22a013f9f9dcd87239cc841203582ba93d7cb')}
            className="text-indigo-400 hover:text-indigo-300 font-bold ml-2 underline underline-offset-2 shrink-0"
          >
            Load Hash
          </button>
        </div>
      )}
    </div>
  );
}
