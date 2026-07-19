/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useAuthStore } from '../stores/authStore';

export function useAuth() {
  const {
    currentUser,
    permissions,
    isLoading,
    login,
    logout,
    hasPermission,
    hasAnyPermission,
    hasCapability,
    hasAnyCapability,
  } = useAuthStore();

  const isSuperAdmin = hasPermission('SUPER_ADMIN') || hasCapability('ADMIN');
  const isTeacher = hasCapability('TEACHING');
  const isStudent = hasCapability('LEARNING') && !isTeacher && !isSuperAdmin;

  return {
    user: currentUser,
    permissions,
    isLoading,
    login,
    logout,
    isSuperAdmin,
    isTeacher,
    isStudent,
    canManageMenus: hasPermission('MENU_WRITE') || hasCapability('ADMIN'),
    canManagePages: hasPermission('PAGE_WRITE') || hasCapability('ADMIN'),
    canManageCourses: hasPermission('COURSE_WRITE') || hasCapability('TEACHING'),
    canIssueCertificates: hasPermission('CERT_WRITE') || hasCapability('TEACHING'),
    canManageUsers: hasPermission('USER_WRITE') || hasCapability('ADMIN'),
    canUseAI: hasPermission('AI_ACCESS') || hasCapability('AI_BASIC') || hasCapability('AI_PREMIUM'),
    hasPermission,
    hasAnyPermission,
    hasCapability,
    hasAnyCapability,
  };
}
export default useAuth;
