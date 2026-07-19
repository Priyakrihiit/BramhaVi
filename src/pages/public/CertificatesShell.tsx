/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { api } from '../../services/api';
import { Certificate } from '../../types';
import { Award, ShieldCheck, CheckCircle, Search } from 'lucide-react';

export const CertificatesShell: React.FC = () => {
  const [hashInput, setHashInput] = useState('');
  const [cert, setCert] = useState<Certificate | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!hashInput.trim()) return;
    setLoading(true);
    setError(null);
    setCert(null);

    try {
      const res = await api.certificates.verify(hashInput);
      if (res.success && res.data) {
        setCert(res.data);
      } else {
        setError(res.message || 'Verification failed. Hash does not match any active database records.');
      }
    } catch (err) {
      setError('Connection failure communicating with ledger registry.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <React.Fragment>
      <div id="bvg-certs-shell" className="flex-grow flex flex-col items-center justify-center p-6 bg-slate-950">
        <div className="max-w-2xl w-full bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl relative overflow-hidden text-left space-y-6">
          <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-amber-500"></div>

          <div className="text-center space-y-2">
            <Award className="mx-auto text-amber-500" size={48} />
            <h2 className="text-xl font-bold tracking-tight text-white">BrahmaVidya Academic Credentials Ticker</h2>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">Verify the integrity of signed educational diplomas using our secure digital ledger.</p>
          </div>

          <form onSubmit={handleVerify} className="space-y-3">
            <label className="block text-[10px] uppercase font-bold text-slate-500 font-mono tracking-wider">Accreditation Hash</label>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Enter 64-character SHA256 ledger certificate hash..."
                value={hashInput}
                onChange={(e) => setHashInput(e.target.value)}
                className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
              />
              <button
                type="submit"
                disabled={loading}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl transition flex items-center gap-1.5 disabled:opacity-50 shrink-0"
              >
                <Search size={14} />
                {loading ? 'Verifying...' : 'Verify Hash'}
              </button>
            </div>
          </form>

          {error && (
            <div className="p-3 bg-red-950/20 border border-red-900/40 rounded-xl text-xs text-red-400">
              {error}
            </div>
          )}

          {cert && (
            <div className="space-y-4 pt-4 border-t border-slate-800 animate-fade-in">
              <div className="bg-emerald-950/30 border border-emerald-900/40 rounded-xl p-4 flex items-start gap-3">
                <CheckCircle className="text-emerald-500 shrink-0 mt-0.5" size={16} />
                <div>
                  <h4 className="text-xs font-bold text-emerald-400">Signed Credential Match Found</h4>
                  <p className="text-[11px] text-slate-400 mt-0.5">This diploma is fully logged on the dynamic BrahmaVidya ledger. Identity and syllabus compliance are evaluated and verified.</p>
                </div>
              </div>

              <div className="border border-slate-800 bg-slate-950/40 rounded-xl p-6 text-center font-serif text-slate-200 relative">
                <div className="absolute top-4 right-4 text-[9px] font-sans font-mono text-indigo-400 uppercase tracking-wider">
                  Accredited Code: {cert.metadata?.accreditationCode || 'BVG-LDR-99'}
                </div>
                <p className="text-[10px] font-sans text-indigo-300 tracking-wider uppercase font-bold">This is to certify that</p>
                <h3 className="text-2xl font-bold font-sans text-amber-100 my-2">{cert.recipientName}</h3>
                <p className="text-xs italic text-slate-400">has successfully completed academic competencies in</p>
                <h4 className="text-lg font-bold font-sans text-white my-1">{cert.courseTitle}</h4>
                <p className="text-[10px] font-sans leading-relaxed text-slate-500 max-w-sm mx-auto mt-4">
                  Issued on: {new Date(cert.issuedAt).toLocaleDateString()} via secure academic hash.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </React.Fragment>
  );
};

export default CertificatesShell;
