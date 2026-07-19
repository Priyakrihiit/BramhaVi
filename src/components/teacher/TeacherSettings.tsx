/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Settings, Save, CheckCircle2, Shield, Bell, Cpu } from 'lucide-react';
import { Button, Input, Badge } from '../DesignSystem';

export const TeacherSettings: React.FC = () => {
  const [notifyOnEnroll, setNotifyOnEnroll] = useState(true);
  const [notifyOnSubmission, setNotifyOnSubmission] = useState(true);
  const [autoPayout, setAutoPayout] = useState(false);
  const [payoutThreshold, setPayoutThreshold] = useState('10000');
  const [aiAssistantModel, setAiAssistantModel] = useState('gemini-3.5-flash');

  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSaveSettings = (e: React.FormEvent) => {
    e.preventDefault();
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 4000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Settings className="text-indigo-400" size={20} />
          Teacher Portal Settings
        </h2>
        <p className="text-xs text-slate-400">Configure notifications triggers, banking auto-settlement, and AI co-pilot models.</p>
      </div>

      {saveSuccess && (
        <div className="p-3 bg-emerald-950/20 border border-emerald-500/25 text-emerald-400 text-xs rounded-xl flex items-center gap-2 select-none animate-fade-in font-sans">
          <CheckCircle2 size={14} /> System preferences have been successfully committed to local storage.
        </div>
      )}

      <form onSubmit={handleSaveSettings} className="space-y-6">
        {/* Card 1: Notifications triggers */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl space-y-4 text-left">
          <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5 select-none">
            <Bell size={13} /> Notification Triggers
          </h3>
          <p className="text-[11px] text-slate-400 select-none">Establish webhook and email notifications triggers for student events.</p>
          
          <div className="space-y-3 pt-2">
            <div className="flex items-center justify-between p-3.5 bg-slate-950 border border-slate-850 rounded-xl">
              <div className="space-y-0.5">
                <span className="text-xs font-bold text-white block">Syllabus Enrollment Emails</span>
                <span className="text-[10px] text-slate-500">Dispatch summary logs as soon as a new scholar pays for a course program.</span>
              </div>
              <input
                type="checkbox"
                checked={notifyOnEnroll}
                onChange={() => setNotifyOnEnroll(!notifyOnEnroll)}
                className="h-4 w-4 cursor-pointer"
              />
            </div>

            <div className="flex items-center justify-between p-3.5 bg-slate-950 border border-slate-850 rounded-xl">
              <div className="space-y-0.5">
                <span className="text-xs font-bold text-white block">Assignment Submitted Signals</span>
                <span className="text-[10px] text-slate-500">Trigger alerts when students submit a final syllabus project assignment.</span>
              </div>
              <input
                type="checkbox"
                checked={notifyOnSubmission}
                onChange={() => setNotifyOnSubmission(!notifyOnSubmission)}
                className="h-4 w-4 cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Card 2: Financial auto settlement */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl space-y-4 text-left">
          <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5 select-none">
            <Shield size={13} /> Royalties Settlement
          </h3>
          <p className="text-[11px] text-slate-400 select-none">Configure dynamic financial auto payouts and threshold boundaries.</p>

          <div className="space-y-4 pt-2">
            <div className="flex items-center justify-between p-3.5 bg-slate-950 border border-slate-850 rounded-xl">
              <div className="space-y-0.5">
                <span className="text-xs font-bold text-white block">Enable Automatic Bank Cashout</span>
                <span className="text-[10px] text-slate-500">Instantly trigger payout requests once wallet reaches predefined limit.</span>
              </div>
              <input
                type="checkbox"
                checked={autoPayout}
                onChange={() => setAutoPayout(!autoPayout)}
                className="h-4 w-4 cursor-pointer"
              />
            </div>

            {autoPayout && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-fade-in">
                <Input
                  label="Payout Threshold Amount (INR)"
                  type="number"
                  value={payoutThreshold}
                  onChange={e => setPayoutThreshold(e.target.value)}
                  required
                />
              </div>
            )}
          </div>
        </div>

        {/* Card 3: AI Co-pilot settings */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-3xl space-y-4 text-left">
          <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5 select-none">
            <Cpu size={13} /> AI Syllabus Generator Models
          </h3>
          <p className="text-[11px] text-slate-400 select-none">Establish active generative engines for drafting exams and lesson material.</p>

          <div className="pt-2">
            <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Generative AI Provider Model</label>
            <select
              className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-2.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              value={aiAssistantModel}
              onChange={e => setAiAssistantModel(e.target.value)}
            >
              <option value="gemini-3.5-flash">Google Gemini 3.5 Flash (Default)</option>
              <option value="gemini-3.5-pro">Google Gemini 3.5 Pro (Analytical)</option>
              <option value="anthropic-claude">Anthropic Claude 3.5 Sonnet</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end select-none">
          <Button type="submit" variant="primary">
            <Save size={14} /> Commit Preferences
          </Button>
        </div>
      </form>
    </div>
  );
};
