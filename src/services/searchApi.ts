import { ApiResponse } from './api';

export interface SearchDocument {
  id: string;
  index: string;
  index_name: string;
  entity_type: string;
  entity_id: string;
  title: string;
  excerpt: string;
  body: string;
  tags: string;
  categories: string;
  author_name: string;
  url_path: string;
  is_published: boolean;
  published_at: string;
  meta_data: Record<string, any>;
  relevance_score: number;
}

export interface SearchHistory {
  id: string;
  user?: string;
  user_email?: string;
  query: string;
  filters_applied: Record<string, any>;
  results_count: number;
  searched_at: string;
}

export interface SearchTerm {
  id: string;
  term: string;
  frequency: number;
  last_queried_at: string;
}

export interface SearchSuggestion {
  id: string;
  phrase: string;
  weight: number;
  is_active: boolean;
}

export interface SearchRanking {
  id: string;
  document: string;
  document_title?: string;
  query: string;
  boost_score: number;
  is_pinned: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface SearchAnalytics {
  id: string;
  query_string: string;
  total_queries: number;
  total_results: number;
  click_through_rate: number;
  avg_dwell_time: number;
}

export interface SearchFacet {
  id: string;
  name: string;
  field_name: string;
  is_active: boolean;
}

export interface SearchSynonym {
  id: string;
  term: string;
  synonyms: string;
  is_active: boolean;
}

export interface SearchQueryResponse {
  results: SearchDocument[];
  count: number;
  next: string | null;
  previous: string | null;
  facets: Record<string, Record<string, number>>;
  spelling_suggestion: string | null;
}

const BASE_URL = '/api/v1/search';

async function request<T>(url: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
  const token = localStorage.getItem('bvg_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  try {
    const res = await fetch(url, { ...options, headers });
    if (res.status === 204) {
      return { success: true } as any;
    }
    const data = await res.json();
    return {
      success: res.ok,
      data: res.ok ? data : undefined,
      message: res.ok ? undefined : (data.error || 'Request failed'),
    };
  } catch (error) {
    console.error(`API request error on ${url}:`, error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Unknown network failure',
    };
  }
}

export const searchApi = {
  query: (q: string, index?: string, type?: string, facets?: string, page: number = 1) => {
    let url = `${BASE_URL}/query/?q=${encodeURIComponent(q)}&page=${page}`;
    if (index) url += `&index=${encodeURIComponent(index)}`;
    if (type) url += `&entity_type=${encodeURIComponent(type)}`;
    if (facets) url += `&facets=${encodeURIComponent(facets)}`;
    return request<SearchQueryResponse>(url);
  },

  autocomplete: (q: string) =>
    request<{ suggestions: string[] }>(`${BASE_URL}/autocomplete/?q=${encodeURIComponent(q)}`),

  suggestions: (q: string) =>
    request<SearchSuggestion[]>(`${BASE_URL}/suggestions/?q=${encodeURIComponent(q)}`),

  logClick: (historyId: string | null, documentId: string, position: number) =>
    request<{ status: string; id: string }>(`${BASE_URL}/click/`, {
      method: 'POST',
      body: JSON.stringify({ history_id: historyId, document_id: documentId, position }),
    }),

  getHistory: () =>
    request<SearchHistory[]>(`${BASE_URL}/history/`),

  deleteHistory: (id: string) =>
    request<void>(`${BASE_URL}/history/${id}/`, { method: 'DELETE' }),

  getPopular: (limit: number = 10) =>
    request<SearchTerm[]>(`${BASE_URL}/popular/?limit=${limit}`),

  getRankings: () =>
    request<SearchRanking[]>(`${BASE_URL}/ranking/`),

  createRanking: (data: Partial<SearchRanking>) =>
    request<SearchRanking>(`${BASE_URL}/ranking/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  deleteRanking: (id: string) =>
    request<void>(`${BASE_URL}/ranking/${id}/`, { method: 'DELETE' }),

  getAnalytics: () =>
    request<SearchAnalytics[]>(`${BASE_URL}/analytics/`),

  getFacets: () =>
    request<SearchFacet[]>(`${BASE_URL}/facets/`),

  createFacet: (data: Partial<SearchFacet>) =>
    request<SearchFacet>(`${BASE_URL}/facets/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  deleteFacet: (id: string) =>
    request<void>(`${BASE_URL}/facets/${id}/`, { method: 'DELETE' }),

  getSynonyms: () =>
    request<SearchSynonym[]>(`${BASE_URL}/synonyms/`),

  createSynonym: (data: Partial<SearchSynonym>) =>
    request<SearchSynonym>(`${BASE_URL}/synonyms/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  deleteSynonym: (id: string) =>
    request<void>(`${BASE_URL}/synonyms/${id}/`, { method: 'DELETE' }),
};
