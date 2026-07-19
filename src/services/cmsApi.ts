/**
 * CMS APIs client - BrahmaVidya Galaxy
 */

import { ApiResponse } from './api';

// Helper to make API requests with Authorization header
async function request<T>(url: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
  const token = localStorage.getItem('bvg_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      const errorText = await res.text();
      return {
        success: false,
        message: errorText || `HTTP error! status: ${res.status}`,
      };
    }
    const data = await res.json();
    return {
      success: true,
      data,
    };
  } catch (error) {
    console.error(`CMS API error on ${url}:`, error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Unknown network failure',
    };
  }
}

export const cmsApi = {
  articles: {
    list: (params?: Record<string, string>) => {
      const query = params ? new URLSearchParams(params).toString() : '';
      return request<any>(`/api/v1/cms/articles/${query ? '?' + query : ''}`);
    },
    retrieve: (id: string) => request<any>(`/api/v1/cms/articles/${id}/`),
    create: (data: any) => request<any>('/api/v1/cms/articles/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (id: string, data: any) => request<any>(`/api/v1/cms/articles/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => request<any>(`/api/v1/cms/articles/${id}/`, {
      method: 'DELETE',
    }),
    restore: (id: string) => request<any>(`/api/v1/cms/articles/${id}/restore/`, {
      method: 'POST',
    }),
    publish: (id: string) => request<any>(`/api/v1/cms/articles/${id}/publish/`, {
      method: 'POST',
    }),
    unpublish: (id: string) => request<any>(`/api/v1/cms/articles/${id}/unpublish/`, {
      method: 'POST',
    }),
    preview: (id: string) => request<any>(`/api/v1/cms/articles/${id}/preview/`),
    schedule: (id: string, scheduledAt: string) => request<any>(`/api/v1/cms/articles/${id}/schedule/`, {
      method: 'POST',
      body: JSON.stringify({ scheduled_at: scheduledAt }),
    }),
    bulkPublish: (ids: string[]) => request<any>('/api/v1/cms/articles/bulk-publish/', {
      method: 'POST',
      body: JSON.stringify({ ids }),
    }),
    bulkDelete: (ids: string[]) => request<any>('/api/v1/cms/articles/bulk-delete/', {
      method: 'POST',
      body: JSON.stringify({ ids }),
    }),
  },

  categories: {
    list: (params?: Record<string, string>) => {
      const query = params ? new URLSearchParams(params).toString() : '';
      return request<any>(`/api/v1/cms/categories/${query ? '?' + query : ''}`);
    },
    retrieve: (id: string) => request<any>(`/api/v1/cms/categories/${id}/`),
    create: (data: any) => request<any>('/api/v1/cms/categories/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (id: string, data: any) => request<any>(`/api/v1/cms/categories/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => request<any>(`/api/v1/cms/categories/${id}/`, {
      method: 'DELETE',
    }),
    restore: (id: string) => request<any>(`/api/v1/cms/categories/${id}/restore/`, {
      method: 'POST',
    }),
  },

  tags: {
    list: (params?: Record<string, string>) => {
      const query = params ? new URLSearchParams(params).toString() : '';
      return request<any>(`/api/v1/cms/tags/${query ? '?' + query : ''}`);
    },
    retrieve: (id: string) => request<any>(`/api/v1/cms/tags/${id}/`),
    create: (data: any) => request<any>('/api/v1/cms/tags/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (id: string, data: any) => request<any>(`/api/v1/cms/tags/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => request<any>(`/api/v1/cms/tags/${id}/`, {
      method: 'DELETE',
    }),
  },

  authors: {
    list: (params?: Record<string, string>) => {
      const query = params ? new URLSearchParams(params).toString() : '';
      return request<any>(`/api/v1/cms/authors/${query ? '?' + query : ''}`);
    },
    retrieve: (id: string) => request<any>(`/api/v1/cms/authors/${id}/`),
    create: (data: any) => request<any>('/api/v1/cms/authors/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (id: string, data: any) => request<any>(`/api/v1/cms/authors/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => request<any>(`/api/v1/cms/authors/${id}/`, {
      method: 'DELETE',
    }),
  },

  media: {
    list: (params?: Record<string, string>) => {
      const query = params ? new URLSearchParams(params).toString() : '';
      return request<any>(`/api/v1/cms/media/${query ? '?' + query : ''}`);
    },
    retrieve: (id: string) => request<any>(`/api/v1/cms/media/${id}/`),
    create: (formData: FormData) => {
      const token = localStorage.getItem('bvg_token');
      return fetch('/api/v1/cms/media/', {
        method: 'POST',
        headers: {
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
        body: formData,
      }).then(async res => {
        if (!res.ok) {
          const err = await res.text();
          return { success: false, message: err };
        }
        const data = await res.json();
        return { success: true, data };
      }).catch(error => ({ success: false, message: error.message }));
    },
    update: (id: string, data: any) => request<any>(`/api/v1/cms/media/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => request<any>(`/api/v1/cms/media/${id}/`, {
      method: 'DELETE',
    }),
  },

  blocks: {
    list: (params?: Record<string, string>) => {
      const query = params ? new URLSearchParams(params).toString() : '';
      return request<any>(`/api/v1/cms/blocks/${query ? '?' + query : ''}`);
    },
    retrieve: (id: string) => request<any>(`/api/v1/cms/blocks/${id}/`),
    create: (data: any) => request<any>('/api/v1/cms/blocks/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (id: string, data: any) => request<any>(`/api/v1/cms/blocks/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => request<any>(`/api/v1/cms/blocks/${id}/`, {
      method: 'DELETE',
    }),
  },

  templates: {
    list: (params?: Record<string, string>) => {
      const query = params ? new URLSearchParams(params).toString() : '';
      return request<any>(`/api/v1/cms/templates/${query ? '?' + query : ''}`);
    },
    retrieve: (id: string) => request<any>(`/api/v1/cms/templates/${id}/`),
    create: (data: any) => request<any>('/api/v1/cms/templates/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (id: string, data: any) => request<any>(`/api/v1/cms/templates/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => request<any>(`/api/v1/cms/templates/${id}/`, {
      method: 'DELETE',
    }),
  },

  workflow: {
    list: (params?: Record<string, string>) => {
      const query = params ? new URLSearchParams(params).toString() : '';
      return request<any>(`/api/v1/cms/workflow/${query ? '?' + query : ''}`);
    },
    retrieve: (id: string) => request<any>(`/api/v1/cms/workflow/${id}/`),
    create: (data: any) => request<any>('/api/v1/cms/workflow/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (id: string, data: any) => request<any>(`/api/v1/cms/workflow/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => request<any>(`/api/v1/cms/workflow/${id}/`, {
      method: 'DELETE',
    }),
    transition: (id: string, toStatus: string, comment?: string, assignedTo?: string, dueDate?: string) =>
      request<any>(`/api/v1/cms/workflow/${id}/transition/`, {
        method: 'POST',
        body: JSON.stringify({
          to_status: toStatus,
          comment,
          assigned_to: assignedTo,
          due_date: dueDate,
        }),
      }),
  },

  revisions: {
    list: (params?: Record<string, string>) => {
      const query = params ? new URLSearchParams(params).toString() : '';
      return request<any>(`/api/v1/cms/revisions/${query ? '?' + query : ''}`);
    },
    retrieve: (id: string) => request<any>(`/api/v1/cms/revisions/${id}/`),
    rollback: (id: string) => request<any>(`/api/v1/cms/revisions/${id}/rollback/`, {
      method: 'POST',
    }),
  },

  redirects: {
    list: (params?: Record<string, string>) => {
      const query = params ? new URLSearchParams(params).toString() : '';
      return request<any>(`/api/v1/cms/redirects/${query ? '?' + query : ''}`);
    },
    retrieve: (id: string) => request<any>(`/api/v1/cms/redirects/${id}/`),
    create: (data: any) => request<any>('/api/v1/cms/redirects/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (id: string, data: any) => request<any>(`/api/v1/cms/redirects/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => request<any>(`/api/v1/cms/redirects/${id}/`, {
      method: 'DELETE',
    }),
  },

  audit: {
    list: (params?: Record<string, string>) => {
      const query = params ? new URLSearchParams(params).toString() : '';
      return request<any>(`/api/v1/cms/audit/${query ? '?' + query : ''}`);
    },
    retrieve: (id: string) => request<any>(`/api/v1/cms/audit/${id}/`),
  },

  search: {
    query: (params?: Record<string, string>) => {
      const query = params ? new URLSearchParams(params).toString() : '';
      return request<any>(`/api/v1/cms/search/${query ? '?' + query : ''}`);
    },
  },

  faq: {
    list: (params?: Record<string, string>) => {
      const query = params ? new URLSearchParams(params).toString() : '';
      return request<any>(`/api/v1/cms/faq/${query ? '?' + query : ''}`);
    },
    retrieve: (id: string) => request<any>(`/api/v1/cms/faq/${id}/`),
    create: (data: any) => request<any>('/api/v1/cms/faq/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (id: string, data: any) => request<any>(`/api/v1/cms/faq/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => request<any>(`/api/v1/cms/faq/${id}/`, {
      method: 'DELETE',
    }),
    restore: (id: string) => request<any>(`/api/v1/cms/faq/${id}/restore/`, {
      method: 'POST',
    }),
  },

  reactions: {
    list: (params?: Record<string, string>) => {
      const query = params ? new URLSearchParams(params).toString() : '';
      return request<any>(`/api/v1/cms/reactions/${query ? '?' + query : ''}`);
    },
    create: (data: any) => request<any>('/api/v1/cms/reactions/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => request<any>(`/api/v1/cms/reactions/${id}/`, {
      method: 'DELETE',
    }),
  },
};
