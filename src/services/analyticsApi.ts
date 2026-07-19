import { ApiResponse } from './api';

export interface AnalyticsEvent {
  id?: string;
  metric_name: string;
  metric_value: number;
  context_data?: Record<string, any>;
  created_at?: string;
}

export interface UserSession {
  id?: string;
  session_key: string;
  ip_address?: string;
  device_type?: string;
  browser_type?: string;
  country?: string;
  login_at?: string;
  logout_at?: string;
  is_active?: boolean;
}

export interface DashboardWidget {
  id?: string;
  title: string;
  metric_type: string;
  query_target: string;
  color_scheme: string;
  icon_name: string;
  display_order: number;
  is_active: boolean;
}

export interface DashboardStats {
  generated_at: string;
  role: string;
  widgets: {
    id: string;
    title: string;
    value: string;
    color: string;
    icon: string;
  }[];
}

export interface KPI {
  id?: string;
  name: string;
  metric_key: string;
  current_value: number;
  target_value: number;
  status: string;
}

export interface DailySummary {
  id?: string;
  summary_date: string;
  metric_name?: string;
  value: number;
  change_percentage: number;
}

export interface TimeseriesData {
  metric: string;
  days_limit: number;
  timeseries: {
    label: string;
    value: number;
    change: number;
  }[];
}

export interface ExportJob {
  id?: string;
  job_type: string;
  status?: string;
  file_url?: string;
  error_message?: string;
  request_payload?: Record<string, any>;
  created_at?: string;
}

export interface ReportSchedule {
  id?: string;
  report_title: string;
  frequency: string;
  recipients: string[];
  next_run_at: string;
  is_active: boolean;
}

const BASE_URL = '/api/v1/analytics';

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
    return {
      success: res.ok,
      status: res.status,
      data: res.ok ? data : null,
      error: res.ok ? null : (data.detail || data.error || 'Request failed'),
    };
  } catch (err: any) {
    return {
      success: false,
      status: 500,
      data: null,
      error: err.message || 'Network error',
    };
  }
}

export const analyticsApi = {
  events: {
    list: () => request<AnalyticsEvent[]>(`${BASE_URL}/events/`),
    collect: (payload: { metric_name: string; metric_value?: number; context_data?: Record<string, any>; session_key?: string }) =>
      request<AnalyticsEvent>(`${BASE_URL}/events/collect/`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  },
  sessions: {
    list: () => request<UserSession[]>(`${BASE_URL}/sessions/`),
    start: (payload: Partial<UserSession>) =>
      request<UserSession>(`${BASE_URL}/sessions/start/`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    end: (session_key: string) =>
      request<UserSession>(`${BASE_URL}/sessions/end/`, {
        method: 'POST',
        body: JSON.stringify({ session_key }),
      }),
  },
  dashboard: {
    stats: () => request<DashboardStats>(`${BASE_URL}/dashboards/statistics/`),
  },
  widgets: {
    list: () => request<DashboardWidget[]>(`${BASE_URL}/widgets/`),
    create: (widget: Partial<DashboardWidget>) =>
      request<DashboardWidget>(`${BASE_URL}/widgets/`, {
        method: 'POST',
        body: JSON.stringify(widget),
      }),
    update: (id: string, widget: Partial<DashboardWidget>) =>
      request<DashboardWidget>(`${BASE_URL}/widgets/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(widget),
      }),
    delete: (id: string) =>
      request<null>(`${BASE_URL}/widgets/${id}/`, {
        method: 'DELETE',
      }),
  },
  kpis: {
    list: () => request<KPI[]>(`${BASE_URL}/kpis/`),
    create: (kpi: Partial<KPI>) =>
      request<KPI>(`${BASE_URL}/kpis/`, {
        method: 'POST',
        body: JSON.stringify(kpi),
      }),
    update: (id: string, kpi: Partial<KPI>) =>
      request<KPI>(`${BASE_URL}/kpis/${id}/`, {
        method: 'PUT',
        body: JSON.stringify(kpi),
      }),
    delete: (id: string) =>
      request<null>(`${BASE_URL}/kpis/${id}/`, {
        method: 'DELETE',
      }),
  },
  summaries: {
    list: () => request<DailySummary[]>(`${BASE_URL}/summaries/`),
    timeseries: (metric: string, days = 30) =>
      request<TimeseriesData>(`${BASE_URL}/summaries/timeseries/?metric=${metric}&days=${days}`),
  },
  exports: {
    list: () => request<ExportJob[]>(`${BASE_URL}/exports/`),
    create: (job_type: string) =>
      request<ExportJob>(`${BASE_URL}/exports/`, {
        method: 'POST',
        body: JSON.stringify({ job_type }),
      }),
  },
  schedules: {
    list: () => request<ReportSchedule[]>(`${BASE_URL}/schedules/`),
    create: (schedule: Partial<ReportSchedule>) =>
      request<ReportSchedule>(`${BASE_URL}/schedules/`, {
        method: 'POST',
        body: JSON.stringify(schedule),
      }),
    delete: (id: string) =>
      request<null>(`${BASE_URL}/schedules/${id}/`, {
        method: 'DELETE',
      }),
  },
};
