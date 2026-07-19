/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { NavigationMenu } from '../../types';
import { Layers, Plus, Trash2, Edit, Save, ToggleLeft, ToggleRight, ArrowUp, ArrowDown } from 'lucide-react';

export const MenusManagerShell: React.FC = () => {
  const [menus, setMenus] = useState<NavigationMenu[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedMenu, setSelectedMenu] = useState<NavigationMenu | null>(null);

  // Form Fields
  const [title, setTitle] = useState('');
  const [url, setUrl] = useState('');
  const [icon, setIcon] = useState('BookOpen');
  const [displayOrder, setDisplayOrder] = useState('0');
  const [isActive, setIsActive] = useState(true);
  const [parentId, setParentId] = useState<string>('');

  const loadMenus = async () => {
    setLoading(true);
    try {
      const res = await api.menus.list();
      if (res.success && res.data) {
        // Sort by parent then display order
        setMenus(res.data);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMenus();
  }, []);

  const selectMenuForEdit = (menu: NavigationMenu) => {
    setSelectedMenu(menu);
    setTitle(menu.title);
    setUrl(menu.url);
    setIcon(menu.icon);
    setDisplayOrder(String(menu.displayOrder));
    setIsActive(menu.isActive);
    setParentId(menu.parentId || '');
  };

  const handleCreateNew = () => {
    setSelectedMenu({
      id: 'new',
      parentId: null,
      title: 'New Navigation Node',
      url: '/new-url',
      icon: 'BookOpen',
      displayOrder: 0,
      isActive: true,
      requiredPermission: null
    });
    setTitle('');
    setUrl('');
    setIcon('BookOpen');
    setDisplayOrder('0');
    setIsActive(true);
    setParentId('');
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMenu) return;

    const menuData = {
      title,
      url,
      icon,
      displayOrder: parseInt(displayOrder) || 0,
      isActive,
      parentId: parentId || null,
      requiredPermission: null
    };

    try {
      let res;
      if (selectedMenu.id === 'new') {
        res = await api.menus.create(menuData);
      } else {
        res = await api.menus.update(selectedMenu.id, menuData);
      }

      if (res.success) {
        setSelectedMenu(null);
        await loadMenus();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this menu and all its child nodes?')) return;
    try {
      const res = await api.menus.delete(id);
      if (res.success) {
        if (selectedMenu?.id === id) {
          setSelectedMenu(null);
        }
        await loadMenus();
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 text-slate-500 font-mono text-xs">
        <span className="h-1.5 w-1.5 rounded-full bg-indigo-500 animate-ping mr-2"></span>
        Compiling navigation nodes...
      </div>
    );
  }

  // Group menus into parents and their children
  const parentMenus = menus.filter(m => !m.parentId);
  const getChildren = (parentId: string) => menus.filter(m => m.parentId === parentId);

  return (
    <React.Fragment>
      <div id="bvg-admin-menus" className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Menus Tree Layout */}
        <div className="lg:col-span-6 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Navigation Hierarchy</h3>
              <p className="text-xs text-slate-500">Manage structure, layout menus and submenus</p>
            </div>
            <button
              onClick={handleCreateNew}
              className="p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition shadow"
            >
              <Plus size={14} />
              Create Node
            </button>
          </div>

          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
            {parentMenus.map(parent => {
              const children = getChildren(parent.id);
              return (
                <div key={parent.id} className="bg-slate-950 border border-slate-850 rounded-xl overflow-hidden">
                  {/* Parent Item Row */}
                  <div className="p-3 bg-slate-900/60 flex items-center justify-between border-b border-slate-850">
                    <div className="flex items-center gap-2.5">
                      <Layers className="text-indigo-400" size={15} />
                      <div>
                        <span className="text-xs font-bold text-slate-200">{parent.title}</span>
                        <span className="block text-[9px] text-slate-500 font-mono">{parent.url} • ORDER: {parent.displayOrder}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => selectMenuForEdit(parent)}
                        className="p-1 text-slate-400 hover:text-white hover:bg-slate-800 rounded transition"
                      >
                        <Edit size={13} />
                      </button>
                      <button
                        onClick={() => handleDelete(parent.id)}
                        className="p-1 text-rose-500 hover:text-rose-400 hover:bg-slate-800 rounded transition"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </div>

                  {/* Children Items List */}
                  {children.length > 0 ? (
                    <div className="divide-y divide-slate-900/40 bg-slate-950">
                      {children.map(child => (
                        <div key={child.id} className="p-2.5 pl-8 flex items-center justify-between">
                          <div className="flex items-center gap-2 text-xs">
                            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500/60"></span>
                            <div>
                              <span className="font-semibold text-slate-300">{child.title}</span>
                              <span className="block text-[9px] text-slate-500 font-mono">{child.url} • ORDER: {child.displayOrder}</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-1.5">
                            <button
                              onClick={() => selectMenuForEdit(child)}
                              className="p-1 text-slate-400 hover:text-white hover:bg-slate-900 rounded transition"
                            >
                              <Edit size={12} />
                            </button>
                            <button
                              onClick={() => handleDelete(child.id)}
                              className="p-1 text-rose-500 hover:text-rose-400 hover:bg-slate-900 rounded transition"
                            >
                              <Trash2 size={12} />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-2.5 pl-8 text-[10px] text-slate-600 font-mono italic">
                      No nested submenu nodes registered.
                    </div>
                  )}
                </div>
              );
            })}

            {parentMenus.length === 0 && (
              <div className="py-12 text-center text-slate-500 italic text-xs">
                No custom navigation nodes registered. Create one to begin.
              </div>
            )}
          </div>
        </div>

        {/* Edit and Creation Form */}
        <div className="lg:col-span-6 p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Node Properties</h3>
            <p className="text-xs text-slate-500">Configure layout parameters, paths, and parentage</p>
          </div>

          {selectedMenu ? (
            <form onSubmit={handleSave} className="space-y-4 text-xs text-left">
              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold text-slate-500">Node Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  placeholder="e.g. My Profile"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-500">URL / Hash route</label>
                  <input
                    type="text"
                    required
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
                    placeholder="e.g. /profile"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-500">Icon Key</label>
                  <input
                    type="text"
                    required
                    value={icon}
                    onChange={(e) => setIcon(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
                    placeholder="e.g. User, Layers, BookOpen"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-500">Display Order</label>
                  <input
                    type="number"
                    value={displayOrder}
                    onChange={(e) => setDisplayOrder(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] uppercase font-bold text-slate-500">Parent Menu (Nesting)</label>
                  <select
                    value={parentId}
                    onChange={(e) => setParentId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-300 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  >
                    <option value="">-- No Parent (Root Item) --</option>
                    {parentMenus
                      .filter(m => m.id !== selectedMenu.id)
                      .map(p => (
                        <option key={p.id} value={p.id}>{p.title}</option>
                      ))
                    }
                  </select>
                </div>
              </div>

              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-850 flex items-center justify-between">
                <div>
                  <span className="block font-semibold text-slate-200">Active Visibility status</span>
                  <span className="block text-[10px] text-slate-500 font-mono">Render on portal navigation bars</span>
                </div>
                <button
                  type="button"
                  onClick={() => setIsActive(!isActive)}
                  className="text-indigo-400 hover:text-indigo-300"
                >
                  {isActive ? <ToggleRight size={32} /> : <ToggleLeft size={32} className="text-slate-600" />}
                </button>
              </div>

              <div className="pt-3 border-t border-slate-800 flex justify-between">
                <button
                  type="button"
                  onClick={() => setSelectedMenu(null)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-750 text-slate-300 rounded-lg font-semibold transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-semibold transition flex items-center gap-1.5 shadow"
                >
                  <Save size={13} />
                  Save Configurations
                </button>
              </div>
            </form>
          ) : (
            <div className="h-44 flex flex-col items-center justify-center border border-dashed border-slate-800 rounded-xl text-slate-500 font-serif italic text-xs">
              Select or create a navigation node from hierarchy to edit its fields
            </div>
          )}
        </div>

      </div>
    </React.Fragment>
  );
};

export default MenusManagerShell;
