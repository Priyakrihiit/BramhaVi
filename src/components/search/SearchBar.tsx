import React, { useState, useEffect } from 'react';
import { Search, X, Loader } from 'lucide-react';
import { searchApi } from '../../services/searchApi';
import { Autocomplete } from './Autocomplete';

interface SearchBarProps {
  query: string;
  setQuery: (q: string) => void;
  onSearch: (query: string) => void;
  loading: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({ query, setQuery, onSearch, loading }) => {
  const [completions, setCompletions] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    if (!query.trim()) {
      setCompletions([]);
      return;
    }
    const delayDebounce = setTimeout(async () => {
      const res = await searchApi.autocomplete(query);
      if (res.success && res.data) {
        setCompletions(res.data.suggestions);
      }
    }, 150);

    return () => clearTimeout(delayDebounce);
  }, [query]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowDropdown(false);
    onSearch(query);
  };

  const handleSelectCompletion = (val: string) => {
    setQuery(val);
    setShowDropdown(false);
    onSearch(val);
  };

  return (
    <form onSubmit={handleSubmit} className="relative max-w-2xl mx-auto w-full z-30">
      <div className="relative flex items-center">
        <Search className="absolute left-4 h-5 w-5 text-slate-400" />
        <input
          type="text"
          placeholder="Search courses, articles, textbooks, resumes..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setShowDropdown(true);
          }}
          onFocus={() => setShowDropdown(true)}
          className="w-full pl-12 pr-28 py-3.5 bg-white text-slate-900 rounded-2xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-sans text-sm shadow-md"
        />
        <div className="absolute right-3 flex items-center gap-1">
          {query && (
            <button
              type="button"
              onClick={() => {
                setQuery('');
                setCompletions([]);
              }}
              className="p-1 hover:bg-slate-100 rounded-full text-slate-400 hover:text-slate-600 transition"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          {loading && <Loader className="h-4 w-4 text-indigo-500 animate-spin mr-1" />}
          <button
            type="submit"
            className="bg-indigo-600 text-white hover:bg-indigo-700 text-xs font-bold px-4 py-2 rounded-xl transition shadow cursor-pointer"
          >
            Search
          </button>
        </div>
      </div>
      {showDropdown && completions.length > 0 && (
        <Autocomplete
          completions={completions}
          onSelect={handleSelectCompletion}
          onClose={() => setShowDropdown(false)}
        />
      )}
    </form>
  );
};
