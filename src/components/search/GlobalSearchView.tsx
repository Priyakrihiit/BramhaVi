import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { searchApi, SearchDocument, SearchQueryResponse } from '../../services/searchApi';
import { SearchBar } from './SearchBar';
import { SearchResults } from './SearchResults';
import { SearchFilters } from './SearchFilters';
import { SuggestionPanel } from './SuggestionPanel';
import { TrendingPanel } from './TrendingPanel';
import { RecentSearches } from './RecentSearches';
import { AdvancedSearch } from './AdvancedSearch';
import { SearchDashboard } from './SearchDashboard';
import { Layers, ShieldCheck, Database, RefreshCw, LayoutGrid } from 'lucide-react';

export const GlobalSearchView: React.FC = () => {
  const { currentUser } = useAuthStore();
  const isAdmin = currentUser?.is_staff || false;

  // View switch: search query mode or admin dashboard mode
  const [isAdminView, setIsAdminView] = useState(false);

  // Search parameters
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Advanced options
  const [selectedScope, setSelectedScope] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [facetsParam, setFacetsParam] = useState('categories,tags');

  // Search results payload
  const [payload, setPayload] = useState<SearchQueryResponse>({
    results: [],
    count: 0,
    next: null,
    previous: null,
    facets: {},
    spelling_suggestion: null
  });

  // Selected facet filters
  const [selectedFilters, setSelectedFilters] = useState<Record<string, string[]>>({});
  const [currentPage, setCurrentPage] = useState(1);

  // Trigger search execution
  const executeSearch = async (searchTerm: string, pageNum: number = 1) => {
    if (!searchTerm.trim()) return;

    setLoading(true);
    setHasSearched(true);
    setCurrentPage(pageNum);

    // Compile active facets comma-separated string from selected filters list
    const activeFacetsString = facetsParam;

    const res = await searchApi.query(
      searchTerm,
      selectedScope || undefined,
      selectedType || undefined,
      activeFacetsString || undefined,
      pageNum
    );

    setLoading(false);
    if (res.success && res.data) {
      setPayload(res.data);
      // Trigger recent searches widget redraw
      setRefreshTrigger(prev => prev + 1);
    }
  };

  // Perform initial search trigger when scope changes
  useEffect(() => {
    if (query) {
      executeSearch(query, 1);
    }
  }, [selectedScope, selectedType]);

  // Handle facet filter toggles
  const handleFilterChange = (facetName: string, value: string) => {
    const active = selectedFilters[facetName] || [];
    const updated = active.includes(value)
      ? active.filter(v => v !== value)
      : [...active, value];

    const nextFilters = { ...selectedFilters, [facetName]: updated };
    setSelectedFilters(nextFilters);

    // Apply client-side facet result filtering
    // In production, filters are passed as query parameters, here we can filter the payload results locally:
    // This allows instant filtering without a database re-query hit!
  };

  const handleClearFilters = () => {
    setSelectedFilters({});
  };

  const handleSelectSuggestion = (val: string) => {
    setQuery(val);
    executeSearch(val, 1);
  };

  const handleResultClick = async (doc: SearchDocument, position: number) => {
    // Log result CTR parameters
    const historyId = localStorage.getItem('last_search_history_id') || null;
    await searchApi.logClick(historyId, doc.id, position);
  };

  // Local filter result computations
  const getFilteredResults = () => {
    let list = payload.results;
    
    // Scan dynamic facet checkboxes
    Object.entries(selectedFilters).forEach(([facetName, values]) => {
      const activeValues = values as string[];
      if (activeValues.length === 0) return;
      list = list.filter(doc => {
        // Find mapped attribute key in SearchFacet register
        // For simplicity, match against entity_type, categories, or tags
        const attr = facetName.toLowerCase();
        let targetVal = '';
        if (attr === 'index' || attr === 'index_name') targetVal = doc.index_name;
        else if (attr === 'entity_type') targetVal = doc.entity_type;
        else if (attr === 'categories') targetVal = doc.categories || '';
        else if (attr === 'tags') targetVal = doc.tags || '';
        else if (doc.meta_data) {
          // Check inside meta_data object
          // Find matching key case-insensitive
          const matchKey = Object.keys(doc.meta_data).find(k => k.toLowerCase() === attr);
          if (matchKey) targetVal = String(doc.meta_data[matchKey]);
        }

        // Return true if values lists contains doc tag/category value
        return activeValues.some(v => targetVal.toLowerCase().includes(v.toLowerCase()));
      });
    });
    
    return list;
  };

  const filteredDocs = getFilteredResults();

  if (isAdminView && isAdmin) {
    return (
      <div id="search-admin-container" className="min-h-screen bg-slate-50 text-slate-900 font-sans">
        <div className="bg-slate-900 text-white px-6 py-3 flex items-center justify-between border-b border-slate-800 shadow-sm text-xs">
          <span className="font-bold flex items-center gap-1">
            <ShieldCheck className="h-4 w-4 text-indigo-400" /> Platform Search Admin Session
          </span>
          <button
            onClick={() => setIsAdminView(false)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-3 py-1.5 rounded-lg transition cursor-pointer"
          >
            Back to Global Search
          </button>
        </div>
        <SearchDashboard />
      </div>
    );
  }

  return (
    <div id="global-search-root" className="min-h-screen bg-slate-50 text-slate-900 pb-12 font-sans text-xs">
      {/* Brand Search Banner */}
      <div className="bg-slate-900 text-white py-12 px-6 shadow-sm border-b border-slate-800">
        <div className="max-w-4xl mx-auto text-center space-y-4">
          <div className="flex items-center justify-center gap-2">
            <span className="bg-indigo-500/20 text-indigo-300 text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase tracking-wider">
              Unified Platform Search
            </span>
            {isAdmin && (
              <button
                onClick={() => setIsAdminView(true)}
                className="bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase tracking-wider flex items-center gap-1 transition cursor-pointer border border-emerald-500/30"
              >
                <ShieldCheck className="h-3.5 w-3.5" /> Admin Panel
              </button>
            )}
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Search BrahmaVidya Galaxy</h1>
          <p className="text-slate-400 max-w-xl mx-auto leading-relaxed">
            Crawls and matches documents from LMS Courses, CMS Articles, DAM Media Library, Marketplace Books, Portfolio Resumes, and active Jobs instantly.
          </p>

          <div className="mt-6">
            <SearchBar
              query={query}
              setQuery={setQuery}
              onSearch={(val) => executeSearch(val, 1)}
              loading={loading}
            />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 mt-8">
        {/* Spelling and related recommendations */}
        {hasSearched && (
          <div className="mb-6 max-w-4xl mx-auto">
            <SuggestionPanel
              query={query}
              spellingSuggestion={payload.spelling_suggestion}
              onSuggestionSelect={handleSelectSuggestion}
            />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 items-start">
          {/* LEFT SIDEBAR: FILTERS, RECENT, TRENDING, ADVANCED OPTIONS */}
          <div className="space-y-6 lg:sticky lg:top-6">
            {/* dynamic dynamic sidebar facets */}
            {hasSearched && Object.keys(payload.facets).length > 0 && (
              <SearchFilters
                facets={payload.facets}
                selectedFilters={selectedFilters}
                onFilterChange={handleFilterChange}
                onClearFilters={handleClearFilters}
              />
            )}

            <AdvancedSearch
              selectedScope={selectedScope}
              setSelectedScope={setSelectedScope}
              selectedType={selectedType}
              setSelectedType={setSelectedType}
              facetsParam={facetsParam}
              setFacetsParam={setFacetsParam}
            />

            <RecentSearches
              onSelectRecent={handleSelectSuggestion}
              refreshTrigger={refreshTrigger}
            />

            <TrendingPanel onSelectTerm={handleSelectSuggestion} />
          </div>

          {/* RIGHT COLUMN: SEARCH RESULTS */}
          <div className="lg:col-span-3 space-y-6">
            {loading ? (
              <div className="bg-white border border-slate-200 rounded-3xl p-16 text-center shadow-sm">
                <RefreshCw className="h-8 w-8 text-indigo-500 animate-spin mx-auto mb-2" />
                <p className="text-slate-500 font-medium">Crawling indices, parsing vector maps...</p>
              </div>
            ) : !hasSearched ? (
              <div className="bg-white border border-slate-200 rounded-3xl p-16 text-center shadow-sm max-w-lg mx-auto">
                <LayoutGrid className="h-10 w-10 text-slate-300 mx-auto mb-2" />
                <h3 className="font-bold text-slate-800 text-sm">Enter a search keyword</h3>
                <p className="text-slate-400 mt-1">
                  Query items by titles, authors, abstract tags, or dynamic categories to display matched documents.
                </p>
              </div>
            ) : filteredDocs.length === 0 ? (
              <div className="bg-white border border-slate-200 rounded-3xl p-16 text-center shadow-sm max-w-lg mx-auto">
                <Database className="h-10 w-10 text-slate-300 mx-auto mb-2" />
                <h3 className="font-bold text-slate-800 text-sm">No matched results</h3>
                <p className="text-slate-400 mt-1">
                  We could not find any document index mappings matching query "{query}" with the current filters.
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Result Info Header */}
                <div className="flex items-center justify-between bg-white px-5 py-3 rounded-2xl border border-slate-200 shadow-sm">
                  <span className="font-bold text-slate-500 uppercase tracking-wider font-mono">
                    Results for "{query}"
                  </span>
                  <span className="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full font-bold font-mono">
                    {filteredDocs.length} matches
                  </span>
                </div>

                {/* Match Documents List */}
                <SearchResults
                  results={filteredDocs}
                  onResultClick={handleResultClick}
                />

                {/* Pagination Controls */}
                {payload.count > 10 && (
                  <div className="flex justify-center items-center gap-2 pt-4">
                    <button
                      disabled={!payload.previous}
                      onClick={() => executeSearch(query, currentPage - 1)}
                      className="px-4 py-2 border border-slate-200 rounded-xl bg-white hover:bg-slate-50 font-bold transition disabled:opacity-50 cursor-pointer"
                    >
                      Previous
                    </button>
                    <span className="text-slate-500 font-mono">
                      Page {currentPage}
                    </span>
                    <button
                      disabled={!payload.next}
                      onClick={() => executeSearch(query, currentPage + 1)}
                      className="px-4 py-2 border border-slate-200 rounded-xl bg-white hover:bg-slate-50 font-bold transition disabled:opacity-50 cursor-pointer"
                    >
                      Next
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
