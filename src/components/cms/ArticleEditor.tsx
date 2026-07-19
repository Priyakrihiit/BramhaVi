import React, { useEffect, useState } from 'react';
import { cmsApi } from '../../services/cmsApi';
import { FileText, Plus, Trash2, Edit, Save, Globe, EyeOff, Calendar, Eye, CheckSquare, Square } from 'lucide-react';

export const ArticleEditor: React.FC = () => {
  const [articles, setArticles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedArticle, setSelectedArticle] = useState<any | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState('all');

  // Form Fields
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [body, setBody] = useState('');
  const [excerpt, setExcerpt] = useState('');

  // Bulk Actions
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const loadArticles = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      const res = await cmsApi.articles.list(params);
      if (res.success && res.data) {
        setArticles(res.data);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadArticles();
  }, [statusFilter]);

  const selectArticle = (art: any) => {
    setSelectedArticle(art);
    setTitle(art.title);
    setSlug(art.slug);
    setBody(art.body);
    setExcerpt(art.excerpt || '');
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedArticle) return;

    const res = await cmsApi.articles.update(selectedArticle.id, {
      title,
      slug,
      body,
      excerpt,
    });
    if (res.success) {
      setSelectedArticle(null);
      loadArticles();
    }
  };

  const handleCreate = async () => {
    const res = await cmsApi.articles.create({
      title: 'New Article Draft',
      slug: `new-article-${Date.now()}`,
      body: 'Start writing your content here...',
      excerpt: '',
      status: 'draft',
    });
    if (res.success) {
      loadArticles();
    }
  };

  const toggleSelect = (id: string) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const handleBulkPublish = async () => {
    if (selectedIds.length === 0) return;
    const res = await cmsApi.articles.bulkPublish(selectedIds);
    if (res.success) {
      setSelectedIds([]);
      loadArticles();
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) return;
    const res = await cmsApi.articles.bulkDelete(selectedIds);
    if (res.success) {
      setSelectedIds([]);
      loadArticles();
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div className="lg:col-span-7 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">CMS Article Library</h3>
            <p className="text-xs text-slate-500">Manage all editorial publications and draft cycles</p>
          </div>
          <button
            onClick={handleCreate}
            className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl transition flex items-center gap-1.5"
          >
            <Plus size={14} />
            Create Article
          </button>
        </div>

        {/* Bulk controls */}
        {selectedIds.length > 0 && (
          <div className="p-3 bg-slate-950 border border-indigo-950/80 rounded-xl flex items-center justify-between text-xs">
            <span className="text-indigo-400 font-mono font-bold">{selectedIds.length} items selected</span>
            <div className="flex gap-2">
              <button onClick={handleBulkPublish} className="px-2.5 py-1 bg-emerald-950 text-emerald-400 border border-emerald-900/50 rounded-lg hover:bg-emerald-900/20 transition">
                Bulk Publish
              </button>
              <button onClick={handleBulkDelete} className="px-2.5 py-1 bg-red-950 text-red-400 border border-red-900/50 rounded-lg hover:bg-red-900/20 transition">
                Bulk Delete
              </button>
            </div>
          </div>
        )}

        <div className="space-y-3">
          {articles.map((art: any) => (
            <div key={art.id} className="p-4 bg-slate-950 border border-slate-850 rounded-xl flex items-center justify-between">
              <div className="flex items-center gap-3">
                <button onClick={() => toggleSelect(art.id)} className="text-slate-500 hover:text-white transition">
                  {selectedIds.includes(art.id) ? <CheckSquare size={16} className="text-indigo-400" /> : <Square size={16} />}
                </button>
                <FileText className="text-indigo-400" size={16} />
                <div>
                  <span className="block font-semibold text-slate-200 text-xs">{art.title}</span>
                  <span className="block text-[10px] text-slate-500 font-mono">STATUS: {art.status} | SLUG: /{art.slug}</span>
                </div>
              </div>

              <div className="flex gap-2">
                <button onClick={() => selectArticle(art)} className="p-1.5 hover:bg-slate-900 rounded text-indigo-400 transition" title="Edit">
                  <Edit size={14} />
                </button>
                {art.is_published ? (
                  <button onClick={async () => { await cmsApi.articles.unpublish(art.id); loadArticles(); }} className="p-1.5 hover:bg-slate-900 rounded text-amber-400 transition" title="Unpublish">
                    <EyeOff size={14} />
                  </button>
                ) : (
                  <button onClick={async () => { await cmsApi.articles.publish(art.id); loadArticles(); }} className="p-1.5 hover:bg-slate-900 rounded text-emerald-400 transition" title="Publish">
                    <Globe size={14} />
                  </button>
                )}
                <button onClick={async () => { await cmsApi.articles.delete(art.id); loadArticles(); }} className="p-1.5 hover:bg-slate-900 rounded text-red-400 transition" title="Delete">
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="lg:col-span-5 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        {selectedArticle ? (
          <form onSubmit={handleSave} className="space-y-4">
            <h4 className="text-xs font-bold text-white uppercase tracking-widest font-mono text-indigo-400">Edit Article</h4>
            <div>
              <label className="block text-[10px] uppercase font-bold text-slate-400 font-mono mb-1">Title</label>
              <input
                type="text"
                required
                value={title}
                onChange={e => setTitle(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-[10px] uppercase font-bold text-slate-400 font-mono mb-1">Slug</label>
              <input
                type="text"
                required
                value={slug}
                onChange={e => setSlug(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-[10px] uppercase font-bold text-slate-400 font-mono mb-1">Excerpt</label>
              <input
                type="text"
                value={excerpt}
                onChange={e => setExcerpt(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-[10px] uppercase font-bold text-slate-400 font-mono mb-1">Body Markdown Content</label>
              <textarea
                rows={6}
                value={body}
                onChange={e => setBody(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div className="flex gap-2">
              <button
                type="submit"
                className="flex-1 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg transition flex items-center justify-center gap-1.5"
              >
                <Save size={14} />
                Save Changes
              </button>
              <button
                type="button"
                onClick={() => setSelectedArticle(null)}
                className="px-4 py-2 bg-slate-850 hover:bg-slate-800 text-slate-300 font-bold text-xs rounded-xl transition"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <div className="p-8 text-center text-slate-500 text-xs italic">
            Select an article from the library list to edit its fields.
          </div>
        )}
      </div>
    </div>
  );
};
