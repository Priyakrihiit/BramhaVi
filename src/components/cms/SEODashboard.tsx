import React, { useEffect, useState } from 'react';
import { ShieldCheck, Sparkles, Globe } from 'lucide-react';

export const SEODashboard: React.FC = () => {
  return (
    <div className="p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-6">
      <div>
        <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">SEO Integration Controls</h3>
        <p className="text-xs text-slate-500">Track and optimize search engine indexes, sitemaps, and meta parameters</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-4 bg-slate-950 border border-slate-850 rounded-xl space-y-3">
          <div className="flex items-center gap-2 text-indigo-400">
            <Globe size={18} />
            <h4 className="text-xs font-bold uppercase tracking-wider font-mono">Sitemap & Meta Ticker</h4>
          </div>
          <p className="text-[11px] text-slate-400">
            Automated sitemap compilation is enabled. Each time a CMS page or Article is published,
            the backend SEO platform builds unique sitemap XML trees.
          </p>
          <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono border-t border-slate-900 pt-2">
            <span>SITEMAP ENDPOINT</span>
            <span className="text-indigo-400">/sitemap.xml</span>
          </div>
        </div>

        <div className="p-4 bg-slate-950 border border-slate-850 rounded-xl space-y-3">
          <div className="flex items-center gap-2 text-purple-400">
            <Sparkles size={18} />
            <h4 className="text-xs font-bold uppercase tracking-wider font-mono">AI Meta Generator</h4>
          </div>
          <p className="text-[11px] text-slate-400">
            Integrated with Gemini models to construct recommended keywords, descriptions, and sitemap
            meta-tags on Article updates.
          </p>
          <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono border-t border-slate-900 pt-2">
            <span>LLM AUTOSYNC</span>
            <span className="text-emerald-400">ONLINE</span>
          </div>
        </div>
      </div>
    </div>
  );
};
