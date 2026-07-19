import React, { useState, useEffect } from 'react';
import { Bell, CheckCheck, Settings, Mail, MessageSquare, Smartphone, Eye, EyeOff, Plus, Trash2, RefreshCw } from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { api } from '../services/api';

export const NotificationCenter: React.FC = () => {
  const { currentUser } = useAuthStore();
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'notifications' | 'preferences' | 'templates'>('notifications');
  
  // Data States
  const [notifications, setNotifications] = useState<any[]>([]);
  const [preferences, setPreferences] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  // Status Indicators
  const [isLoading, setIsLoading] = useState(false);
  const [hasError, setHasError] = useState(false);

  const loadData = async () => {
    setIsLoading(true);
    setHasError(false);
    try {
      if (activeTab === 'notifications') {
        const res = await api.notifications.list();
        // Django results are typically inside the response body directly, or paginated
        const list = Array.isArray(res.data) ? res.data : (res.data as any).results || [];
        setNotifications(list);
        setUnreadCount(list.filter((n: any) => !n.is_read).length);
      } else if (activeTab === 'preferences') {
        const res = await api.notifications.getPreferences();
        setPreferences(Array.isArray(res.data) ? res.data : []);
      } else if (activeTab === 'templates') {
        const res = await api.notifications.getTemplates();
        setTemplates(Array.isArray(res.data) ? res.data : []);
      }
    } catch (err) {
      console.error('[NOTIFICATIONS CLIENT ERROR] Failed to fetch data:', err);
      setHasError(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (currentUser) {
      loadData();
    }
  }, [activeTab, currentUser]);

  // Live polling refresh loop (every 30s)
  useEffect(() => {
    if (!currentUser) return;
    const interval = setInterval(() => {
      // Quiet background refresh for unread count indicator
      api.notifications.list({ is_read: false }).then(res => {
        const list = Array.isArray(res.data) ? res.data : (res.data as any).results || [];
        setUnreadCount(list.length);
      }).catch(err => console.debug('Quiet notification refresh skipped:', err.message));
    }, 30000);
    return () => clearInterval(interval);
  }, [currentUser]);

  // Real-time EventSource listener
  useEffect(() => {
    if (!currentUser?.id) return;

    const eventSource = new EventSource(`/api/realtime/notifications?userId=${currentUser.id}`);

    eventSource.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.event === 'notification') {
          // Instantly inject new notification into state list
          setNotifications(prev => [payload.data, ...prev]);
          setUnreadCount(c => c + 1);
        }
      } catch (err) {
        console.debug('Skip heartbeats/connected event parsing.');
      }
    };

    eventSource.onerror = () => {
      console.warn('Real-time notification stream disconnected. Reconnecting...');
    };

    return () => {
      eventSource.close();
    };
  }, [currentUser]);

  const markAllAsRead = async () => {
    try {
      await api.notifications.markAllRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true, read_at: new Date().toISOString() })));
      setUnreadCount(0);
    } catch (err) {
      console.error('[NOTIFICATIONS CLIENT ERROR] Mark all read failed:', err);
    }
  };

  const toggleReadStatus = async (id: string, currentlyRead: boolean) => {
    try {
      if (!currentlyRead) {
        await api.notifications.markRead(id);
        setNotifications(prev => prev.map(n => {
          if (n.id === id) {
            setUnreadCount(c => Math.max(0, c - 1));
            return { ...n, is_read: true, read_at: new Date().toISOString() };
          }
          return n;
        }));
      }
    } catch (err) {
      console.error('[NOTIFICATIONS CLIENT ERROR] Mark read failed:', err);
    }
  };

  const togglePreference = async (prefId: string, channel: 'email' | 'sms' | 'push') => {
    const targetPref = preferences.find(p => p.id === prefId);
    if (!targetPref) return;

    const channelKey = `${channel}_enabled`;
    const nextValue = !targetPref[channelKey];
    
    try {
      await api.notifications.updatePreference(prefId, { [channelKey]: nextValue });
      setPreferences(prev => prev.map(p => {
        if (p.id === prefId) {
          return { ...p, [channelKey]: nextValue };
        }
        return p;
      }));
    } catch (err) {
      console.error('[NOTIFICATIONS CLIENT ERROR] Update preference failed:', err);
    }
  };

  const isAdmin = currentUser?.role === 'SUPERADMIN' || currentUser?.role === 'ADMIN';

  return (
    <div className="relative">
      {/* Bell Trigger */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-xl bg-slate-900 border border-indigo-950 text-slate-400 hover:text-white transition cursor-pointer"
      >
        <Bell size={15} className={unreadCount > 0 ? "animate-bounce" : ""} />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-rose-500 text-white text-[9px] font-black rounded-full flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </button>

      {/* Drawer Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-3 w-80 bg-[#0d1329] border border-indigo-950/80 rounded-2xl shadow-2xl p-4 z-50 text-xs text-slate-300">
          <div className="flex items-center justify-between border-b border-indigo-950/60 pb-2 mb-3">
            <span className="font-bold text-white tracking-tight">Notification Center</span>
            <div className="flex items-center gap-2">
              <button onClick={loadData} className="text-slate-500 hover:text-white cursor-pointer">
                <RefreshCw size={11} className={isLoading ? "animate-spin" : ""} />
              </button>
              {unreadCount > 0 && (
                <button 
                  onClick={markAllAsRead}
                  className="text-[10px] text-indigo-400 hover:text-indigo-300 flex items-center gap-1 cursor-pointer"
                >
                  <CheckCheck size={11} /> Mark all read
                </button>
              )}
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex gap-2 mb-3 border-b border-indigo-950/40 pb-2">
            <button 
              onClick={() => setActiveTab('notifications')}
              className={`pb-1 px-1 font-bold ${activeTab === 'notifications' ? 'text-indigo-400 border-b border-indigo-400' : 'text-slate-500'}`}
            >
              Alerts
            </button>
            <button 
              onClick={() => setActiveTab('preferences')}
              className={`pb-1 px-1 font-bold ${activeTab === 'preferences' ? 'text-indigo-400 border-b border-indigo-400' : 'text-slate-500'}`}
            >
              Preferences
            </button>
            {isAdmin && (
              <button 
                onClick={() => setActiveTab('templates')}
                className={`pb-1 px-1 font-bold ${activeTab === 'templates' ? 'text-indigo-400 border-b border-indigo-400' : 'text-slate-500'}`}
              >
                Templates
              </button>
            )}
          </div>

          {/* Loading Skeleton */}
          {isLoading && (
            <div className="space-y-2 py-4">
              <div className="h-10 bg-slate-900/60 animate-pulse rounded-lg"></div>
              <div className="h-10 bg-slate-900/60 animate-pulse rounded-lg"></div>
              <div className="h-10 bg-slate-900/60 animate-pulse rounded-lg"></div>
            </div>
          )}

          {/* Error State */}
          {hasError && !isLoading && (
            <div className="text-center py-6">
              <p className="text-rose-400 font-bold mb-2">Connection failed</p>
              <button onClick={loadData} className="px-3 py-1 bg-indigo-650 text-white rounded font-bold hover:bg-indigo-600 transition">
                Retry
              </button>
            </div>
          )}

          {/* Tab Content */}
          {!isLoading && !hasError && (
            <>
              {activeTab === 'notifications' && (
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="text-center py-6 text-slate-500">No new alerts.</div>
                  ) : (
                    notifications.map(n => (
                      <div 
                        key={n.id} 
                        className={`p-2.5 rounded-lg border transition ${n.is_read ? 'bg-slate-950/20 border-slate-900 text-slate-400' : 'bg-indigo-950/20 border-indigo-900 text-white'}`}
                      >
                        <div className="flex justify-between items-start gap-1">
                          <span className="font-bold">{n.title}</span>
                          {!n.is_read && (
                            <button 
                              onClick={() => toggleReadStatus(n.id, n.is_read)}
                              className="text-indigo-400 hover:text-white cursor-pointer"
                            >
                              <Eye size={11} />
                            </button>
                          )}
                        </div>
                        <p className="text-[10px] mt-1 text-slate-400">{n.content}</p>
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'preferences' && (
                <div className="space-y-3">
                  {preferences.length === 0 ? (
                    <div className="text-center py-6 text-slate-500">No categories loaded.</div>
                  ) : (
                    preferences.map(p => (
                      <div key={p.id} className="flex justify-between items-center border-b border-indigo-950/40 pb-2">
                        <span className="font-mono text-indigo-300 font-bold uppercase">{p.category}</span>
                        <div className="flex gap-2">
                          <button 
                            onClick={() => togglePreference(p.id, 'email')}
                            className={`p-1 rounded ${p.email_enabled ? 'text-indigo-400 bg-indigo-950/50' : 'text-slate-600'}`}
                          >
                            <Mail size={12} />
                          </button>
                          <button 
                            onClick={() => togglePreference(p.id, 'sms')}
                            className={`p-1 rounded ${p.sms_enabled ? 'text-indigo-400 bg-indigo-950/50' : 'text-slate-600'}`}
                          >
                            <MessageSquare size={12} />
                          </button>
                          <button 
                            onClick={() => togglePreference(p.id, 'push')}
                            className={`p-1 rounded ${p.push_enabled ? 'text-indigo-400 bg-indigo-950/50' : 'text-slate-600'}`}
                          >
                            <Smartphone size={12} />
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'templates' && (
                <div className="space-y-2">
                  <div className="flex justify-between mb-2">
                    <span className="font-bold text-slate-400">Manage Templates</span>
                  </div>
                  {templates.length === 0 ? (
                    <div className="text-center py-6 text-slate-500">No templates found.</div>
                  ) : (
                    templates.map(t => (
                      <div key={t.id} className="p-2 bg-slate-900 border border-slate-800 rounded-lg flex justify-between items-center">
                        <div>
                          <span className="font-bold block">{t.name}</span>
                          <span className="text-[9px] text-slate-500 font-mono">{t.code}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};
