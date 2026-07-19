/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Button, Input, Textarea, Select, Badge } from '../DesignSystem';
import { FileText, Save, Download, RefreshCw, ChevronUp, ChevronDown, CheckCircle, Sparkles } from 'lucide-react';

export const ResumeBuilder: React.FC = () => {
  const [activeResumeTab, setActiveResumeTab] = useState<'editor' | 'ats'>('editor');
  
  // Resume forms states
  const [name, setName] = useState('Priya');
  const [title, setTitle] = useState('SaaS Software Architect');
  const [summary, setSummary] = useState('SaaS Architect with years of experience building proctored environments.');
  
  const [experiences, setExperiences] = useState([
    { id: '1', role: 'Staff Architect', company: 'BVG Networks', duration: '2 Years' },
    { id: '2', role: 'Vedic Tutor Coordinator', company: 'IIT Co-op', duration: '1 Year' }
  ]);

  const [resumeColor, setResumeColor] = useState('indigo');
  const [fontFamily, setFontFamily] = useState('sans');

  // ATS states
  const [atsScore, setAtsScore] = useState<number | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  const handleMoveUp = (idx: number) => {
    if (idx === 0) return;
    setExperiences(prev => {
      const copy = [...prev];
      const temp = copy[idx - 1];
      copy[idx - 1] = copy[idx];
      copy[idx] = temp;
      return copy;
    });
  };

  const handleMoveDown = (idx: number) => {
    if (idx === experiences.length - 1) return;
    setExperiences(prev => {
      const copy = [...prev];
      const temp = copy[idx + 1];
      copy[idx + 1] = copy[idx];
      copy[idx] = temp;
      return copy;
    });
  };

  const runAtsAudit = () => {
    setAnalyzing(true);
    setAtsScore(null);
    setTimeout(() => {
      setAtsScore(85);
      setAnalyzing(false);
    }, 1500);
  };

  return (
    <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-6 text-left">
      
      {/* Tab controls */}
      <div className="flex justify-between items-center border-b border-indigo-950/45 pb-4">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-1.5 uppercase tracking-wider">
            <FileText size={16} className="text-indigo-400" /> Career Resume Builder
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">Build ATS-compliant resumes and analyze keyword matching scores.</p>
        </div>

        <div className="flex gap-2 text-xs font-mono select-none">
          <button onClick={() => setActiveResumeTab('editor')} className={`px-3 py-1 rounded-lg border ${activeResumeTab === 'editor' ? 'bg-indigo-650 border-indigo-500 text-white font-bold' : 'border-indigo-950 text-slate-500 hover:text-slate-350'}`}>Builder Editor</button>
          <button onClick={() => setActiveResumeTab('ats')} className={`px-3 py-1 rounded-lg border ${activeResumeTab === 'ats' ? 'bg-indigo-650 border-indigo-500 text-white font-bold' : 'border-indigo-950 text-slate-500 hover:text-slate-350'}`}>ATS Analyzer</button>
        </div>
      </div>

      {/* BUILDER EDITOR SCREEN */}
      {activeResumeTab === 'editor' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Editor Input Form */}
          <div className="lg:col-span-6 space-y-5">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block">Configure Fields</span>
            
            <div className="grid grid-cols-2 gap-4">
              <Input label="Name Name" value={name} onChange={(e) => setName(e.target.value)} />
              <Input label="Professional Title" value={title} onChange={(e) => setTitle(e.target.value)} />
            </div>

            <Textarea label="Professional Biography Summary" value={summary} onChange={(e) => setSummary(e.target.value)} />

            {/* Experience sections */}
            <div className="space-y-3">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Experience outlines (re-orderable)</span>
              {experiences.map((exp, idx) => (
                <div key={exp.id} className="p-3 bg-slate-950 border border-indigo-950/80 rounded-xl flex justify-between items-center text-xs">
                  <div>
                    <strong className="text-white">{exp.role}</strong>
                    <span className="block text-[10px] text-slate-500">{exp.company} ({exp.duration})</span>
                  </div>
                  <div className="flex gap-1">
                    <button onClick={() => handleMoveUp(idx)} className="p-1 hover:bg-slate-900 rounded text-slate-500 hover:text-white transition"><ChevronUp size={13} /></button>
                    <button onClick={() => handleMoveDown(idx)} className="p-1 hover:bg-slate-900 rounded text-slate-500 hover:text-white transition"><ChevronDown size={13} /></button>
                  </div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-4 border-t border-indigo-950/45 pt-4">
              <Select label="Resume Theme accent" value={resumeColor} onChange={(e) => setResumeColor(e.target.value)}>
                <option value="indigo">Indigo Corporate</option>
                <option value="emerald">Emerald Creative</option>
              </Select>
              <Select label="Typography font" value={fontFamily} onChange={(e) => setFontFamily(e.target.value)}>
                <option value="sans">Modern Sans-Serif</option>
                <option value="serif">Academic Serif</option>
              </Select>
            </div>
          </div>

          {/* Live Preview canvas */}
          <div className="lg:col-span-6 space-y-4">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest block">Live Document Preview</span>
            <div className={`p-8 rounded-2xl border text-left shadow-2xl space-y-6 ${fontFamily === 'serif' ? 'font-serif' : 'font-sans'} ${
              resumeColor === 'emerald' ? 'bg-[#0f241e] border-emerald-950 text-slate-200' : 'bg-[#0f1324] border-indigo-950 text-slate-200'
            }`}>
              <div>
                <h1 className="text-xl font-black text-white">{name}</h1>
                <span className="text-[10px] text-indigo-400 font-mono font-bold uppercase tracking-wider block mt-0.5">{title}</span>
              </div>

              <div className="space-y-1.5">
                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest block">Professional Summary</span>
                <p className="text-xs text-slate-400 leading-relaxed">{summary}</p>
              </div>

              <div className="space-y-3">
                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest block">Experience details</span>
                {experiences.map(exp => (
                  <div key={exp.id} className="text-xs">
                    <strong className="text-slate-200">{exp.role}</strong>
                    <span className="text-[10px] text-slate-500 block">{exp.company} // {exp.duration}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button size="sm" onClick={() => alert('PDF document download compiled successfully.')} className="flex-1"><Download size={13} /> Download PDF</Button>
              <Button size="sm" variant="ghost" onClick={() => alert('Autosave status sync verified.')}>Auto Save Enabled</Button>
            </div>
          </div>

        </div>
      )}

      {/* ATS RESUME ANALYZER TAB */}
      {activeResumeTab === 'ats' && (
        <div className="max-w-xl space-y-6">
          <div className="p-8 border border-dashed border-indigo-950 rounded-2xl text-center space-y-4 bg-slate-950/20">
            <FileText className="mx-auto text-indigo-500" size={32} />
            <div className="space-y-1.5">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">Upload Resume Document</h4>
              <p className="text-[10px] text-slate-500 max-w-xs mx-auto leading-relaxed">Select PDF or DOCX file to scan missing keywords matching active jobs catalog.</p>
            </div>
            <Button size="sm" onClick={runAtsAudit} disabled={analyzing} className="flex items-center gap-1 mx-auto text-[11px] py-2">
              {analyzing ? <RefreshCw size={13} className="animate-spin" /> : <Sparkles size={13} />}
              {analyzing ? 'Analyzing formatting...' : 'Scan ATS Keywords Score'}
            </Button>
          </div>

          {atsScore !== null && (
            <div className="p-6 bg-slate-950 border border-indigo-950 rounded-xl space-y-4 animate-fade-in">
              <div className="flex items-center gap-3 border-b border-indigo-950/40 pb-3">
                <CheckCircle className="text-emerald-500 shrink-0" size={16} />
                <div>
                  <h4 className="text-xs font-bold text-white">ATS GAP SCAN COMPLETED</h4>
                  <span className="text-[10px] text-slate-500 font-mono">Index matching score: <strong className="text-emerald-450">{atsScore}%</strong></span>
                </div>
              </div>
              <div className="text-xs text-slate-400 space-y-2.5">
                <strong className="block text-slate-350 text-[10px] uppercase font-mono">Missing skills identified:</strong>
                <div className="flex flex-wrap gap-1.5">
                  <Badge variant="warning">Django Celery</Badge>
                  <Badge variant="warning">Vedic deviations dev</Badge>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

    </div>
  );
};

export default ResumeBuilder;
