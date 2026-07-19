/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { ApiResponse } from './api';

// Helper to make student API requests
async function studentRequest<T>(url: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
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
    console.warn(`Student API request on ${url} failed, using local/fallback mechanism:`, error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Network failure',
    };
  }
}

// Interfaces for Student Dashboard Models
export interface LearningHistory {
  id: string;
  student: string;
  enrollment: string;
  node: string;
  node_title?: string;
  accessed_at: string;
}

export interface ContinueLearning {
  id: string;
  student: string;
  enrollment: string;
  course_title: string;
  last_node: string;
  last_node_title: string;
  last_accessed_at: string;
}

export interface Bookmark {
  id: string;
  student: string;
  content_type: string;
  content_id: string;
  title: string;
  source_name: string;
  url_path: string;
  note?: string;
  created_at: string;
}

export interface StudentNote {
  id: string;
  student: string;
  node: string;
  node_title?: string;
  title: string;
  content: string;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
}

export interface StudyGoal {
  id: string;
  student: string;
  title: string;
  description?: string;
  target_date: string;
  progress_percentage: number;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'OVERDUE';
}

export interface StudySession {
  id: string;
  student: string;
  node?: string;
  node_title?: string;
  started_at: string;
  ended_at?: string;
  duration_seconds: number;
  is_active: boolean;
}

export interface StudyCalendarEvent {
  id: string;
  student: string;
  title: string;
  description?: string;
  starts_at: string;
  ends_at: string;
  node?: string;
}

export interface DailyProgress {
  id: string;
  date: string;
  minutes_spent: number;
  xp_gained: number;
}

export interface WeeklyProgress {
  id: string;
  week_start: string;
  minutes_spent: number;
  xp_gained: number;
}

export interface MonthlyProgress {
  id: string;
  year: number;
  month: number;
  minutes_spent: number;
  xp_gained: number;
}

export interface LearningStreak {
  id: string;
  current_streak: number;
  longest_streak: number;
  last_active_date: string;
  total_xp: number;
  current_level: number;
}

export interface Achievement {
  id: string;
  code: string;
  title: string;
  description: string;
  category: string;
  xp_reward: number;
  icon_name?: string;
}

export interface StudentAchievement {
  id: string;
  student: string;
  achievement: Achievement;
  unlocked_at: string;
}

export interface StudentPreference {
  id: string;
  student: string;
  daily_target_minutes: number;
  compact_sidebar: boolean;
}

export interface LearningReminder {
  id: string;
  student: string;
  title: string;
  message?: string;
  remind_at: string;
  is_sent: boolean;
}

export interface DashboardSummary {
  streak: LearningStreak;
  daily_progress: DailyProgress[];
  weekly_progress: WeeklyProgress[];
  monthly_progress: MonthlyProgress[];
  achievements: StudentAchievement[];
  recent_bookmarks: Bookmark[];
  continue_learning: ContinueLearning[];
  upcoming_goals: StudyGoal[];
  upcoming_events: StudyCalendarEvent[];
}

export const studentApi = {
  // Aggregate Summary Endpoint
  getSummary: () => studentRequest<DashboardSummary>('/api/student/dashboard/summary/'),

  // Learning History
  listHistory: () => studentRequest<LearningHistory[]>('/api/student/history/'),
  
  // Continue Learning
  listContinueLearning: () => studentRequest<ContinueLearning[]>('/api/student/continue-learning/'),

  // Bookmarks
  listBookmarks: () => studentRequest<Bookmark[]>('/api/student/bookmarks/'),
  toggleBookmark: (data: { content_type: string; content_id: string; title: string; source_name?: string; url_path?: string; note?: string }) =>
    studentRequest<{ created: boolean; bookmark?: Bookmark }>('/api/student/bookmarks/toggle/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Notes
  listNotes: () => studentRequest<StudentNote[]>('/api/student/notes/'),
  createNote: (data: { node: string; title: string; content: string }) =>
    studentRequest<StudentNote>('/api/student/notes/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateNote: (id: string, data: Partial<StudentNote>) =>
    studentRequest<StudentNote>(`/api/student/notes/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  deleteNote: (id: string) =>
    studentRequest<void>(`/api/student/notes/${id}/`, {
      method: 'DELETE',
    }),
  pinNote: (id: string) =>
    studentRequest<{ is_pinned: boolean }>(`/api/student/notes/${id}/pin/`, {
      method: 'POST',
    }),

  // Goals
  listGoals: () => studentRequest<StudyGoal[]>('/api/student/goals/'),
  createGoal: (data: { title: string; description?: string; target_date: string; status?: string }) =>
    studentRequest<StudyGoal>('/api/student/goals/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateGoal: (id: string, data: Partial<StudyGoal>) =>
    studentRequest<StudyGoal>(`/api/student/goals/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  updateGoalProgress: (id: string, data: { progress_percentage: number; status?: string }) =>
    studentRequest<StudyGoal>(`/api/student/goals/${id}/update_progress/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  deleteGoal: (id: string) =>
    studentRequest<void>(`/api/student/goals/${id}/`, {
      method: 'DELETE',
    }),

  // Sessions / Study Timer
  listSessions: () => studentRequest<StudySession[]>('/api/student/sessions/'),
  startSession: (data: { node?: string }) =>
    studentRequest<StudySession>('/api/student/sessions/start_session/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  endSession: (id: string) =>
    studentRequest<StudySession>(`/api/student/sessions/${id}/end_session/`, {
      method: 'POST',
    }),

  // Calendar
  listCalendarEvents: () => studentRequest<StudyCalendarEvent[]>('/api/student/calendar-events/'),
  createCalendarEvent: (data: { title: string; description?: string; starts_at: string; ends_at: string }) =>
    studentRequest<StudyCalendarEvent>('/api/student/calendar-events/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Streak & Gamification
  getStreak: () => studentRequest<LearningStreak>('/api/student/streaks/'),
  listAchievements: () => studentRequest<Achievement[]>('/api/student/achievements/'),
  listStudentAchievements: () => studentRequest<StudentAchievement[]>('/api/student/student-achievements/'),

  // Preferences
  getPreferences: () => studentRequest<StudentPreference[]>('/api/student/preferences/'),
  updatePreferences: (id: string, data: Partial<StudentPreference>) =>
    studentRequest<StudentPreference>(`/api/student/preferences/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
};
