/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  Eye,
  Sliders,
  CheckCircle,
  HelpCircle,
  Volume2,
  BookOpen,
  Keyboard,
  Compass
} from 'lucide-react';

export const ProdModule13Accessibility: React.FC = () => {
  const [fontSize, setFontSize] = useState<'normal' | 'large' | 'extra'>('normal');
  const [contrast, setContrast] = useState<'default' | 'high'>('default');
  const [screenReaderLog, setScreenReaderLog] = useState<string>('Welcome. Selected default dashboard tab.');

  const [checklist, setChecklist] = useState([
    { id: '1', task: 'All interactive elements have unique HTML "id" attributes for DOM selectors', done: true },
    { id: '2', task: 'Visual components include explicit "aria-label" or "aria-expanded" properties', done: true },
    { id: '3', task: 'Color contrast ratio complies with WCAG AA standard (at least 4.5:1)', done: true },
    { id: '4', task: 'Keyboard sequential navigation follows standard "tabIndex" flows', done: true }
  ]);

  const speakText = (text: string) => {
    setScreenReaderLog(`Screen Reader Output: "${text}"`);
  };

  return (
    <div id="accessibility-compliance-root" className="space-y-6">
      {/* Sub controls layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 space-y-2">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">Contrast Options</span>
            <Eye className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="flex gap-2 mt-2">
            <button
              onClick={() => { setContrast('default'); speakText('Contrast reset to dark default'); }}
              className={`flex-1 text-[10px] font-mono font-bold py-1 rounded border transition ${contrast === 'default' ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-slate-900 border-slate-800 text-slate-400'}`}
            >
              Default Dark
            </button>
            <button
              onClick={() => { setContrast('high'); speakText('High contrast activated'); }}
              className={`flex-1 text-[10px] font-mono font-bold py-1 rounded border transition ${contrast === 'high' ? 'bg-amber-400 border-amber-300 text-slate-950 font-black' : 'bg-slate-900 border-slate-800 text-slate-400'}`}
            >
              High Contrast (AA)
            </button>
          </div>
        </div>

        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 space-y-2">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">Font Scale Modifier</span>
            <Compass className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="flex gap-1.5 mt-2">
            {(['normal', 'large', 'extra'] as const).map(sz => (
              <button
                key={sz}
                onClick={() => { setFontSize(sz); speakText(`Font scale altered to ${sz}`); }}
                className={`flex-1 text-[10px] font-mono font-bold py-1 rounded border capitalize transition ${fontSize === sz ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-slate-900 border-slate-800 text-slate-400'}`}
              >
                {sz}
              </button>
            ))}
          </div>
        </div>

        <div className="bg-slate-950/50 border border-slate-900 rounded-xl p-4 space-y-2">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-slate-500 font-mono font-bold uppercase">Simulated Assistive Reader</span>
            <Volume2 className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="bg-[#050914] border border-slate-900 p-2 rounded text-[10px] text-emerald-400 font-mono truncate mt-2">
            {screenReaderLog}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 text-left">
        {/* Dynamic Sandbox Display */}
        <div className="lg:col-span-7 bg-[#050914] border border-indigo-950/40 rounded-xl p-5 space-y-4">
          <div className="border-b border-slate-900 pb-2">
            <span className="text-xs font-bold text-slate-300 font-sans">Active Accessibility Content Sandbox</span>
          </div>

          <div
            className={`p-5 rounded-xl border transition-all ${
              contrast === 'high'
                ? 'bg-black border-amber-400 text-amber-400'
                : 'bg-slate-950 border-slate-900 text-slate-300'
            }`}
          >
            <h3
              className={`font-black font-sans leading-snug tracking-tight ${
                fontSize === 'normal' ? 'text-sm' : fontSize === 'large' ? 'text-base' : 'text-lg'
              }`}
            >
              High Accessibility Design Blueprint
            </h3>

            <p
              className={`mt-2 leading-relaxed font-sans ${
                fontSize === 'normal' ? 'text-xs' : fontSize === 'large' ? 'text-sm' : 'text-base'
              }`}
            >
              This sandbox updates typography dimensions on trigger commands, matching user custom client adjustments. High contrast mode implements pure black layers with vivid, WCAG AA compliant highlights.
            </p>

            <button
              onClick={() => speakText('Action Button triggered')}
              aria-label="Confirm Action trigger"
              className={`mt-4 font-bold font-sans px-4 py-1.5 rounded-lg transition ${
                contrast === 'high'
                  ? 'bg-amber-400 text-black hover:bg-amber-300 border border-amber-300'
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white'
              } ${fontSize === 'normal' ? 'text-[11px]' : fontSize === 'large' ? 'text-xs' : 'text-sm'}`}
            >
              Action Button
            </button>
          </div>
        </div>

        {/* Accessibility Best Practice Checklist */}
        <div className="lg:col-span-5 bg-slate-950/40 border border-slate-900 rounded-xl p-4 flex flex-col justify-between h-full min-h-[280px]">
          <div className="space-y-4">
            <div className="flex items-center gap-1.5 border-b border-slate-900 pb-2 text-slate-300">
              <Keyboard className="w-4 h-4 text-indigo-400" />
              <span className="text-xs font-bold font-sans uppercase tracking-wider font-mono">WCAG AA Standard Compliance Checklist</span>
            </div>

            <div className="space-y-2">
              {checklist.map(item => (
                <div key={item.id} className="flex gap-2 bg-[#050914] p-2 rounded-lg border border-slate-900/60 text-left">
                  <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <p className="text-[10px] text-slate-400 font-sans leading-relaxed">{item.task}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-3 border-t border-slate-900 mt-4">
            <p className="text-[10px] text-slate-500 leading-normal">
              Compliance is periodically audited using automated DOM validators during production deployment checks.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProdModule13Accessibility;
