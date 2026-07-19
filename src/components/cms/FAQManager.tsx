import React, { useEffect, useState } from 'react';
import { cmsApi } from '../../services/cmsApi';
import { HelpCircle, Plus, Trash2 } from 'lucide-react';

export const FAQManager: React.FC = () => {
  const [faqs, setFaqs] = useState<any[]>([]);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const loadFaqs = async () => {
    const res = await cmsApi.faq.list();
    if (res.success && res.data) {
      setFaqs(res.data);
    }
  };

  useEffect(() => {
    loadFaqs();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await cmsApi.faq.create({ question, answer });
    if (res.success) {
      setQuestion('');
      setAnswer('');
      loadFaqs();
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div className="lg:col-span-8 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">FAQ manager</h3>
          <p className="text-xs text-slate-500">Edit, publish, and order public academy Q&As</p>
        </div>

        <div className="space-y-3">
          {faqs.length === 0 ? (
            <div className="p-8 text-center bg-slate-950 border border-slate-850 rounded-xl text-slate-500 text-xs italic">
              No FAQs created yet. Add one on the right.
            </div>
          ) : (
            faqs.map(faq => (
              <div key={faq.id} className="p-4 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <HelpCircle className="text-indigo-400" size={16} />
                  <div>
                    <span className="block font-semibold text-slate-200 text-xs">{faq.question}</span>
                    <span className="block text-[10px] text-slate-500 mt-1">{faq.answer}</span>
                  </div>
                </div>
                <button
                  onClick={async () => {
                    await cmsApi.faq.delete(faq.id);
                    loadFaqs();
                  }}
                  className="p-1.5 hover:bg-red-950/30 text-slate-500 hover:text-red-400 rounded-lg transition animate-pulse"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="lg:col-span-4 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
        <h4 className="text-xs font-bold text-white uppercase tracking-widest font-mono text-indigo-400">Add FAQ</h4>
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-400 font-mono mb-1">Question</label>
            <input
              type="text"
              required
              value={question}
              onChange={e => setQuestion(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              placeholder="E.g. What is BrahmaVidya?"
            />
          </div>
          <div>
            <label className="block text-[10px] uppercase font-bold text-slate-400 font-mono mb-1">Answer</label>
            <textarea
              rows={4}
              required
              value={answer}
              onChange={e => setAnswer(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              placeholder="Describe answer details..."
            />
          </div>
          <button
            type="submit"
            className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg transition"
          >
            Add Q&A
          </button>
        </form>
      </div>
    </div>
  );
};
