/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { Tutorial } from '../../types';
import { Bookmark, Plus, Trash2, Edit, Save, Globe, EyeOff, Search, ChevronLeft, ChevronRight, RotateCcw } from 'lucide-react';

export const TutorialsManagerShell: React.FC = () => {
  const [tutorials, setTutorials] = useState<Tutorial[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTutorial, setSelectedTutorial] = useState<Tutorial | null>(null);

  // Pagination & Filtering state
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [includeDeleted, setIncludeDeleted] = useState(false);
  const [isPublishedFilter, setIsPublishedFilter] = useState<string>('all');

  // Form Fields
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [content, setContent] = useState('');
  const [isPublished, setIsPublished] = useState(false);

  const loadTutorials = async () => {
    setLoading(true);
    try {
      const isPubParam = isPublishedFilter === 'published' ? true : isPublishedFilter === 'draft' ? false : undefined;
      const res = await api.tutorials.list({
        search: search || undefined,
        isPublished: isPubParam,
        includeDeleted,
        page,
        limit: 5
      });

      if (res.success && res.data) {
        setTutorials(res.data);
        setTotal((res as any).total || res.data.length);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTutorials();
  }, [search, page, includeDeleted, isPublishedFilter]);

  const selectTutorialForEdit = (tutorial: Tutorial) => {
    setSelectedTutorial(tutorial);
    setTitle(tutorial.title);
    setSlug(tutorial.slug);
    setContent(tutorial.content);
    setIsPublished(tutorial.isPublished);
  };

  const handleCreateNew = () => {
    setSelectedTutorial({
      id: 'new',
      title: 'New Tutorial Course',
      slug: 'new-tutorial-course',
      content: '',
      authorId: 'user-admin',
      authorEmail: 'admin@brahmavidya.edu',
      isPublished: false,
      isDeleted: false
    });
    setTitle('');
    setSlug('');
    setContent('');
    setIsPublished(false);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTutorial) return;

    const finalSlug = slug || title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

    const tutorialData = {
      title,
      slug: finalSlug,
      content,
      isPublished,
      authorId: selectedTutorial.authorId || 'user-admin',
      authorEmail: selectedTutorial.authorEmail || 'admin@brahmavidya.edu'
    };

    try {
      let res;
      if (selectedTutorial.id === 'new') {
        res = await api.tutorials.create(tutorialData);
      } else {
        res = await api.tutorials.update(selectedTutorial.id, tutorialData);
      }

      if (res.success) {
        setSelectedTutorial(null);
        await loadTutorials();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (idOrSlug: string) => {
    if (!window.confirm('Are you sure you want to soft-delete this tutorial?')) return;
    try {
      const res = await api.tutorials.delete(idOrSlug);
      if (res.success) {
        if (selectedTutorial?.id === idOrSlug || selectedTutorial?.slug === idOrSlug) {
          setSelectedTutorial(null);
        }
        await loadTutorials();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleRestore = async (idOrSlug: string) => {
    try {
      const res = await api.tutorials.restore(idOrSlug);
      if (res.success) {
        await loadTutorials();
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <React.Fragment>
      <div id="bvg-admin-tutorials" className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Side: Directory & Filters */}
        <div className="lg:col-span-5 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Tutorial Directory</h3>
              <p className="text-xs text-slate-500">Draft, compose, and manage academic tutorials</p>
            </div>
            <button
              onClick={handleCreateNew}
              className="p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition shadow"
            >
              <Plus size={14} />
              Create Tutorial
            </button>
          </div>

          {/* Search & Filters */}
          <div className="space-y-2">
            <div className="relative">
              <Search className="absolute left-3 top-3 text-slate-500" size={14} />
              <input
                type="text"
                placeholder="Search tutorials..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 pl-9 text-slate-300 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
              />
            </div>

            <div className="grid grid-cols-2 gap-2 text-[10px]">
              <select
                value={isPublishedFilter}
                onChange={(e) => { setIsPublishedFilter(e.target.value); setPage(1); }}
                className="bg-slate-950 border border-slate-800 text-slate-300 rounded-lg p-2 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="all">All States</option>
                <option value="published">Published Only</option>
                <option value="draft">Drafts Only</option>
              </select>

              <button
                onClick={() => { setIncludeDeleted(!includeDeleted); setPage(1); }}
                className={`flex items-center justify-center border rounded-lg p-2 text-xs font-semibold transition ${includeDeleted ? 'bg-indigo-650/20 border-indigo-500/50 text-indigo-200' : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'}`}
              >
                {includeDeleted ? 'Showing Soft Deleted' : 'Exclude Soft Deleted'}
              </button>
            </div>
          </div>

          {/* Tutorials List */}
          {loading ? (
            <div className="flex items-center justify-center py-12 text-slate-500 font-mono text-xs">
              <span className="h-1 w-1 rounded-full bg-indigo-500 animate-ping mr-2"></span>
              Refreshing tutorial records...
            </div>
          ) : (
            <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
              {tutorials.map(tutorial => (
                <div
                  key={tutorial.id}
                  className={`p-3 rounded-xl border flex items-center justify-between text-left text-xs transition ${selectedTutorial?.id === tutorial.id ? 'bg-indigo-600/10 border-indigo-500' : 'bg-slate-950 border-slate-850 hover:bg-slate-850'}`}
                >
                  <button
                    onClick={() => selectTutorialForEdit(tutorial)}
                    className="flex-1 flex items-center gap-3 text-left"
                  >
                    <Bookmark className={tutorial.isPublished ? 'text-indigo-400' : 'text-slate-500'} size={15} />
                    <div className="min-w-0 flex-1">
                      <span className="block font-semibold text-slate-200 truncate">{tutorial.title}</span>
                      <div className="flex items-center gap-1.5 mt-0.5 text-[9px] text-slate-500 font-mono">
                        {tutorial.isPublished ? (
                          <span className="text-indigo-400 flex items-center gap-0.5 font-bold">
                            <Globe size={9} /> PUBLISHED
                          </span>
                        ) : (
                          <span className="text-amber-500 flex items-center gap-0.5 font-bold">
                            <EyeOff size={9} /> DRAFT
                          </span>
                        )}
                        <span>•</span>
                        <span className="truncate">/{tutorial.slug}</span>
                        {tutorial.isDeleted && (
                          <span className="text-red-400 font-bold ml-1 uppercase">[DELETED]</span>
                        )}
                      </div>
                    </div>
                  </button>

                  <div className="flex items-center gap-1.5 pl-2">
                    {tutorial.isDeleted ? (
                      <button
                        onClick={() => handleRestore(tutorial.id)}
                        className="p-1 text-emerald-500 hover:text-emerald-400 hover:bg-slate-800 rounded transition"
                        title="Restore soft deleted tutorial"
                      >
                        <RotateCcw size={13} />
                      </button>
                    ) : (
                      <button
                        onClick={() => handleDelete(tutorial.id)}
                        className="p-1 text-rose-500 hover:text-rose-400 hover:bg-slate-800 rounded transition"
                        title="Soft delete tutorial"
                      >
                        <Trash2 size={13} />
                      </button>
                    )}
                  </div>
                </div>
              ))}

              {tutorials.length === 0 && (
                <div className="py-12 text-center text-slate-500 italic text-xs">
                  No tutorials match your filter criteria.
                </div>
              )}
            </div>
          )}

          {/* Pagination bar */}
          <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-500 font-mono">
            <span>TOTAL: {total} ITEMS</span>
            <div className="flex items-center gap-1.5">
              <button
                disabled={page <= 1}
                onClick={() => setPage(p => Math.max(1, p - 1))}
                className="p-1.5 bg-slate-950 border border-slate-800 rounded hover:bg-slate-850 disabled:opacity-40 transition"
              >
                <ChevronLeft size={12} />
              </button>
              <span>PAGE {page}</span>
              <button
                disabled={tutorials.length < 5}
                onClick={() => setPage(p => p + 1)}
                className="p-1.5 bg-slate-950 border border-slate-800 rounded hover:bg-slate-850 disabled:opacity-40 transition"
              >
                <ChevronRight size={12} />
              </button>
            </div>
          </div>
        </div>

        {/* Right Side: Editor */}
        <div className="lg:col-span-7 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Syllabus Guide Content</h3>
            <p className="text-xs text-slate-500">Draft rich academic guide markdown blocks</p>
          </div>

          {selectedTutorial ? (
            <form onSubmit={handleSave} className="space-y-4 text-xs text-left">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-500">Tutorial Title</label>
                  <input
                    type="text"
                    required
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    placeholder="e.g. Master React hooks"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-500">Slug path (URL-friendly)</label>
                  <input
                    type="text"
                    value={slug}
                    onChange={(e) => setSlug(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
                    placeholder="Auto-generated if left blank"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold text-slate-500">Tutorial Body Content (Markdown format)</label>
                <textarea
                  required
                  rows={8}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono leading-relaxed"
                  placeholder="# Lesson Overview..."
                />
              </div>

              {/* Publish State */}
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-850 flex items-center justify-between">
                <div>
                  <span className="block font-semibold text-slate-200">Publish immediately to student directory</span>
                  <span className="block text-[10px] text-slate-500 font-mono">Published tutorials are accessible by all enrolled students</span>
                </div>
                <button
                  type="button"
                  onClick={() => setIsPublished(!isPublished)}
                  className="text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                >
                  {isPublished ? (
                    <span className="text-[10px] font-bold uppercase tracking-wider bg-indigo-950 border border-indigo-800 text-indigo-400 px-2 py-0.5 rounded mr-1">PUBLISHED</span>
                  ) : (
                    <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-900 border border-slate-800 text-slate-500 px-2 py-0.5 rounded mr-1">DRAFT</span>
                  )}
                  {isPublished ? <Globe size={26} className="text-indigo-400" /> : <EyeOff size={26} className="text-slate-500" />}
                </button>
              </div>

              <div className="pt-3 border-t border-slate-800 flex justify-between">
                <button
                  type="button"
                  onClick={() => setSelectedTutorial(null)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-750 text-slate-300 rounded-lg font-semibold transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-semibold transition flex items-center gap-1.5 shadow"
                >
                  <Save size={13} />
                  Save Tutorial
                </button>
              </div>
            </form>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center border border-dashed border-slate-800 rounded-xl text-slate-500 font-serif italic text-xs">
              Select a tutorial from listing to edit its layout content or SEO configurations
            </div>
          )}
        </div>

      </div>
    </React.Fragment>
  );
};

export default TutorialsManagerShell;
