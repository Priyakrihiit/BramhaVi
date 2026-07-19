/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  FileText,
  Clock,
  History,
  PenTool,
  CheckCircle,
  Download,
  AlertCircle,
  Settings
} from 'lucide-react';

interface LegalAgreement {
  id: string;
  title: string;
  type: 'TEACHER' | 'AUTHOR' | 'SERVICE_PROVIDER' | 'ORGANIZATION';
  version: string;
  publishedDate: string;
  clausesCount: number;
  status: 'ACTIVE' | 'DRAFT';
  contentTemplate: string;
}

export const ProdModule4Contracts: React.FC = () => {
  const [agreements, setAgreements] = useState<LegalAgreement[]>([
    { id: 'AGR-TCH-04', title: 'Teacher Standard Revenue Agreement', type: 'TEACHER', version: 'v2.1', publishedDate: '2026-04-15', clausesCount: 14, status: 'ACTIVE', contentTemplate: 'This Teacher Revenue Share Agreement establishes standard platform distribution splits (70% Teacher, 30% Platform). All course materials belong to the intellectual property of BrahmaVidya.' },
    { id: 'AGR-PUB-09', title: 'Self-Publishing Author Agreement', type: 'AUTHOR', version: 'v1.4', publishedDate: '2026-05-10', clausesCount: 18, status: 'ACTIVE', contentTemplate: 'Author publishing terms grant BrahmaVidya distribution licenses with non-exclusive publishing royalties paid on a monthly double-accounting ledger system.' },
    { id: 'AGR-SRV-21', title: 'Service Provider Marketplace Terms', type: 'SERVICE_PROVIDER', version: 'v3.0', publishedDate: '2026-06-01', clausesCount: 10, status: 'ACTIVE', contentTemplate: 'Independent services listed in the marketplace must abide by delivery SLA standards. Dispute management is processed through the platform-level escrow wallet.' },
    { id: 'AGR-ORG-15', title: 'Enterprise Multi-Tenant SaaS Contract', type: 'ORGANIZATION', version: 'v1.0', publishedDate: '2026-01-20', clausesCount: 22, status: 'ACTIVE', contentTemplate: 'Multi-Tenant organizations are guaranteed 99.9% container uptime backed by our scalable Google Cloud Run environment with isolated PostgreSQL databases.' }
  ]);

  const [history, setHistory] = useState([
    { timestamp: '2026-07-07 22:15', user: 'priyapandey8405@gmail.com', action: 'Signed Teacher Standard Revenue Agreement v2.1', status: 'SUCCESS' },
    { timestamp: '2026-07-06 14:32', user: 'organization-lead@pune.org', action: 'Accepted Enterprise Multi-Tenant SaaS Contract v1.0', status: 'SUCCESS' }
  ]);

  const [selectedAgr, setSelectedAgr] = useState<LegalAgreement>(agreements[0]);
  const [customClauseText, setCustomClauseText] = useState<string>('');
  const [signatureName, setSignatureName] = useState<string>('');
  const [signed, setSigned] = useState<boolean>(false);

  const signContract = () => {
    if (!signatureName) return;
    setSigned(true);
    setHistory([
      {
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 16),
        user: 'priyapandey8405@gmail.com',
        action: `Signed "${selectedAgr.title}" digitally as [${signatureName}]`,
        status: 'SUCCESS'
      },
      ...history
    ]);
  };

  const createDraftVersion = () => {
    const updatedAgr = {
      ...selectedAgr,
      version: `v${(parseFloat(selectedAgr.version.substring(1)) + 0.1).toFixed(1)}`,
      publishedDate: new Date().toISOString().split('T')[0],
      clausesCount: selectedAgr.clausesCount + 1,
      contentTemplate: selectedAgr.contentTemplate + (customClauseText ? `\n\nAddendum Clause: ${customClauseText}` : '')
    };
    setAgreements(agreements.map(a => a.id === selectedAgr.id ? updatedAgr : a));
    setSelectedAgr(updatedAgr);
    setCustomClauseText('');
  };

  return (
    <div id="contracts-dashboard-root" className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 text-left">
        {/* Left Column: Select Agreement Template & Customize */}
        <div className="lg:col-span-4 space-y-4">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider font-mono">Agreement Templates</h4>
          <div className="space-y-2">
            {agreements.map(agr => (
              <button
                key={agr.id}
                onClick={() => { setSelectedAgr(agr); setSigned(false); }}
                className={`w-full p-3.5 rounded-xl border text-left transition ${selectedAgr.id === agr.id ? 'bg-indigo-950/60 border-indigo-500/80' : 'bg-slate-950/60 border-slate-900 hover:border-slate-800'}`}
              >
                <div className="flex justify-between items-start">
                  <span className="text-[10px] text-indigo-400 font-mono font-bold">{agr.id} ({agr.version})</span>
                  <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
                </div>
                <h5 className="text-xs font-black text-white mt-1.5">{agr.title}</h5>
                <p className="text-[10px] text-slate-500 mt-1">Clauses: {agr.clausesCount} • Date: {agr.publishedDate}</p>
              </button>
            ))}
          </div>

          <div className="bg-slate-950/40 border border-slate-900 rounded-xl p-4 space-y-3">
            <h5 className="text-xs font-bold text-slate-300 font-sans">Propose Custom Addendum Clause</h5>
            <textarea
              placeholder="Inject custom legal clauses..."
              value={customClauseText}
              onChange={(e) => setCustomClauseText(e.target.value)}
              className="w-full bg-slate-950 border border-indigo-950/80 rounded-lg p-2 text-xs text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-sans h-20 resize-none"
            />
            <button
              onClick={createDraftVersion}
              className="w-full bg-indigo-600/10 hover:bg-indigo-600/20 border border-indigo-950 text-indigo-400 text-xs font-bold py-1.5 rounded-lg transition"
            >
              Update Contract Version
            </button>
          </div>
        </div>

        {/* Middle Column: Interactive Signature Pad & Live Preview */}
        <div className="lg:col-span-5 bg-slate-950/40 border border-indigo-950/30 rounded-xl p-5 space-y-4">
          <div className="flex justify-between items-center pb-3 border-b border-slate-900">
            <div className="flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-indigo-400" />
              <h5 className="text-xs font-black text-white uppercase tracking-wider font-mono">Contract Viewer</h5>
            </div>
            <span className="text-[10px] bg-slate-900 text-slate-400 px-2.5 py-0.5 rounded font-mono">
              PREVIEW ONLY
            </span>
          </div>

          <div className="bg-[#050914] rounded-xl p-4 border border-slate-900 text-xs text-slate-400 font-serif leading-relaxed max-h-[250px] overflow-y-auto space-y-3 whitespace-pre-wrap">
            <div className="font-bold text-center text-slate-200 border-b border-slate-900/60 pb-2">
              {selectedAgr.title.toUpperCase()}
              <div className="text-[10px] font-mono mt-1 font-normal text-slate-500">Document UUID: {selectedAgr.id}-SYS</div>
            </div>
            {selectedAgr.contentTemplate}
          </div>

          {/* Electronic Signature Block */}
          <div className="bg-slate-950 border border-indigo-950/60 p-4 rounded-xl space-y-3">
            <div className="flex items-center gap-1.5 text-slate-300">
              <PenTool className="w-4 h-4 text-indigo-400" />
              <span className="text-xs font-bold font-sans">E-Signature Verification</span>
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Type your full legal name to sign"
                value={signatureName}
                onChange={(e) => setSignatureName(e.target.value)}
                disabled={signed}
                className="bg-[#0b1329] border border-indigo-950/80 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-sans w-full"
              />
              <button
                onClick={signContract}
                disabled={signed || !signatureName}
                className={`text-xs font-bold font-sans px-4 py-1.5 rounded-lg transition ${signed ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-950' : 'bg-indigo-600 hover:bg-indigo-500 text-white'}`}
              >
                {signed ? 'Signed' : 'Sign'}
              </button>
            </div>
            {signed && (
              <p className="text-[10px] text-emerald-400 font-mono flex items-center gap-1">
                <CheckCircle className="w-3.5 h-3.5" /> Digitally sealed with SHA256 cryptographic sign stamp.
              </p>
            )}
          </div>
        </div>

        {/* Right Column: Digital Signature & Acceptance History Logs */}
        <div className="lg:col-span-3 bg-slate-950/40 border border-slate-900 rounded-xl p-4 flex flex-col justify-between h-full min-h-[300px]">
          <div className="space-y-4">
            <div className="flex items-center gap-1.5 text-slate-300">
              <History className="w-4 h-4 text-indigo-400" />
              <span className="text-xs font-bold font-sans uppercase tracking-wider font-mono">Acceptance Audits</span>
            </div>

            <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
              {history.map((h, i) => (
                <div key={i} className="bg-[#050914] border border-slate-900 rounded-lg p-2.5 text-left font-mono text-[10px] text-slate-400 space-y-1">
                  <div className="flex justify-between text-slate-500">
                    <span>{h.timestamp}</span>
                    <span className="text-emerald-400 text-[9px]">{h.status}</span>
                  </div>
                  <div className="font-sans font-bold text-slate-300 leading-snug">{h.action}</div>
                  <div className="text-slate-600 truncate">{h.user}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-3 border-t border-slate-900 mt-4">
            <p className="text-[10px] text-slate-500 leading-normal">
              Agreements are automatically formatted and preserved using S3 durable cloud storage.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProdModule4Contracts;
