/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { Page } from '../../types';
import { Layout, Edit, Plus, Trash2, Globe, Save } from 'lucide-react';

export const PageBuilderShell: React.FC = () => {
  const [pages, setPages] = useState<Page[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPage, setSelectedPage] = useState<Page | null>(null);
  
  // Forms
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [seoTitle, setSeoTitle] = useState('');
  const [seoDesc, setSeoDesc] = useState('');

  const loadPages = async () => {
    setLoading(true);
    try {
      const res = await api.pages.list();
      if (res.success && res.data) {
        setPages(res.data);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPages();
  }, []);

  const selectPageForEdit = (page: Page) => {
    setSelectedPage(page);
    setTitle(page.title);
    setSlug(page.slug);
    setSeoTitle(page.seoTitle || '');
    setSeoDesc(page.seoDescription || '');
  };

  const handleSavePage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPage) return;

    try {
      const res = await api.pages.update(selectedPage.id, {
        title,
        slug,
        seoTitle,
        seoDescription: seoDesc,
      });

      if (res.success) {
        setSelectedPage(null);
        await loadPages();
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 text-slate-500 font-mono text-xs">
        <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-ping mr-2"></span>
        Compiling layout builders...
      </div>
    );
  }

  return (
    <React.Fragment>
      <div id="bvg-admin-pagebuilder" className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Pages directory */}
        <div className="lg:col-span-5 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Layout Files Directory</h3>
            <p className="text-xs text-slate-500">Edit dynamic pages or construct layout blocks</p>
          </div>

          <div className="space-y-2">
            {pages.map(page => (
              <button
                key={page.id}
                onClick={() => selectPageForEdit(page)}
                className="w-full p-3 bg-slate-950 hover:bg-slate-850 rounded-xl border border-slate-800 flex items-center justify-between text-left text-xs transition"
              >
                <div className="flex items-center gap-3">
                  <Layout className="text-indigo-400" size={15} />
                  <div>
                    <span className="block font-semibold text-slate-200">{page.title}</span>
                    <span className="block text-[10px] text-slate-500 font-mono">SLUG: /{page.slug}</span>
                  </div>
                </div>
                <Edit className="text-slate-500 hover:text-white" size={14} />
              </button>
            ))}
          </div>
        </div>

        {/* Dynamic block and SEO editor */}
        <div className="lg:col-span-7 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Metadata & Layout Settings</h3>
            <p className="text-xs text-slate-500">Alter layouts, headers, descriptions, and keywords</p>
          </div>

          {selectedPage ? (
            <form onSubmit={handleSavePage} className="space-y-4 text-xs text-left">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-500">Page Name</label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-500">Slug path</label>
                  <input
                    type="text"
                    value={slug}
                    onChange={(e) => setSlug(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold text-slate-500 flex items-center gap-1">
                  <Globe size={11} className="text-indigo-400" />
                  Meta SEO Title
                </label>
                <input
                  type="text"
                  value={seoTitle}
                  onChange={(e) => setSeoTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold text-slate-500">Meta SEO Description</label>
                <textarea
                  rows={3}
                  value={seoDesc}
                  onChange={(e) => setSeoDesc(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div className="pt-3 border-t border-slate-800 flex justify-between">
                <button
                  type="button"
                  onClick={() => setSelectedPage(null)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-750 text-slate-300 rounded-lg font-semibold transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-semibold transition flex items-center gap-1.5 shadow"
                >
                  <Save size={13} />
                  Save Configurations
                </button>
              </div>
            </form>
          ) : (
            <div className="h-44 flex flex-col items-center justify-center border border-dashed border-slate-800 rounded-xl text-slate-500 font-serif italic text-xs">
              Select a page from directory to inspect and alter its metadata properties
            </div>
          )}
        </div>

      </div>
    </React.Fragment>
  );
};

export default PageBuilderShell;
