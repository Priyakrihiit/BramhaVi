/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  QrCode,
  Search,
  ShieldAlert,
  FileCheck,
  CheckCircle,
  AlertTriangle,
  Code,
  Cpu,
  Copy,
  UploadCloud,
  FileText
} from 'lucide-react';

interface VerifiedCertificate {
  uuid: string;
  studentName: string;
  courseTitle: string;
  issuedDate: string;
  issuerSignature: string;
  fraudRisk: 'NONE' | 'LOW' | 'HIGH';
  tamperCheck: 'PASSED' | 'FAILED';
}

export const ProdModule5Verification: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState<string>('cert-88a2-9901-bv');
  const [certResult, setCertResult] = useState<VerifiedCertificate | null>({
    uuid: 'cert-88a2-9901-bv',
    studentName: 'Priya Pandey',
    courseTitle: 'Full-Stack BrahmaVidya Architecture v1.KP',
    issuedDate: '2026-07-07',
    issuerSignature: 'SHA256:0b98a10787e91129b8c0054ff89a3f2b4c10a300fe99ab18b87c67c55c091910',
    fraudRisk: 'NONE',
    tamperCheck: 'PASSED'
  });

  const [activeTab, setActiveTab] = useState<'verify' | 'api' | 'fraud'>('verify');
  const [tamperedCert, setTamperedCert] = useState<boolean>(false);
  const [uploadState, setUploadState] = useState<'IDLE' | 'ANALYZING' | 'DONE'>('IDLE');

  const runVerification = () => {
    if (searchQuery.trim() === 'cert-88a2-9901-bv') {
      setCertResult({
        uuid: 'cert-88a2-9901-bv',
        studentName: 'Priya Pandey',
        courseTitle: 'Full-Stack BrahmaVidya Architecture v1.KP',
        issuedDate: '2026-07-07',
        issuerSignature: 'SHA256:0b98a10787e91129b8c0054ff89a3f2b4c10a300fe99ab18b87c67c55c091910',
        fraudRisk: 'NONE',
        tamperCheck: 'PASSED'
      });
    } else {
      setCertResult({
        uuid: searchQuery || 'cert-unknown',
        studentName: 'Unregistered Candidate',
        courseTitle: 'Unverified Subject Matter',
        issuedDate: '-',
        issuerSignature: 'None / Missing Signature Hash',
        fraudRisk: 'HIGH',
        tamperCheck: 'FAILED'
      });
    }
  };

  const simulateUpload = () => {
    setUploadState('ANALYZING');
    setTimeout(() => {
      setUploadState('DONE');
      setTamperedCert(true);
    }, 1500);
  };

  return (
    <div id="cert-verification-root" className="space-y-6">
      {/* Upper Navigation Tabs */}
      <div className="flex border-b border-slate-900 pb-3 gap-2">
        <button
          onClick={() => setActiveTab('verify')}
          className={`px-4 py-1.5 rounded-lg text-xs font-bold font-sans transition ${activeTab === 'verify' ? 'bg-indigo-600 text-white' : 'bg-slate-900/40 text-slate-400 hover:bg-slate-900'}`}
        >
          Verify Certificate
        </button>
        <button
          onClick={() => setActiveTab('api')}
          className={`px-4 py-1.5 rounded-lg text-xs font-bold font-sans transition ${activeTab === 'api' ? 'bg-indigo-600 text-white' : 'bg-slate-900/40 text-slate-400 hover:bg-slate-900'}`}
        >
          Public Verification API
        </button>
        <button
          onClick={() => setActiveTab('fraud')}
          className={`px-4 py-1.5 rounded-lg text-xs font-bold font-sans transition ${activeTab === 'fraud' ? 'bg-indigo-600 text-white' : 'bg-slate-900/40 text-slate-400 hover:bg-slate-900'}`}
        >
          Fraud Detection AI
        </button>
      </div>

      {activeTab === 'verify' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 text-left">
          {/* Certificate Input Search */}
          <div className="lg:col-span-5 space-y-4">
            <div className="bg-slate-950/40 border border-slate-900 p-4 rounded-xl space-y-3">
              <h4 className="text-xs font-bold text-slate-300 font-sans">Query Verification Portal</h4>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Enter Certificate UUID"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-[#0b1329] border border-indigo-950/80 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-sans w-full"
                />
                <button
                  onClick={runVerification}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-4 py-1.5 rounded-lg transition shrink-0"
                >
                  Verify
                </button>
              </div>
              <p className="text-[10px] text-slate-500 font-sans">
                Try querying our default valid credential code: <code className="text-indigo-400">cert-88a2-9901-bv</code>
              </p>
            </div>

            {/* Simulated QR Code Stamp */}
            <div className="bg-[#050914] border border-indigo-950/40 rounded-xl p-4 flex items-center gap-4">
              <div className="bg-white p-2.5 rounded-lg shrink-0 shadow-lg border border-slate-200">
                <QrCode className="w-16 h-16 text-slate-950" />
              </div>
              <div className="space-y-1">
                <span className="text-[9px] bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded border border-indigo-950/60 font-mono">
                  PUBLIC VALIDATION ROUTE
                </span>
                <h5 className="text-xs font-bold text-slate-200 mt-1">Direct Verification Landing URL</h5>
                <p className="text-[10px] text-slate-500 font-mono break-all leading-relaxed">
                  https://bvgalaxy.com/verify/cert-88a2-9901-bv
                </p>
              </div>
            </div>
          </div>

          {/* Verification Audit Result Card */}
          <div className="lg:col-span-7 bg-slate-950/40 border border-indigo-950/30 rounded-xl p-5 space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-900">
              <FileCheck className="w-4.5 h-4.5 text-indigo-400" />
              <h4 className="text-xs font-black text-white uppercase tracking-wider font-mono">Digital Signature Audit</h4>
            </div>

            {certResult ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-[#050914] p-3 rounded-lg border border-slate-900">
                    <p className="text-[10px] text-slate-500">Student Name</p>
                    <p className="text-xs font-bold text-slate-200 mt-0.5 font-sans">{certResult.studentName}</p>
                  </div>
                  <div className="bg-[#050914] p-3 rounded-lg border border-slate-900">
                    <p className="text-[10px] text-slate-500">Issued Date</p>
                    <p className="text-xs font-bold text-slate-200 mt-0.5 font-mono">{certResult.issuedDate}</p>
                  </div>
                </div>

                <div className="bg-[#050914] p-3 rounded-lg border border-slate-900">
                  <p className="text-[10px] text-slate-500">Course / Accolade Title</p>
                  <p className="text-xs font-bold text-slate-200 mt-0.5 font-sans">{certResult.courseTitle}</p>
                </div>

                <div className="bg-[#050914] p-3 rounded-lg border border-slate-900">
                  <p className="text-[10px] text-slate-500">SHA256 Cryptographic Issuer Stamp</p>
                  <p className="text-[10px] font-mono text-indigo-400 mt-1 leading-normal break-all bg-slate-950 p-2 rounded">
                    {certResult.issuerSignature}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-2">
                  <div className={`p-2.5 rounded-lg border flex items-center gap-2 ${certResult.tamperCheck === 'PASSED' ? 'bg-emerald-500/10 border-emerald-950 text-emerald-400' : 'bg-rose-500/10 border-rose-950 text-rose-400'}`}>
                    <CheckCircle className="w-4 h-4 shrink-0" />
                    <div>
                      <p className="text-[10px] text-slate-500 leading-none">Tamper Check</p>
                      <p className="text-xs font-bold mt-1 font-sans">{certResult.tamperCheck}</p>
                    </div>
                  </div>

                  <div className={`p-2.5 rounded-lg border flex items-center gap-2 ${certResult.fraudRisk === 'NONE' ? 'bg-emerald-500/10 border-emerald-950 text-emerald-400' : 'bg-rose-500/10 border-rose-950 text-rose-400'}`}>
                    <ShieldAlert className="w-4 h-4 shrink-0" />
                    <div>
                      <p className="text-[10px] text-slate-500 leading-none">Fraud Risk Index</p>
                      <p className="text-xs font-bold mt-1 font-sans">{certResult.fraudRisk}</p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-16 text-slate-600 text-xs italic">
                Enter a UUID to audit certificate authenticity.
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'api' && (
        <div className="bg-slate-950/40 border border-slate-900 rounded-xl p-5 text-left space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-900">
            <Code className="w-4.5 h-4.5 text-indigo-400" />
            <h4 className="text-xs font-black text-white uppercase tracking-wider font-mono">Public Verification REST API</h4>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed font-sans">
            Secure, high-concurrency endpoint to query credential hashes externally from company services or employers.
          </p>

          <div className="space-y-1">
            <div className="flex justify-between items-center bg-slate-950 px-3 py-1.5 rounded-t-lg border-t border-x border-slate-900 text-[10px] font-mono text-indigo-400">
              <span>GET /api/v1/verify/cert-88a2-9901-bv</span>
              <button className="flex items-center gap-1 hover:text-white transition">
                <Copy className="w-3.5 h-3.5" /> Copy Endpoint
              </button>
            </div>
            <pre className="bg-slate-950 border border-slate-900 rounded-b-lg p-3.5 font-mono text-[10px] text-slate-300 overflow-x-auto leading-normal">
{`{
  "success": true,
  "verified": true,
  "certificate": {
    "uuid": "cert-88a2-9901-bv",
    "recipient": "Priya Pandey",
    "subject": "Full-Stack BrahmaVidya Architecture v1.KP",
    "timestamp": "2026-07-07T23:01:00Z",
    "hash": "0b98a10787e91129b8c0054ff89a3f2b4c10a300fe99ab18b87c67c55c091910"
  },
  "tamperCheck": "PASSED",
  "issuer": "BrahmaVidya Registrar Certificate Authority"
}`}
            </pre>
          </div>
        </div>
      )}

      {activeTab === 'fraud' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
          {/* File upload simulator for fraud analyzer */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-xl p-5 space-y-4">
            <h4 className="text-xs font-bold text-slate-300 font-sans">Upload Certificate File (.pdf, .png)</h4>
            <div
              onClick={simulateUpload}
              className="border border-dashed border-indigo-950 hover:border-indigo-500/50 bg-[#050914] hover:bg-slate-950/60 rounded-xl p-8 text-center cursor-pointer transition space-y-3"
            >
              <UploadCloud className="w-10 h-10 text-indigo-400 mx-auto" />
              <div>
                <p className="text-xs font-bold text-slate-300">Drag & Drop certificate here</p>
                <p className="text-[10px] text-slate-500 mt-1">Supports PDF or PNG image vectors up to 10MB</p>
              </div>
              <button className="bg-indigo-600 hover:bg-indigo-500 text-white text-[10px] font-bold px-3 py-1.5 rounded transition">
                Select File
              </button>
            </div>

            {uploadState === 'ANALYZING' && (
              <div className="p-3 bg-indigo-950/40 border border-indigo-900 rounded-lg text-xs text-indigo-300 flex items-center gap-2">
                <Cpu className="w-4 h-4 animate-spin text-indigo-400" />
                <span>AI running spectral cryptographic tamper checks...</span>
              </div>
            )}
          </div>

          {/* AI Fraud Analysis Audit Results */}
          <div className="bg-slate-950/40 border border-indigo-950/30 rounded-xl p-5 space-y-4">
            <h4 className="text-xs font-bold text-slate-300 font-sans">AI Fraud Risk Analysis Output</h4>
            {tamperedCert ? (
              <div className="space-y-4">
                <div className="p-3.5 bg-rose-500/10 border border-rose-950 text-rose-400 rounded-xl flex items-start gap-2 text-xs">
                  <AlertTriangle className="w-5 h-5 shrink-0" />
                  <div className="space-y-1">
                    <p className="font-bold">HIGH FRAUD RISK SUSPECTED</p>
                    <p className="text-[10px] text-slate-400 leading-normal">
                      Vector analysis detected altered text bounding coordinates. Metadata timestamps contradict internal signature hashes.
                    </p>
                  </div>
                </div>

                <div className="bg-[#050914] p-3 rounded-lg border border-slate-900 text-xs space-y-1.5 font-mono">
                  <div className="flex justify-between border-b border-slate-900/60 pb-1">
                    <span className="text-slate-500">Metadata Match:</span>
                    <span className="text-rose-400 font-bold">FAILED</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-900/60 pb-1">
                    <span className="text-slate-500">Signature Hash:</span>
                    <span className="text-rose-400 font-bold">INVALID (TAMPERED)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Certificate State:</span>
                    <span className="text-rose-400 font-bold">BLACKLISTED</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-16 text-slate-600 text-xs italic">
                Upload a document to run real-time automated fraud detection.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProdModule5Verification;
