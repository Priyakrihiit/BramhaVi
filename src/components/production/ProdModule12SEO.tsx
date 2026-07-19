/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import {
  Search,
  Eye,
  FileText,
  Code,
  CheckCircle,
  Copy,
  TrendingUp,
  Globe
} from 'lucide-react';

export const ProdModule12SEO: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'opengraph' | 'sitemap' | 'schema' | 'robots'>('opengraph');
  const [copied, setCopied] = useState<boolean>(false);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const xmlSitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://bvgalaxy.com/</loc>
    <lastmod>2026-07-07</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://bvgalaxy.com/courses</loc>
    <lastmod>2026-07-07</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://bvgalaxy.com/saas</loc>
    <lastmod>2026-07-07</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>`;

  const schemaJsonLd = `{
  "@context": "https://schema.org",
  "@type": "EducationalOrganization",
  "name": "BrahmaVidya Galaxy Platform",
  "url": "https://bvgalaxy.com",
  "logo": "https://bvgalaxy.com/logo.png",
  "description": "Multi-tier SaaS platform and LMS ecosystem",
  "sameAs": [
    "https://twitter.com/bvgalaxy",
    "https://github.com/bvgalaxy"
  ]
}`;

  return (
    <div id="seo-engine-root" className="space-y-6">
      {/* Sub Tabs */}
      <div className="flex border-b border-slate-900 pb-3 gap-2">
        <button
          onClick={() => setActiveTab('opengraph')}
          className={`px-4 py-1.5 rounded-lg text-xs font-bold font-sans transition ${activeTab === 'opengraph' ? 'bg-indigo-600 text-white' : 'bg-slate-900/40 text-slate-400 hover:bg-slate-900'}`}
        >
          OpenGraph Previews
        </button>
        <button
          onClick={() => setActiveTab('sitemap')}
          className={`px-4 py-1.5 rounded-lg text-xs font-bold font-sans transition ${activeTab === 'sitemap' ? 'bg-indigo-600 text-white' : 'bg-slate-900/40 text-slate-400 hover:bg-slate-900'}`}
        >
          XML Sitemap Generator
        </button>
        <button
          onClick={() => setActiveTab('schema')}
          className={`px-4 py-1.5 rounded-lg text-xs font-bold font-sans transition ${activeTab === 'schema' ? 'bg-indigo-600 text-white' : 'bg-slate-900/40 text-slate-400 hover:bg-slate-900'}`}
        >
          Schema.org JSON-LD
        </button>
        <button
          onClick={() => setActiveTab('robots')}
          className={`px-4 py-1.5 rounded-lg text-xs font-bold font-sans transition ${activeTab === 'robots' ? 'bg-indigo-600 text-white' : 'bg-slate-900/40 text-slate-400 hover:bg-slate-900'}`}
        >
          Robots.txt
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 text-left">
        {/* Tab content panel */}
        <div className="lg:col-span-8 bg-[#050914] border border-indigo-950/40 rounded-xl p-5 space-y-4">
          {activeTab === 'opengraph' && (
            <div className="space-y-4">
              <div className="border-b border-slate-900 pb-2 flex justify-between items-center">
                <span className="text-xs font-bold text-slate-300 font-sans">OpenGraph Preview Card</span>
                <span className="text-[10px] bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded font-mono">SOCIAL META TAGS</span>
              </div>

              {/* Simulated Social Share Preview */}
              <div className="bg-slate-950/60 rounded-xl overflow-hidden border border-slate-900 max-w-md mx-auto">
                <div className="bg-gradient-to-r from-slate-900 to-indigo-950 h-32 flex items-center justify-center p-4">
                  <h3 className="text-sm font-black text-white font-sans text-center">BrahmaVidya Galaxy Platform</h3>
                </div>
                <div className="p-4 text-left space-y-1 bg-[#0b1329]">
                  <span className="text-[9px] text-indigo-400 font-mono tracking-wider">BVGALAXY.COM</span>
                  <h5 className="text-xs font-bold text-white">Full-Stack SaaS Platform & CMS LMS Engine</h5>
                  <p className="text-[10px] text-slate-400 line-clamp-2">
                    Connect multiple tenants, deploy custom sites, configure Celery workflows, and run double-entry ledgers instantly.
                  </p>
                </div>
              </div>

              <div className="space-y-2 pt-2">
                <span className="text-[10px] text-slate-500 font-mono">Rendered Meta Tags</span>
                <pre className="bg-slate-950 p-3 rounded-lg border border-slate-900 text-[10px] text-slate-400 font-mono leading-relaxed overflow-x-auto">
{`<meta property="og:title" content="BrahmaVidya Galaxy Platform" />
<meta property="og:description" content="Multi-tenant full-stack SaaS platform" />
<meta property="og:image" content="https://bvgalaxy.com/banner.png" />
<meta property="og:url" content="https://bvgalaxy.com" />`}
                </pre>
              </div>
            </div>
          )}

          {activeTab === 'sitemap' && (
            <div className="space-y-3">
              <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                <span className="text-xs font-bold text-slate-300 font-sans">Sitemap XML Content</span>
                <button
                  onClick={() => copyToClipboard(xmlSitemap)}
                  className="text-[10px] text-slate-400 hover:text-indigo-400 flex items-center gap-1 font-mono"
                >
                  {copied ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  Copy Sitemap
                </button>
              </div>
              <pre className="bg-slate-950 border border-slate-900 rounded-lg p-3.5 font-mono text-[10px] text-slate-300 overflow-x-auto leading-normal">
                {xmlSitemap}
              </pre>
            </div>
          )}

          {activeTab === 'schema' && (
            <div className="space-y-3">
              <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                <span className="text-xs font-bold text-slate-300 font-sans">Schema JSON-LD Snippet</span>
                <button
                  onClick={() => copyToClipboard(schemaJsonLd)}
                  className="text-[10px] text-slate-400 hover:text-indigo-400 flex items-center gap-1 font-mono"
                >
                  {copied ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  Copy JSON-LD
                </button>
              </div>
              <pre className="bg-slate-950 border border-slate-900 rounded-lg p-3.5 font-mono text-[10px] text-indigo-300 overflow-x-auto leading-normal">
                {schemaJsonLd}
              </pre>
            </div>
          )}

          {activeTab === 'robots' && (
            <div className="space-y-3">
              <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                <span className="text-xs font-bold text-slate-300 font-sans">Robots Rules (robots.txt)</span>
              </div>
              <pre className="bg-slate-950 border border-slate-900 rounded-lg p-3.5 font-mono text-[10px] text-slate-300 leading-normal">
{`# robots.txt for BrahmaVidya Galaxy Platform
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/v1/mobile/downloads/

Sitemap: https://bvgalaxy.com/sitemap.xml`}
              </pre>
            </div>
          )}
        </div>

        {/* Dynamic SEO Tools Panel */}
        <div className="lg:col-span-4 bg-slate-950/40 border border-slate-900 rounded-xl p-4 flex flex-col justify-between h-full min-h-[280px]">
          <div className="space-y-4">
            <div className="flex items-center gap-1.5 border-b border-slate-900 pb-2 text-slate-300">
              <TrendingUp className="w-4 h-4 text-indigo-400" />
              <span className="text-xs font-bold font-sans uppercase tracking-wider font-mono">Dynamic SEO Health</span>
            </div>

            <div className="space-y-3 text-xs leading-relaxed">
              <div className="flex justify-between p-2.5 bg-slate-950 rounded-lg border border-slate-900">
                <span className="text-slate-400 font-sans">Sitemap Validated</span>
                <span className="text-emerald-400 font-mono font-bold">100% OK</span>
              </div>
              <div className="flex justify-between p-2.5 bg-slate-950 rounded-lg border border-slate-900">
                <span className="text-slate-400 font-sans">Schema.org Score</span>
                <span className="text-emerald-400 font-mono font-bold">EXCELLENT</span>
              </div>
              <div className="flex justify-between p-2.5 bg-slate-950 rounded-lg border border-slate-900">
                <span className="text-slate-400 font-sans">Canonical URLs Check</span>
                <span className="text-emerald-400 font-mono font-bold">PASSED</span>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-900 mt-4">
            <p className="text-[10px] text-slate-500 leading-normal">
              Dynamic headers are automatically compiled on server request using our optimized Nginx configs.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProdModule12SEO;
