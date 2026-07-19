import React, { useState, useEffect } from 'react';
import { TrendingUp } from 'lucide-react';
import { searchApi, SearchTerm } from '../../services/searchApi';

interface TrendingPanelProps {
  onSelectTerm: (term: string) => void;
}

export const TrendingPanel: React.FC<TrendingPanelProps> = ({ onSelectTerm }) => {
  const [trends, setTrends] = useState<SearchTerm[]>([]);

  useEffect(() => {
    const fetchTrends = async () => {
      const res = await searchApi.getPopular(6);
      if (res.success && res.data) {
        setTrends(res.data);
      }
    };
    fetchTrends();
  }, []);

  if (trends.length === 0) return null;

  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-xs">
      <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center gap-1.5 font-mono border-b border-slate-100 pb-2.5">
        <TrendingUp className="h-4 w-4 text-indigo-600" /> Popular Searches
      </h3>
      <ul className="space-y-2">
        {trends.map((item) => (
          <li key={item.id}>
            <button
              onClick={() => onSelectTerm(item.term)}
              className="w-full text-left flex items-center justify-between text-slate-600 hover:text-indigo-600 hover:underline transition cursor-pointer"
            >
              <span>{item.term}</span>
              <span className="text-[10px] font-mono text-slate-400">
                {item.frequency} queries
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};
