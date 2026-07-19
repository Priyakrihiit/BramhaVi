/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { User } from '../types';
import { api } from '../services/api';

const ROLE_TO_CAPABILITIES: Record<string, string[]> = {
  'role-super-admin': ['ADMIN', 'TEACHING', 'AUTHORING', 'LEARNING', 'RESUME_BUILDER', 'PORTFOLIO_BUILDER', 'WEBSITE_BUILDER', 'COMMUNITY', 'AI_BASIC'],
  'role-teacher': ['TEACHING', 'LEARNING', 'RESUME_BUILDER', 'PORTFOLIO_BUILDER', 'WEBSITE_BUILDER', 'COMMUNITY', 'AI_BASIC'],
  'role-student': ['LEARNING', 'RESUME_BUILDER', 'PORTFOLIO_BUILDER', 'WEBSITE_BUILDER', 'COMMUNITY', 'AI_BASIC'],
  'role-content-creator': ['AUTHORING', 'LEARNING', 'RESUME_BUILDER', 'PORTFOLIO_BUILDER', 'WEBSITE_BUILDER', 'COMMUNITY', 'AI_BASIC'],
};

interface AuthContextType {
  currentUser: User | null;
  permissions: string[];
  isLoading: boolean;
  login: (email: string) => Promise<boolean>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
  hasPermission: (permissionCode: string) => boolean;
  hasAnyPermission: (permissionCodes: string[]) => boolean;
  hasCapability: (capabilityCode: string) => boolean;
  hasAnyCapability: (capabilityCodes: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [permissions, setPermissions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshProfile = useCallback(async () => {
    const token = localStorage.getItem('bvg_token');
    if (!token) {
      setCurrentUser(null);
      setPermissions([]);
      setIsLoading(false);
      return;
    }

    try {
      const res = await api.auth.getProfile();
      if (res.success && res.user) {
        setCurrentUser(res.user);
        setPermissions(res.permissions || []);
      } else {
        // Token is invalid/expired
        localStorage.removeItem('bvg_token');
        setCurrentUser(null);
        setPermissions([]);
      }
    } catch (err) {
      console.error('Failed to refresh profile:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string): Promise<boolean> => {
    setIsLoading(true);
    try {
      const res = await api.auth.login(email);
      if (res.success && res.user && res.token) {
        localStorage.setItem('bvg_token', res.token);
        setCurrentUser(res.user);
        await refreshProfile();
        return true;
      }
      return false;
    } catch (err) {
      console.error('Login error:', err);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('bvg_token');
    setCurrentUser(null);
    setPermissions([]);
  };

  const hasPermission = useCallback((permissionCode: string): boolean => {
    if (permissions.includes('SUPER_ADMIN')) return true;
    return permissions.includes(permissionCode);
  }, [permissions]);

  const hasAnyPermission = useCallback((permissionCodes: string[]): boolean => {
    if (permissions.includes('SUPER_ADMIN')) return true;
    return permissionCodes.some(code => permissions.includes(code));
  }, [permissions]);

  const hasCapability = useCallback((capabilityCode: string): boolean => {
    if (permissions.includes('SUPER_ADMIN')) return true;
    if (currentUser?.capabilities) {
      if (currentUser.capabilities.some(cap => cap.capabilityCode === capabilityCode && cap.status === 'ACTIVE')) {
        return true;
      }
    }
    if (currentUser?.roleId && ROLE_TO_CAPABILITIES[currentUser.roleId]?.includes(capabilityCode)) {
      return true;
    }
    return false;
  }, [currentUser, permissions]);

  const hasAnyCapability = useCallback((capabilityCodes: string[]): boolean => {
    if (permissions.includes('SUPER_ADMIN')) return true;
    return capabilityCodes.some(code => hasCapability(code));
  }, [hasCapability, permissions]);

  useEffect(() => {
    refreshProfile();
  }, [refreshProfile]);

  return (
    <React.Fragment>
      <AuthContext.Provider
        value={{
          currentUser,
          permissions,
          isLoading,
          login,
          logout,
          refreshProfile,
          hasPermission,
          hasAnyPermission,
          hasCapability,
          hasAnyCapability,
        }}
      >
        {children}
      </AuthContext.Provider>
    </React.Fragment>
  );
};

export const useAuthStore = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthStore must be used within an AuthProvider');
  }
  return context;
};
