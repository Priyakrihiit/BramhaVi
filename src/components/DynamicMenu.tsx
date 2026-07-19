/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { useMenuStore } from '../stores/menuStore';
import { useLayoutStore } from '../stores/layoutStore';
import DynamicIcon from './DynamicIcon';

export const DynamicMenu: React.FC = () => {
  const { getVisibleHeaderMenus, getVisibleSubmenus } = useMenuStore();
  const { navigateTo, currentPath } = useLayoutStore();
  const headers = getVisibleHeaderMenus();

  return (
    <React.Fragment>
      <nav id="bvg-dynamic-navbar" className="hidden lg:flex items-center gap-6 text-sm font-medium text-slate-300">
        {headers.map(menu => {
          const submenus = getVisibleSubmenus(menu.id);
          const hasChildren = submenus.length > 0;
          const isActive = currentPath === menu.url || currentPath.startsWith(menu.url + '/');

          return (
            <div key={menu.id} className="relative group py-2">
              <button
                onClick={() => navigateTo(menu.url)}
                className={`flex items-center gap-1.5 transition duration-150 hover:text-indigo-400 ${isActive ? 'text-indigo-400 font-semibold' : 'text-slate-300'}`}
              >
                <DynamicIcon name={menu.icon} size={15} className="text-indigo-400 shrink-0" />
                <span>{menu.title}</span>
                {hasChildren && (
                  <svg className="w-3 h-3 text-slate-500 group-hover:text-indigo-400 transition-transform duration-150 group-hover:rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                )}
              </button>

              {hasChildren && (
                <div className="absolute top-full left-0 mt-1 w-56 bg-slate-900 border border-slate-800 rounded-lg p-2 shadow-2xl opacity-0 translate-y-2 pointer-events-none group-hover:opacity-100 group-hover:translate-y-0 group-hover:pointer-events-auto transition duration-200 z-50">
                  <div className="py-1 flex flex-col gap-0.5">
                    {submenus.map(sub => {
                      const isSubActive = currentPath === sub.url;
                      return (
                        <button
                          key={sub.id}
                          onClick={() => navigateTo(sub.url)}
                          className={`flex items-center gap-2.5 px-3 py-2 text-left rounded-md transition text-xs ${isSubActive ? 'bg-indigo-950 text-indigo-400 font-semibold' : 'hover:bg-slate-850 hover:text-indigo-300 text-slate-400'}`}
                        >
                          <DynamicIcon name={sub.icon} size={13} className={isSubActive ? 'text-indigo-400' : 'text-slate-500'} />
                          <span>{sub.title}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </nav>
    </React.Fragment>
  );
};

export default DynamicMenu;
