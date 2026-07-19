/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { useLayoutStore } from '../../stores/layoutStore';
import { useAuthStore } from '../../stores/authStore';
import { Button } from '../../components/DesignSystem';
import { LayoutGrid, FileText, ChevronRight, Star, Heart, Monitor, ArrowRight } from 'lucide-react';

export const TemplatesPage: React.FC = () => {
  const { currentPath, navigateTo } = useLayoutStore();
  const { currentUser } = useAuthStore();

  const isPortfolio = currentPath === '/portfolio';

  const portfolios = [
    { name: 'Creative Developer Showcase', desc: 'Glassmorphism layout with terminal CLI visual cards, smooth slider carousels, and responsive layouts.', rating: 4.9, count: 1205 },
    { name: 'Minimalist Consultant Outline', desc: 'Clean white/dark theme typography ideal for freelance consultants and technical copywriters.', rating: 4.8, count: 654 },
    { name: 'Corporate Business Agency', desc: 'Rich landing pages, service outlines cards, client milestone forms, and dynamic payment links.', rating: 4.7, count: 832 },
  ];

  const resumes = [
    { name: 'ATS-Optimized Executive', desc: 'Engineered specifically for corporate parsing parsers. Single-column, clear section grids.', rating: 5.0, count: 2405 },
    { name: 'Academic Curriculum Vitae', desc: 'Multi-page formal layout for research abstracts, publications list, and educational projects.', rating: 4.9, count: 1402 },
    { name: 'Modern Functional Blueprint', desc: 'Focuses heavily on skills taxonomy and dynamic capabilities profiles rather than dates.', rating: 4.8, count: 902 },
  ];

  const handleUseTemplate = (tempName: string) => {
    if (!currentUser) {
      alert('Authentication required to clone builders templates. Redirecting to login desk...');
      navigateTo('/auth');
    } else {
      alert(`Cloned template "${tempName}" into your active workspace dashboard.`);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-[#070b19]">
      {/* Hero Header */}
      <section className="relative py-16 px-8 text-left border-b border-indigo-950/40">
        <div className="absolute top-1/4 left-1/4 w-[300px] h-[300px] bg-indigo-650/10 rounded-full blur-[100px] pointer-events-none"></div>
        <div className="max-w-4xl mx-auto space-y-4">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest font-mono">
            {isPortfolio ? 'WEBSITE BUILDER TEMPLATES' : 'RESUME BUILDER LAYOUTS'}
          </span>
          <h1 className="text-3xl font-black text-white tracking-tight">
            {isPortfolio ? 'Portfolio Templates Gallery' : 'ATS Resume Templates'}
          </h1>
          <p className="text-slate-400 text-xs max-w-lg leading-relaxed">
            {isPortfolio 
              ? 'Choose a premium template layout to bootstrap your personal, developer, consultant, or business website instantly.'
              : 'Pick an ATS-compliant, recruiter-approved resume outline to build your career document and start analyzing gaps with AI.'
            }
          </p>
        </div>
      </section>

      {/* Templates Grid */}
      <section className="py-16 px-6 max-w-5xl mx-auto w-full text-left">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {(isPortfolio ? portfolios : resumes).map((temp, idx) => (
            <div 
              key={idx}
              className="bg-slate-900 border border-indigo-950 rounded-2xl flex flex-col justify-between overflow-hidden hover:border-indigo-900 transition duration-200"
            >
              <div className="p-5 space-y-3">
                <div className="aspect-[16/10] w-full bg-slate-950/60 border border-indigo-950 rounded-xl flex items-center justify-center relative overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-tr from-indigo-900/10 via-slate-950 to-indigo-900/10"></div>
                  {isPortfolio ? <Monitor size={24} className="text-indigo-500/50" /> : <FileText size={24} className="text-indigo-500/50" />}
                </div>
                <h4 className="text-sm font-bold text-white leading-snug">{temp.name}</h4>
                <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed">{temp.desc}</p>
              </div>
              <div className="p-4 border-t border-indigo-950/40 bg-slate-900/60 flex justify-between items-center text-[10px] text-slate-500 font-mono">
                <div className="flex items-center gap-1 text-amber-400">
                  <Star size={11} fill="currentColor" />
                  <span>{temp.rating}</span>
                </div>
                <button
                  onClick={() => handleUseTemplate(temp.name)}
                  className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-0.5 transition cursor-pointer"
                >
                  Use Template <ChevronRight size={13} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default TemplatesPage;
