import React, { useState, useEffect } from 'react';
import { searchApi, SearchRanking, SearchSynonym, SearchFacet } from '../../services/searchApi';
import { Sliders, Pin, ArrowUp, Plus, Trash2, Tag, HelpCircle } from 'lucide-react';

export const SearchAdmin: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'rankings' | 'synonyms' | 'facets'>('rankings');
  const [rankings, setRankings] = useState<SearchRanking[]>([]);
  const [synonyms, setSynonyms] = useState<SearchSynonym[]>([]);
  const [facets, setFacets] = useState<SearchFacet[]>([]);

  // Form states
  const [rankingForm, setRankingForm] = useState({ document: '', query: '', boost_score: 1.0, is_pinned: false });
  const [synonymForm, setSynonymForm] = useState({ term: '', synonyms: '' });
  const [facetForm, setFacetForm] = useState({ name: '', field_name: '' });

  const [message, setMessage] = useState('');

  const fetchAll = async () => {
    const resRank = await searchApi.getRankings();
    if (resRank.success && resRank.data) setRankings(resRank.data);

    const resSyn = await searchApi.getSynonyms();
    if (resSyn.success && resSyn.data) setSynonyms(resSyn.data);

    const resFacet = await searchApi.getFacets();
    if (resFacet.success && resFacet.data) setFacets(resFacet.data);
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const handleCreateRanking = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await searchApi.createRanking(rankingForm);
    if (res.success) {
      setMessage('Ranking override created successfully.');
      setRankingForm({ document: '', query: '', boost_score: 1.0, is_pinned: false });
      fetchAll();
    } else {
      setMessage(`Error: ${res.message}`);
    }
  };

  const handleDeleteRanking = async (id: string) => {
    const res = await searchApi.deleteRanking(id);
    if (res.success) fetchAll();
  };

  const handleCreateSynonym = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await searchApi.createSynonym(synonymForm);
    if (res.success) {
      setMessage('Synonym map created successfully.');
      setSynonymForm({ term: '', synonyms: '' });
      fetchAll();
    } else {
      setMessage(`Error: ${res.message}`);
    }
  };

  const handleDeleteSynonym = async (id: string) => {
    const res = await searchApi.deleteSynonym(id);
    if (res.success) fetchAll();
  };

  const handleCreateFacet = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await searchApi.createFacet({ ...facetForm, is_active: true });
    if (res.success) {
      setMessage('Search facet created successfully.');
      setFacetForm({ name: '', field_name: '' });
      fetchAll();
    } else {
      setMessage(`Error: ${res.message}`);
    }
  };

  const handleDeleteFacet = async (id: string) => {
    const res = await searchApi.deleteFacet(id);
    if (res.success) fetchAll();
  };

  return (
    <div className="space-y-6 font-sans text-xs">
      {/* Settings Navigation Bar */}
      <div className="flex border-b border-slate-200">
        {(['rankings', 'synonyms', 'facets'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => {
              setActiveTab(tab);
              setMessage('');
            }}
            className={`px-6 py-2.5 font-bold uppercase tracking-wider font-mono border-b-2 cursor-pointer transition ${
              activeTab === tab
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-400 hover:text-slate-600'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {message && (
        <div className="p-3 bg-indigo-50 border border-indigo-100 rounded-xl text-indigo-700 font-semibold">
          {message}
        </div>
      )}

      {/* Tab 1: Rankings Overrides */}
      {activeTab === 'rankings' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center gap-1.5 font-mono border-b border-slate-100 pb-2">
              <Plus className="h-4 w-4 text-indigo-600" /> Create Override
            </h3>
            <form onSubmit={handleCreateRanking} className="space-y-3.5">
              <div className="space-y-1">
                <label className="font-bold text-slate-500 uppercase font-mono text-[9px] block">Document ID (UUID)</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 7bf3b680-2a25-4a3b-8401-69095d9f9f17"
                  value={rankingForm.document}
                  onChange={(e) => setRankingForm({ ...rankingForm, document: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
              <div className="space-y-1">
                <label className="font-bold text-slate-500 uppercase font-mono text-[9px] block">Trigger Query Term</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. python"
                  value={rankingForm.query}
                  onChange={(e) => setRankingForm({ ...rankingForm, query: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
              <div className="space-y-1">
                <label className="font-bold text-slate-500 uppercase font-mono text-[9px] block">Boost score factor</label>
                <input
                  type="number"
                  step="0.1"
                  required
                  value={rankingForm.boost_score}
                  onChange={(e) => setRankingForm({ ...rankingForm, boost_score: parseFloat(e.target.value) })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
              <div className="flex items-center gap-2 py-1.5">
                <input
                  type="checkbox"
                  id="is_pinned"
                  checked={rankingForm.is_pinned}
                  onChange={(e) => setRankingForm({ ...rankingForm, is_pinned: e.target.checked })}
                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 h-4 w-4 cursor-pointer"
                />
                <label htmlFor="is_pinned" className="font-bold text-slate-600 cursor-pointer">
                  Pin result to top position
                </label>
              </div>
              <button
                type="submit"
                className="w-full bg-indigo-600 text-white font-bold py-2.5 rounded-xl hover:bg-indigo-700 transition cursor-pointer shadow"
              >
                Add Override
              </button>
            </form>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm lg:col-span-2 space-y-4">
            <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center gap-1.5 font-mono">
              <Sliders className="h-4 w-4 text-indigo-600" /> Active Overrides ({rankings.length})
            </h3>
            {rankings.length === 0 ? (
              <div className="text-center py-10 text-slate-400">No active ranking overrides configured.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-slate-100 text-[10px] font-bold text-slate-400 uppercase font-mono">
                      <th className="py-2.5">Document Title</th>
                      <th className="py-2.5">Trigger Keyword</th>
                      <th className="py-2.5 text-center">Score Boost</th>
                      <th className="py-2.5 text-center">Pinned</th>
                      <th className="py-2.5 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50 text-slate-600">
                    {rankings.map((r) => (
                      <tr key={r.id} className="hover:bg-slate-50/50 transition">
                        <td className="py-2.5 font-semibold text-slate-800">{r.document_title || r.document}</td>
                        <td className="py-2.5 font-mono">{r.query}</td>
                        <td className="py-2.5 text-center font-mono flex items-center justify-center gap-0.5">
                          <ArrowUp className="h-3.5 w-3.5 text-indigo-500" /> {r.boost_score}
                        </td>
                        <td className="py-2.5 text-center">
                          {r.is_pinned ? (
                            <span className="inline-flex items-center gap-0.5 bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-mono font-bold">
                              <Pin className="h-3 w-3" /> Pinned
                            </span>
                          ) : (
                            <span className="text-slate-400 font-mono">-</span>
                          )}
                        </td>
                        <td className="py-2.5 text-right">
                          <button
                            onClick={() => handleDeleteRanking(r.id)}
                            className="text-slate-400 hover:text-rose-600 transition cursor-pointer"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Synonyms Mappings */}
      {activeTab === 'synonyms' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center gap-1.5 font-mono border-b border-slate-100 pb-2">
              <Plus className="h-4 w-4 text-indigo-600" /> Add Synonym map
            </h3>
            <form onSubmit={handleCreateSynonym} className="space-y-3.5">
              <div className="space-y-1">
                <label className="font-bold text-slate-500 uppercase font-mono text-[9px] block">Primary Term</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. exam"
                  value={synonymForm.term}
                  onChange={(e) => setSynonymForm({ ...synonymForm, term: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
              <div className="space-y-1">
                <label className="font-bold text-slate-500 uppercase font-mono text-[9px] block">Equivalent terms (comma separated)</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. test, assessment, quiz"
                  value={synonymForm.synonyms}
                  onChange={(e) => setSynonymForm({ ...synonymForm, synonyms: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
              <button
                type="submit"
                className="w-full bg-indigo-600 text-white font-bold py-2.5 rounded-xl hover:bg-indigo-700 transition cursor-pointer shadow"
              >
                Add Synonym Set
              </button>
            </form>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm lg:col-span-2 space-y-4">
            <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center gap-1.5 font-mono">
              <HelpCircle className="h-4 w-4 text-indigo-600" /> Synonym Maps ({synonyms.length})
            </h3>
            {synonyms.length === 0 ? (
              <div className="text-center py-10 text-slate-400">No synonyms maps configured.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-slate-100 text-[10px] font-bold text-slate-400 uppercase font-mono">
                      <th className="py-2.5">Trigger Term</th>
                      <th className="py-2.5">Synonyms list</th>
                      <th className="py-2.5 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50 text-slate-600">
                    {synonyms.map((s) => (
                      <tr key={s.id} className="hover:bg-slate-50/50 transition">
                        <td className="py-2.5 font-semibold text-slate-800">{s.term}</td>
                        <td className="py-2.5">{s.synonyms}</td>
                        <td className="py-2.5 text-right">
                          <button
                            onClick={() => handleDeleteSynonym(s.id)}
                            className="text-slate-400 hover:text-rose-600 transition cursor-pointer"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Search Facets */}
      {activeTab === 'facets' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center gap-1.5 font-mono border-b border-slate-100 pb-2">
              <Plus className="h-4 w-4 text-indigo-600" /> Configure Facet
            </h3>
            <form onSubmit={handleCreateFacet} className="space-y-3.5">
              <div className="space-y-1">
                <label className="font-bold text-slate-500 uppercase font-mono text-[9px] block">Facet Name (Visual Label)</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Difficulty Level"
                  value={facetForm.name}
                  onChange={(e) => setFacetForm({ ...facetForm, name: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
              <div className="space-y-1">
                <label className="font-bold text-slate-500 uppercase font-mono text-[9px] block">Field Key (JSON metadata path)</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. level"
                  value={facetForm.field_name}
                  onChange={(e) => setFacetForm({ ...facetForm, field_name: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
              <button
                type="submit"
                className="w-full bg-indigo-600 text-white font-bold py-2.5 rounded-xl hover:bg-indigo-700 transition cursor-pointer shadow"
              >
                Register Facet
              </button>
            </form>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm lg:col-span-2 space-y-4">
            <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center gap-1.5 font-mono">
              <Tag className="h-4 w-4 text-indigo-600" /> Configured Facets ({facets.length})
            </h3>
            {facets.length === 0 ? (
              <div className="text-center py-10 text-slate-400">No dynamic facets configured yet.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-slate-100 text-[10px] font-bold text-slate-400 uppercase font-mono">
                      <th className="py-2.5">Display label</th>
                      <th className="py-2.5">JSON meta attribute key</th>
                      <th className="py-2.5 text-center">Status</th>
                      <th className="py-2.5 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50 text-slate-600">
                    {facets.map((f) => (
                      <tr key={f.id} className="hover:bg-slate-50/50 transition">
                        <td className="py-2.5 font-semibold text-slate-800">{f.name}</td>
                        <td className="py-2.5 font-mono">{f.field_name}</td>
                        <td className="py-2.5 text-center">
                          <span className="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-mono font-bold text-[9px]">
                            ACTIVE
                          </span>
                        </td>
                        <td className="py-2.5 text-right">
                          <button
                            onClick={() => handleDeleteFacet(f.id)}
                            className="text-slate-400 hover:text-rose-600 transition cursor-pointer"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
