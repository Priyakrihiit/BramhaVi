/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useLayoutStore } from '../stores/layoutStore';
import DynamicIcon from './DynamicIcon';

interface SidebarItem {
  id: string;
  title: string;
  icon: string;
  path: string;
  requiredPermission?: string;
  children?: Omit<SidebarItem, 'children'>[];
}

const ADMIN_SIDEBAR_CONFIG: SidebarItem[] = [
  {
    id: 'dashboard',
    title: 'Platform Control Center',
    icon: 'ShieldCheck',
    path: '/admin/dashboard',
  },
  {
    id: 'syllabus',
    title: 'Curriculum & Syllabi',
    icon: 'BookOpen',
    path: '/admin/courses',
    requiredPermission: 'COURSE_WRITE',
  },
  {
    id: 'cms',
    title: 'Enterprise CMS Hub',
    icon: 'FolderOpen',
    path: '/admin/cms',
    requiredPermission: 'PAGE_WRITE',
  },
  {
    id: 'blogs',
    title: 'CMS Blogs',
    icon: 'FileText',
    path: '/admin/blogs',
    requiredPermission: 'PAGE_WRITE',
  },
  {
    id: 'tutorials',
    title: 'CMS Tutorials',
    icon: 'Bookmark',
    path: '/admin/tutorials',
    requiredPermission: 'PAGE_WRITE',
  },
  {
    id: 'menus',
    title: 'Navigation Nodes',
    icon: 'Layers',
    path: '/admin/menus',
    requiredPermission: 'MENU_WRITE',
  },
  {
    id: 'certificates',
    title: 'Accreditation Signer',
    icon: 'Award',
    path: '/admin/certificates',
    requiredPermission: 'CERT_WRITE',
  },
  {
    id: 'rbac',
    title: 'RBAC Authorization',
    icon: 'Users',
    path: '/admin/roles',
    requiredPermission: 'SUPER_ADMIN',
  },
  {
    id: 'analytics',
    title: 'Enterprise Analytics',
    icon: 'BarChart2',
    path: '/admin/analytics',
  },
  {
    id: 'settings',
    title: 'Platform Configurations',
    icon: 'Settings',
    path: '/admin/settings',
    requiredPermission: 'SUPER_ADMIN',
  },
];

export const DynamicSidebar: React.FC = () => {
  const { navigateTo, activeAdminTab } = useLayoutStore();
  const [collapsed, setCollapsed] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    academics: true,
  });

  const toggleGroup = (id: string) => {
    setExpandedGroups(prev => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <React.Fragment>
      <aside
        id="bvg-dynamic-sidebar"
        className={`bg-[#0b1329] border-r border-indigo-950/80 flex flex-col transition-all duration-300 h-full text-left ${collapsed ? 'w-16' : 'w-64'}`}
      >
        {/* Toggle Collapse Bar */}
        <div className="p-4 border-b border-indigo-950/80 flex items-center justify-between shrink-0">
          {!collapsed && (
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-indigo-500 animate-pulse"></span>
              <span className="text-[10px] font-bold text-indigo-300 uppercase tracking-widest">Control Panels</span>
            </div>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 hover:bg-slate-900 rounded-lg text-slate-400 hover:text-white transition shrink-0 ml-auto"
          >
            {collapsed ? (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
              </svg>
            )}
          </button>
        </div>

        {/* Sidebar Nav */}
        <nav className="flex-1 overflow-y-auto p-3 space-y-1.5 scrollbar-thin scrollbar-thumb-indigo-950">
          {ADMIN_SIDEBAR_CONFIG.map(item => {
            const isActive = activeAdminTab === item.id;
            const hasChildren = item.children && item.children.length > 0;
            const isExpanded = expandedGroups[item.id];

            return (
              <div key={item.id} className="space-y-1">
                <button
                  onClick={() => {
                    if (hasChildren) {
                      toggleGroup(item.id);
                    } else {
                      navigateTo(item.path);
                    }
                  }}
                  className={`w-full flex items-center rounded-xl p-2.5 transition text-xs relative ${isActive ? 'bg-indigo-600/25 text-indigo-200 border-l-2 border-indigo-500 font-semibold' : 'hover:bg-slate-900 text-slate-400 hover:text-slate-200'}`}
                >
                  <DynamicIcon name={item.icon} size={15} className={`shrink-0 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`} />
                  
                  {!collapsed && (
                    <React.Fragment>
                      <span className="ml-3 font-medium truncate">{item.title}</span>
                      {hasChildren && (
                        <svg className={`w-3 h-3 ml-auto text-slate-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      )}
                    </React.Fragment>
                  )}
                </button>

                {hasChildren && isExpanded && !collapsed && (
                  <div className="pl-6 space-y-1">
                    {item.children!.map(child => {
                      const isChildActive = activeAdminTab === child.id;
                      return (
                        <button
                          key={child.id}
                          onClick={() => navigateTo(child.path)}
                          className={`w-full text-left p-2 rounded-lg text-[11px] transition ${isChildActive ? 'text-indigo-400 font-semibold bg-slate-900' : 'text-slate-500 hover:text-slate-300 hover:bg-slate-950'}`}
                        >
                          {child.title}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </nav>

        {/* Footer info card */}
        {!collapsed && (
          <div className="p-4 border-t border-indigo-950/80 bg-slate-950/40 text-left shrink-0">
            <div className="bg-indigo-950/20 border border-indigo-900/30 rounded-xl p-3">
              <span className="block text-[9px] uppercase tracking-wider text-indigo-400 font-bold mb-1">System Core</span>
              <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                <span>V1.9 LEDGER</span>
                <span className="text-emerald-400">SYNCED</span>
              </div>
            </div>
          </div>
        )}
      </aside>
    </React.Fragment>
  );
};

export default DynamicSidebar;
