/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { ApiResponse } from './api';

// Helper to make live classes API requests
async function liveRequest<T>(url: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
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
    console.warn(`Live API request on ${url} failed:`, error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Network failure',
    };
  }
}

export const liveApi = {
  // 1. Live Classes CRUD & Actions
  getLiveClasses: () => liveRequest<any[]>('/api/v1/live/live-classes/'),
  createLiveClass: (payload: any) => liveRequest<any>('/api/v1/live/live-classes/', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  startSession: (id: string) => liveRequest<any>(`/api/v1/live/live-classes/${id}/start-session/`, {
    method: 'POST',
  }),
  endSession: (id: string) => liveRequest<any>(`/api/v1/live/live-classes/${id}/end-session/`, {
    method: 'POST',
  }),
  recordAttendance: (id: string, payload: any) => liveRequest<any>(`/api/v1/live/live-classes/${id}/record-attendance/`, {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  createPoll: (id: string, payload: any) => liveRequest<any>(`/api/v1/live/live-classes/${id}/create-poll/`, {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  // 2. Chat messages
  getChatMessages: (liveClassId: string) => liveRequest<any[]>(`/api/v1/live/chat-messages/?live_class_id=${liveClassId}`),
  sendChatMessage: (payload: any) => liveRequest<any>('/api/v1/live/chat-messages/', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  // 3. Whiteboards
  getWhiteboards: (liveClassId: string) => liveRequest<any[]>(`/api/v1/live/whiteboards/?live_class_id=${liveClassId}`),
  saveWhiteboard: (payload: any) => liveRequest<any>('/api/v1/live/whiteboards/', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  // 4. Poll votes
  castVote: (pollId: string, optionId: string) => liveRequest<any>(`/api/v1/live/polls/${pollId}/vote/`, {
    method: 'POST',
    body: JSON.stringify({ option_id: optionId }),
  }),

  // 5. Recordings
  getRecordings: (liveClassId: string) => liveRequest<any[]>(`/api/v1/live/recordings/?live_class_id=${liveClassId}`),

  // 6. Calendar Events
  getCalendarEvents: () => liveRequest<any[]>('/api/v1/live/calendar-events/'),

  // 7. Reminders
  getReminders: () => liveRequest<any[]>('/api/v1/live/reminders/'),
  createReminder: (payload: any) => liveRequest<any>('/api/v1/live/reminders/', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
};
