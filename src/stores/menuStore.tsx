/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { NavigationMenu } from '../types';
import { api } from '../services/api';
import { useAuthStore } from './authStore';

interface MenuContextType {
  menus: NavigationMenu[];
  isLoading: boolean;
  refreshMenus: () => Promise<void>;
  getVisibleHeaderMenus: () => NavigationMenu[];
  getVisibleSubmenus: (parentId: string) => NavigationMenu[];
  addMenu: (menu: Omit<NavigationMenu, 'id' | 'isActive'>) => Promise<boolean>;
  editMenu: (id: string, menu: Partial<NavigationMenu>) => Promise<boolean>;
  deleteMenu: (id: string) => Promise<boolean>;
}

const MenuContext = createContext<MenuContextType | undefined>(undefined);

export const MenuProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [menus, setMenus] = useState<NavigationMenu[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const { hasPermission } = useAuthStore();

  const refreshMenus = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await api.menus.list();
      if (res.success && res.data) {
        setMenus(res.data);
      }
    } catch (err) {
      console.error('Failed to load navigation menus:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getVisibleHeaderMenus = useCallback((): NavigationMenu[] => {
    return menus
      .filter(m => m.isActive && !m.parentId)
      .filter(m => {
        if (!m.requiredPermission) return true;
        return hasPermission(m.requiredPermission);
      })
      .sort((a, b) => a.displayOrder - b.displayOrder);
  }, [menus, hasPermission]);

  const getVisibleSubmenus = useCallback((parentId: string): NavigationMenu[] => {
    return menus
      .filter(m => m.isActive && m.parentId === parentId)
      .filter(m => {
        if (!m.requiredPermission) return true;
        return hasPermission(m.requiredPermission);
      })
      .sort((a, b) => a.displayOrder - b.displayOrder);
  }, [menus, hasPermission]);

  const addMenu = async (menuData: Omit<NavigationMenu, 'id' | 'isActive'>): Promise<boolean> => {
    try {
      const res = await api.menus.create({
        ...menuData,
        isActive: true,
      });
      if (res.success) {
        await refreshMenus();
        return true;
      }
      return false;
    } catch (err) {
      console.error('Failed to add menu:', err);
      return false;
    }
  };

  const editMenu = async (id: string, menuData: Partial<NavigationMenu>): Promise<boolean> => {
    try {
      const res = await api.menus.update(id, menuData);
      if (res.success) {
        await refreshMenus();
        return true;
      }
      return false;
    } catch (err) {
      console.error('Failed to edit menu:', err);
      return false;
    }
  };

  const deleteMenu = async (id: string): Promise<boolean> => {
    try {
      const res = await api.menus.delete(id);
      if (res.success) {
        await refreshMenus();
        return true;
      }
      return false;
    } catch (err) {
      console.error('Failed to delete menu:', err);
      return false;
    }
  };

  useEffect(() => {
    refreshMenus();
  }, [refreshMenus]);

  return (
    <React.Fragment>
      <MenuContext.Provider
        value={{
          menus,
          isLoading,
          refreshMenus,
          getVisibleHeaderMenus,
          getVisibleSubmenus,
          addMenu,
          editMenu,
          deleteMenu,
        }}
      >
        {children}
      </MenuContext.Provider>
    </React.Fragment>
  );
};

export const useMenuStore = () => {
  const context = useContext(MenuContext);
  if (!context) {
    throw new Error('useMenuStore must be used within a MenuProvider');
  }
  return context;
};
