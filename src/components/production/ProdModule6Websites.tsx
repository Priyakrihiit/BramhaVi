/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  Layout,
  Globe,
  Settings,
  BarChart,
  Grid,
  CheckCircle,
  Eye,
  Settings2,
  Lock,
  Plus,
  RefreshCw,
  Trash2
} from 'lucide-react';

interface WebsiteTemplate {
  id: string;
  name: string;
  category: 'PORTFOLIO' | 'BUSINESS' | 'AGENCY' | 'MANUFACTURING' | 'ECOMMERCE' | 'LANDING' | 'BLOG';
  theme: string;
  pagesCount: number;
}

export const ProdModule6Websites: React.FC = () => {
  const [websites, setWebsites] = useState([
    { id: 'web-01', name: 'Priya Pandey Portfolio', category: 'PORTFOLIO', domain: 'portfolio.bvgalaxy.com', status: 'LIVE', customDomain: 'priyapandey.dev', ssl: 'ACTIVE' },
    { id: 'web-02', name: 'Pune Vedic Tech Agency', category: 'AGENCY', domain: 'vedictech.bvgalaxy.com', status: 'LIVE', customDomain: 'vedictech.pune.in', ssl: 'ACTIVE' }
  ]);

  const [activeWebsiteId, setActiveWebsiteId] = useState<string>('web-01');
  const [activeSection, setActiveSection] = useState<'templates' | 'seo' | 'domain' | 'analytics'>('templates');

  const [seoTitle, setSeoTitle] = useState<string>('Priya Pandey | Full-Stack BrahmaVidya AI Architect');
  const [seoDesc, setSeoDesc] = useState<string>('Personal academic portfolio showcasing machine learning systems, certifications, and research publications.');
  const [customDomainInput, setCustomDomainInput] = useState<string>('');
  const [sslStatus, setSslStatus] = useState<'NONE' | 'PENDING' | 'ACTIVE'>('NONE');

  const templates: WebsiteTemplate[] = [
    { id: 't-01', name: 'Cosmic Minimal', category: 'PORTFOLIO', theme: 'Slate / Dark', pagesCount: 4 },
    { id: 't-02', name: 'Corporate Grid', category: 'BUSINESS', theme: 'Indigo / White', pagesCount: 6 },
    { id: 't-03', name: 'Product Landing', category: 'LANDING', theme: 'Emerald / Minimal', pagesCount: 1 },
    { id: 't-04', name: 'Vedic Scholar Blog', category: 'BLOG', theme: 'Amber / Editorial', pagesCount: 12 },
    { id: 't-05', name: 'B2B Manufacturing Suite', category: 'MANUFACTURING', theme: 'Steel / Dark', pagesCount: 8 }
  ];

  const triggerSSLVerification = () => {
    if (!customDomainInput) return;
    setSslStatus('PENDING');
    setTimeout(() => {
      setSslStatus('ACTIVE');
      setWebsites(websites.map(w => {
        if (w.id === activeWebsiteId) {
          return { ...w, customDomain: customDomainInput, ssl: 'ACTIVE' };
        }
        return w;
      }));
    }, 1500);
  };

  const activeWeb = websites.find(w => w.id === activeWebsiteId) || websites[0];

  return (
    <div id="website-builder-root" className="space-y-6">
      {/* Site Selector Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-slate-950/40 p-4 rounded-xl border border-slate-900 text-left">
        <div>
          <span className="text-[9px] bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded border border-indigo-950 font-mono">
            WEBSITE BUILDER PRO
          </span>
          <h3 className="text-sm font-black text-white mt-1">Active Site: {activeWeb.name}</h3>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={activeWebsiteId}
            onChange={(e) => setActiveWebsiteId(e.target.value)}
            className="bg-[#0f172a] border border-indigo-950 text-xs text-indigo-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-sans"
          >
            {websites.map(w => (
              <option key={w.id} value={w.id}>{w.name}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 text-left">
        {/* Left Side: Builder Category Tabs */}
        <div className="lg:col-span-3 space-y-2">
          <button
            onClick={() => setActiveSection('templates')}
            className={`w-full p-3 rounded-xl border text-left transition flex items-center gap-2.5 font-sans ${activeSection === 'templates' ? 'bg-indigo-950/60 border-indigo-500/80 text-white font-bold' : 'bg-slate-950/60 border-slate-900 text-slate-400 hover:border-slate-800'}`}
          >
            <Grid className="w-4.5 h-4.5 text-indigo-400" />
            <span className="text-xs">Templates & Layouts</span>
          </button>
          <button
            onClick={() => setActiveSection('seo')}
            className={`w-full p-3 rounded-xl border text-left transition flex items-center gap-2.5 font-sans ${activeSection === 'seo' ? 'bg-indigo-950/60 border-indigo-500/80 text-white font-bold' : 'bg-slate-950/60 border-slate-900 text-slate-400 hover:border-slate-800'}`}
          >
            <Settings2 className="w-4.5 h-4.5 text-indigo-400" />
            <span className="text-xs">SEO & Metadata</span>
          </button>
          <button
            onClick={() => setActiveSection('domain')}
            className={`w-full p-3 rounded-xl border text-left transition flex items-center gap-2.5 font-sans ${activeSection === 'domain' ? 'bg-indigo-950/60 border-indigo-500/80 text-white font-bold' : 'bg-slate-950/60 border-slate-900 text-slate-400 hover:border-slate-800'}`}
          >
            <Globe className="w-4.5 h-4.5 text-indigo-400" />
            <span className="text-xs">Custom Domains & SSL</span>
          </button>
          <button
            onClick={() => setActiveSection('analytics')}
            className={`w-full p-3 rounded-xl border text-left transition flex items-center gap-2.5 font-sans ${activeSection === 'analytics' ? 'bg-indigo-950/60 border-indigo-500/80 text-white font-bold' : 'bg-slate-950/60 border-slate-900 text-slate-400 hover:border-slate-800'}`}
          >
            <BarChart className="w-4.5 h-4.5 text-indigo-400" />
            <span className="text-xs">Live Site Analytics</span>
          </button>
        </div>

        {/* Right Side: Tab Panel Content */}
        <div className="lg:col-span-9 bg-slate-950/40 border border-indigo-950/30 rounded-xl p-5 space-y-4">
          {activeSection === 'templates' && (
            <div className="space-y-4">
              <div className="border-b border-slate-900 pb-2">
                <h4 className="text-xs font-black text-white uppercase tracking-wider font-mono">Available Mobile-Responsive Templates</h4>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {templates.map(tmpl => (
                  <div key={tmpl.id} className="bg-[#050914] border border-slate-900 rounded-xl p-4 flex flex-col justify-between hover:border-indigo-950/80 transition">
                    <div className="space-y-1">
                      <span className="text-[8px] bg-indigo-500/10 text-indigo-400 px-1.5 py-0.5 rounded border border-indigo-950 font-mono font-bold uppercase">
                        {tmpl.category}
                      </span>
                      <h5 className="text-xs font-black text-slate-200 mt-2">{tmpl.name}</h5>
                      <p className="text-[10px] text-slate-500 font-sans mt-1">Theme Colors: {tmpl.theme} • Pages: {tmpl.pagesCount}</p>
                    </div>
                    <div className="mt-4 pt-3 border-t border-slate-900 flex justify-between items-center">
                      <span className="text-[9px] text-slate-600 font-mono">ID: {tmpl.id}</span>
                      <button className="bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 hover:text-indigo-300 px-3 py-1 text-[10px] rounded-lg transition font-bold font-sans">
                        Apply Template
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeSection === 'seo' && (
            <div className="space-y-4">
              <div className="border-b border-slate-900 pb-2">
                <h4 className="text-xs font-black text-white uppercase tracking-wider font-mono">SEO Optimization & Meta Tag Injections</h4>
              </div>

              <div className="space-y-3">
                <div className="space-y-1">
                  <label className="text-[10px] text-slate-400 font-mono font-bold">Meta Title Tag</label>
                  <input
                    type="text"
                    value={seoTitle}
                    onChange={(e) => setSeoTitle(e.target.value)}
                    className="w-full bg-[#050914] border border-indigo-950 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-sans"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] text-slate-400 font-mono font-bold">Meta Description Tag</label>
                  <textarea
                    value={seoDesc}
                    onChange={(e) => setSeoDesc(e.target.value)}
                    className="w-full bg-[#050914] border border-indigo-950 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-sans h-20 resize-none"
                  />
                </div>

                <button className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold font-sans px-4 py-2 rounded-lg transition">
                  Save Meta Tags
                </button>
              </div>
            </div>
          )}

          {activeSection === 'domain' && (
            <div className="space-y-4">
              <div className="border-b border-slate-900 pb-2">
                <h4 className="text-xs font-black text-white uppercase tracking-wider font-mono">Custom Domain Mapping & SSL Seals</h4>
              </div>

              <div className="bg-[#050914] border border-slate-900 rounded-xl p-4 space-y-4">
                <div className="flex justify-between text-xs border-b border-slate-900 pb-2">
                  <span className="text-slate-500">Subdomain URL:</span>
                  <span className="text-indigo-400 font-bold font-mono">{activeWeb.domain}</span>
                </div>

                {activeWeb.customDomain ? (
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-500">Mapped Custom Domain:</span>
                    <span className="text-emerald-400 font-bold font-mono">{activeWeb.customDomain} (SSL Active)</span>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="space-y-1">
                      <label className="text-[10px] text-slate-400 font-mono font-bold">Add Custom Domain (e.g. priyapandey.dev)</label>
                      <input
                        type="text"
                        placeholder="yourdomain.com"
                        value={customDomainInput}
                        onChange={(e) => setCustomDomainInput(e.target.value)}
                        className="w-full bg-slate-950 border border-indigo-950 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
                      />
                    </div>

                    <button
                      onClick={triggerSSLVerification}
                      className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold font-sans px-3.5 py-1.5 rounded-lg transition"
                    >
                      Map Domain & Provision Free Let's Encrypt SSL
                    </button>
                  </div>
                )}

                {sslStatus === 'PENDING' && (
                  <div className="p-3 bg-indigo-950/30 border border-indigo-900 rounded-lg text-xs text-indigo-400 animate-pulse">
                    Generating ACME challenge files & verifying DNS CNAME records...
                  </div>
                )}
              </div>
            </div>
          )}

          {activeSection === 'analytics' && (
            <div className="space-y-4">
              <div className="border-b border-slate-900 pb-2">
                <h4 className="text-xs font-black text-white uppercase tracking-wider font-mono">Real-time Traffic & Performance</h4>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="bg-[#050914] p-3 rounded-lg border border-slate-900">
                  <p className="text-[10px] text-slate-500">Monthly Pageviews</p>
                  <p className="text-sm font-bold text-slate-200 mt-1 font-mono">14,204 Visitors</p>
                </div>
                <div className="bg-[#050914] p-3 rounded-lg border border-slate-900">
                  <p className="text-[10px] text-slate-500">Average Session Time</p>
                  <p className="text-sm font-bold text-slate-200 mt-1 font-mono">3 Mins 42 Secs</p>
                </div>
                <div className="bg-[#050914] p-3 rounded-lg border border-slate-900">
                  <p className="text-[10px] text-slate-500">SEO Score (Lighthouse)</p>
                  <p className="text-sm font-bold text-emerald-400 mt-1 font-mono">100 / 100</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProdModule6Websites;
