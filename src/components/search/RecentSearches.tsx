import React, { useState, useEffect } from 'react';
import { History, Trash2 } from 'lucide-react';
import { searchApi, SearchHistory } from '../../services/searchApi';

interface RecentSearchesProps {
  onSelectRecent: (query: string) => void;
  refreshTrigger: number;
}

export const RecentSearches: React.FC<RecentSearchesProps> = ({ onSelectRecent, refreshTrigger }) => {
  const [history, setHistory] = useState<SearchHistory[]>([]);

  const fetchHistory = async () => {
    const res = await searchApi.getHistory();
    if (res.success && res.data) {
      setHistory(res.data);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [refreshTrigger]);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    const res = await searchApi.deleteHistory(id);
    if (res.success) {
      setHistory(history.filter((item) => item.id !== id));
    }
  };

  if (history.length === 0) return null;

  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-xs">
      <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center gap-1.5 font-mono border-b border-slate-100 pb-2.5">
        <History className="h-4 w-4 text-indigo-600" /> Recent Searches
      </h3>
      <ul className="space-y-2">
        {history.map((item) => (
          <li key={item.id} className="group flex items-center justify-between">
            <button
              onClick={() => onSelectRecent(item.query)}
              className="flex-1 text-left text-slate-600 hover:text-indigo-600 hover:underline transition cursor-pointer"
            >
              {item.query}
            </button>
            <button
              onClick={(e) => handleDelete(e, item.id)}
              className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-rose-600 p-0.5 rounded transition cursor-pointer"
              title="Delete search log"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};
