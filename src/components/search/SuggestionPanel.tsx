import React, { useState, useEffect } from 'react';
import { HelpCircle, Sparkles } from 'lucide-react';
import { searchApi, SearchSuggestion } from '../../services/searchApi';

interface SuggestionPanelProps {
  query: string;
  spellingSuggestion: string | null;
  onSuggestionSelect: (val: string) => void;
}

export const SuggestionPanel: React.FC<SuggestionPanelProps> = ({
  query,
  spellingSuggestion,
  onSuggestionSelect
}) => {
  const [related, setRelated] = useState<SearchSuggestion[]>([]);

  useEffect(() => {
    if (!query.trim()) {
      setRelated([]);
      return;
    }
    const fetchRelated = async () => {
      const res = await searchApi.suggestions(query);
      if (res.success && res.data) {
        setRelated(res.data);
      }
    };
    fetchRelated();
  }, [query]);

  if (!spellingSuggestion && related.length === 0) return null;

  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-xs">
      {spellingSuggestion && (
        <div className="flex items-center gap-2 text-slate-700 bg-amber-50 border border-amber-100 p-3 rounded-xl">
          <HelpCircle className="h-4 w-4 text-amber-500 flex-shrink-0" />
          <span>
            Did you mean:{' '}
            <button
              onClick={() => onSuggestionSelect(spellingSuggestion)}
              className="text-indigo-600 font-bold hover:underline font-mono ml-0.5 cursor-pointer"
            >
              {spellingSuggestion}
            </button>
            ?
          </span>
        </div>
      )}

      {related.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-bold text-slate-800 flex items-center gap-1.5 uppercase font-mono text-[10px] tracking-wider text-slate-400">
            <Sparkles className="h-3.5 w-3.5 text-indigo-500" /> Related Suggestions
          </h4>
          <div className="flex flex-wrap gap-2">
            {related.map((item) => (
              <button
                key={item.id}
                onClick={() => onSuggestionSelect(item.phrase)}
                className="bg-slate-50 hover:bg-indigo-50 text-slate-600 hover:text-indigo-700 border border-slate-200 hover:border-indigo-200 px-3 py-1.5 rounded-xl transition cursor-pointer"
              >
                {item.phrase}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
