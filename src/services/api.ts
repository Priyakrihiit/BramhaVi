/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { User, Role, Permission, NavigationMenu, Page, CourseStructure, Certificate, SystemSettings, Blog, Tutorial, Book, BookReview, PublishSubmission, RoyaltyStatement, WithdrawalRequest, Product, Order, ServiceRequest, Quotation, Transaction, Invoice } from '../types';

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  simulated?: boolean;
  status?: number;
  error?: string;
}

export interface AuthResponse {
  success: boolean;
  token?: string;
  user?: User;
  permissions?: string[];
  message?: string;
}

export interface PlatformStats {
  totalStudents: { value: string; change: string };
  totalTeachers: { value: string; change: string };
  totalCourses: { value: string; change: string };
  totalRevenue: { value: string; change: string };
  activeUsers: { value: string; change: string };
}

export interface ActivityLog {
  text: string;
  time: string;
  timestamp: string;
}

export interface TaskSummary {
  id: string;
  name: string;
  count: number;
  color: string;
}

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
    const data = await res.json();
    return data;
  } catch (error) {
    console.error(`API request error on ${url}:`, error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Unknown network failure',
    };
  }
}

export const api = {
  auth: {
    login: async (email: string): Promise<AuthResponse> => {
      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email }),
        });
        return await res.json();
      } catch (error) {
        return { success: false, message: 'Login connection failed' };
      }
    },
    getProfile: async (): Promise<AuthResponse> => {
      const token = localStorage.getItem('bvg_token');
      if (!token) return { success: false, message: 'No session token' };
      try {
        const res = await fetch('/api/auth/me', {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        return await res.json();
      } catch (error) {
        return { success: false, message: 'Failed fetching profile credentials' };
      }
    },
  },

  stats: {
    get: () => request<PlatformStats>('/api/stats'),
  },

  settings: {
    get: () => request<SystemSettings>('/api/settings'),
    update: (data: Partial<SystemSettings>) =>
      request<SystemSettings>('/api/settings', {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
  },

  menus: {
    list: () => request<NavigationMenu[]>('/api/menus'),
    create: (data: Omit<NavigationMenu, 'id'>) =>
      request<NavigationMenu>('/api/menus', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Partial<NavigationMenu>) =>
      request<NavigationMenu>(`/api/menus/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      request<void>(`/api/menus/${id}`, {
        method: 'DELETE',
      }),
  },

  pages: {
    list: () => request<Page[]>('/api/pages'),
    create: (data: Omit<Page, 'id'>) =>
      request<Page>('/api/pages', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Partial<Page>) =>
      request<Page>(`/api/pages/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      request<void>(`/api/pages/${id}`, {
        method: 'DELETE',
      }),
  },

  blogs: {
    list: (params?: { search?: string; author?: string; isPublished?: boolean; includeDeleted?: boolean; page?: number; limit?: number }) => {
      const q = new URLSearchParams();
      if (params) {
        if (params.search) q.set('search', params.search);
        if (params.author) q.set('author', params.author);
        if (params.isPublished !== undefined) q.set('isPublished', String(params.isPublished));
        if (params.includeDeleted !== undefined) q.set('includeDeleted', String(params.includeDeleted));
        if (params.page !== undefined) q.set('page', String(params.page));
        if (params.limit !== undefined) q.set('limit', String(params.limit));
      }
      const queryStr = q.toString();
      return request<Blog[]>(`/api/blogs${queryStr ? '?' + queryStr : ''}`);
    },
    get: (idOrSlug: string) => request<Blog>(`/api/blogs/${idOrSlug}`),
    create: (data: Omit<Blog, 'id'>) =>
      request<Blog>('/api/blogs', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (idOrSlug: string, data: Partial<Blog>) =>
      request<Blog>(`/api/blogs/${idOrSlug}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    delete: (idOrSlug: string) =>
      request<void>(`/api/blogs/${idOrSlug}`, {
        method: 'DELETE',
      }),
    restore: (idOrSlug: string) =>
      request<void>(`/api/blogs/${idOrSlug}/restore`, {
        method: 'POST',
      }),
  },

  tutorials: {
    list: (params?: { search?: string; author?: string; isPublished?: boolean; includeDeleted?: boolean; page?: number; limit?: number }) => {
      const q = new URLSearchParams();
      if (params) {
        if (params.search) q.set('search', params.search);
        if (params.author) q.set('author', params.author);
        if (params.isPublished !== undefined) q.set('isPublished', String(params.isPublished));
        if (params.includeDeleted !== undefined) q.set('includeDeleted', String(params.includeDeleted));
        if (params.page !== undefined) q.set('page', String(params.page));
        if (params.limit !== undefined) q.set('limit', String(params.limit));
      }
      const queryStr = q.toString();
      return request<Tutorial[]>(`/api/tutorials${queryStr ? '?' + queryStr : ''}`);
    },
    get: (idOrSlug: string) => request<Tutorial>(`/api/tutorials/${idOrSlug}`),
    create: (data: Omit<Tutorial, 'id'>) =>
      request<Tutorial>('/api/tutorials', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (idOrSlug: string, data: Partial<Tutorial>) =>
      request<Tutorial>(`/api/tutorials/${idOrSlug}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    delete: (idOrSlug: string) =>
      request<void>(`/api/tutorials/${idOrSlug}`, {
        method: 'DELETE',
      }),
    restore: (idOrSlug: string) =>
      request<void>(`/api/tutorials/${idOrSlug}/restore`, {
        method: 'POST',
      }),
  },

  roles: {
    list: () => request<Role[]>('/api/roles'),
    create: (data: Omit<Role, 'id'>) =>
      request<Role>('/api/roles', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Partial<Role>) =>
      request<Role>(`/api/roles/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
  },

  permissions: {
    list: () => request<Permission[]>('/api/permissions'),
  },

  courses: {
    list: () => request<CourseStructure[]>('/api/courses'),
    create: (data: Omit<CourseStructure, 'id'>) =>
      request<CourseStructure>('/api/courses', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Partial<CourseStructure>) =>
      request<CourseStructure>(`/api/courses/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      request<void>(`/api/courses/${id}`, {
        method: 'DELETE',
      }),
  },

  certificates: {
    list: () => request<Certificate[]>('/api/certificates'),
    verify: (hash: string) => request<Certificate>(`/api/certificates/verify/${hash}`),
    create: (data: { recipientName: string; courseTitle: string; recipientId?: string; courseId?: string; metadata?: any }) =>
      request<Certificate>('/api/certificates', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  activities: {
    list: () => request<ActivityLog[]>('/api/activities'),
  },

  tasks: {
    list: () => request<TaskSummary[]>('/api/tasks'),
  },

  ai: {
    chat: (message: string) =>
      request<{ text: string }>('/api/ai/chat', {
        method: 'POST',
        body: JSON.stringify({ message }),
      }),
    generateCurriculum: (title: string) =>
      request<Array<{
        type: 'MODULE';
        title: string;
        description: string;
        children: Array<{
          type: 'LESSON';
          title: string;
          description: string;
          duration: string;
        }>;
      }>>('/api/ai/generate-curriculum', {
        method: 'POST',
        body: JSON.stringify({ title }),
      }),
    generateQuiz: (topic: string) =>
      request<Array<{
        question: string;
        options: string[];
        answer: string;
      }>>('/api/ai/generate-quiz', {
        method: 'POST',
        body: JSON.stringify({ topic }),
      }),
  },

  books: {
    list: (params?: { category?: string; tag?: string; q?: string }) => {
      const qParams = new URLSearchParams();
      if (params?.category) qParams.set('category', params.category);
      if (params?.tag) qParams.set('tag', params.tag);
      if (params?.q) qParams.set('q', params.q);
      const url = `/api/books${qParams.toString() ? '?' + qParams.toString() : ''}`;
      return request<Book[]>(url);
    },
    get: (id: string) => request<Book & { reviews: BookReview[] }>(`/api/books/${id}`),
    addReview: (id: string, data: { userId: string; userName: string; rating: number; comment: string }) =>
      request<BookReview>(`/api/books/${id}/reviews`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    generateEbook: (courseId: string, title?: string) =>
      request<Book & { markdownContent: string }>('/api/books/generate-ebook', {
        method: 'POST',
        body: JSON.stringify({ courseId, title }),
      }),
  },

  publishing: {
    listSubmissions: (userId?: string) =>
      request<PublishSubmission[]>(`/api/publishing/submissions${userId ? '?userId=' + userId : ''}`),
    submit: (data: { userId: string; userName: string; title: string; category: string; description: string; fileFormat: 'PDF' | 'EPUB' }) =>
      request<PublishSubmission>('/api/publishing/submissions', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    paySubmission: (id: string, userId: string) =>
      request<PublishSubmission>(`/api/publishing/submissions/${id}/pay`, {
        method: 'POST',
        body: JSON.stringify({ userId }),
      }),
    reviewSubmission: (id: string, data: { status: 'APPROVED' | 'REJECTED'; adminNotes: string }) =>
      request<PublishSubmission>(`/api/publishing/submissions/${id}/review`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  royalties: {
    listStatements: (authorId?: string) =>
      request<RoyaltyStatement[]>(`/api/royalties/statements${authorId ? '?authorId=' + authorId : ''}`),
    listWithdrawals: (userId?: string) =>
      request<WithdrawalRequest[]>(`/api/royalties/withdrawals${userId ? '?userId=' + userId : ''}`),
    requestWithdraw: (data: { userId: string; amount: number; bankDetails?: string }) =>
      request<WithdrawalRequest>('/api/royalties/withdraw', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    approveWithdrawal: (id: string) =>
      request<WithdrawalRequest>(`/api/royalties/withdrawals/${id}/approve`, {
        method: 'POST',
      }),
  },

  marketplace: {
    listProducts: (params?: { type?: string; q?: string }) => {
      const qParams = new URLSearchParams();
      if (params?.type) qParams.set('type', params.type);
      if (params?.q) qParams.set('q', params.q);
      const url = `/api/marketplace/products${qParams.toString() ? '?' + qParams.toString() : ''}`;
      return request<Product[]>(url);
    },
    checkout: (data: { userId: string; items: Array<{ id: string; name: string; quantity: number }>; couponCode?: string; billingAddress?: string }) =>
      request<{ order: Order; invoice: Invoice }>('/api/marketplace/cart/checkout', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    listOrders: (userId?: string) =>
      request<Order[]>(`/api/marketplace/orders${userId ? '?userId=' + userId : ''}`),
    listInvoices: (userId?: string) =>
      request<Invoice[]>(`/api/marketplace/invoices${userId ? '?userId=' + userId : ''}`),
    submitServiceRequest: (data: { userId: string; userName: string; serviceType: string; description: string; budget: number }) =>
      request<ServiceRequest>('/api/marketplace/services/request', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    listServiceRequests: (userId?: string) =>
      request<ServiceRequest[]>(`/api/marketplace/services/requests${userId ? '?userId=' + userId : ''}`),
    createQuotation: (data: { requestId: string; teacherId: string; teacherName: string; amount: number; timelineDays: number; notes: string }) =>
      request<Quotation>('/api/marketplace/services/quotations', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    listQuotations: (requestId?: string) =>
      request<Quotation[]>(`/api/marketplace/services/quotations${requestId ? '?requestId=' + requestId : ''}`),
    acceptQuotation: (id: string, userId: string) =>
      request<Quotation>(`/api/marketplace/services/quotations/${id}/accept`, {
        method: 'POST',
        body: JSON.stringify({ userId }),
      }),
  },

  finance: {
    listTransactions: (userId?: string) =>
      request<Transaction[]>(`/api/finance/transactions${userId ? '?userId=' + userId : ''}`),
  },

  search: {
    globalSearch: (q: string) =>
      request<{
        books: Book[];
        courses: CourseStructure[];
        blogs: Blog[];
        tutorials: Tutorial[];
        services: Product[];
      }>(`/api/search?q=${encodeURIComponent(q)}`),
  },

  capabilities: {
    list: () => request<any[]>('/api/users/capabilities'),
    getMine: () => request<any[]>('/api/users/me/capabilities'),
    request: (code: string, applicationData?: any) =>
      request<any>(`/api/users/me/capabilities/${code}/request`, {
        method: 'POST',
        body: JSON.stringify({ application_data: applicationData }),
      }),
    deactivate: (code: string) =>
      request<any>(`/api/users/me/capabilities/${code}/deactivate`, {
        method: 'POST',
      }),
    reactivate: (code: string) =>
      request<any>(`/api/users/me/capabilities/${code}/reactivate`, {
        method: 'POST',
      }),
  },

  adminCapabilities: {
    listApplications: () => request<any[]>('/api/admin/capability-applications'),
    approveApplication: (id: string, notes?: string) =>
      request<any>(`/api/admin/capability-applications/${id}/approve`, {
        method: 'POST',
        body: JSON.stringify({ notes }),
      }),
    rejectApplication: (id: string, notes?: string) =>
      request<any>(`/api/admin/capability-applications/${id}/reject`, {
        method: 'POST',
        body: JSON.stringify({ notes }),
      }),
    suspendUserCapability: (userId: string, code: string) =>
      request<any>(`/api/admin/users/${userId}/capabilities/${code}/suspend`, {
        method: 'POST',
      }),
    reinstateUserCapability: (userId: string, code: string) =>
      request<any>(`/api/admin/users/${userId}/capabilities/${code}/reinstate`, {
        method: 'POST',
      }),
  },

  notifications: {
    list: (params?: { is_read?: boolean; category?: string; search?: string }) => {
      const q = new URLSearchParams();
      if (params) {
        if (params.is_read !== undefined) q.set('is_read', String(params.is_read));
        if (params.category) q.set('category', params.category);
        if (params.search) q.set('search', params.search);
      }
      const queryStr = q.toString();
      return request<any[]>(`/api/notifications/records${queryStr ? '?' + queryStr : ''}`);
    },
    markRead: (id: string) =>
      request<any>(`/api/notifications/records/${id}/read/`, {
        method: 'POST',
      }),
    markAllRead: () =>
      request<any>('/api/notifications/records/read-all/', {
        method: 'POST',
      }),
    getPreferences: () => request<any[]>('/api/notifications/preferences/'),
    updatePreference: (id: string, data: any) =>
      request<any>(`/api/notifications/preferences/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    getAnnouncements: () => request<any[]>('/api/notifications/announcements/'),
    getTemplates: () => request<any[]>('/api/notifications/templates/'),
  },
};
