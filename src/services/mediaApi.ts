/**
 * Enterprise DAM API client - BrahmaVidya Galaxy
 */

import { ApiResponse } from './api';

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
    console.error(`DAM API error on ${url}:`, error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Unknown network failure',
    };
  }
}

export const mediaApi = {
  folders: {
    list: () => request<any>('/api/v1/cms/folders/'),
    create: (data: any) => request<any>('/api/v1/cms/folders/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => request<any>(`/api/v1/cms/folders/${id}/`, {
      method: 'DELETE',
    }),
  },
  collections: {
    list: () => request<any>('/api/v1/cms/collections/'),
    create: (data: any) => request<any>('/api/v1/cms/collections/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => request<any>(`/api/v1/cms/collections/${id}/`, {
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
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        body: formData,
      }).then(async (res) => {
        if (!res.ok) return { success: false, message: 'Upload failed.' };
        return { success: true, data: await res.json() };
      }).catch(err => ({ success: false, message: err.message }));
    },
    delete: (id: string) => request<any>(`/api/v1/cms/media/${id}/`, {
      method: 'DELETE',
    }),
    favorite: (id: string) => request<any>(`/api/v1/cms/media/${id}/favorite/`, {
      method: 'POST',
    }),
    download: (id: string) => request<any>(`/api/v1/cms/media/${id}/download/`, {
      method: 'POST',
    }),
    share: (id: string, data: any) => request<any>(`/api/v1/cms/media/${id}/share/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  },
  versions: {
    list: (mediaFileId: string) => request<any>(`/api/v1/cms/media-versions/?media_file=${mediaFileId}`),
  },
  workflows: {
    list: () => request<any>('/api/v1/cms/media-workflows/'),
    transition: (id: string, data: any) => request<any>(`/api/v1/cms/media-workflows/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  },
};
