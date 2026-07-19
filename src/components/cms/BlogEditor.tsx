import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { Blog } from '../../types';
import { FileText, Plus, Trash2, Edit, Save, Globe, EyeOff } from 'lucide-react';

export const BlogEditor: React.FC = () => {
  const [blogs, setBlogs] = useState<Blog[]>([]);
  const [selectedBlog, setSelectedBlog] = useState<Blog | null>(null);

  // Form Fields
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [content, setContent] = useState('');

  const loadBlogs = async () => {
    const res = await api.blogs.list();
    if (res.success && res.data) {
      setBlogs(res.data);
    }
  };

  useEffect(() => {
    loadBlogs();
  }, []);

  const selectBlog = (blog: Blog) => {
    setSelectedBlog(blog);
    setTitle(blog.title);
    setSlug(blog.slug);
    setContent(blog.content);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBlog) return;

    const res = await api.blogs.update(selectedBlog.id, {
      title,
      slug,
      content,
    });
    if (res.success) {
      setSelectedBlog(null);
      loadBlogs();
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div className="lg:col-span-7 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">CMS Blogs Editor</h3>
          <p className="text-xs text-slate-500">Edit blog drafts, increments view logs, and customize tags</p>
        </div>

        <div className="space-y-3">
          {blogs.map(blog => (
            <div key={blog.id} className="p-4 bg-slate-950 border border-slate-850 rounded-xl flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileText className="text-indigo-400" size={16} />
                <div>
                  <span className="block font-semibold text-slate-200 text-xs">{blog.title}</span>
                  <span className="block text-[10px] text-slate-500 font-mono">SLUG: /{blog.slug}</span>
                </div>
              </div>
              <div className="flex gap-2">
                <button onClick={() => selectBlog(blog)} className="p-1.5 hover:bg-slate-900 rounded text-indigo-400 transition" title="Edit">
                  <Edit size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="lg:col-span-5 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        {selectedBlog ? (
          <form onSubmit={handleSave} className="space-y-4">
            <h4 className="text-xs font-bold text-white uppercase tracking-widest font-mono text-indigo-400">Edit Blog Post</h4>
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
              <label className="block text-[10px] uppercase font-bold text-slate-400 font-mono mb-1">Markdown Body</label>
              <textarea
                rows={6}
                value={content}
                onChange={e => setContent(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-indigo-500"
              />
            </div>
            <button
              type="submit"
              className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg transition flex items-center justify-center gap-1.5"
            >
              <Save size={14} />
              Save Post
            </button>
          </form>
        ) : (
          <div className="p-8 text-center text-slate-500 text-xs italic">
            Select a blog from the list to modify its content fields.
          </div>
        )}
      </div>
    </div>
  );
};
