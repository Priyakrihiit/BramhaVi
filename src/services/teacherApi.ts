/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { ApiResponse } from './api';

// Helper to make teacher API requests
async function teacherRequest<T>(url: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
  const token = localStorage.getItem('bvg_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      throw new Error(`HTTP error ${res.status}`);
    }
    const data = await res.json();
    return {
      success: true,
      data,
    };
  } catch (error) {
    console.warn(`Teacher API request on ${url} failed, using fallback:`, error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Network failure',
    };
  }
}

export const teacherApi = {
  // 1. Dashboard summary aggregation
  getDashboardSummary: () => teacherRequest<any>('/api/teacher/dashboard/summary/'),

  // 2. Instructor profiles management
  getProfile: (id: string) => teacherRequest<any>(`/api/teacher/profiles/${id}/`),
  updateProfile: (id: string, payload: any) => teacherRequest<any>(`/api/teacher/profiles/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  }),

  // 3. Wallet accounting
  getWallet: () => teacherRequest<any>('/api/teacher/wallet/'),

  // 4. Earnings logs
  getEarnings: (params?: any) => {
    let query = '';
    if (params) {
      query = '?' + new URLSearchParams(params).toString();
    }
    return teacherRequest<any>(`/api/teacher/earnings/${query}`);
  },

  // 5. Cohort batches
  getBatches: () => teacherRequest<any>('/api/teacher/batches/'),
  createBatch: (payload: any) => teacherRequest<any>('/api/teacher/batches/', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  // 6. Teaching sessions availability
  getSessions: () => teacherRequest<any>('/api/teacher/sessions/'),
  createSession: (payload: any) => teacherRequest<any>('/api/teacher/sessions/', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  // 7. Attendance logs
  getAttendance: (params?: any) => {
    let query = '';
    if (params) {
      query = '?' + new URLSearchParams(params).toString();
    }
    return teacherRequest<any>(`/api/teacher/attendance/${query}`);
  },
  markAttendance: (payload: any) => teacherRequest<any>('/api/teacher/attendance/', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  // 8. Courses syllabus management
  getCourses: () => teacherRequest<any>('/api/teacher/courses/'),

  // 9. Lessons management
  getLessons: () => teacherRequest<any>('/api/teacher/lessons/'),
  createLesson: (payload: any) => teacherRequest<any>('/api/teacher/lessons/', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  // 10. Assignments curation
  getAssignments: () => teacherRequest<any>('/api/teacher/assignments/'),
  createAssignment: (payload: any) => teacherRequest<any>('/api/teacher/assignments/', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  // 11. Submissions evaluation
  getSubmissions: () => teacherRequest<any>('/api/teacher/submissions/'),
  gradeSubmission: (id: string, grade: number, feedback: string) => teacherRequest<any>(`/api/teacher/submissions/${id}/grade-submission/`, {
    method: 'POST',
    body: JSON.stringify({ grade, feedback }),
  }),
};
