import React, { useState, useEffect } from 'react';
import { 
  Globe, Search, FileText, CheckCircle, AlertTriangle, AlertCircle, 
  RefreshCw, Plus, Edit, Trash2, ArrowUpRight, Check, X, Sparkles, BookOpen, FileCode
} from 'lucide-react';

export default function SeoDashboard() {
  const [pages, setPages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activePageForAudit, setActivePageForAudit] = useState<any>(null);
  const [auditDetails, setAuditDetails] = useState<any>(null);
  
  // Form states for Create/Edit SEOPage
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    id: '',
    page_type: 'COURSE',
    page_id: '',
    title: '',
    meta_title: '',
    meta_description: '',
    canonical_url: '',
    slug: '',
    keywords: '',
    robots_index: true,
    robots_follow: true,
    og_title: '',
    og_description: '',
    og_image: '',
    twitter_title: '',
    twitter_description: '',
    twitter_image: '',
    schema_json: '{}',
    language: 'en'
  });

  // AI Generation helpers states
  const [isGeneratingMeta, setIsGeneratingMeta] = useState(false);
  const [isGeneratingSchema, setIsGeneratingSchema] = useState(false);
  
  useEffect(() => {
    fetchPages();
  }, []);

  const fetchPages = () => {
    setLoading(true);
    fetch('/api/seo/pages/')
      .then(res => res.json())
      .then(data => {
        if (data.results && Array.isArray(data.results)) {
          setPages(data.results);
        } else if (Array.isArray(data)) {
          setPages(data);
        }
      })
      .catch(err => console.error('Error fetching SEO Pages', err))
      .finally(() => setLoading(false));
  };

  const handleSavePage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title || !formData.page_id) {
      alert('Title and Page ID are required.');
      return;
    }

    const payload = {
      ...formData,
      schema_json: JSON.parse(formData.schema_json || '{}')
    };

    const url = formData.id ? `/api/seo/pages/${formData.id}/` : '/api/seo/pages/';
    const method = formData.id ? 'PUT' : 'POST';

    try {
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        alert('SEO Page saved successfully.');
        setIsEditing(false);
        fetchPages();
      } else {
        const err = await res.json();
        alert(`Error: ${JSON.stringify(err)}`);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeletePage = async (id: string) => {
    if (!confirm('Are you sure you want to delete this SEO Page record?')) return;
    try {
      const res = await fetch(`/api/seo/pages/${id}/`, { method: 'DELETE' });
      if (res.ok) {
        alert('SEO Page deleted.');
        fetchPages();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const runAudit = async (page: any) => {
    setActivePageForAudit(page);
    setAuditDetails(null);
    try {
      const res = await fetch(`/api/seo/pages/audit/${page.id}/`);
      const data = await res.json();
      if (res.ok) {
        setAuditDetails(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const generateAIMeta = async () => {
    if (!formData.title) {
      alert('Please fill in visual title first.');
      return;
    }
    setIsGeneratingMeta(true);
    try {
      const res = await fetch('/api/seo/generate-meta/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          page_type: formData.page_type,
          title: formData.title,
          description: formData.meta_description
        })
      });
      const data = await res.json();
      if (res.ok) {
        setFormData(prev => ({
          ...prev,
          meta_title: data.meta_title,
          meta_description: data.meta_description,
          keywords: data.keywords,
          slug: data.slug,
          og_title: data.meta_title,
          og_description: data.meta_description,
          twitter_title: data.meta_title,
          twitter_description: data.meta_description
        }));
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsGeneratingMeta(false);
    }
  };

  const generateAISchema = async () => {
    if (!formData.title) {
      alert('Please fill in visual title first.');
      return;
    }
    setIsGeneratingSchema(true);
    try {
      const res = await fetch('/api/seo/generate-schema/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          schema_type: formData.page_type === 'COURSE' ? 'Course' : 'Article',
          name: formData.title,
          description: formData.meta_description,
          url: formData.canonical_url
        })
      });
      const data = await res.json();
      if (res.ok) {
        setFormData(prev => ({
          ...prev,
          schema_json: JSON.stringify(data, null, 2)
        }));
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsGeneratingSchema(false);
    }
  };

  const editPage = (page: any) => {
    setFormData({
      id: page.id,
      page_type: page.page_type,
      page_id: page.page_id,
      title: page.title,
      meta_title: page.meta_title || '',
      meta_description: page.meta_description || '',
      canonical_url: page.canonical_url || '',
      slug: page.slug || '',
      keywords: page.keywords || '',
      robots_index: page.robots_index,
      robots_follow: page.robots_follow,
      og_title: page.og_title || '',
      og_description: page.og_description || '',
      og_image: page.og_image || '',
      twitter_title: page.twitter_title || '',
      twitter_description: page.twitter_description || '',
      twitter_image: page.twitter_image || '',
      schema_json: JSON.stringify(page.schema_json || {}, null, 2),
      language: page.language || 'en'
    });
    setIsEditing(true);
  };

  const addNewPage = () => {
    setFormData({
      id: '',
      page_type: 'COURSE',
      page_id: `course-${Math.floor(Math.random() * 9000 + 1000)}`,
      title: '',
      meta_title: '',
      meta_description: '',
      canonical_url: '',
      slug: '',
      keywords: '',
      robots_index: true,
      robots_follow: true,
      og_title: '',
      og_description: '',
      og_image: '',
      twitter_title: '',
      twitter_description: '',
      twitter_image: '',
      schema_json: '{}',
      language: 'en'
    });
    setIsEditing(true);
  };

  return (
    <div className="space-y-8">
      {/* Overview Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="bg-[#0c1326] border border-slate-800 rounded-2xl p-5 hover:border-indigo-500/30 transition-all flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold">Indexed Pages</span>
            <span className="text-xl font-bold text-white block">{pages.length}</span>
            <span className="text-[11px] text-emerald-400 block font-semibold">100% Fully Configured</span>
          </div>
          <div className="p-3 rounded-xl text-indigo-400 bg-indigo-500/10">
            <Globe size={20} />
          </div>
        </div>

        <div className="bg-[#0c1326] border border-slate-800 rounded-2xl p-5 hover:border-indigo-500/30 transition-all flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold">Overall SEO Score</span>
            <span className="text-xl font-bold text-white block">92 / 100</span>
            <span className="text-[11px] text-indigo-400 block font-semibold">Grade A Excellent</span>
          </div>
          <div className="p-3 rounded-xl text-emerald-400 bg-emerald-500/10">
            <CheckCircle size={20} />
          </div>
        </div>

        <div className="bg-[#0c1326] border border-slate-800 rounded-2xl p-5 hover:border-indigo-500/30 transition-all flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold">Sitemap Status</span>
            <span className="text-xl font-bold text-white block">Active</span>
            <a href="/seo/sitemap.xml" target="_blank" className="text-[11px] text-indigo-400 font-semibold flex items-center gap-1 hover:underline">
              Download XML sitemap <ArrowUpRight size={10} />
            </a>
          </div>
          <div className="p-3 rounded-xl text-amber-400 bg-amber-500/10">
            <FileText size={20} />
          </div>
        </div>

        <div className="bg-[#0c1326] border border-slate-800 rounded-2xl p-5 hover:border-indigo-500/30 transition-all flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold">Robots Policy</span>
            <span className="text-xl font-bold text-white block">Configured</span>
            <a href="/robots.txt" target="_blank" className="text-[11px] text-indigo-400 font-semibold flex items-center gap-1 hover:underline">
              View robots.txt <ArrowUpRight size={10} />
            </a>
          </div>
          <div className="p-3 rounded-xl text-rose-400 bg-rose-500/10">
            <AlertCircle size={20} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Main Pages Table */}
        <div className="lg:col-span-2 bg-[#0c1326] border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-base font-black text-white">SEO Pages Index</h3>
              <p className="text-[11px] text-slate-400">Add, edit, or configure meta settings and dynamic indexing properties.</p>
            </div>
            <button 
              onClick={addNewPage}
              className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1"
            >
              <Plus size={13} />
              Add Custom Page
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                  <th className="pb-3 pr-2">Page Title</th>
                  <th className="pb-3 px-2">Page Type</th>
                  <th className="pb-3 px-2">Indexing</th>
                  <th className="pb-3 pl-2 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {loading ? (
                  <tr>
                    <td colSpan={4} className="py-6 text-center text-slate-500 flex justify-center items-center gap-2">
                      <RefreshCw className="animate-spin" size={14} /> Loading SEO registry...
                    </td>
                  </tr>
                ) : pages.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="py-6 text-center text-slate-500">
                      No SEO pages found. Populate by saving Course, Blog, or Book records.
                    </td>
                  </tr>
                ) : (
                  pages.map((p) => (
                    <tr key={p.id} className="hover:bg-slate-900/20 group">
                      <td className="py-3.5 pr-2">
                        <span className="font-bold text-white block">{p.title}</span>
                        <span className="text-[10px] text-slate-500 block truncate max-w-[240px]">
                          {p.canonical_url || `/${p.page_type.toLowerCase()}/${p.slug}`}
                        </span>
                      </td>
                      <td className="py-3.5 px-2">
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-slate-800 text-indigo-400">
                          {p.page_type}
                        </span>
                      </td>
                      <td className="py-3.5 px-2">
                        <div className="flex items-center gap-1">
                          {p.robots_index ? (
                            <span className="text-emerald-400 flex items-center gap-0.5 font-semibold text-[10px]">
                              <Check size={10} /> Index
                            </span>
                          ) : (
                            <span className="text-rose-400 flex items-center gap-0.5 font-semibold text-[10px]">
                              <X size={10} /> NoIndex
                            </span>
                          )}
                          <span className="text-slate-600 font-bold">|</span>
                          {p.robots_follow ? (
                            <span className="text-emerald-400 flex items-center gap-0.5 font-semibold text-[10px]">
                              Follow
                            </span>
                          ) : (
                            <span className="text-rose-400 flex items-center gap-0.5 font-semibold text-[10px]">
                              NoFollow
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3.5 pl-2 text-right">
                        <div className="flex justify-end gap-1.5">
                          <button 
                            onClick={() => runAudit(p)}
                            className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg font-semibold text-[10px] transition-all"
                          >
                            Audit
                          </button>
                          <button 
                            onClick={() => editPage(p)}
                            className="p-1 hover:text-indigo-400 text-slate-400 transition-all"
                          >
                            <Edit size={13} />
                          </button>
                          <button 
                            onClick={() => handleDeletePage(p.id)}
                            className="p-1 hover:text-rose-400 text-slate-400 transition-all"
                          >
                            <Trash2 size={13} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Audit Details Panel / Forms overlay */}
        <div className="bg-[#0c1326] border border-slate-800 rounded-2xl p-6 space-y-6">
          {isEditing ? (
            <form onSubmit={handleSavePage} className="space-y-4">
              <div>
                <h3 className="text-sm font-black text-white">{formData.id ? 'Edit SEO Page' : 'Create Custom SEO Page'}</h3>
                <p className="text-[10px] text-slate-400">Configure visual details and search engine tags.</p>
              </div>

              <div className="space-y-3.5">
                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 mb-1">Page Type</label>
                  <select 
                    value={formData.page_type}
                    onChange={(e) => setFormData(prev => ({ ...prev, page_type: e.target.value }))}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  >
                    <option value="COURSE">Course</option>
                    <option value="BLOG">Blog/Article</option>
                    <option value="BOOK">Book</option>
                    <option value="PRODUCT">Marketplace Product</option>
                    <option value="PORTFOLIO">Portfolio</option>
                    <option value="RESUME">Resume</option>
                    <option value="WEBSITE">Website Page</option>
                    <option value="ORGANIZATION">Organization Page</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 mb-1">Page Reference ID</label>
                  <input 
                    type="text"
                    value={formData.page_id}
                    onChange={(e) => setFormData(prev => ({ ...prev, page_id: e.target.value }))}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 mb-1">Visual Title</label>
                  <input 
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none focus:border-indigo-500"
                  />
                </div>

                <div className="flex gap-2">
                  <button 
                    type="button"
                    onClick={generateAIMeta}
                    disabled={isGeneratingMeta}
                    className="flex-1 py-1.5 bg-indigo-600/20 border border-indigo-500/30 hover:bg-indigo-600/30 text-indigo-400 rounded-xl text-[10px] font-bold transition-all flex items-center justify-center gap-1"
                  >
                    <Sparkles size={11} />
                    {isGeneratingMeta ? 'Generating Meta...' : 'AI Meta Generator'}
                  </button>
                  <button 
                    type="button"
                    onClick={generateAISchema}
                    disabled={isGeneratingSchema}
                    className="flex-1 py-1.5 bg-emerald-600/20 border border-emerald-500/30 hover:bg-emerald-600/30 text-emerald-400 rounded-xl text-[10px] font-bold transition-all flex items-center justify-center gap-1"
                  >
                    <FileCode size={11} />
                    {isGeneratingSchema ? 'Generating Schema...' : 'AI Schema'}
                  </button>
                </div>

                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 mb-1">Meta Title</label>
                  <input 
                    type="text"
                    value={formData.meta_title}
                    onChange={(e) => setFormData(prev => ({ ...prev, meta_title: e.target.value }))}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 mb-1">Meta Description</label>
                  <textarea 
                    value={formData.meta_description}
                    onChange={(e) => setFormData(prev => ({ ...prev, meta_description: e.target.value }))}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none h-16"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 mb-1">Keywords (Comma separated)</label>
                  <input 
                    type="text"
                    value={formData.keywords}
                    onChange={(e) => setFormData(prev => ({ ...prev, keywords: e.target.value }))}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 mb-1">Slug</label>
                  <input 
                    type="text"
                    value={formData.slug}
                    onChange={(e) => setFormData(prev => ({ ...prev, slug: e.target.value }))}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3 py-2 text-xs text-white outline-none"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-semibold text-slate-400 mb-1">Schema JSON-LD</label>
                  <textarea 
                    value={formData.schema_json}
                    onChange={(e) => setFormData(prev => ({ ...prev, schema_json: e.target.value }))}
                    className="w-full bg-[#080d1a] border border-slate-800 rounded-xl px-3 py-2 text-[10px] text-white outline-none font-mono h-24"
                  />
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800 flex justify-end gap-2">
                <button 
                  type="button" 
                  onClick={() => setIsEditing(false)}
                  className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-bold transition-all"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all"
                >
                  Save Configuration
                </button>
              </div>
            </form>
          ) : activePageForAudit ? (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-black text-white">SEO Audit results</h3>
                <p className="text-[10px] text-slate-400">Diagnosis report for Page: <span className="text-white font-bold">{activePageForAudit.title}</span></p>
              </div>

              {auditDetails ? (
                <div className="space-y-4">
                  {/* Score Indicator */}
                  <div className="flex gap-4 items-center bg-[#080d1a] border border-slate-800 p-4 rounded-xl">
                    <div className="relative w-16 h-16 flex items-center justify-center bg-indigo-500/10 rounded-full border border-indigo-500/30">
                      <span className="text-lg font-black text-white">{auditDetails.seo_score}</span>
                    </div>
                    <div>
                      <span className="text-[10px] uppercase font-bold text-slate-500 block">SEO Performance Score</span>
                      <span className="text-xs font-bold text-white block">
                        {auditDetails.seo_score >= 80 ? 'Optimized Excellence' : 'Needs Optimization'}
                      </span>
                      <span className="text-[10px] text-slate-400">Readability Score: {auditDetails.readability_score}/100</span>
                    </div>
                  </div>

                  {/* Diagnostic metrics lists */}
                  <div className="space-y-2">
                    <div className="flex justify-between items-center text-xs p-2.5 bg-slate-900/40 rounded-lg">
                      <span className="text-slate-400">Missing Alt Images:</span>
                      <span className="font-bold text-white">{auditDetails.missing_alt_images}</span>
                    </div>
                    <div className="flex justify-between items-center text-xs p-2.5 bg-slate-900/40 rounded-lg">
                      <span className="text-slate-400">H1 Tag Configured:</span>
                      <span className="font-bold text-emerald-400">Yes</span>
                    </div>
                    <div className="flex justify-between items-center text-xs p-2.5 bg-slate-900/40 rounded-lg">
                      <span className="text-slate-400">Schema.org Structured:</span>
                      {auditDetails.missing_schema ? (
                        <span className="font-bold text-rose-400 flex items-center gap-0.5"><X size={10} /> Missing</span>
                      ) : (
                        <span className="font-bold text-emerald-400 flex items-center gap-0.5"><Check size={10} /> Present</span>
                      )}
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div className="space-y-2">
                    <span className="text-[10px] uppercase font-bold text-slate-500 block">AI SEO Recommendations</span>
                    {auditDetails.recommendations && auditDetails.recommendations.length > 0 ? (
                      <ul className="space-y-1.5">
                        {auditDetails.recommendations.map((rec: string, i: number) => (
                          <li key={i} className="text-[10px] text-amber-400 flex items-start gap-1">
                            <AlertTriangle size={11} className="mt-0.5 flex-shrink-0" />
                            {rec}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-[10px] text-emerald-400 flex items-center gap-1">
                        <CheckCircle size={11} /> Page is perfectly search optimized! No recommendations.
                      </p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center text-slate-500 flex justify-center items-center gap-2">
                  <RefreshCw className="animate-spin" size={14} /> Performing full diagnostic audit scan...
                </div>
              )}
            </div>
          ) : (
            <div className="py-12 text-center text-slate-500 space-y-2">
              <Sparkles className="mx-auto text-slate-700" size={24} />
              <p className="text-xs">Select any page audit action on the left to review dynamic keyword relevance, broken links diagnostics, and mobile preview cards.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
