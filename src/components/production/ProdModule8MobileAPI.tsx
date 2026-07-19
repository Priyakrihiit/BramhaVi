/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  Code,
  BookOpen,
  Terminal,
  Activity,
  Layers,
  Cpu,
  Copy,
  CheckCircle,
  Database,
  Smartphone,
  Check
} from 'lucide-react';

interface APIEndpoint {
  method: 'GET' | 'POST' | 'PUT';
  path: string;
  desc: string;
  responseBody: string;
}

export const ProdModule8MobileAPI: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'endpoints' | 'offline' | 'push'>('endpoints');
  const [copiedPath, setCopiedPath] = useState<string | null>(null);

  const ENDPOINTS: APIEndpoint[] = [
    {
      method: 'GET',
      path: '/api/v1/mobile/courses?page=1&limit=10',
      desc: 'Retrieves courses paginated for Flutter infinite scrolling. Includes lightweight optimized images.',
      responseBody: `{
  "success": true,
  "currentPage": 1,
  "totalPages": 5,
  "totalItems": 48,
  "data": [
    {
      "id": "course-ml-101",
      "title": "Introduction to AI & Deep Learning",
      "instructor": "Dr. Ramesh Sharma",
      "thumbnailUrl": "https://img.bvgalaxy.com/cache/ml-101_300x168.webp",
      "rating": 4.9,
      "enrolledCount": 1420
    }
  ]
}`
    },
    {
      method: 'POST',
      path: '/api/v1/mobile/sync/queue',
      desc: 'Synchronizes offline completed lectures, local bookmarks, and progress marks accumulated while disconnected.',
      responseBody: `{
  "success": true,
  "synchronizedItems": 4,
  "serverTimestamp": "2026-07-07T23:01:00Z",
  "status": "COMPLETED"
}`
    },
    {
      method: 'GET',
      path: '/api/v1/mobile/downloads/offline-video?id=lec-4402',
      desc: 'Fetch raw video byte streams optimized for Flutter download managers with offline security decoders.',
      responseBody: `{
  "success": true,
  "videoId": "lec-4402",
  "downloadUrl": "https://bv-s3-private.s3.amazonaws.com/videos/lec-4402_lowres.mp4",
  "checksum": "sha256-a0f19c82b120",
  "allowOfflineExpiryDays": 30
}`
    }
  ];

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedPath(id);
    setTimeout(() => setCopiedPath(null), 2000);
  };

  return (
    <div id="mobile-api-root" className="space-y-6">
      {/* Sub Tabs */}
      <div className="flex border-b border-slate-900 pb-3 gap-2">
        <button
          onClick={() => setActiveTab('endpoints')}
          className={`px-4 py-1.5 rounded-lg text-xs font-bold font-sans transition ${activeTab === 'endpoints' ? 'bg-indigo-600 text-white' : 'bg-slate-900/40 text-slate-400 hover:bg-slate-900'}`}
        >
          Flutter REST Endpoints
        </button>
        <button
          onClick={() => setActiveTab('offline')}
          className={`px-4 py-1.5 rounded-lg text-xs font-bold font-sans transition ${activeTab === 'offline' ? 'bg-indigo-600 text-white' : 'bg-slate-900/40 text-slate-400 hover:bg-slate-900'}`}
        >
          Offline Sync Guide
        </button>
        <button
          onClick={() => setActiveTab('push')}
          className={`px-4 py-1.5 rounded-lg text-xs font-bold font-sans transition ${activeTab === 'push' ? 'bg-indigo-600 text-white' : 'bg-slate-900/40 text-slate-400 hover:bg-slate-900'}`}
        >
          Push Notifications
        </button>
      </div>

      {activeTab === 'endpoints' && (
        <div className="space-y-4 text-left">
          <div className="bg-[#050914] p-3 rounded-lg border border-slate-900 text-xs text-slate-400 leading-relaxed font-sans">
            BrahmaVidya REST API v1 is fully optimized for Flutter clients, utilizing WebP aggressive image caching, compressed Gzip payloads, and fast Cursor Pagination for optimal 60fps view performance.
          </div>

          <div className="space-y-4">
            {ENDPOINTS.map((ep, idx) => (
              <div key={idx} className="bg-slate-950/40 border border-slate-900 rounded-xl p-4 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-900 pb-2">
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] font-mono font-bold px-2.5 py-0.5 rounded ${ep.method === 'GET' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-indigo-500/10 text-indigo-400'}`}>
                      {ep.method}
                    </span>
                    <span className="text-xs font-bold text-slate-300 font-mono">{ep.path}</span>
                  </div>
                  <button
                    onClick={() => handleCopy(ep.path, ep.path)}
                    className="text-[10px] text-slate-500 hover:text-indigo-400 flex items-center gap-1 font-mono transition"
                  >
                    {copiedPath === ep.path ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    Copy Path
                  </button>
                </div>

                <p className="text-[11px] text-slate-400 font-sans leading-normal">{ep.desc}</p>

                <div className="space-y-1">
                  <span className="text-[10px] text-slate-500 font-mono">Simulated Response Payload</span>
                  <pre className="bg-slate-950 border border-slate-900 rounded-lg p-3 font-mono text-[10px] text-indigo-300 overflow-x-auto leading-normal">
                    {ep.responseBody}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'offline' && (
        <div className="bg-slate-950/40 border border-slate-900 rounded-xl p-5 text-left space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-slate-900">
            <Smartphone className="w-4.5 h-4.5 text-indigo-400" />
            <h4 className="text-xs font-black text-white uppercase tracking-wider font-mono">Flutter Offline Hive Storage Sync Architecture</h4>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed font-sans">
            Our Flutter application stores completed quizzes and lesson states locally inside an encrypted Hive database when internet access is suspended. Once the device recovers network connection, the local Sync Queue submits queued payloads atomically.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-[#050914] p-3 rounded-lg border border-slate-900">
              <span className="text-[10px] text-indigo-400 font-mono font-bold">STEP 1</span>
              <h5 className="text-xs font-bold text-white mt-1">Local Transaction Logging</h5>
              <p className="text-[10px] text-slate-500 mt-1">Hive records and indexes action tags locally.</p>
            </div>
            <div className="bg-[#050914] p-3 rounded-lg border border-slate-900">
              <span className="text-[10px] text-indigo-400 font-mono font-bold">STEP 2</span>
              <h5 className="text-xs font-bold text-white mt-1">Automatic Heartbeat Test</h5>
              <p className="text-[10px] text-slate-500 mt-1">Network status checks ping global REST gateways.</p>
            </div>
            <div className="bg-[#050914] p-3 rounded-lg border border-slate-900">
              <span className="text-[10px] text-indigo-400 font-mono font-bold">STEP 3</span>
              <h5 className="text-xs font-bold text-white mt-1">Atomic Endpoint Sync</h5>
              <p className="text-[10px] text-slate-500 mt-1">Queue submits transaction logs cleanly.</p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'push' && (
        <div className="bg-slate-950/40 border border-slate-900 rounded-xl p-5 text-left space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-slate-900">
            <Activity className="w-4.5 h-4.5 text-indigo-400" />
            <h4 className="text-xs font-black text-white uppercase tracking-wider font-mono">FCM (Firebase Cloud Messaging) Ingress</h4>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed font-sans">
            Push triggers utilize Firebase FCM protocols combined with localized SendGrid/Twilio notification dispatchers to ensure fast multi-device sync alerts.
          </p>

          <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-900">
            <span className="text-[10px] text-indigo-400 font-mono font-bold">FCM Payload Sample</span>
            <pre className="bg-slate-950 p-2 text-[10px] text-slate-300 font-mono leading-normal overflow-x-auto mt-2">
{`{
  "to": "/topics/enrolled_ml_101",
  "notification": {
    "title": "New Assignment Published",
    "body": "Dr. Ramesh Sharma published grading tasks for ML Foundations.",
    "sound": "default"
  },
  "data": {
    "courseId": "course-ml-101",
    "click_action": "FLUTTER_NOTIFICATION_CLICK"
  }
}`}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProdModule8MobileAPI;
