import React, { useEffect, useState } from 'react';
import { cmsApi } from '../../services/cmsApi';
import { FolderTree, Plus, Trash2 } from 'lucide-react';

export const CategoryManager: React.FC = () => {
  const [categories, setCategories] = useState<any[]>([]);
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');

  const loadCategories = async () => {
    const res = await cmsApi.categories.list();
    if (res.success && res.data) {
      setCategories(res.data);
    }
  };

  useEffect(() => {
    loadCategories();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await cmsApi.categories.create({ name, slug });
    if (res.success) {
      setName('');
      setSlug('');
      loadCategories();
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div className="lg:col-span-8 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Categories taxonomy</h3>
          <p className="text-xs text-slate-500">Group articles or forum posts into nesting departments</p>
        </div>

        <div className="space-y-2">
          {categories.length === 0 ? (
            <div className="p-8 text-center bg-slate-950 border border-slate-850 rounded-xl text-slate-500 text-xs italic">
              No categories mapped yet. Add one on the right.
            </div>
          ) : (
            categories.map(cat => (
              <div key={cat.id} className="p-3 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FolderTree className="text-indigo-400" size={15} />
                  <div>
                    <span className="block font-semibold text-slate-200 text-xs">{cat.name}</span>
                    <span className="block text-[10px] text-slate-500 font-mono">SLUG: /{cat.slug}</span>
                  </div>
                </div>
                <button
                  onClick={async () => {
                    await cmsApi.categories.delete(cat.id);
                    loadCategories();
                  }}
                  className="p-1.5 hover:bg-red-950/30 text-slate-500 hover:text-red-400 rounded-lg transition"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="lg:col-span-4 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <h4 className="text-xs font-bold text-white uppercase tracking-widest font-mono text-indigo-400">Add Category</h4>
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-400 font-mono mb-1">Name</label>
            <input
              type="text"
              required
              value={name}
              onChange={e => setName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              placeholder="E.g. Engineering Tutorials"
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
              placeholder="engineering-tutorials"
            />
          </div>
          <button
            type="submit"
            className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg transition"
          >
            Create Category
          </button>
        </form>
      </div>
    </div>
  );
};
