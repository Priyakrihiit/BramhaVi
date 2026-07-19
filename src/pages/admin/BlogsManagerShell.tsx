/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { Blog } from '../../types';
import { FileText, Plus, Trash2, Edit, Save, Globe, EyeOff, Search, ChevronLeft, ChevronRight, RotateCcw } from 'lucide-react';

export const BlogsManagerShell: React.FC = () => {
  const [blogs, setBlogs] = useState<Blog[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedBlog, setSelectedBlog] = useState<Blog | null>(null);

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

  const loadBlogs = async () => {
    setLoading(true);
    try {
      const isPubParam = isPublishedFilter === 'published' ? true : isPublishedFilter === 'draft' ? false : undefined;
      const res = await api.blogs.list({
        search: search || undefined,
        isPublished: isPubParam,
        includeDeleted,
        page,
        limit: 5
      });

      if (res.success && res.data) {
        setBlogs(res.data);
        // If API returns count, set it, else use data length
        setTotal((res as any).total || res.data.length);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBlogs();
  }, [search, page, includeDeleted, isPublishedFilter]);

  const selectBlogForEdit = (blog: Blog) => {
    setSelectedBlog(blog);
    setTitle(blog.title);
    setSlug(blog.slug);
    setContent(blog.content);
    setIsPublished(blog.isPublished);
  };

  const handleCreateNew = () => {
    setSelectedBlog({
      id: 'new',
      title: 'New Blog Post',
      slug: 'new-blog-post',
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
    if (!selectedBlog) return;

    // Helper to generate slug if missing
    const finalSlug = slug || title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

    const blogData = {
      title,
      slug: finalSlug,
      content,
      isPublished,
      authorId: selectedBlog.authorId || 'user-admin',
      authorEmail: selectedBlog.authorEmail || 'admin@brahmavidya.edu'
    };

    try {
      let res;
      if (selectedBlog.id === 'new') {
        res = await api.blogs.create(blogData);
      } else {
        res = await api.blogs.update(selectedBlog.id, blogData);
      }

      if (res.success) {
        setSelectedBlog(null);
        await loadBlogs();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (idOrSlug: string) => {
    if (!window.confirm('Are you sure you want to soft-delete this blog post?')) return;
    try {
      const res = await api.blogs.delete(idOrSlug);
      if (res.success) {
        if (selectedBlog?.id === idOrSlug || selectedBlog?.slug === idOrSlug) {
          setSelectedBlog(null);
        }
        await loadBlogs();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleRestore = async (idOrSlug: string) => {
    try {
      const res = await api.blogs.restore(idOrSlug);
      if (res.success) {
        await loadBlogs();
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <React.Fragment>
      <div id="bvg-admin-blogs" className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Side: Directory & Filters */}
        <div className="lg:col-span-5 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Blog Files Directory</h3>
              <p className="text-xs text-slate-500">Draft, schedule, publish, and restore blog content</p>
            </div>
            <button
              onClick={handleCreateNew}
              className="p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition shadow"
            >
              <Plus size={14} />
              Create Blog
            </button>
          </div>

          {/* Search & Filters */}
          <div className="space-y-2">
            <div className="relative">
              <Search className="absolute left-3 top-3 text-slate-500" size={14} />
              <input
                type="text"
                placeholder="Search blogs..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 pl-9 text-slate-300 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
              />
            </div>

            <div className="grid grid-cols-2 gap-2 text-[10px]">
              {/* IsPublished Select */}
              <select
                value={isPublishedFilter}
                onChange={(e) => { setIsPublishedFilter(e.target.value); setPage(1); }}
                className="bg-slate-950 border border-slate-800 text-slate-300 rounded-lg p-2 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="all">All States</option>
                <option value="published">Published Only</option>
                <option value="draft">Drafts Only</option>
              </select>

              {/* Include Deleted Toggle */}
              <button
                onClick={() => { setIncludeDeleted(!includeDeleted); setPage(1); }}
                className={`flex items-center justify-center border rounded-lg p-2 text-xs font-semibold transition ${includeDeleted ? 'bg-indigo-650/20 border-indigo-500/50 text-indigo-200' : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'}`}
              >
                {includeDeleted ? 'Showing Soft Deleted' : 'Exclude Soft Deleted'}
              </button>
            </div>
          </div>

          {/* Blogs Directory List */}
          {loading ? (
            <div className="flex items-center justify-center py-12 text-slate-500 font-mono text-xs">
              <span className="h-1 w-1 rounded-full bg-indigo-500 animate-ping mr-2"></span>
              Refreshing blog records...
            </div>
          ) : (
            <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
              {blogs.map(blog => (
                <div
                  key={blog.id}
                  className={`p-3 rounded-xl border flex items-center justify-between text-left text-xs transition ${selectedBlog?.id === blog.id ? 'bg-indigo-600/10 border-indigo-500' : 'bg-slate-950 border-slate-850 hover:bg-slate-850'}`}
                >
                  <button
                    onClick={() => selectBlogForEdit(blog)}
                    className="flex-1 flex items-center gap-3 text-left"
                  >
                    <FileText className={blog.isPublished ? 'text-indigo-400' : 'text-slate-500'} size={15} />
                    <div className="min-w-0 flex-1">
                      <span className="block font-semibold text-slate-200 truncate">{blog.title}</span>
                      <div className="flex items-center gap-1.5 mt-0.5 text-[9px] text-slate-500 font-mono">
                        {blog.isPublished ? (
                          <span className="text-indigo-400 flex items-center gap-0.5 font-bold">
                            <Globe size={9} /> PUBLISHED
                          </span>
                        ) : (
                          <span className="text-amber-500 flex items-center gap-0.5 font-bold">
                            <EyeOff size={9} /> DRAFT
                          </span>
                        )}
                        <span>•</span>
                        <span className="truncate">/{blog.slug}</span>
                        {blog.isDeleted && (
                          <span className="text-red-400 font-bold ml-1 uppercase">[DELETED]</span>
                        )}
                      </div>
                    </div>
                  </button>

                  <div className="flex items-center gap-1.5 pl-2">
                    {blog.isDeleted ? (
                      <button
                        onClick={() => handleRestore(blog.id)}
                        className="p-1 text-emerald-500 hover:text-emerald-400 hover:bg-slate-800 rounded transition"
                        title="Restore soft deleted blog"
                      >
                        <RotateCcw size={13} />
                      </button>
                    ) : (
                      <button
                        onClick={() => handleDelete(blog.id)}
                        className="p-1 text-rose-500 hover:text-rose-400 hover:bg-slate-800 rounded transition"
                        title="Soft delete blog"
                      >
                        <Trash2 size={13} />
                      </button>
                    )}
                  </div>
                </div>
              ))}

              {blogs.length === 0 && (
                <div className="py-12 text-center text-slate-500 italic text-xs">
                  No blogs match your filter criteria.
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
                disabled={blogs.length < 5}
                onClick={() => setPage(p => p + 1)}
                className="p-1.5 bg-slate-950 border border-slate-800 rounded hover:bg-slate-850 disabled:opacity-40 transition"
              >
                <ChevronRight size={12} />
              </button>
            </div>
          </div>
        </div>

        {/* Right Side: Markdown SEO Editor */}
        <div className="lg:col-span-7 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Article Editor & Workflow</h3>
            <p className="text-xs text-slate-500">Formulate dynamic Markdown content and SEO-aligned slugs</p>
          </div>

          {selectedBlog ? (
            <form onSubmit={handleSave} className="space-y-4 text-xs text-left">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-500">Blog Title</label>
                  <input
                    type="text"
                    required
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    placeholder="Enter blog headline"
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
                <label className="text-[10px] uppercase font-bold text-slate-500">Markdown Content Body</label>
                <textarea
                  required
                  rows={8}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono leading-relaxed"
                  placeholder="# Enter markdown here..."
                />
              </div>

              {/* Publish Switcher */}
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-850 flex items-center justify-between">
                <div>
                  <span className="block font-semibold text-slate-200">Publish immediately to website feed</span>
                  <span className="block text-[10px] text-slate-500 font-mono">Published blogs are accessible by all readers</span>
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
                  {isPublished ? (
                    <Globe size={26} className="text-indigo-400" />
                  ) : (
                    <EyeOff size={26} className="text-slate-500" />
                  )}
                </button>
              </div>

              <div className="pt-3 border-t border-slate-800 flex justify-between">
                <button
                  type="button"
                  onClick={() => setSelectedBlog(null)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-750 text-slate-300 rounded-lg font-semibold transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-semibold transition flex items-center gap-1.5 shadow"
                >
                  <Save size={13} />
                  Save Article
                </button>
              </div>
            </form>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center border border-dashed border-slate-800 rounded-xl text-slate-500 font-serif italic text-xs">
              Select an article from directory listing to modify parameters or build content
            </div>
          )}
        </div>

      </div>
    </React.Fragment>
  );
};

export default BlogsManagerShell;
