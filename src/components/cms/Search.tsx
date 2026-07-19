import React, { useState } from 'react';
import { cmsApi } from '../../services/cmsApi';
import { Search as SearchIcon, FileText } from 'lucide-react';

export const Search: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await cmsApi.search.query({ search: query });
      if (res.success && res.data) {
        setResults(res.data);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-6">
      <div>
        <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Search Index Debugger</h3>
        <p className="text-xs text-slate-500">Query the unified search index database directly to confirm sitemaps and indexes sync</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="flex-1 relative">
          <input
            type="text"
            required
            value={query}
            onChange={e => setQuery(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            placeholder="Type search terms..."
          />
          <SearchIcon size={14} className="text-slate-500 absolute left-3 top-3" />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg transition"
        >
          {loading ? 'Searching...' : 'Run Query'}
        </button>
      </form>

      <div className="space-y-3">
        {results.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-xs italic">
            No search matches found.
          </div>
        ) : (
          results.map(res => (
            <div key={res.id} className="p-4 bg-slate-950 border border-slate-850 rounded-xl flex items-center gap-3">
              <FileText className="text-indigo-400" size={16} />
              <div>
                <span className="block font-semibold text-slate-200 text-xs">{res.title}</span>
                <span className="block text-[10px] text-slate-500 font-mono">TYPE: {res.content_type} | BY: {res.author_name}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
