import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { MessageSquare, ShieldAlert, Trash2 } from 'lucide-react';

export const CommentModeration: React.FC = () => {
  const [comments, setComments] = useState<any[]>([]);

  const loadComments = async () => {
    // Blogs comments or general comments
    const res = await api.blogs.list();
    if (res.success && res.data) {
      // Collect nested comments
      const all: any[] = [];
      res.data.forEach((b: any) => {
        if (b.comments) {
          b.comments.forEach((c: any) => {
            all.push({ ...c, blogTitle: b.title });
          });
        }
      });
      setComments(all);
    }
  };

  useEffect(() => {
    loadComments();
  }, []);

  const handleModerate = async (id: string) => {
    // Endpoint trigger moderate
    const token = localStorage.getItem('bvg_token');
    await fetch(`/api/v1/cms/comments/${id}/moderate/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    loadComments();
  };

  return (
    <div className="p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
      <div>
        <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Comment Moderation Center</h3>
        <p className="text-xs text-slate-500">Review blog comments, flag spam, and replace content with moderation banners</p>
      </div>

      <div className="space-y-3">
        {comments.length === 0 ? (
          <div className="p-8 text-center bg-slate-950 border border-slate-850 rounded-xl text-slate-500 text-xs italic">
            No comments reported or found.
          </div>
        ) : (
          comments.map(c => (
            <div key={c.id} className="p-4 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between">
              <div className="flex items-center gap-3">
                <MessageSquare className="text-indigo-400" size={16} />
                <div>
                  <p className="text-xs text-slate-200 font-medium">{c.content}</p>
                  <span className="block text-[9px] text-slate-500 font-mono mt-1">BY: {c.author?.fullName || 'Anonymous'} | BLOG: {c.blogTitle}</span>
                </div>
              </div>
              <button
                onClick={() => handleModerate(c.id)}
                className="px-2.5 py-1 bg-red-950 text-red-400 border border-red-900/50 rounded-lg text-[10px] hover:bg-red-900/20 transition flex items-center gap-1"
              >
                <ShieldAlert size={10} /> Moderate
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
