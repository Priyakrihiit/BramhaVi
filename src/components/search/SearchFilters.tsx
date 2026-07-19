import React from 'react';
import { Filter } from 'lucide-react';

interface SearchFiltersProps {
  facets: Record<string, Record<string, number>>;
  selectedFilters: Record<string, string[]>;
  onFilterChange: (facetName: string, value: string) => void;
  onClearFilters: () => void;
}

export const SearchFilters: React.FC<SearchFiltersProps> = ({
  facets,
  selectedFilters,
  onFilterChange,
  onClearFilters
}) => {
  const hasSelections = Object.values(selectedFilters).some(arr => (arr as string[]).length > 0);

  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6 font-sans">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center gap-1.5 font-mono">
          <Filter className="h-4 w-4 text-indigo-600" /> Filters
        </h3>
        {hasSelections && (
          <button
            onClick={onClearFilters}
            className="text-[10px] font-bold text-rose-500 hover:text-rose-700 transition cursor-pointer"
          >
            Clear All
          </button>
        )}
      </div>

      <div className="space-y-6">
        {Object.entries(facets).map(([facetName, values]) => {
          const options = Object.entries(values);
          if (options.length === 0) return null;

          return (
            <div key={facetName} className="space-y-2.5">
              <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider font-mono">
                {facetName}
              </h4>
              <div className="space-y-1.5">
                {options.map(([val, count]) => {
                  const isChecked = (selectedFilters[facetName] || []).includes(val);
                  return (
                    <label
                      key={val}
                      className="flex items-center justify-between text-xs text-slate-600 hover:text-slate-800 transition cursor-pointer"
                    >
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => onFilterChange(facetName, val)}
                          className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 h-3.5 w-3.5"
                        />
                        <span>{val}</span>
                      </div>
                      <span className="bg-slate-100 text-slate-500 text-[10px] font-mono px-1.5 py-0.2 rounded-full">
                        {count}
                      </span>
                    </label>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
